import streamlit as st
import sqlite3
import pandas as pd

# Konfigurasi halaman
st.set_page_config(page_title="Paparan Senarai Subjek")
st.title("📂 Paparan Senarai Subjek")

# Fungsi sambungan ke pangkalan data
def create_connection():
    return sqlite3.connect("database/fskm_course_filing.db", check_same_thread=False)

# Sambung ke DB
conn = create_connection()
c = conn.cursor()

# Ambil semua data subjek
df = pd.read_sql_query("SELECT * FROM subjects", conn)

# Pilihan penapis
programs = sorted(df['program_code'].dropna().unique().tolist())
semesters = sorted(df['semester'].dropna().unique().tolist())

selected_program = st.selectbox("🎓 Pilih Program", ["Semua"] + programs)
selected_semester = st.selectbox("📘 Pilih Semester", ["Semua"] + semesters)

# Penapisan
if selected_program != "Semua":
    df = df[df['program_code'] == selected_program]
if selected_semester != "Semua":
    df = df[df['semester'] == selected_semester]

# Susun dan papar jadual
df = df[['subject_code', 'subject_name', 'program_code', 'semester']].sort_values(by="subject_code")
st.dataframe(df, use_container_width=True)

conn.close()
