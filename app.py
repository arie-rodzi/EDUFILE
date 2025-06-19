
import streamlit as st
import sqlite3
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="EDUFILE – FSKM UiTM Seremban", layout="wide")

# Sambungan ke pangkalan data
DB_PATH = "database/fskm_course_filing.db"

def create_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Fungsi semak log masuk
def login(user_id, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, name, role FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = c.fetchone()
    conn.close()
    return result

# Tajuk utama
st.title("📚 EDUFILE – FSKM UiTM Seremban")

# Simpan status log masuk dalam session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.user_name = ""
    st.session_state.user_role = ""

# Borang log masuk
if not st.session_state.logged_in:
    st.subheader("Log Masuk Pengguna")
    with st.form("login_form"):
        user_id = st.text_input("ID Pengguna")
        password = st.text_input("Katalaluan", type="password")
        submitted = st.form_submit_button("Log Masuk")

        if submitted:
            user = login(user_id, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_name = user[1]
                st.session_state.user_role = user[2]
                st.success(f"Selamat datang, {user[1]} ({user[2]})")
                st.experimental_rerun()
            else:
                st.error("ID atau Katalaluan salah. Sila cuba lagi.")
else:
    st.sidebar.success(f"Log Masuk sebagai: {st.session_state.user_name} ({st.session_state.user_role})")
    pilihan = st.sidebar.radio("Navigasi", [
        "📂 Paparan Senarai Subjek",
        "📄 Paparan Fail Subjek"
    ])

    # Akses tambahan untuk LIC
    if st.session_state.user_role == "staff":
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM subjects WHERE lic_staff_id=?", (st.session_state.user_id,))
        is_lic = c.fetchone()[0] > 0
        conn.close()

        if is_lic:
            pilihan = st.sidebar.radio("", [pilihan, "📤 Muat Naik Fail"])

    # Akses tambahan untuk admin
    if st.session_state.user_role == "admin":
        pilihan = st.sidebar.radio("", [pilihan, "⚙️ Panel Admin", "📦 Muat Turun Semua", "🔒 Tukar Katalaluan"])

    # Papar modul berdasarkan pilihan
    if pilihan == "📂 Paparan Senarai Subjek":
        st.experimental_set_query_params(page="1_lihat_subjek")
        st.switch_page("pages/1_lihat_subjek.py")
    elif pilihan == "📄 Paparan Fail Subjek":
        st.experimental_set_query_params(page="4_paparan_fail")
        st.switch_page("pages/4_paparan_fail.py")
    elif pilihan == "📤 Muat Naik Fail":
        st.experimental_set_query_params(page="2_muat_naik_fail")
        st.switch_page("pages/2_muat_naik_fail.py")
    elif pilihan == "⚙️ Panel Admin":
        st.experimental_set_query_params(page="5_admin_panel")
        st.switch_page("pages/5_admin_panel.py")
    elif pilihan == "📦 Muat Turun Semua":
        st.experimental_set_query_params(page="6_muat_turun_zip")
        st.switch_page("pages/6_muat_turun_zip.py")
    elif pilihan == "🔒 Tukar Katalaluan":
        st.experimental_set_query_params(page="7_tukar_katalaluan")
        st.switch_page("pages/7_tukar_katalaluan.py")

    if st.button("Log Keluar"):
        st.session_state.logged_in = False
        st.session_state.user_id = ""
        st.session_state.user_name = ""
        st.session_state.user_role = ""
        st.rerun()
