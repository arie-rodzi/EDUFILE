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
    return sqlite3.connect("database/edufile.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Semak login
if "username" not in st.session_state or not st.session_state.logged_in:
    st.warning("Sila log masuk terlebih dahulu.")
    st.stop()

# Semak peranan
if st.session_state.user_role != "LIC":
    st.warning("Modul ini hanya untuk pengguna dengan peranan LIC.")
    st.stop()

# Dapatkan subjek yang diurus oleh LIC ini
c.execute("SELECT subject_code, subject_name FROM subjects WHERE lecturer_username = ? AND role = 'LIC'", (st.session_state.username,))
subjects = c.fetchall()
subject_dict = {code: name for code, name in subjects}

if not subject_dict:
    st.warning("Anda tidak mempunyai subjek yang ditugaskan sebagai LIC.")
    st.stop()

# Borang muat naik
selected_code = st.selectbox("🎓 Pilih Subjek", list(subject_dict.keys()), format_func=lambda x: f"{x} - {subject_dict[x]}")
file_type = st.selectbox("📁 Jenis Fail", ["1. Pelan Pengajian", "2. Silibus", "3. Jadual Spesifikasi", "4. EES", "5. Penilaian Berterusan", "6. Peperiksaan Akhir", "7. Analisis CDL–CQI"])
file_description = st.text_input("📝 Tajuk Fail / Keterangan", placeholder="Contoh: Assignment 1, Kuiz Topik 2")
uploaded_file = st.file_uploader("📤 Pilih Fail PDF", type=["pdf"])

if uploaded_file and file_description and st.button("Muat Naik"):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    clean_desc = file_description.replace(" ", "_").replace("/", "_")
    filename = f"{selected_code}_{file_type.split('.')[0]}_{clean_desc}_{timestamp}.pdf"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Simpan fail fizikal
    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())

    # Simpan maklumat ke DB
    c.execute("""
        INSERT INTO uploads (subject_code, category, file_name, uploader, upload_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        selected_code, file_type, filename,
        st.session_state.username,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    st.success("✅ Fail berjaya dimuat naik!")

elif uploaded_file and not file_description:
    st.warning("❗ Sila isikan tajuk atau keterangan fail sebelum muat naik.")

conn.close()
