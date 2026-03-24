from __future__ import annotations

import re
from io import BytesIO

import pandas as pd
import streamlit as st

from src.ocr_service import run_ocr, system_ready, vercel_friendly_note
from src.pdf_tools import (
    add_text_watermark,
    compress_pdf,
    delete_pages,
    excel_to_pdf,
    images_to_pdf,
    merge_pdfs,
    page_count,
    parse_page_list,
    pdf_to_excel,
    pdf_to_images,
    pdf_to_word,
    reorder_pdf,
    rotate_pdf,
    split_pdf,
    tool_availability,
    word_to_pdf,
)
from src.text_utils import (
    COLOR_SCHEMES,
    DEFAULT_STOPWORDS,
    build_wordcloud_debug_report,
    extract_text_from_excel,
    extract_text_from_txt,
    get_available_fonts,
    make_wordcloud,
    normalize_text,
    top_terms,
)

st.set_page_config(page_title="Arabic PDF Suite", page_icon="📄", layout="wide")

if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""
if "active_tool" not in st.session_state:
    st.session_state.active_tool = "Merge PDF"

TOOLS = [
    ("Merge PDF", "🧩", "Combine multiple PDFs into one polished file."),
    ("Split PDF", "✂️", "Export specific pages or page ranges into separate PDFs."),
    ("Compress PDF", "🗜️", "Reduce PDF size for faster sharing."),
    ("PDF to Images", "🖼️", "Turn each page into PNG or JPG."),
    ("Images to PDF", "📚", "Build a single PDF from images."),
    ("Word to PDF", "📝", "Convert DOCX or TXT into PDF."),
    ("PDF to Word", "📄", "Extract PDF text into DOCX or TXT."),
    ("Add Watermark", "💧", "Stamp confidential or branded text over pages."),
    ("Rotate Pages", "🔄", "Rotate selected pages by 90, 180, or 270 degrees."),
    ("Delete Pages", "🗑️", "Remove unwanted pages permanently."),
    ("Reorder Pages", "↕️", "Rearrange pages into a new order."),
    ("OCR", "🔎", "Arabic + English OCR with searchable PDF output."),
    ("Arabic Word Cloud", "☁️", "Generate Arabic insights from text, OCR, or Excel."),
    ("PDF to Excel", "📊", "Extract page lines into a spreadsheet."),
    ("Excel to PDF", "📈", "Render workbook content into PDF."),
]

ready, missing = system_ready()
availability = tool_availability()

