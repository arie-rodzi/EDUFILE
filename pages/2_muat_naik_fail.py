# Create the new Streamlit module for uploading files using the updated database structure

upload_module_code = """
import streamlit as st
import sqlite3
import os
from datetime import datetime

st.set_page_config(page_title="Muat Naik Fail Kursus", layout="wide")
st.title("📤 Muat Naik Fail Kursus (Versi Baharu)")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Sambungan ke pangkalan data
def create_connection():
    return sqlite3.connect("database/edufile_final.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Dapatkan subjek berdasarkan username
if "username" not in st.session_state:
    st.warning("Sila log masuk dahulu.")
    st.stop()

c.execute("SELECT subject_code, subject_name FROM subjects WHERE lecturer_username = ?", (st.session_state.username,))
subjects = c.fetchall()
subject_dict = {code: name for code, name in subjects}

if not subject_dict:
    st.warning("Anda tidak mempunyai subjek yang ditugaskan.")
    st.stop()

# Borang muat naik
selected_code = st.selectbox("Pilih Subjek", list(subject_dict.keys()), format_func=lambda x: f"{x} - {subject_dict[x]}")
file_type = st.selectbox("Jenis Fail", ["RPS", "RPH", "Rubrik", "Nota", "Soalan", "Kuiz", "Ujian", "Assignment", "JSU", "CQI", "EES"])
file_description = st.text_input("Nama Penuh Fail / Tajuk", placeholder="Contoh: Assessment 1 STA602 Oct2023-Feb2024")
uploaded_file = st.file_uploader("Pilih Fail PDF", type=["pdf"])

if uploaded_file and file_description and st.button("Muat Naik"):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    clean_desc = file_description.replace(" ", "_").replace("/", "_")
    filename = f"{selected_code}_{file_type}_{clean_desc}_{timestamp}.pdf"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Simpan fail
    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())

    # Simpan ke pangkalan data
    c.execute(\"""
        INSERT INTO uploaded_files (subject_code, file_type, file_description, filename, uploaded_by, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?)
    \""", (selected_code, file_type, file_description, filename, st.session_state.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    st.success("✅ Fail berjaya dimuat naik!")

elif uploaded_file and not file_description:
    st.warning("Sila isikan nama penuh atau tajuk fail sebelum muat naik.")

# Papar senarai fail
st.markdown("---")
st.subheader("📁 Senarai Fail Telah Dimuat Naik")

df_uploaded = c.execute(\"""
    SELECT file_type, file_description, filename, uploaded_at
    FROM uploaded_files
    WHERE subject_code = ? AND uploaded_by = ?
\""", (selected_code, st.session_state.username)).fetchall()

if df_uploaded:
    for ftype, fdesc, fname, uploaded_at in df_uploaded:
        st.markdown(f"- **{ftype}** | {fdesc} \n\n`{fname}` *(Dimuat naik: {uploaded_at})*")
else:
    st.info("Tiada fail dimuat naik untuk subjek ini.")

conn.close()
"""

# Save the module
module_path = "/mnt/data/2_muat_naik_fail.py"
with open(module_path, "w", encoding="utf-8") as f:
    f.write(upload_module_code)

module_path
