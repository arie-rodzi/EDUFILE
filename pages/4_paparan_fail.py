import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Muat Naik & Papar Fail Subjek")
st.title("📤📄 Muat Naik & Paparan Fail Subjek")

# Fungsi sambungan ke DB
def create_connection():
    return sqlite3.connect("database/fskm_course_filing.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Dapatkan senarai subjek
subject_df = pd.read_sql_query("SELECT subject_code, subject_name FROM subjects", conn)
subject_dict = dict(zip(subject_df.subject_code, subject_df.subject_name))

# Pilihan subjek
selected_code = st.selectbox("Pilih Subjek", list(subject_dict.keys()))
selected_name = subject_dict[selected_code]
st.markdown(f"### Fail untuk {selected_code} - {selected_name}")

# --- BORANG MUAT NAIK ---
with st.expander("📤 Muat Naik Fail Baharu"):
    uploaded_file = st.file_uploader("Pilih fail PDF untuk dimuat naik", type=["pdf"])
    file_type = st.selectbox("Jenis Fail", ["Course Info", "SOW", "RPS", "Nota", "Tutorial", "Soalan", "Lain-lain"])
    uploaded_by = st.text_input("Nama Pengguna")
    if st.button("Muat Naik"):
        if uploaded_file and uploaded_by:
            uploads_dir = "uploads"
            os.makedirs(uploads_dir, exist_ok=True)
            filepath = os.path.join(uploads_dir, uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.read())

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("""
                INSERT INTO uploaded_files (subject_code, file_type, filename, uploaded_by, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (selected_code, file_type, uploaded_file.name, uploaded_by, now))
            conn.commit()
            st.success("✅ Fail berjaya dimuat naik.")
            st.rerun()
        else:
            st.warning("Sila pilih fail dan isi nama pengguna.")

# --- PAPARAN FAIL ---
st.markdown("### 📄 Senarai Fail Dimuat Naik")
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
        try:
            with open(filepath, "rb") as f:
                st.download_button("⬇️ Muat Turun", f, file_name=row['filename'], mime="application/pdf")
        except FileNotFoundError:
            st.warning(f"❌ Fail tidak ditemui: {row['filename']}")
else:
    st.info("Tiada fail dimuat naik untuk subjek ini.")

conn.close()
