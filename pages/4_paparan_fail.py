import streamlit as st
import sqlite3
import pandas as pd
import os
import zipfile
import io

st.set_page_config(page_title="Paparan & Muat Turun Fail Subjek")
st.title("📄📦 Paparan Fail Subjek & Muat Turun Semua")

# Sambungan ke DB
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

# Paparkan fail yang dimuat naik
query = "SELECT file_type, filename, uploaded_by, uploaded_at FROM uploaded_files WHERE subject_code=?"
df_files = pd.read_sql_query(query, conn, params=(selected_code,))

if not df_files.empty:
    st.markdown("#### 📃 Senarai Fail")
    for _, row in df_files.iterrows():
        filepath = os.path.join("uploads", row['filename'])
        col1, col2, col3 = st.columns([4, 3, 3])
        col1.markdown(f"**📁 {row['file_type']}**")
        col2.markdown(f"👤 Oleh: {row['uploaded_by']}")
        col3.markdown(f"🕒 {row['uploaded_at']}")
        try:
            with open(filepath, "rb") as f:
                st.download_button("⬇️ Muat Turun", f, file_name=row['filename'], mime="application/pdf")
        except FileNotFoundError:
            st.warning(f"❌ Fail tidak ditemui: {row['filename']}")

    # --- ZIP & Download Semua ---
    st.markdown("---")
    if st.button("📦 Muat Turun Semua Fail Sebagai ZIP"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for _, row in df_files.iterrows():
                filepath = os.path.join("uploads", row['filename'])
                if os.path.exists(filepath):
                    zipf.write(filepath, arcname=row['filename'])

        zip_buffer.seek(0)
        st.download_button(
            label="📥 Klik untuk Muat Turun ZIP",
            data=zip_buffer,
            file_name=f"{selected_code}_fail_subjek.zip",
            mime="application/zip"
        )

else:
    st.info("Tiada fail dimuat naik untuk subjek ini.")

conn.close()
