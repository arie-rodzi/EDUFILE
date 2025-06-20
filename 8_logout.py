
import streamlit as st

st.set_page_config(page_title="Log Keluar", layout="wide")
st.title("🚪 Log Keluar")

st.write("Anda akan log keluar dari sistem.")

if st.button("Sahkan Log Keluar"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Berjaya log keluar.")
    st.switch_page("app.py")
