from __future__ import annotations

import re
from io import BytesIO

import pandas as pd
import streamlit as st

from src.ocr_service import run_ocr, system_ready, vercel_friendly_note
from src.pdf_tools import (
    compress_pdf,
    delete_pages,
    merge_pdfs,
    page_count,
    parse_page_list,
    reorder_pdf,
    rotate_pdf,
    split_pdf,
)
from src.text_utils import (
    COLOR_SCHEMES,
    DEFAULT_STOPWORDS,
    extract_text_from_excel,
    extract_text_from_txt,
    get_available_fonts,
    make_wordcloud,
    normalize_text,
    top_terms,
)

st.set_page_config(page_title="Arabic PDF Suite", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
      .block-container {max-width: 1120px; padding-top: 1.4rem; padding-bottom: 2rem;}
      div[data-testid='stMetric'] {background: #f8fbff; border: 1px solid #e6f0ff; padding: 12px; border-radius: 14px;}
      .tool-card {padding: 16px 18px; border: 1px solid #e7eefc; border-radius: 16px; background: #fbfdff; min-height: 118px;}
      .hero {padding: 18px; border: 1px solid #e7eefc; border-radius: 18px; background: linear-gradient(180deg, #fbfdff 0%, #f4f8ff 100%);}
      .small-note {color: #5b6470; font-size: 0.92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""

st.title("Arabic PDF Suite")
st.caption("Arabic-first OCR, PDF editing, and word cloud generation. No login. No permanent storage.")

with st.container(border=True):
    ready, missing = system_ready()
    a, b, c = st.columns(3)
    a.metric("OCR", "Ready" if ready else "Unavailable")
    b.metric("Privacy", "No signup")
    c.metric("Storage", "Temporary processing")
    if ready:
        st.success("OCR is ready on this machine.")
    else:
        st.warning(f"OCR is unavailable here. Missing system packages: {', '.join(missing)}")
        st.caption(vercel_friendly_note())

home_tab, ocr_tab, pdf_tab, cloud_tab, template_tab, deploy_tab = st.tabs(
    ["🏠 Home", "📄 OCR", "🧩 PDF Tools", "☁️ Word Cloud", "📝 Templates", "🚀 Deploy"]
)

with home_tab:
    st.markdown(
        """
        <div class='hero'>
          <h3 style='margin:0 0 8px 0;'>One lightweight Arabic document app</h3>
          <p style='margin:0;'>Upload a PDF, extract Arabic text, clean pages, merge files, and generate a word cloud — all in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='tool-card'><h4>📄 OCR PDF</h4><p>Turn Arabic PDFs into searchable PDFs and extracted text you can reuse anywhere.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='tool-card'><h4>🧩 PDF Tools</h4><p>Merge, split, delete pages, rotate pages, and reorder pages without leaving the browser.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='tool-card'><h4>☁️ Word Cloud</h4><p>Generate Arabic word clouds from OCR output, pasted text, TXT files, or Excel sheets.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='tool-card'><h4>📝 Templates</h4><p>Use ready-made templates for surveys, feedback, workshops, and customer comments.</p></div>", unsafe_allow_html=True)
    st.info("Best path for normal users: host it once and share the URL. Best path for private use: run locally with Docker or the launch scripts.")

with ocr_tab:
    st.subheader("OCR Arabic PDF")
    st.caption("Upload one PDF. Get a searchable PDF and extracted Arabic text.")
    pdf = st.file_uploader("Upload PDF", type=["pdf"], key="ocr_pdf")
    run_button = st.button("Run OCR", type="primary", disabled=pdf is None or not ready)

    if run_button and pdf is not None:
        try:
            with st.spinner("Running OCR..."):
                result = run_ocr(pdf.getvalue(), pdf.name)
                extracted_text = result.txt_path.read_text(encoding="utf-8", errors="ignore")
                st.session_state.analysis_text = extracted_text
            st.success("OCR finished.")
            x, y = st.columns(2)
            x.download_button("Download searchable PDF", result.pdf_path.read_bytes(), result.pdf_path.name, mime="application/pdf")
            y.download_button("Download extracted TXT", extracted_text.encode("utf-8"), result.txt_path.name, mime="text/plain")
            st.text_area("Extracted text", extracted_text, height=260)
            st.caption("Tip: your extracted text is already available in the Word Cloud tab.")
        except Exception as exc:
            st.error(str(exc))

with pdf_tab:
    st.subheader("PDF Tools")
    st.caption("Clean, combine, or rearrange PDFs without creating an account.")
    tool = st.selectbox("Choose tool", ["Merge PDFs", "Split PDF", "Delete pages", "Rotate pages", "Reorder pages", "Compress PDF"])

    try:
        if tool == "Merge PDFs":
            files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, key="merge_pdf")
            st.caption("Tip: files are merged in the same order you upload them.")
            if st.button("Merge PDFs", type="primary", disabled=not files):
                merged = merge_pdfs(files)
                st.download_button("Download merged PDF", merged.data, merged.filename, mime="application/pdf")

        elif tool == "Split PDF":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="split_pdf")
            ranges = st.text_input("Pages or ranges", placeholder="Example: 1-3,5,7-9")
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Split PDF", type="primary", disabled=not file or not ranges.strip()):
                zip_data = split_pdf(file, ranges)
                st.download_button("Download split files (ZIP)", zip_data, "split_pdfs.zip", mime="application/zip")

        elif tool == "Delete pages":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="delete_pdf")
            pages = st.text_input("Pages to delete", placeholder="Example: 2,4,8")
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Delete selected pages", type="primary", disabled=not file or not pages.strip()):
                result = delete_pages(file, parse_page_list(pages))
                st.download_button("Download cleaned PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Rotate pages":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="rotate_pdf")
            pages = st.text_input("Pages to rotate", placeholder="Example: 1,2")
            angle = st.selectbox("Angle", [90, 180, 270])
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Rotate pages", type="primary", disabled=not file or not pages.strip()):
                result = rotate_pdf(file, parse_page_list(pages), angle)
                st.download_button("Download rotated PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Reorder pages":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="reorder_pdf")
            order = st.text_input("New page order", placeholder="Example: 3,1,2,4")
            if file:
                count = page_count(file)
                st.caption(f"Total pages: {count}. Enter every page exactly once.")
            if st.button("Reorder PDF", type="primary", disabled=not file or not order.strip()):
                result = reorder_pdf(file, parse_page_list(order))
                st.download_button("Download reordered PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Compress PDF":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="compress_pdf")
            if file:
                original_size = len(file.getvalue()) / 1024
                st.caption(f"Original size: {original_size:.1f} KB")
            if st.button("Compress PDF", type="primary", disabled=not file):
                result = compress_pdf(file)
                compressed_size = len(result.data) / 1024
                if file:
                    delta = len(file.getvalue()) - len(result.data)
                    if delta > 0:
                        st.success(f"Compression finished. Saved {delta / 1024:.1f} KB.")
                    else:
                        st.info("Compression finished. This file was already tightly packed, so size stayed about the same.")
                st.caption(f"Compressed size: {compressed_size:.1f} KB")
                st.download_button("Download compressed PDF", result.data, result.filename, mime="application/pdf")
    except Exception as exc:
        st.error(f"PDF tool failed: {exc}")

with cloud_tab:
    st.subheader("Arabic Word Cloud")
    st.caption("Create a word cloud from text, Excel, TXT, or the last OCR result. Uses original Arabic rendering.")
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
    
    # Customization options
    st.markdown("#### Customize")
    col1, col2 = st.columns(2)
    
    with col1:
        available_fonts = get_available_fonts()
        font_names = list(available_fonts.keys())
        selected_font = st.selectbox("Font", font_names, index=0 if font_names else 0)
        
        color_schemes = list(COLOR_SCHEMES.keys())
        selected_scheme = st.selectbox("Color scheme", color_schemes, index=color_schemes.index("ELM Brand"))
        
        transparent = st.checkbox("Transparent background", value=True)
        bg_color = st.color_picker("Background color", "#FFFFFF", disabled=transparent)
    
    with col2:
        max_words = st.slider("Max words", min_value=50, max_value=500, value=200, step=10)
        width = st.slider("Width", min_value=400, max_value=2000, value=800, step=50)
        height = st.slider("Height", min_value=400, max_value=2000, value=800, step=50)
    
    # Filler/Stopword management
    with st.expander("🔤 Filler words (stopwords)", expanded=False):
        st.caption("Words to exclude from the word cloud. Separate with commas or spaces.")
        extra_fillers = st.text_area(
            "Add more fillers",
            placeholder="مثال: كلمة، كلمة أخرى",
            help="Add words you want to exclude"
        )
        exclude_fillers = st.text_area(
            "Remove from default fillers",
            placeholder="مثال: كلمة",
            help="Remove words from the default filler list (if you want them to appear)"
        )
        
        # Parse input
        extra_stopwords = [w.strip() for w in re.split(r'[,\s]+', extra_fillers) if w.strip()]
        exclude_stopwords = [w.strip() for w in re.split(r'[,\s]+', exclude_fillers) if w.strip()]
        
        if extra_stopwords:
            st.caption(f"Adding {len(extra_stopwords)} filler(s): {', '.join(extra_stopwords[:5])}{'...' if len(extra_stopwords) > 5 else ''}")
        if exclude_stopwords:
            st.caption(f"Excluding {len(exclude_stopwords)} filler(s): {', '.join(exclude_stopwords[:5])}{'...' if len(exclude_stopwords) > 5 else ''}")
    
    if st.button("Generate word cloud", type="primary", disabled=not bool(clean_text.strip())):
        with st.spinner("Generating word cloud..."):
            image = make_wordcloud(
                clean_text,
                font_name=selected_font,
                color_scheme=selected_scheme,
                background_color=None if transparent else bg_color,
                max_words=max_words,
                prefer_horizontal=0.9,
                width=width,
                height=height,
                transparent=transparent,
                extra_stopwords=extra_stopwords if extra_stopwords else None,
                exclude_stopwords=exclude_stopwords if exclude_stopwords else None,
            )
        active_stopwords = None
        if extra_stopwords or exclude_stopwords:
            active_stopwords = list(DEFAULT_STOPWORDS)
            if extra_stopwords:
                active_stopwords.extend(extra_stopwords)
            if exclude_stopwords:
                excluded = set(exclude_stopwords)
                active_stopwords = [w for w in active_stopwords if w not in excluded]
        top = top_terms(clean_text, limit=15, stopwords=active_stopwords)
        st.image(image, caption="Arabic word cloud", use_container_width=True)
        img_buffer = BytesIO()
        image.save(img_buffer, format="PNG")
        st.download_button("Download PNG", img_buffer.getvalue(), file_name="arabic_wordcloud.png", mime="image/png")
        if top:
            st.markdown("#### Top terms")
            st.dataframe(pd.DataFrame(top, columns=["Word", "Count"]), use_container_width=True, hide_index=True)

with template_tab:
    st.subheader("Templates")
    st.caption("Pick a starter template, edit the text, then send it to the Word Cloud tool.")
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

with deploy_tab:
    st.subheader("Deploy or run locally")
    st.markdown("**Hosted version**: use Railway, Render, Fly.io, or a VPS with Docker.")
    st.markdown("**Local version**: double-click `run.bat` on Windows or run `./run.sh` on macOS/Linux.")
    st.code("docker compose up --build", language="bash")
    st.markdown("<p class='small-note'>For a public site, host once and share the URL. Users should not need Docker.</p>", unsafe_allow_html=True)
