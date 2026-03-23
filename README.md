# Arabic OCR + Word Cloud

One lightweight app that combines your two ideas into a single clean product:

- **Arabic PDF OCR** → searchable PDF + extracted TXT
- **Arabic text analysis** → Arabic-safe word cloud from OCR output, pasted text, TXT, or Excel

Built to stay **minimal, fast, and easy to deploy**.

---

## What it does

### 1) OCR
Upload an Arabic PDF and get:
- searchable PDF
- extracted UTF-8 text
- text sent directly into the analysis tab

### 2) Word Cloud
Generate a word cloud from:
- pasted Arabic text
- TXT upload
- Excel upload (`.xlsx` / `.xls`)
- the latest OCR result

Arabic shaping and bidi rendering are handled for proper display.

---

## Why this architecture

This app uses **Streamlit** because it is the fastest path to a clean, minimal UX without dragging in a heavy frontend stack.

### Good fit for:
- local desktop-ish use
- internal web app
- Docker deployment
- simple self-hosting

### Not ideal for:
- **Vercel OCR runtime**

Why? OCR needs **system binaries**:
- Tesseract OCR
- Ghostscript

Vercel is fine for lightweight Python UI experiments, but **not a reliable place for full OCR pipelines**. If you want public deployment with OCR working properly, use:
- Docker
- VPS
- Railway
- Render
- Fly.io
- your own server

---

## Local run

### 1) Install system dependencies

#### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ara ghostscript qpdf pngquant
```

#### macOS
```bash
brew install tesseract ghostscript qpdf pngquant
brew install tesseract-lang
```

#### Windows
Install:
- Tesseract OCR
- Arabic language pack (`ara`)
- Ghostscript

---

### 2) Install Python dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Run
```bash
streamlit run app.py
```

Open the local URL Streamlit gives you.

---

## Docker

Build:
```bash
docker build -t arabic-ocr-wordcloud .
```

Run:
```bash
docker run --rm -p 8501:8501 arabic-ocr-wordcloud
```

Then open:
- <http://localhost:8501>

---

## Project structure

```text
.
├── app.py
├── Dockerfile
├── requirements.txt
├── .gitignore
├── assets/
└── src/
    ├── ocr_service.py
    └── text_utils.py
```

---

## UX decisions

- one page
- two tabs only
- minimal choices
- OCR output flows directly into analysis
- clean downloads, no clutter

---

## Notes

- If OCR says dependencies are missing, the UI still works for text/Excel/word-cloud generation.
- Private/public hosting is your choice, but **full OCR belongs on Docker/self-host**, not Vercel.
- If you later want a prettier production version, the next upgrade path is **Next.js frontend + Python OCR worker**, but that’s extra complexity you probably don’t need yet.

---

## Suggested repo name

A clean merged repo name:
- `arabic-ocr-suite`
- `arabic-insight-studio`
- `arabic-ocr-wordcloud`

My vote: **`arabic-ocr-wordcloud`**. Clear, boring, effective.
