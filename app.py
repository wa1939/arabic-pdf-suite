from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from src.ocr_service import run_ocr, system_ready, vercel_friendly_note
from src.pdf_tools import delete_pages, merge_pdfs, page_count, reorder_pdf, rotate_pdf, split_pdf
from src.text_utils import (
    extract_text_from_excel,
    extract_text_from_txt,
    make_wordcloud,
    normalize_text,
    top_terms,
)

st.set_page_config(page_title="Arabic PDF Suite", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
      .block-container {max-width: 1100px; padding-top: 1.6rem; padding-bottom: 2rem;}
      div[data-testid='stMetric'] {background: #f8fbff; border: 1px solid #e6f0ff; padding: 12px; border-radius: 14px;}
      .tool-card {padding: 14px 16px; border: 1px solid #e7eefc; border-radius: 16px; background: #fbfdff;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""

st.title("Arabic PDF Suite")
st.caption("Arabic-first OCR, PDF tools, and word cloud generation. No login. No saved files.")

with st.container(border=True):
    ready, missing = system_ready()
    a, b, c = st.columns(3)
    a.metric("OCR", "Ready" if ready else "Unavailable")
    b.metric("Privacy", "No signup")
    c.metric("Storage", "Temporary only")
    if ready:
        st.success("Full OCR is available on this machine.")
    else:
        st.warning(f"OCR is unavailable here. Missing system packages: {', '.join(missing)}")
        st.caption(vercel_friendly_note())

home_tab, ocr_tab, pdf_tab, cloud_tab, template_tab = st.tabs(
    ["🏠 Home", "📄 OCR", "🧩 PDF Tools", "☁️ Word Cloud", "📝 Templates"]
)

with home_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='tool-card'><h4>📄 OCR PDF</h4><p>Turn Arabic PDFs into searchable PDFs and extracted text.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='tool-card'><h4>🧩 PDF Tools</h4><p>Merge, split, delete pages, rotate pages, and reorder PDFs.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='tool-card'><h4>☁️ Word Cloud</h4><p>Generate Arabic word clouds from PDF text, pasted text, TXT, or Excel.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='tool-card'><h4>📝 Templates</h4><p>Use ready-made text templates for feedback, surveys, and workshops.</p></div>", unsafe_allow_html=True)
    st.info("Best deployment path: hosted URL for normal users, Docker for self-hosting, run.bat/run.sh for local use.")

with ocr_tab:
    st.subheader("OCR Arabic PDF")
    pdf = st.file_uploader("Upload PDF", type=["pdf"], key="ocr_pdf")
    run_button = st.button("Run OCR", type="primary", disabled=pdf is None or not ready)

    if run_button and pdf is not None:
        with st.spinner("Running OCR..."):
            result = run_ocr(pdf.getvalue(), pdf.name)
            extracted_text = result.txt_path.read_text(encoding="utf-8", errors="ignore")
            st.session_state.analysis_text = extracted_text
        st.success("OCR finished.")
        x, y = st.columns(2)
        x.download_button("Download searchable PDF", result.pdf_path.read_bytes(), result.pdf_path.name, mime="application/pdf")
        y.download_button("Download extracted TXT", extracted_text.encode("utf-8"), result.txt_path.name, mime="text/plain")
        st.text_area("Extracted text", extracted_text, height=260)
        st.caption("You can use this text directly in the Word Cloud tab.")

with pdf_tab:
    st.subheader("PDF Tools")
    tool = st.selectbox("Choose tool", ["Merge PDFs", "Split PDF", "Delete pages", "Rotate pages", "Reorder pages"])

    if tool == "Merge PDFs":
        files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, key="merge_pdf")
        if st.button("Merge", type="primary", disabled=not files):
            merged = merge_pdfs(files)
            st.download_button("Download merged PDF", merged.data, merged.filename, mime="application/pdf")

    elif tool == "Split PDF":
        file = st.file_uploader("Upload PDF", type=["pdf"], key="split_pdf")
        ranges = st.text_input("Pages or ranges", placeholder="Example: 1-3,5,7-9")
        if file:
            st.caption(f"Total pages: {page_count(file)}")
        if st.button("Split", type="primary", disabled=not file or not ranges.strip()):
            outputs = split_pdf(file, ranges)
            for item in outputs:
                st.download_button(f"Download {item.filename}", item.data, item.filename, mime="application/pdf")

    elif tool == "Delete pages":
        file = st.file_uploader("Upload PDF", type=["pdf"], key="delete_pdf")
        pages = st.text_input("Pages to delete", placeholder="Example: 2,4,8")
        if file:
            st.caption(f"Total pages: {page_count(file)}")
        if st.button("Delete selected pages", type="primary", disabled=not file or not pages.strip()):
            result = delete_pages(file, [int(x.strip()) for x in pages.split(",") if x.strip()])
            st.download_button("Download cleaned PDF", result.data, result.filename, mime="application/pdf")

    elif tool == "Rotate pages":
        file = st.file_uploader("Upload PDF", type=["pdf"], key="rotate_pdf")
        pages = st.text_input("Pages to rotate", placeholder="Example: 1,2")
        angle = st.selectbox("Angle", [90, 180, 270])
        if file:
            st.caption(f"Total pages: {page_count(file)}")
        if st.button("Rotate", type="primary", disabled=not file or not pages.strip()):
            result = rotate_pdf(file, [int(x.strip()) for x in pages.split(",") if x.strip()], angle)
            st.download_button("Download rotated PDF", result.data, result.filename, mime="application/pdf")

    elif tool == "Reorder pages":
        file = st.file_uploader("Upload PDF", type=["pdf"], key="reorder_pdf")
        order = st.text_input("New page order", placeholder="Example: 3,1,2,4")
        if file:
            count = page_count(file)
            st.caption(f"Total pages: {count}")
        if st.button("Reorder", type="primary", disabled=not file or not order.strip()):
            result = reorder_pdf(file, [int(x.strip()) for x in order.split(",") if x.strip()])
            st.download_button("Download reordered PDF", result.data, result.filename, mime="application/pdf")

with cloud_tab:
    st.subheader("Arabic Word Cloud")
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
    if st.button("Generate word cloud", type="primary", disabled=not bool(clean_text.strip())):
        image = make_wordcloud(clean_text)
        top = top_terms(clean_text, limit=15)
        st.image(image, caption="Arabic word cloud", use_container_width=True)
        img_buffer = BytesIO()
        image.save(img_buffer, format="PNG")
        st.download_button("Download PNG", img_buffer.getvalue(), file_name="arabic_wordcloud.png", mime="image/png")
        if top:
            st.markdown("#### Top terms")
            st.dataframe(pd.DataFrame(top, columns=["Word", "Count"]), use_container_width=True, hide_index=True)

with template_tab:
    st.subheader("Templates")
    template = st.selectbox("Choose template", [
        "Workshop feedback",
        "Employee comments",
        "Student feedback",
        "Customer feedback",
    ])
    defaults = {
        "Workshop feedback": "اكتب تعليقات الورشة هنا ثم ولّد السحابة النصية",
        "Employee comments": "اكتب تعليقات الموظفين هنا ثم ولّد السحابة النصية",
        "Student feedback": "اكتب تعليقات الطلاب هنا ثم ولّد السحابة النصية",
        "Customer feedback": "اكتب تعليقات العملاء هنا ثم ولّد السحابة النصية",
    }
    temp_text = st.text_area("Template text", defaults[template], height=220)
    if st.button("Use in Word Cloud", type="primary"):
        st.session_state.analysis_text = temp_text
        st.success("Template text moved to the Word Cloud tab.")