st.markdown(
    """
    <style>
    :root {
        --bg: #f6f8fc;
        --card: #ffffff;
        --ink: #0f172a;
        --muted: #5b6470;
        --line: #e2e8f0;
        --brand: #e5322d;
        --brand2: #1d4ed8;
    }
    .stApp { background: linear-gradient(180deg,#f8fafc 0%, #eef4ff 100%); }
    .block-container { max-width: 1220px; padding-top: 1.2rem; padding-bottom: 3rem; }
    .hero {
        background: radial-gradient(circle at top right, rgba(29,78,216,.14), transparent 28%),
                    radial-gradient(circle at top left, rgba(229,50,45,.12), transparent 24%),
                    #ffffff;
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 28px;
        box-shadow: 0 24px 64px rgba(15,23,42,.08);
    }
    .metric-strip {
        background: rgba(255,255,255,.78);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px 18px;
        height: 100%;
    }
    .tool-card {
        background: rgba(255,255,255,.94);
        border: 1px solid #e6edf7;
        border-radius: 22px;
        padding: 18px;
        min-height: 176px;
        box-shadow: 0 12px 30px rgba(15,23,42,.06);
    }
    .tool-card h4 { margin: .4rem 0; }
    .tool-card p { color: var(--muted); min-height: 54px; }
    .section-card {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 22px;
        box-shadow: 0 14px 34px rgba(15,23,42,.05);
    }
    .pill { display:inline-block; padding:7px 12px; border-radius:999px; border:1px solid #dbeafe; background:#eff6ff; margin-right:8px; margin-top:8px; font-size:.9rem; }
    div[data-testid='stMetric'] { background:#fff; border:1px solid #e6edf7; padding:8px; border-radius:16px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='hero'>
      <div style='display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap;'>
        <div style='max-width:760px;'>
          <div style='font-size:.95rem;color:#e5322d;font-weight:700;margin-bottom:8px;'>Arabic PDF Suite</div>
          <h1 style='margin:0 0 10px 0;font-size:2.5rem;line-height:1.05;color:#0f172a;'>A proper PDF workspace, not a glorified demo.</h1>
          <p style='margin:0;color:#475569;font-size:1.08rem;'>Merge, split, convert, OCR, watermark, analyze, and package Arabic-first documents in one clean interface. Built for real work, not vibes.</p>
          <div>
            <span class='pill'>Arabic-first</span>
            <span class='pill'>No signup</span>
            <span class='pill'>Runs locally or self-hosted</span>
            <span class='pill'>Port 3000 ready</span>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
mc1, mc2, mc3, mc4 = st.columns(4)
mc1.metric("PDF tools", "15")
mc2.metric("OCR", "Ready" if ready else "Missing deps")
mc3.metric("Desktop packaging", "Included")
mc4.metric("Deployment targets", "Vercel · Railway · Docker")

st.write("")
st.subheader("Toolbox")
card_columns = st.columns(3)
for idx, (name, icon, desc) in enumerate(TOOLS):
    with card_columns[idx % 3]:
        st.markdown(f"<div class='tool-card'><div style='font-size:1.8rem'>{icon}</div><h4>{name}</h4><p>{desc}</p></div>", unsafe_allow_html=True)
        if st.button(f"Open {name}", key=f"open-{name}", use_container_width=True):
            st.session_state.active_tool = name

st.write("")
left, right = st.columns([1.1, 2.2], gap="large")

with left:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Control Panel")
    selected = st.selectbox("Choose a tool", [name for name, _, _ in TOOLS], index=[name for name, _, _ in TOOLS].index(st.session_state.active_tool))
    st.session_state.active_tool = selected
    st.caption("Everything routes through one cleaner workflow. Much better than burying users in random tabs.")
    if ready:
        st.success("OCR stack is installed.")
    else:
        st.warning(f"OCR dependencies missing: {', '.join(missing)}")
        st.caption(vercel_friendly_note())
    st.markdown("**Conversion notes**")
    st.markdown(f"- LibreOffice: {'Yes' if availability['libreoffice'] else 'No'}")
    st.markdown(f"- Tesseract: {'Yes' if availability['tesseract'] else 'No'}")
    st.markdown(f"- Ghostscript: {'Yes' if availability['ghostscript'] else 'No'}")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    tool = st.session_state.active_tool
    st.subheader(tool)

    try:
        if tool == "Merge PDF":
            files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, key="merge_pdf")
            if st.button("Merge now", type="primary", disabled=not files):
                merged = merge_pdfs(files)
                st.download_button("Download merged PDF", merged.data, merged.filename, mime="application/pdf")

        elif tool == "Split PDF":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="split_pdf")
            ranges = st.text_input("Pages or ranges", placeholder="1-3,5,7-9")
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Split PDF", type="primary", disabled=not file or not ranges.strip()):
                zip_data = split_pdf(file, ranges)
                st.download_button("Download ZIP", zip_data, "split_pdfs.zip", mime="application/zip")

        elif tool == "Compress PDF":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="compress_pdf")
            if file and st.button("Compress", type="primary"):
                result = compress_pdf(file)
                st.download_button("Download compressed PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "PDF to Images":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_to_images")
            dpi = st.slider("DPI", 72, 300, 150, 6)
            fmt = st.segmented_control("Format", ["png", "jpg"], default="png")
            if file and st.button("Extract pages", type="primary"):
                zip_data = pdf_to_images(file, image_format=fmt, dpi=dpi)
                st.download_button("Download images ZIP", zip_data, "pdf_pages.zip", mime="application/zip")

        elif tool == "Images to PDF":
            files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, key="images_to_pdf")
            if files and st.button("Convert to PDF", type="primary"):
                result = images_to_pdf(files)
                st.download_button("Download PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Word to PDF":
            file = st.file_uploader("Upload DOCX or TXT", type=["docx", "txt"], key="word_to_pdf")
            st.caption("Pragmatic mode: DOCX/TXT content is rendered into a clean PDF.")
            if file and st.button("Convert Word to PDF", type="primary"):
                result = word_to_pdf(file)
                st.download_button("Download PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "PDF to Word":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_to_word")
            st.caption("Exports extracted text into DOCX when possible, otherwise TXT.")
            if file and st.button("Convert PDF to Word", type="primary"):
                result = pdf_to_word(file)
                st.download_button("Download file", result.data, result.filename, mime=result.mime_type)

        elif tool == "Add Watermark":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="watermark_pdf")
            watermark_text = st.text_input("Watermark text", value="سري / Confidential")
            pages = st.text_input("Pages (optional)", placeholder="1-3,5")
            opacity = st.slider("Opacity", 0.05, 0.9, 0.18, 0.01)
            rotation = st.slider("Rotation", -90, 90, 35, 5)
            if file and st.button("Apply watermark", type="primary"):
                page_values = parse_page_list(pages) if pages.strip() else None
                result = add_text_watermark(file, watermark_text, pages=page_values, opacity=opacity, rotation=rotation)
                st.download_button("Download watermarked PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Rotate Pages":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="rotate_pdf")
            pages = st.text_input("Pages to rotate", placeholder="1,2")
            angle = st.selectbox("Angle", [90, 180, 270])
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Rotate pages", type="primary", disabled=not file or not pages.strip()):
                result = rotate_pdf(file, parse_page_list(pages), angle)
                st.download_button("Download rotated PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Delete Pages":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="delete_pdf")
            pages = st.text_input("Pages to delete", placeholder="2,4,8")
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Delete selected pages", type="primary", disabled=not file or not pages.strip()):
                result = delete_pages(file, parse_page_list(pages))
                st.download_button("Download cleaned PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Reorder Pages":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="reorder_pdf")
            order = st.text_input("New page order", placeholder="3,1,2,4")
            if file:
                count = page_count(file)
                st.caption(f"Total pages: {count}. Enter every page exactly once.")
            if st.button("Reorder PDF", type="primary", disabled=not file or not order.strip()):
                result = reorder_pdf(file, parse_page_list(order))
                st.download_button("Download reordered PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "OCR":
            pdf = st.file_uploader("Upload PDF", type=["pdf"], key="ocr_pdf")
            language = st.selectbox("OCR language", [("ara", "Arabic"), ("eng", "English"), ("ara+eng", "Arabic + English")], format_func=lambda item: item[1])
            if st.button("Run OCR", type="primary", disabled=pdf is None or not ready):
                with st.spinner("Running OCR…"):
                    result = run_ocr(pdf.getvalue(), pdf.name, language=language[0])
                    extracted_text = result.txt_path.read_text(encoding="utf-8", errors="ignore")
                    st.session_state.analysis_text = extracted_text
                st.success("OCR finished.")
                x, y = st.columns(2)
                x.download_button("Download searchable PDF", result.pdf_path.read_bytes(), result.pdf_path.name, mime="application/pdf")
                y.download_button("Download extracted TXT", extracted_text.encode("utf-8"), result.txt_path.name, mime="text/plain")
                st.text_area("Extracted text", extracted_text, height=240)

        elif tool == "Arabic Word Cloud":
            source = st.radio("Input source", ["Paste text", "Upload TXT", "Upload Excel", "Use last OCR result"], horizontal=True)
            text_value = ""
            if source == "Paste text":
                text_value = st.text_area("Arabic text", st.session_state.analysis_text, height=220)
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
            c1, c2 = st.columns(2)
            with c1:
                available_fonts = get_available_fonts()
                font_names = list(available_fonts.keys())
                selected_font = st.selectbox("Font", font_names, index=0 if font_names else None)
                selected_scheme = st.selectbox("Color scheme", list(COLOR_SCHEMES.keys()), index=list(COLOR_SCHEMES.keys()).index("ELM Brand"))
                transparent = st.checkbox("Transparent background", value=True)
                bg_color = st.color_picker("Background color", "#FFFFFF", disabled=transparent)
            with c2:
                max_words = st.slider("Max words", 50, 500, 200, 10)
                width = st.slider("Width", 400, 2000, 900, 50)
                height = st.slider("Height", 400, 2000, 800, 50)

            with st.expander("Filler words"):
                extra_fillers = st.text_area("Add more fillers", placeholder="مثال: كلمة، كلمة أخرى")
                exclude_fillers = st.text_area("Remove from default fillers", placeholder="مثال: كلمة")
                extra_stopwords = [w.strip() for w in re.split(r'[,\s]+', extra_fillers) if w.strip()]
                exclude_stopwords = [w.strip() for w in re.split(r'[,\s]+', exclude_fillers) if w.strip()]

            if st.button("Generate word cloud", type="primary", disabled=not bool(clean_text.strip())):
                with st.spinner("Generating word cloud…"):
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
                        extra_stopwords=extra_stopwords or None,
                        exclude_stopwords=exclude_stopwords or None,
                    )
                    debug = build_wordcloud_debug_report(clean_text)
                active_stopwords = list(DEFAULT_STOPWORDS)
                active_stopwords.extend(extra_stopwords)
                active_stopwords = [w for w in active_stopwords if w not in set(exclude_stopwords)]
                top = top_terms(clean_text, limit=15, stopwords=active_stopwords)
                st.image(image, caption="Arabic word cloud", use_container_width=True)
                img_buffer = BytesIO()
                image.save(img_buffer, format="PNG")
                st.download_button("Download PNG", img_buffer.getvalue(), file_name="arabic_wordcloud.png", mime="image/png")
                if top:
                    st.dataframe(pd.DataFrame(top, columns=["Word", "Count"]), use_container_width=True, hide_index=True)
                with st.expander("Debug details"):
                    st.json(debug)

        elif tool == "PDF to Excel":
            file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_to_excel")
            st.caption("Exports one row per extracted text line. Reliable, simple, useful.")
            if file and st.button("Convert PDF to Excel", type="primary"):
                result = pdf_to_excel(file)
                st.download_button("Download Excel", result.data, result.filename, mime=result.mime_type)

        elif tool == "Excel to PDF":
            file = st.file_uploader("Upload Excel", type=["xlsx", "xlsm", "xltx", "xltm"], key="excel_to_pdf")
            if file and st.button("Convert Excel to PDF", type="primary"):
                result = excel_to_pdf(file)
                st.download_button("Download PDF", result.data, result.filename, mime="application/pdf")

    except Exception as exc:
        st.error(f"Tool failed: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
ft1, ft2 = st.columns(2)
with ft1:
    st.markdown("<div class='section-card'><h4>Deployment</h4><p>Docker, Railway, Render, and Vercel configs are included. Full OCR needs Docker or a real host because system binaries matter.</p></div>", unsafe_allow_html=True)
with ft2:
    st.markdown("<div class='section-card'><h4>Desktop Packaging</h4><p>PyInstaller, macOS app bundle script, and Linux AppImage/snap scaffolding are included so this can ship like an actual product.</p></div>", unsafe_allow_html=True)
