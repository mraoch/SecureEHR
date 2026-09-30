import csv
from pathlib import Path
import re
import pandas as pd
import streamlit as st
import psycopg2
from psycopg2 import sql

# Set Streamlit page layout to wide
st.set_page_config(layout="wide")

# ========================================================
# CONFIGURATION & GLOBAL CONSTANTS
# ========================================================
FILE_PATH = Path(r"D:\EHR\SecureEHR\data\data.csv")

DB_CONFIG = {
    "dbname": "dbfde",
    "user": "postgres",       
    "password": "123",        
    "host": "localhost",
    "port": "5432"
}

TABLE_NAME = "patient_records"

# ========================================================
# DATABASE PIPELINE HELPER FUNCTIONS
# ========================================================
def sync_csv_to_postgres(file_path, db_config, table_name=TABLE_NAME):
    """Dynamically drops, creates, and populates the Postgres table from the CSV."""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            rows = list(reader)
        
        clean_headers = [h.strip().lower().replace(" ", "_").replace("-", "_") for h in headers]
        
        cursor.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name)))
        columns_schema = ", ".join([f"{h} TEXT" for h in clean_headers])
        cursor.execute(f"CREATE TABLE {table_name} ({columns_schema});")
        
        insert_query = sql.SQL("INSERT INTO {} VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(sql.Placeholder() * len(clean_headers))
        )
        
        for row in rows:
            if len(row) < len(clean_headers):
                row.extend([''] * (len(clean_headers) - len(row)))
            cursor.execute(insert_query, row[:len(clean_headers)])
            
        conn.commit()
        cursor.close()
        conn.close()
        return True, len(clean_headers), len(rows), headers
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        return False, 0, 0, str(e)


def append_record_to_postgres(db_config, form_data, table_name=TABLE_NAME):
    """Appends a single manual form entry into the database table."""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        columns = [sql.Identifier(k) for k in form_data.keys()]
        values = list(form_data.values())
        
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(columns),
            sql.SQL(', ').join(sql.Placeholder() * len(values))
        )
        
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Record successfully validated and appended!"
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        return False, str(e)


def fetch_live_db_data(db_config, table_name=TABLE_NAME):
    """Fetches up-to-date data from Postgres to display in the preview."""
    try:
        conn = psycopg2.connect(**db_config)
        df_live = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df_live
    except Exception as e:
        return None

