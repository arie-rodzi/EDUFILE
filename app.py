import streamlit as st
import sqlite3
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="EDUFILE – FSKM UiTM Seremban", layout="wide")

# Fail pangkalan data
DB_PATH = "database/fskm_course_filing.db"

# Fungsi sambungan ke pangkalan data
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

# Inisialisasi session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.user_name = ""
    st.session_state.user_role = ""

# Halaman Log Masuk
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
                st.rerun()
            else:
                st.error("ID atau Katalaluan salah. Sila cuba lagi.")

# Halaman Selepas Log Masuk
else:
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.user_name}** ({st.session_state.user_role})")
        st.markdown("---")

    # Navigasi ikut peranan
    if st.session_state.user_role == "admin":
        pilihan = st.sidebar.radio("Navigasi", [
            "📂 Paparan Senarai Subjek",
            "📄 Paparan Fail Subjek",
            "⚙️ Panel Admin",
            "📦 Muat Turun Semua",
            "🔒 Tukar Katalaluan"
        ], key="admin_menu")

    elif st.session_state.user_role == "staff":
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM subjects WHERE lic_staff_id=?", (st.session_state.user_id,))
        is_lic = c.fetchone()[0] > 0
        conn.close()

        staff_menu = [
            "📂 Paparan Senarai Subjek",
            "📄 Paparan Fail Subjek"
        ]
        if is_lic:
            staff_menu.append("📤 Muat Naik Fail")

        pilihan = st.sidebar.radio("Navigasi", staff_menu, key="staff_menu")

    else:
        pilihan = st.sidebar.radio("Navigasi", [
            "📂 Paparan Senarai Subjek",
            "📄 Paparan Fail Subjek"
        ], key="default_menu")

    # Navigasi halaman
    if pilihan == "📂 Paparan Senarai Subjek":
        st.switch_page("pages/1_lihat_subjek.py")
    elif pilihan == "📄 Paparan Fail Subjek":
        st.switch_page("pages/4_paparan_fail.py")
    elif pilihan == "📤 Muat Naik Fail":
        st.switch_page("pages/2_muat_naik_fail.py")
    elif pilihan == "⚙️ Panel Admin":
        st.switch_page("pages/5_admin_panel.py")
    elif pilihan == "📦 Muat Turun Semua":
        st.switch_page("pages/6_muat_turun_zip.py")
    elif pilihan == "🔒 Tukar Katalaluan":
        st.switch_page("pages/7_tukar_katalaluan.py")

    # Log Keluar (sentiasa di sidebar)
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Log Keluar"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
