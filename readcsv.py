import csv
import pandas as pd
import streamlit as st

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
