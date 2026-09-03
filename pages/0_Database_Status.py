import os
import streamlit as st

st.set_page_config(page_title="Database Status", page_icon="🗄️")
st.title("🗄️ Database Status")
st.caption("Private diagnostic page for verifying the CMA Coach database connection.")

url = os.getenv("CMA_DATABASE_URL")

if not url:
    st.error("CMA_DATABASE_URL is not set. The app is using SQLite.")
else:
    st.info("CMA_DATABASE_URL is set in the running app.")
    try:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(
            url,
            row_factory=dict_row,
            connect_timeout=10,
            sslmode="require",
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database() AS database_name, current_user AS database_user")
                info = cur.fetchone()
                cur.execute("SELECT COUNT(*) AS attempt_count FROM attempts")
                count = cur.fetchone()["attempt_count"]

        st.success("Connected to Supabase/PostgreSQL successfully.")
        st.write(f"**Database:** `{info['database_name']}`")
        st.write(f"**User:** `{info['database_user']}`")
        st.write(f"**Attempts currently stored in Supabase:** `{count}`")
    except Exception as exc:
        st.error("CMA_DATABASE_URL is set, but the database connection failed.")
        st.code(str(exc), language="text")
