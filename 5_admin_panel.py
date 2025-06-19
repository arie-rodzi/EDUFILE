
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Panel Admin")
st.title("⚙️ Panel Pentadbir")

# Sambung ke database
def create_connection():
    return sqlite3.connect("database/fskm_course_filing.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# SEMAKAN PENGGUNA
st.header("📋 Senarai Pengguna")
df_users = pd.read_sql_query("SELECT user_id, name, role, email FROM users", conn)
st.dataframe(df_users, use_container_width=True)

# SEMAKAN SUBJEK
st.header("📚 Senarai Subjek & LIC")
df_subjects = pd.read_sql_query("SELECT * FROM subjects", conn)

# Padankan nama LIC dari users
user_map = df_users.set_index('user_id')['name'].to_dict()
df_subjects['LIC'] = df_subjects['lic_staff_id'].map(user_map)
df_subjects_view = df_subjects[['subject_code', 'subject_name', 'program_code', 'semester', 'LIC']]
st.dataframe(df_subjects_view, use_container_width=True)

# PENGURUSAN TAMBAHAN (opsyenal)
with st.expander("➕ Tambah Subjek Baru"):
    with st.form("form_tambah_subjek"):
        kod = st.text_input("Kod Subjek")
        nama = st.text_input("Nama Subjek")
        program = st.text_input("Kod Program")
        semester = st.text_input("Semester")
        lic_id = st.selectbox("Pilih Pensyarah (LIC)", df_users[df_users['role']=='staff']['user_id'].tolist())
        hantar = st.form_submit_button("Tambah")
        if hantar:
            c.execute("INSERT INTO subjects VALUES (?, ?, ?, ?, ?)", (kod, nama, program, semester, lic_id))
            conn.commit()
            st.success("Subjek berjaya ditambah.")

conn.close()
