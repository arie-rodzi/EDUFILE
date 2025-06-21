import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Paparan Senarai Subjek")
st.title("📂 Paparan Senarai Subjek Kursus")

def create_connection():
    return sqlite3.connect("database/edufile.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Ambil semua subjek
df = pd.read_sql_query("SELECT * FROM subjects", conn)

# Semakan kolum 'program' wujud dan tidak kosong
if 'program' in df.columns and not df['program'].dropna().empty:
    programs = sorted(df['program'].dropna().unique().tolist())
    selected_program = st.selectbox("🎓 Pilih Program", ["Semua"] + programs)
else:
    st.warning("Kolum 'program' tidak dijumpai atau tiada data.")
    selected_program = "Semua"

# Tapis ikut program
if selected_program != "Semua":
    df = df[df['program'] == selected_program]

# Susun kolum jika wujud
expected_cols = ['subject_code', 'subject_name', 'program', 'role', 'lecturer_username']
df_cols = [col for col in expected_cols if col in df.columns]
df = df[df_cols]

# Tukar nama paparan
rename_map = {
    "subject_code": "Kod Kursus",
    "subject_name": "Nama Kursus",
    "program": "Program",
    "role": "Peranan",
    "lecturer_username": "Username Pensyarah"
}
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

# Papar
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Tiada data untuk dipaparkan.")

conn.close()
