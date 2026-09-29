import csv
import pandas as pd
import streamlit as st

"""
# 1. MUST BE FIRST: Configure the page layout
st.set_page_config(
    page_title="Responsive Data App", layout="wide", initial_sidebar_state="expanded"
)

# Define the file path correctly using a raw string (r"...")
FILE_PATH = r"D:\EHR\SecureEHR\data\data.csv"

st.title("📋 Local CSV Viewer")

try:
    # 2. Extract headers via the csv module (Fast & prints to terminal console)
    with open(FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header_list = next(reader)       

    # 3. Load the data using Pandas for Streamlit rendering
    df = pd.read_csv(FILE_PATH)

    # 4. Display the headers in the browser UI
    st.subheader("CSV Headers:")
    
    # ⬇️ FIXED: Define the badges variable before using it in st.markdown
    badges = "".join([
        f'<span style="background-color: #f0f2f6; color: #31333F; padding: 6px 12px; '
        f'margin: 4px 6px; border-radius: 16px; font-weight: 500; '
        f'font-family: monospace; display: inline-block;">{h}</span>' 
        for h in header_list
    ])

    # Render the badges horizontally as HTML
    st.markdown(badges, unsafe_allow_html=True)
    
    # Optional spacing
    st.write("") 

    # 5. Display the full interactive dataframe in wide layout
    st.subheader("Full Data:")
    st.dataframe(df, use_container_width=True)
    
except FileNotFoundError:
    st.error(f"Could not find the file at: '{FILE_PATH}'. Please verify the path exists.")
"""

# 1. Read only the header row from your CSV file
# (Replace 'your_file.csv' with your actual file path or uploaded file buffer)
try:
    df = pd.read_csv("your_file.csv", nrows=0)
    headers_list = df.columns.tolist()
except FileNotFoundError:
    # Fallback placeholder for demonstration
    headers_list = ["First Name", "Last Name", "Age", "Country", "Occupation"]

# 2. Join the headers into a single comma-delimited text string
comma_delimited_text = ", ".join(headers_list)

# 3. Build a custom HTML table layout
# Row 1 merges all cells to show the full comma-delimited text string.
# Row 2 contains each individual header string inside its own individual cell.
num_columns = len(headers_list)

html_table = f"""
<style>
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        text-align: center;
    }}
    .custom-table th, .custom-table td {{
        border: 1px solid #ddd;
        padding: 12px;
    }}
    .merged-row {{
        background-color: #f4f4f4;
        font-weight: bold;
        color: #333;
    }}
    .individual-row {{
        background-color: #ffffff;
        color: #555;
    }}
</style>

<table class="custom-table">
    <thead>
        <!-- Row 1: Merged across all column cells -->
        <tr class="merged-row">
            <th colspan="{num_columns}">{comma_delimited_text}</th>
        </tr>
    </thead>
    <tbody>
        <!-- Row 2: Each header in an individual cell -->
        <tr class="individual-row">
            {"".join(f"<td>{header}</td>" for header in headers_list)}
        </tr>
    </tbody>
</table>
"""

# 4. Render the table in Streamlit
st.title("CSV Header Display Matrix")
st.markdown(html_table, unsafe_allow_html=True)