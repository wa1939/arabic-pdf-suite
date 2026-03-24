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
    images_to_pdf,
    merge_pdfs,
    page_count,
    parse_page_list,
    pdf_to_images,
    reorder_pdf,
    rotate_pdf,
    split_pdf,
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
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "English"

ui_lang = st.sidebar.radio("Language / اللغة", ["English", "العربية"], index=0 if st.session_state.ui_lang == "English" else 1)
st.session_state.ui_lang = ui_lang
is_ar = ui_lang == "العربية"
rtl = st.sidebar.toggle("RTL layout / تخطيط RTL", value=is_ar)

labels = {
    "title": "Arabic PDF Suite" if not is_ar else "حزمة المستندات العربية",
    "caption": "Arabic-first OCR, PDF editing, image conversion, watermarking, and word cloud generation." if not is_ar else "أدوات عربية لاستخراج النصوص وتحرير ملفات PDF وتحويل الصور وإضافة العلامة المائية وإنشاء السحابة النصية.",
    "home": "🏠 Home" if not is_ar else "🏠 الرئيسية",
    "ocr": "📄 OCR" if not is_ar else "📄 التعرف الضوئي",
    "pdf": "🧩 PDF Tools" if not is_ar else "🧩 أدوات PDF",
    "cloud": "☁️ Word Cloud" if not is_ar else "☁️ السحابة النصية",
    "template": "📝 Templates" if not is_ar else "📝 قوالب",
    "deploy": "🚀 Deploy" if not is_ar else "🚀 التشغيل",
}

st.markdown(
    f"""
    <style>
      html, body, [class*="css"] {{direction: {'rtl' if rtl else 'ltr'}; text-align: {'right' if rtl else 'left'};}}
      .block-container {{max-width: 1180px; padding-top: 1.2rem; padding-bottom: 2rem;}}
      .hero {{padding: 22px; border: 1px solid #e2e8f0; border-radius: 22px; background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%); box-shadow: 0 12px 40px rgba(15, 23, 42, 0.06);}}
      .tool-card {{padding: 18px; border: 1px solid #e5edf8; border-radius: 18px; background: #ffffff; min-height: 132px; box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04); margin-bottom: 12px;}}
      div[data-testid='stMetric'] {{background: #f8fbff; border: 1px solid #dbeafe; padding: 12px; border-radius: 14px;}}
      .small-note {{color: #5b6470; font-size: 0.92rem;}}
      .pill {{display:inline-block; padding:6px 10px; border-radius:999px; background:#eef5ff; border:1px solid #dbeafe; margin: 4px 6px 0 0;}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(labels["title"])
st.caption(labels["caption"])

with st.container(border=True):
    ready, missing = system_ready()
    a, b, c = st.columns(3)
    a.metric("OCR", "Ready" if ready else "Unavailable")
    b.metric("Privacy", "No signup" if not is_ar else "بدون تسجيل")
    c.metric("Storage", "Temporary" if not is_ar else "مؤقت")
    if ready:
        st.success("OCR is ready on this machine." if not is_ar else "خدمة OCR جاهزة على هذا الجهاز.")
    else:
        st.warning((f"OCR is unavailable here. Missing system packages: {', '.join(missing)}") if not is_ar else (f"خدمة OCR غير متاحة حالياً. الحزم الناقصة: {', '.join(missing)}"))
        st.caption(vercel_friendly_note())

home_tab, ocr_tab, pdf_tab, cloud_tab, template_tab, deploy_tab = st.tabs(
    [labels["home"], labels["ocr"], labels["pdf"], labels["cloud"], labels["template"], labels["deploy"]]
)

with home_tab:
    st.markdown(
        f"""
        <div class='hero'>
          <h3 style='margin:0 0 8px 0;'>{'One clean Arabic document workspace' if not is_ar else 'مساحة واحدة نظيفة للمستندات العربية'}</h3>
          <p style='margin:0;'>{'Upload a PDF, extract text, convert pages to images, rebuild image scans into PDFs, add watermarks, and generate Arabic word clouds.' if not is_ar else 'ارفع ملف PDF، استخرج النص، حوّل الصفحات إلى صور، حوّل الصور إلى PDF، أضف علامة مائية، وأنشئ سحابة نصية عربية.'}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='tool-card'><h4>📄 {'OCR PDF' if not is_ar else 'استخراج النص من PDF'}</h4><p>{'Turn Arabic PDFs into searchable PDFs and extracted text.' if not is_ar else 'حوّل ملفات PDF العربية إلى ملفات قابلة للبحث مع نص مستخرج.'}</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tool-card'><h4>🧩 {'PDF + Image Tools' if not is_ar else 'أدوات PDF والصور'}</h4><p>{'Merge, split, delete, rotate, reorder, convert PDF pages to images, and convert images back to PDF.' if not is_ar else 'دمج وتقسيم وحذف وتدوير وترتيب الصفحات وتحويل صفحات PDF إلى صور وتحويل الصور إلى PDF.'}</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='tool-card'><h4>💧 {'Watermark' if not is_ar else 'العلامة المائية'}</h4><p>{'Apply a text watermark to selected pages with one click.' if not is_ar else 'أضف علامة مائية نصية إلى صفحات محددة بسهولة.'}</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tool-card'><h4>☁️ {'Arabic Word Cloud' if not is_ar else 'السحابة النصية العربية'}</h4><p>{'Arabic shaping is handled before rendering so letters stay connected and RTL-safe.' if not is_ar else 'يتم تشكيل الكلمات العربية قبل الرسم حتى تبقى الحروف متصلة وباتجاه صحيح.'}</p></div>", unsafe_allow_html=True)

with ocr_tab:
    st.subheader("OCR Arabic PDF" if not is_ar else "OCR لملفات PDF العربية")
    pdf = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="ocr_pdf")
    run_button = st.button("Run OCR" if not is_ar else "تشغيل OCR", type="primary", disabled=pdf is None or not ready)

    if run_button and pdf is not None:
        try:
            with st.spinner("Running OCR..." if not is_ar else "جاري تشغيل OCR..."):
                result = run_ocr(pdf.getvalue(), pdf.name)
                extracted_text = result.txt_path.read_text(encoding="utf-8", errors="ignore")
                st.session_state.analysis_text = extracted_text
            st.success("OCR finished." if not is_ar else "اكتمل OCR.")
            x, y = st.columns(2)
            x.download_button("Download searchable PDF" if not is_ar else "تنزيل PDF قابل للبحث", result.pdf_path.read_bytes(), result.pdf_path.name, mime="application/pdf")
            y.download_button("Download extracted TXT" if not is_ar else "تنزيل النص المستخرج", extracted_text.encode("utf-8"), result.txt_path.name, mime="text/plain")
            st.text_area("Extracted text" if not is_ar else "النص المستخرج", extracted_text, height=260)
        except Exception as exc:
            st.error(str(exc))

