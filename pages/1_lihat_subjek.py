import streamlit as st
import sqlite3
import pandas as pd

# Konfigurasi halaman
st.set_page_config(page_title="Paparan Senarai Subjek")
st.title("📂 Paparan Senarai Subjek Kursus")

# Fungsi sambungan ke pangkalan data
def create_connection():
    return sqlite3.connect("database/edufile.db", check_same_thread=False)

# Sambung ke DB
conn = create_connection()
c = conn.cursor()

# Ambil semua subjek
df = pd.read_sql_query("SELECT * FROM subjects", conn)

# Dapatkan senarai program
programs = sorted(df['program'].dropna().unique().tolist())
selected_program = st.selectbox("🎓 Pilih Program", ["Semua"] + programs)

# Tapis ikut program
if selected_program != "Semua":
    df = df[df['program'] == selected_program]

# Susun dan papar jadual
df = df[['subject_code', 'subject_name', 'program', 'role', 'lecturer_username']].sort_values(by="subject_code")
df = df.rename(columns={
    "subject_code": "Kod Kursus",
    "subject_name": "Nama Kursus",
    "program": "Program",
    "role": "Peranan",
    "lecturer_username": "Username Pensyarah"
})
st.dataframe(df, use_container_width=True)

conn.close()