# ========================================================
# DATA VALIDATION ENGINE
# ========================================================
def validate_ehr_inputs(form_inputs):
    """Validates dictionary input based on standard EHR fields."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    phone_regex = r"^\+?[1-9]\d{1,14}$"  
    date_regex = r"^\d{4}-\d{2}-\d{2}$"  

    for key, value in form_inputs.items():
        clean_val = value.strip()
        
        if any(req in key for req in ["id", "name", "primary"]) and not clean_val:
            return False, f"The field **'{key.replace('_', ' ').title()}'** is a mandatory record attribute."
            
        if clean_val:
            if "age" in key:
                if not clean_val.isdigit() or not (0 <= int(clean_val) <= 125):
                    return False, f"Invalid value in **Age**: '{value}'. Must be between 0 and 125."
            
            elif "email" in key:
                if not re.match(email_regex, clean_val):
                    return False, f"Invalid format in **Email**: '{value}'."
            
            elif "phone" in key or "contact" in key:
                stripped_phone = clean_val.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                if not re.match(phone_regex, stripped_phone):
                    return False, f"Invalid entry in **Phone**: '{value}'."
            
            elif "date" in key:
                if not re.match(date_regex, clean_val):
                    return False, f"Invalid format in **Date**: '{value}'. Use YYYY-MM-DD."
                    
            elif "gender" in key:
                if clean_val.lower() not in ["male", "female", "other", "m", "f", "u", "unknown"]:
                    return False, f"Unrecognised entry in **Gender**: '{value}'."

    return True, "Passed structural validation checks."


# ========================================================
# MAIN APP EXECUTION (STREAMLIT UI)
# ========================================================
def main():
    st.title("📋 SecureEHR Database Sync & Form Management")

    # 1. Validation check for file path existence [1]
    if not FILE_PATH.exists():
        st.error(f"Could not find the local CSV file at: '{FILE_PATH}'. Please verify the path exists.")
        return

    # 2. Extract Headers safely
    try:
        with open(FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header_list = next(reader)
            header_count = len(header_list)       
    except Exception as file_err:
        st.error(f"Failed to read local CSV file layout: {file_err}")
        return
    
    clean_headers_list = [h.strip().lower().replace(" ", "_").replace("-", "_") for h in header_list]

    # 3. Initial database setup tracking
    if 'db_synced' not in st.session_state:
        with st.spinner("Initial database setup..."):
            sync_csv_to_postgres(FILE_PATH, DB_CONFIG)
        st.session_state['db_synced'] = True

    # 4. System Control Room Panel
    st.subheader("⚙️ System Control Room")
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        st.info("💡 Field constraints (Age limits, Emails format, Date structures) are systematically applied upon entry execution below.")
    with action_col2:
        st.write("") 
        if st.button("🔄 Trigger CSV Re-Sync", use_container_width=True, type="primary"):
            with st.spinner("Overwriting data structures..."):
                success, col_count, row_count, result_data = sync_csv_to_postgres(FILE_PATH, DB_CONFIG)
            if success:
                st.toast("Database reset completely from CSV!", icon="🔄")
                st.rerun()  
            else:
                st.error(f"Sync failed: {result_data}")

    # 5. Custom Schema Matrix Mapping Layout (💡 Fixed text layout closure spacing error)
    comma_delimited_text = ", ".join(header_list)
    html_cells = "".join(f"<td>📦 {h}</td>" for h in clean_headers_list)
    
    html_table = f"""
    <style>
        .custom-table {{ width: 100%; border-collapse: collapse; font-family: 'Segoe UI', sans-serif; text-align: center; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .custom-table th, .custom-table td {{ border: 1px solid #e0e0e0; padding: 12px; }}
        .merged-row {{ background-color: #2e7d32; color: white; font-weight: bold; font-size: 1.05em; }}
        .individual-row {{ background-color: #f9f9f9; color: #333333; font-weight: 600; }}
    </style>
    <table class="custom-table">
        <thead>
            <tr class="merged-row"><th colspan="{header_count}">Active Database Table Columns: ({comma_delimited_text})</th></tr>
        </thead>
        <tbody>
            <tr class="individual-row">{html_cells}</tr>
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)
    st.write("")

    # 6. DATA ENTRY FORM WITH VALIDATION ENGINES
    st.markdown("---")
    st.subheader("📝 Secure Manual Record Insertion Form")
    
    with st.form("manual_append_form", clear_on_submit=False):
        st.write("Ensure your entry data follows format constraints before clicking upload:")
        
        form_inputs = {}
        input_cols = st.columns(3)
        
        for index, field_name in enumerate(clean_headers_list):
            current_col = input_cols[index % 3]
            with current_col:
                pretty_label = field_name.replace("_", " ").title()
                
                hint = ""
                if "date" in field_name: hint = " (YYYY-MM-DD)"
                elif "age" in field_name: hint = " (0-125)"
                elif "id" in field_name or "name" in field_name: hint = " *" 
                
                form_inputs[field_name] = st.text_input(label=f"Enter {pretty_label}{hint}", key=f"input_{field_name}")

        submit_button = st.form_submit_button(label="➕ Validate & Append Record", type="secondary")
        
        if submit_button:
            if all(val.strip() == "" for val in form_inputs.values()):
                st.warning("⚠️ Empty inputs detected. Row compilation skipped.")
            else:
                is_valid, validation_msg = validate_ehr_inputs(form_inputs)
                
                if not is_valid:
                    st.error(f"🚨 **Validation Failure:** {validation_msg}")
                else:
                    is_valid, validation_msg = validate_ehr_inputs(form_inputs)