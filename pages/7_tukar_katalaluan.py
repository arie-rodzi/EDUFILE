import streamlit as st
import sqlite3
import hashlib

st.set_page_config(page_title="Tukar Katalaluan")
st.title("🔒 Tukar Katalaluan")

# Sambungan ke pangkalan data
def create_connection():
    return sqlite3.connect("database/edufile.db", check_same_thread=False)

# Fungsi hash SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = create_connection()
c = conn.cursor()

# Semak jika log masuk
if "username" not in st.session_state or not st.session_state.logged_in:
    st.warning("Sila log masuk terlebih dahulu.")
    st.stop()

# Borang tukar katalaluan
with st.form("form_tukar_katalaluan"):
    current_pw = st.text_input("🔐 Katalaluan Semasa", type="password")
    new_pw = st.text_input("🆕 Katalaluan Baharu", type="password")
    confirm_pw = st.text_input("✅ Sahkan Katalaluan Baharu", type="password")
    submit = st.form_submit_button("Tukar Katalaluan")

    if submit:
        # Semak katalaluan semasa
        hashed_current = hash_password(current_pw)
        c.execute("SELECT password_hash FROM users WHERE username=?", (st.session_state.username,))
        actual_pw = c.fetchone()

        if not actual_pw or hashed_current != actual_pw[0]:
            st.error("❌ Katalaluan semasa tidak tepat.")
        elif new_pw != confirm_pw:
            st.error("❌ Katalaluan baharu dan pengesahan tidak sepadan.")
        elif len(new_pw) < 6:
            st.error("❌ Katalaluan mestilah sekurang-kurangnya 6 aksara.")
        else:
            # Kemaskini katalaluan baharu (dihash) dan tamatkan keperluan tukar
            hashed_new = hash_password(new_pw)
            c.execute("UPDATE users SET password_hash=?, force_change=0 WHERE username=?",
                      (hashed_new, st.session_state.username))
            conn.commit()
            st.success("✅ Katalaluan berjaya dikemaskini.")
            st.session_state.force_change = 0
            st.rerun()

conn.close()
