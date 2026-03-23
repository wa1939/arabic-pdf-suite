from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from src.ocr_service import run_ocr, system_ready, vercel_friendly_note
from src.text_utils import extract_text_from_excel, extract_text_from_txt, make_wordcloud, normalize_text, top_terms

st.set_page_config(page_title="Arabic OCR + Word Cloud", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
      .block-container {max-width: 1050px; padding-top: 2rem; padding-bottom: 2rem;}
      div[data-testid='stMetric'] {background: #f8fbff; border: 1px solid #e6f0ff; padding: 12px; border-radius: 14px;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""

st.title("Arabic OCR + Word Cloud")
st.caption("One tiny app for Arabic PDF OCR, text extraction, and clean word-cloud analysis.")

with st.container(border=True):
    ready, missing = system_ready()
    left, right = st.columns([1, 2])
    with left:
        st.metric("OCR Engine", "Ready" if ready else "Missing deps")
    with right:
        if ready:
            st.success("Tesseract + Ghostscript detected. Full OCR is available.")
        else:
            st.warning(f"OCR disabled here. Missing: {', '.join(missing)}")
            st.caption(vercel_friendly_note())

ocr_tab, cloud_tab = st.tabs(["📄 OCR", "☁️ Word Cloud"])

with ocr_tab:
    st.subheader("Turn Arabic PDFs into searchable text")
    pdf = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")
    run_button = st.button("Run OCR", type="primary", disabled=pdf is None or not ready)

    if run_button and pdf is not None:
        with st.spinner("Running OCR..."):
            result = run_ocr(pdf.getvalue(), pdf.name)
            extracted_text = result.txt_path.read_text(encoding="utf-8", errors="ignore")
            st.session_state.analysis_text = extracted_text

        st.success("Done.")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download searchable PDF",
                data=result.pdf_path.read_bytes(),
                file_name=result.pdf_path.name,
                mime="application/pdf",
            )
        with col2:
            st.download_button(
                "Download extracted text",
                data=extracted_text.encode("utf-8"),
                file_name=result.txt_path.name,
                mime="text/plain",
            )

        st.text_area("Extracted text", extracted_text, height=260)
        st.caption("Tip: the extracted text is already pushed into the Word Cloud tab.")

with cloud_tab:
    st.subheader("Generate an Arabic word cloud from text, TXT, or Excel")
    source = st.radio("Input source", ["Paste text", "Upload TXT", "Upload Excel", "Use last OCR result"], horizontal=True)

    text_value = ""
    if source == "Paste text":
        text_value = st.text_area("Arabic text", st.session_state.analysis_text, height=220, placeholder="Paste Arabic text here...")
    elif source == "Upload TXT":
        txt_file = st.file_uploader("Upload TXT", type=["txt"], key="txt_uploader")
        if txt_file:
            text_value = extract_text_from_txt(txt_file.getvalue())
            st.text_area("Preview", text_value, height=220)
    elif source == "Upload Excel":
        xlsx = st.file_uploader("Upload Excel", type=["xlsx", "xls"], key="xlsx_uploader")
        preferred_column = st.text_input("Column name (optional)", value="النص المراد تحليله")
        if xlsx:
            text_value = extract_text_from_excel(xlsx.getvalue(), preferred_column=preferred_column.strip() or None)
            st.text_area("Preview", text_value, height=220)
    else:
        text_value = st.session_state.analysis_text
        st.text_area("Last OCR text", text_value, height=220)

    clean_text = normalize_text(text_value)
    generate = st.button("Generate word cloud", type="primary", disabled=not bool(clean_text.strip()))

    if generate and clean_text:
        image = make_wordcloud(clean_text)
        top = top_terms(clean_text, limit=15)
        st.image(image, caption="Arabic word cloud", use_container_width=True)

        img_buffer = BytesIO()
        image.save(img_buffer, format="PNG")
        st.download_button("Download PNG", img_buffer.getvalue(), file_name="arabic_wordcloud.png", mime="image/png")

        if top:
            st.markdown("#### Top terms")
            st.dataframe(pd.DataFrame(top, columns=["Word", "Count"]), use_container_width=True, hide_index=True)
