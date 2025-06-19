import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd
import os
import base64

# Konfigurasi halaman
st.set_page_config(page_title="Paparan & Muat Turun Fail Subjek")
st.title("📄📥 Paparan Fail Subjek & Muat Turun")

# Fungsi sambungan ke DB
def create_connection():
    return sqlite3.connect("database/fskm_course_filing.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Dapatkan senarai subjek
subject_df = pd.read_sql_query("SELECT subject_code, subject_name FROM subjects", conn)
subject_dict = dict(zip(subject_df.subject_code, subject_df.subject_name))

# Pilih subjek
selected_code = st.selectbox("Pilih Subjek", list(subject_dict.keys()))
selected_name = subject_dict[selected_code]
st.markdown(f"### Fail untuk {selected_code} - {selected_name}")

# Fungsi paparan PDF
def show_pdf_base64(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>
    """
    components.html(pdf_display, height=620)

# Dapatkan fail
query = """
    SELECT file_type, filename, uploaded_by, uploaded_at 
    FROM uploaded_files 
    WHERE subject_code=?
"""
df_files = pd.read_sql_query(query, conn, params=(selected_code,))

if not df_files.empty:
    for _, row in df_files.iterrows():
        filepath = os.path.join("uploads", row['filename'])

        col1, col2, col3 = st.columns([4, 3, 3])
        col1.markdown(f"**📁 {row['file_type']}**")
        col2.markdown(f"👤 Oleh: {row['uploaded_by']}")
        col3.markdown(f"🕒 {row['uploaded_at']}")

        # Papar PDF dalam base64
        if row['filename'].endswith(".pdf") and os.path.exists(filepath):
            show_pdf_base64(filepath)

        # Butang Muat Turun
        try:
            with open(filepath, "rb") as f:
                st.download_button("⬇️ Muat Turun", f, file_name=row['filename'], mime="application/pdf")
        except FileNotFoundError:
            st.warning(f"❌ Fail tidak ditemui: {row['filename']}")
else:
    st.info("Tiada fail dimuat naik untuk subjek ini.")

conn.close()