with pdf_tab:
    st.subheader("PDF Tools" if not is_ar else "أدوات PDF")
    tool_options = [
        "Merge PDFs",
        "Split PDF",
        "Delete pages",
        "Rotate pages",
        "Reorder pages",
        "Compress PDF",
        "PDF to images",
        "Images to PDF",
        "Watermark PDF",
    ]
    tool = st.selectbox("Choose tool" if not is_ar else "اختر الأداة", tool_options)

    try:
        if tool == "Merge PDFs":
            files = st.file_uploader("Upload PDFs" if not is_ar else "ارفع ملفات PDF", type=["pdf"], accept_multiple_files=True, key="merge_pdf")
            if st.button("Merge PDFs" if not is_ar else "دمج الملفات", type="primary", disabled=not files):
                merged = merge_pdfs(files)
                st.download_button("Download merged PDF" if not is_ar else "تنزيل الملف المدمج", merged.data, merged.filename, mime="application/pdf")

        elif tool == "Split PDF":
            file = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="split_pdf")
            ranges = st.text_input("Pages or ranges" if not is_ar else "الصفحات أو النطاقات", placeholder="1-3,5,7-9")
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Split PDF" if not is_ar else "تقسيم الملف", type="primary", disabled=not file or not ranges.strip()):
                zip_data = split_pdf(file, ranges)
                st.download_button("Download ZIP" if not is_ar else "تنزيل ZIP", zip_data, "split_pdfs.zip", mime="application/zip")

        elif tool == "Delete pages":
            file = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="delete_pdf")
            pages = st.text_input("Pages to delete" if not is_ar else "الصفحات المراد حذفها", placeholder="2,4,8")
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Delete selected pages" if not is_ar else "حذف الصفحات", type="primary", disabled=not file or not pages.strip()):
                result = delete_pages(file, parse_page_list(pages))
                st.download_button("Download cleaned PDF" if not is_ar else "تنزيل الملف بعد الحذف", result.data, result.filename, mime="application/pdf")

        elif tool == "Rotate pages":
            file = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="rotate_pdf")
            pages = st.text_input("Pages to rotate" if not is_ar else "الصفحات المراد تدويرها", placeholder="1,2")
            angle = st.selectbox("Angle" if not is_ar else "الزاوية", [90, 180, 270])
            if file:
                st.caption(f"Total pages: {page_count(file)}")
            if st.button("Rotate pages" if not is_ar else "تدوير الصفحات", type="primary", disabled=not file or not pages.strip()):
                result = rotate_pdf(file, parse_page_list(pages), angle)
                st.download_button("Download rotated PDF" if not is_ar else "تنزيل الملف", result.data, result.filename, mime="application/pdf")

        elif tool == "Reorder pages":
            file = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="reorder_pdf")
            order = st.text_input("New page order" if not is_ar else "ترتيب الصفحات الجديد", placeholder="3,1,2,4")
            if file:
                count = page_count(file)
                st.caption((f"Total pages: {count}. Enter every page exactly once.") if not is_ar else f"عدد الصفحات: {count}. أدخل كل صفحة مرة واحدة فقط.")
            if st.button("Reorder PDF" if not is_ar else "إعادة الترتيب", type="primary", disabled=not file or not order.strip()):
                result = reorder_pdf(file, parse_page_list(order))
                st.download_button("Download reordered PDF" if not is_ar else "تنزيل الملف", result.data, result.filename, mime="application/pdf")

        elif tool == "Compress PDF":
            file = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="compress_pdf")
            if file and st.button("Compress PDF" if not is_ar else "ضغط الملف", type="primary"):
                result = compress_pdf(file)
                st.download_button("Download compressed PDF" if not is_ar else "تنزيل الملف المضغوط", result.data, result.filename, mime="application/pdf")

        elif tool == "PDF to images":
            file = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="pdf_to_images")
            dpi = st.slider("DPI", 72, 300, 150, 12)
            fmt = st.selectbox("Image format" if not is_ar else "صيغة الصورة", ["png", "jpg"])
            if file and st.button("Extract pages as images" if not is_ar else "استخراج الصفحات كصور", type="primary"):
                zip_data = pdf_to_images(file, image_format=fmt, dpi=dpi)
                st.download_button("Download images ZIP" if not is_ar else "تنزيل الصور ZIP", zip_data, "pdf_pages.zip", mime="application/zip")

        elif tool == "Images to PDF":
            files = st.file_uploader("Upload images" if not is_ar else "ارفع الصور", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, key="images_to_pdf")
            if files and st.button("Convert images to PDF" if not is_ar else "تحويل الصور إلى PDF", type="primary"):
                result = images_to_pdf(files)
                st.download_button("Download PDF" if not is_ar else "تنزيل PDF", result.data, result.filename, mime="application/pdf")

        elif tool == "Watermark PDF":
            file = st.file_uploader("Upload PDF" if not is_ar else "ارفع ملف PDF", type=["pdf"], key="watermark_pdf")
            watermark_text = st.text_input("Watermark text" if not is_ar else "نص العلامة المائية", value="سري / Confidential")
            pages = st.text_input("Pages (optional)" if not is_ar else "الصفحات (اختياري)", placeholder="1-3,5")
            opacity = st.slider("Opacity" if not is_ar else "الشفافية", 0.05, 0.9, 0.18, 0.01)
            rotation = st.slider("Rotation" if not is_ar else "الدوران", -90, 90, 35, 5)
            if file and st.button("Add watermark" if not is_ar else "إضافة علامة مائية", type="primary"):
                page_values = parse_page_list(pages) if pages.strip() else None
                result = add_text_watermark(file, watermark_text, pages=page_values, opacity=opacity, rotation=rotation)
                st.download_button("Download watermarked PDF" if not is_ar else "تنزيل الملف", result.data, result.filename, mime="application/pdf")
    except Exception as exc:
        st.error(f"PDF tool failed: {exc}")

