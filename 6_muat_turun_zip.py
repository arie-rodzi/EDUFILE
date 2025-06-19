
import streamlit as st
import os
import zipfile
from io import BytesIO

st.set_page_config(page_title="Muat Turun Semua Fail")
st.title("📦 Muat Turun Semua Fail Subjek")

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER) or not os.listdir(UPLOAD_FOLDER):
    st.info("Tiada fail dimuat naik dalam sistem.")
else:
    # Sediakan fail ZIP dalam memori
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(UPLOAD_FOLDER):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                zipf.write(filepath, os.path.relpath(filepath, UPLOAD_FOLDER))

    zip_buffer.seek(0)
    st.download_button(
        label="📥 Muat Turun Semua dalam ZIP",
        data=zip_buffer,
        file_name="semua_fail_kursus.zip",
        mime="application/zip"
    )
