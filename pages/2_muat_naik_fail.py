import streamlit as st
import sqlite3
import os
from datetime import datetime

st.set_page_config(page_title="Muat Naik Fail Kursus")
st.title("📤 Muat Naik Fail Kursus (Untuk LIC Sahaja)")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Sambungan ke pangkalan data
def create_connection():
    return sqlite3.connect("database/fskm_course_filing.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Dapatkan subjek yang diurus oleh LIC ini
c.execute("SELECT subject_code, subject_name FROM subjects WHERE lic_staff_id = ?", (st.session_state.user_id,))
subjects = c.fetchall()
subject_dict = {code: name for code, name in subjects}

if not subject_dict:
    st.warning("Anda tidak mempunyai subjek yang ditugaskan sebagai LIC.")
    st.stop()

# Borang muat naik
selected_code = st.selectbox("Pilih Subjek", list(subject_dict.keys()), format_func=lambda x: f"{x} - {subject_dict[x]}")
file_type = st.selectbox("Jenis Fail", ["RPS", "RPH", "Rubrik", "Nota", "Soalan", "Kuiz", "Ujian", "Assignment"])
file_description = st.text_input("Tajuk Fail / Keterangan", placeholder="Contoh: Assignment 1, Kuiz Topik 2")

uploaded_file = st.file_uploader("Pilih Fail PDF", type=["pdf"])

if uploaded_file and file_description and st.button("Muat Naik"):
    # Format nama fail
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    clean_desc = file_description.replace(" ", "_").replace("/", "_")
    filename = f"{selected_code}_{file_type}_{clean_desc}_{timestamp}.pdf"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Simpan fail
    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())

    # Simpan ke pangkalan data
    c.execute(
        "INSERT INTO uploaded_files (subject_code, file_type, filename, uploaded_by, uploaded_at) VALUES (?, ?, ?, ?, ?)",
        (selected_code, file_type, filename, st.session_state.user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    st.success("✅ Fail berjaya dimuat naik!")

elif uploaded_file and not file_description:
    st.warning("Sila isikan tajuk atau keterangan fail sebelum muat naik.")

conn.close()
