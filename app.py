import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="EDUFILE – FSKM UiTM Seremban", layout="wide")

# Laluan fail DB baharu
DB_PATH = "database/edufile.db"

# Fungsi sambungan ke DB
def create_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Fungsi untuk hash katalaluan
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi login disemak semula
def login(username, password):
    conn = create_connection()
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT user_id, username, name, role, force_change FROM users WHERE username=? AND password_hash=?", (username, hashed))
    result = c.fetchone()
    conn.close()
    return result

# Tajuk utama
st.title("📚 EDUFILE – FSKM UiTM Seremban")

# Inisialisasi sesi
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.username = ""
    st.session_state.user_name = ""
    st.session_state.user_role = ""
    st.session_state.force_change = 0

# Halaman Log Masuk
if not st.session_state.logged_in:
    st.subheader("🔐 Log Masuk Pengguna")
    with st.form("login_form"):
        username = st.text_input("🆔 ID Pengguna (Username)")
        password = st.text_input("🔑 Katalaluan", type="password")
        submitted = st.form_submit_button("Log Masuk")

        if submitted:
            user = login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.user_name = user[2]
                st.session_state.user_role = user[3]
                st.session_state.force_change = user[4]

                st.success(f"Selamat datang, {user[2]} ({user[3]})")

                if user[4] == 1:
                    st.warning("⚠️ Anda perlu menukar katalaluan terlebih dahulu.")
                    st.switch_page("pages/7_tukar_katalaluan.py")
                else:
                    st.rerun()
            else:
                st.error("❌ ID Pengguna atau Katalaluan tidak sah.")

# Selepas log masuk
else:
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.user_name}** ({st.session_state.user_role})")
        st.markdown("---")

    role = st.session_state.user_role.upper()

    # Navigasi ikut peranan
    if role == "ADMIN":
        pilihan = st.sidebar.radio("Navigasi", [
            "📂 Paparan Senarai Subjek",
            "📄 Paparan Fail Subjek",
            "⚙️ Panel Admin",
            "📦 Muat Turun Semua",
            "🔒 Tukar Katalaluan"
        ])
    elif role in ["RP", "LIC"]:
        pilihan = st.sidebar.radio("Navigasi", [
            "📂 Paparan Senarai Subjek",
            "📄 Paparan Fail Subjek",
            "📤 Muat Naik Fail",
            "📦 Muat Turun Semua",
            "🔒 Tukar Katalaluan"
        ])
    else:
        pilihan = st.sidebar.radio("Navigasi", [
            "📂 Paparan Senarai Subjek",
            "📄 Paparan Fail Subjek"
        ])

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

    # Butang Log Keluar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Log Keluar"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
