import streamlit as st
import psycopg2
import pandas as pd

st.title("PostgreSQL Connection App")

# --- Action 1: Manual Connection Test ---
if st.button("Connect to DB"):
    try:
        # Attempt to connect to your PostgreSQL database
        connection = psycopg2.connect(
            host="localhost",
            database="dbfde",
            user="fde",
            password="dbfde",
            port="5432"
        )
        
        # Display success message if connection works
        st.success("Successfully connected to targeted Database and User of PostgreSQL!")
        
        # Close the connection safely
        connection.close()
        
    except Exception as e:
        # Display error message if connection fails
        st.error(f"Connection failed: {e}")

st.divider() # Visual separation between the two features

# --- Action 2: Fetch Data using Streamlit Secrets ---
if st.button("Fetch Databases and Users"):
    try:
        # 1. Initialize the built-in PostgreSQL SQL connection
        # This automatically safely pulls credentials from .streamlit/secrets.toml
        conn = st.connection("postgresql", type="sql")

        # 2. Fetch all databases from the system catalog
        # Setting ttl=0 ensures we bypass caching to see live database updates
        db_query = "SELECT datname AS database_name FROM pg_database WHERE datistemplate = false;"
        df_databases = conn.query(db_query, ttl=0)

        # 3. Fetch all users/roles from the system catalog
        user_query = "SELECT usename AS username, usesuper AS is_superuser FROM pg_user;"
        df_users = conn.query(user_query, ttl=0)

        # ---- Display Layout ----
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🗄️ Available Databases")
            if not df_databases.empty:
                st.dataframe(df_databases, use_container_width=True)
            else:
                st.warning("No databases found.")
                
        with col2:
            st.subheader("👥 Database Users")
            if not df_users.empty:
                st.dataframe(df_users, use_container_width=True)
            else:
                st.warning("No users found.")
                
    except Exception as e:
        st.error(f"Failed to fetch metadata: {e}")