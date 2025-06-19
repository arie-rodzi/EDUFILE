
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Paparan Senarai Subjek")
st.title("📂 Paparan Senarai Subjek")

# Sambung ke pangkalan data
def create_connection():
    return sqlite3.connect("database/fskm_course_filing.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Dapatkan semua subjek
df = pd.read_sql_query("SELECT * FROM subjects", conn)

# Paparan penapis
programs = df['program_code'].unique().tolist()
semesters = df['semester'].unique().tolist()

selected_program = st.selectbox("Pilih Program", ["Semua"] + programs)
selected_semester = st.selectbox("Pilih Semester", ["Semua"] + semesters)

# Penapisan data
if selected_program != "Semua":
    df = df[df['program_code'] == selected_program]
if selected_semester != "Semua":
    df = df[df['semester'] == selected_semester]

# Papar jadual
st.dataframe(df[['subject_code', 'subject_name', 'program_code', 'semester']], use_container_width=True)

conn.close()
