import pandas as pd
import streamlit as st

st.title("Read Local CSV and Print Headers")

# Load the local CSV file
df = pd.read_csv("D:\EHR\SecureEHR\data\data.csv")

# Display the headers/column names
st.subheader("CSV Headers:")
st.write(list(df.columns))

# Optional: Display the full dataframe
st.subheader("Full Data:")
st.write(df)