with cloud_tab:
    st.subheader("Arabic Word Cloud" if not is_ar else "السحابة النصية العربية")
    st.caption("Arabic words are tokenized first, then reshaped before rendering for safer connected letters." if not is_ar else "يتم تقطيع الكلمات العربية أولاً ثم تشكيلها قبل الرسم لضمان الحروف المتصلة بشكل أفضل.")
    source = st.radio("Input source" if not is_ar else "مصدر النص", ["Paste text", "Upload TXT", "Upload Excel", "Use last OCR result"], horizontal=True)

    text_value = ""
    if source == "Paste text":
        text_value = st.text_area("Arabic text" if not is_ar else "النص العربي", st.session_state.analysis_text, height=220, placeholder="Paste Arabic text here..." if not is_ar else "الصق النص العربي هنا...")
    elif source == "Upload TXT":
        txt_file = st.file_uploader("Upload TXT" if not is_ar else "ارفع TXT", type=["txt"], key="txt_uploader")
        if txt_file:
            text_value = extract_text_from_txt(txt_file.getvalue())
            st.text_area("Preview" if not is_ar else "معاينة", text_value, height=220)
    elif source == "Upload Excel":
        xlsx = st.file_uploader("Upload Excel" if not is_ar else "ارفع Excel", type=["xlsx", "xls"], key="xlsx_uploader")
        preferred_column = st.text_input("Column name (optional)" if not is_ar else "اسم العمود (اختياري)", value="النص المراد تحليله")
        if xlsx:
            text_value = extract_text_from_excel(xlsx.getvalue(), preferred_column=preferred_column.strip() or None)
            st.text_area("Preview" if not is_ar else "معاينة", text_value, height=220)
    else:
        text_value = st.session_state.analysis_text
        st.text_area("Last OCR text" if not is_ar else "آخر نص OCR", text_value, height=220)

    clean_text = normalize_text(text_value)
    st.markdown("#### Customize" if not is_ar else "#### التخصيص")
    col1, col2 = st.columns(2)
    with col1:
        available_fonts = get_available_fonts()
        font_names = list(available_fonts.keys())
        selected_font = st.selectbox("Font" if not is_ar else "الخط", font_names, index=0 if font_names else None)
        selected_scheme = st.selectbox("Color scheme" if not is_ar else "نظام الألوان", list(COLOR_SCHEMES.keys()), index=list(COLOR_SCHEMES.keys()).index("ELM Brand"))
        transparent = st.checkbox("Transparent background" if not is_ar else "خلفية شفافة", value=True)
        bg_color = st.color_picker("Background color" if not is_ar else "لون الخلفية", "#FFFFFF", disabled=transparent)
    with col2:
        max_words = st.slider("Max words" if not is_ar else "أقصى عدد كلمات", 50, 500, 200, 10)
        width = st.slider("Width" if not is_ar else "العرض", 400, 2000, 900, 50)
        height = st.slider("Height" if not is_ar else "الارتفاع", 400, 2000, 800, 50)

    with st.expander("🔤 Filler words (stopwords)" if not is_ar else "🔤 الكلمات المستبعدة", expanded=False):
        extra_fillers = st.text_area("Add more fillers" if not is_ar else "أضف كلمات مستبعدة", placeholder="مثال: كلمة، كلمة أخرى")
        exclude_fillers = st.text_area("Remove from default fillers" if not is_ar else "إزالة من الكلمات المستبعدة الافتراضية", placeholder="مثال: كلمة")
        extra_stopwords = [w.strip() for w in re.split(r'[,\s]+', extra_fillers) if w.strip()]
        exclude_stopwords = [w.strip() for w in re.split(r'[,\s]+', exclude_fillers) if w.strip()]
    if 'extra_stopwords' not in locals():
        extra_stopwords, exclude_stopwords = [], []

    if st.button("Generate word cloud" if not is_ar else "إنشاء السحابة النصية", type="primary", disabled=not bool(clean_text.strip())):
        with st.spinner("Generating word cloud..." if not is_ar else "جاري إنشاء السحابة..."):
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
        active_stopwords = None
        if extra_stopwords or exclude_stopwords:
            active_stopwords = list(DEFAULT_STOPWORDS)
            if extra_stopwords:
                active_stopwords.extend(extra_stopwords)
            if exclude_stopwords:
                excluded = set(exclude_stopwords)
                active_stopwords = [w for w in active_stopwords if w not in excluded]
        top = top_terms(clean_text, limit=15, stopwords=active_stopwords)
        st.image(image, caption="Arabic word cloud" if not is_ar else "السحابة النصية العربية", use_container_width=True)
        img_buffer = BytesIO()
        image.save(img_buffer, format="PNG")
        st.download_button("Download PNG" if not is_ar else "تنزيل PNG", img_buffer.getvalue(), file_name="arabic_wordcloud.png", mime="image/png")
        if top:
            st.dataframe(pd.DataFrame(top, columns=["Word" if not is_ar else "الكلمة", "Count" if not is_ar else "العدد"]), use_container_width=True, hide_index=True)
        with st.expander("Debug details" if not is_ar else "تفاصيل الفحص"):
            st.json(debug)

with template_tab:
    st.subheader("Templates" if not is_ar else "قوالب")
    template = st.selectbox("Choose template" if not is_ar else "اختر القالب", [
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
    temp_text = st.text_area("Template text" if not is_ar else "نص القالب", defaults[template], height=220)
    if st.button("Use in Word Cloud" if not is_ar else "استخدام في السحابة النصية", type="primary"):
        st.session_state.analysis_text = temp_text
        st.success("Template text moved to the Word Cloud tab." if not is_ar else "تم نقل النص إلى تبويب السحابة النصية.")

with deploy_tab:
    st.subheader("Deploy or run locally" if not is_ar else "التشغيل أو النشر")
    st.markdown("**Hosted version**: Railway, Render, Fly.io, or any VPS with Docker." if not is_ar else "**النسخة المستضافة**: Railway أو Render أو Fly.io أو أي VPS يدعم Docker.")
    st.markdown("**Local version**: run `./run.sh` on macOS/Linux or `run.bat` on Windows." if not is_ar else "**النسخة المحلية**: شغّل `./run.sh` على macOS/Linux أو `run.bat` على Windows.")
    st.code("docker compose up --build", language="bash")
