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

# Guna username sebagai kunci
c.execute("SELECT subject_code, subject_name FROM subjects WHERE lecturer_username = ?", (st.session_state.username,))
subjects = c.fetchall()
subject_dict = {code: name for code, name in subjects}

if not subject_dict:
    st.warning("Anda tidak mempunyai subjek yang ditugaskan.")
    st.stop()

# Borang muat naik
selected_code = st.selectbox("Pilih Subjek", list(subject_dict.keys()), format_func=lambda x: f"{x} - {subject_dict[x]}")
file_type = st.selectbox("Jenis Fail", ["RPS", "RPH", "Rubrik", "Nota", "Soalan", "Kuiz", "Ujian", "Assignment"])
file_description = st.text_input("Tajuk Fail / Keterangan", placeholder="Contoh: Assignment 1, Kuiz Topik 2")
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
    c.execute("""
        INSERT INTO uploaded_files (subject_code, file_type, filename, uploaded_by, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
    """, (selected_code, file_type, filename, st.session_state.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    st.success("✅ Fail berjaya dimuat naik!")

elif uploaded_file and not file_description:
    st.warning("Sila isikan tajuk atau keterangan fail sebelum muat naik.")

# Papar senarai fail yang telah dimuat naik
st.markdown("---")
st.subheader("📁 Senarai Fail Telah Dimuat Naik")
df_uploaded = c.execute("""
    SELECT file_type, filename, uploaded_at
    FROM uploaded_files
    WHERE subject_code = ? AND uploaded_by = ?
""", (selected_code, st.session_state.username)).fetchall()

# Semakan status lengkap
required_types = ["RPS", "RPH", "Rubrik", "Nota", "Soalan", "Kuiz", "Ujian", "Assignment"]
uploaded_types = set(row[0] for row in df_uploaded)

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### ✅ Status Fail Subjek")
    for ft in required_types:
        status = "✅" if ft in uploaded_types else "❌"
        st.markdown(f"- **{ft}**: {status}")

with col2:
    st.markdown("#### 📊 Fail Dimuat Naik")
    if df_uploaded:
        for ftype, fname, uploaded_at in df_uploaded:
            st.markdown(f"- **{ftype}**: `{fname}` *(Dimuat naik: {uploaded_at})*")
    else:
        st.info("Tiada fail dimuat naik untuk subjek ini.")

conn.close()
