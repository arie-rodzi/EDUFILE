
import streamlit as st
import sqlite3

st.set_page_config(page_title="Tukar Katalaluan")
st.title("🔒 Tukar Katalaluan")

# Sambungan ke pangkalan data
def create_connection():
    return sqlite3.connect("database/fskm_course_filing.db", check_same_thread=False)

conn = create_connection()
c = conn.cursor()

# Semak jika log masuk
if "user_id" not in st.session_state or not st.session_state.logged_in:
    st.warning("Sila log masuk terlebih dahulu.")
    st.stop()

# Borang tukar katalaluan
with st.form("form_tukar_katalaluan"):
    current_pw = st.text_input("Katalaluan Semasa", type="password")
    new_pw = st.text_input("Katalaluan Baharu", type="password")
    confirm_pw = st.text_input("Sahkan Katalaluan Baharu", type="password")
    submit = st.form_submit_button("Tukar Katalaluan")

    if submit:
        c.execute("SELECT password FROM users WHERE user_id=?", (st.session_state.user_id,))
        actual_pw = c.fetchone()

        if not actual_pw or current_pw != actual_pw[0]:
            st.error("Katalaluan semasa tidak tepat.")
        elif new_pw != confirm_pw:
            st.error("Katalaluan baharu dan pengesahan tidak sepadan.")
        else:
            c.execute("UPDATE users SET password=? WHERE user_id=?", (new_pw, st.session_state.user_id))
            conn.commit()
            st.success("Katalaluan berjaya dikemas kini.")

conn.close()
