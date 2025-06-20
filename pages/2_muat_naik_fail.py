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

# Semak log masuk
if "user_id" not in st.session_state or not st.session_state.logged_in:
    st.warning("Sila log masuk terlebih dahulu.")
    st.stop()

# Dapatkan subjek LIC
c.execute("SELECT subject_code, subject_name FROM subjects WHERE lic_staff_id = ?", (st.session_state.user_id,))
subjects = c.fetchall()
subject_dict = {code: name for code, name in subjects}

if not subject_dict:
    st.warning("Anda tidak mempunyai subjek yang ditugaskan sebagai LIC.")
    st.stop()

selected_code = st.selectbox("📘 Pilih Subjek", list(subject_dict.keys()), format_func=lambda x: f"{x} – {subject_dict[x]}")

# --- SENARAI FAIL YANG TELAH DIMUAT NAIK ---
st.subheader("📄 Senarai Fail Yang Telah Dimuat Naik")
c.execute("SELECT file_type, file_description, filename, uploaded_at FROM uploaded_files WHERE subject_code=? ORDER BY uploaded_at DESC", (selected_code,))
rows = c.fetchall()

if rows:
    for row in rows:
        st.markdown(f"""
        ✅ **{row[0]} – {row[1]}**  
        🕒 {row[3]}  
        📎 `{row[2]}`  
        """)
else:
    st.info("Tiada fail dimuat naik untuk subjek ini.")

st.divider()

# --- BORANG MUAT NAIK ---
st.subheader("📥 Muat Naik Fail Baharu")
file_type = st.selectbox("Jenis Fail", ["RPS", "RPH", "Rubrik", "Nota", "Soalan", "Kuiz", "Ujian", "Assignment"])
file_description = st.text_input("Tajuk Fail / Keterangan", placeholder="Contoh: Assignment 1, Kuiz Topik 2")
uploaded_file = st.file_uploader("Pilih Fail PDF", type=["pdf"])

if uploaded_file and file_description and st.button("Muat Naik"):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    clean_desc = file_description.replace(" ", "_").replace("/", "_")
    filename = f"{selected_code}_{file_type}_{clean_desc}_{timestamp}.pdf"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())

    c.execute(
        "INSERT INTO uploaded_files (subject_code, file_type, file_description, filename, uploaded_by, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
        (selected_code, file_type, file_description, filename, st.session_state.user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    st.success("✅ Fail berjaya dimuat naik.")
    st.rerun()

elif uploaded_file and not file_description:
    st.warning("Sila isikan tajuk atau keterangan fail sebelum muat naik.")

conn.close()
