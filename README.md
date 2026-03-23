# Arabic PDF Suite

A single lightweight app that merges your existing projects into one Arabic-first document tool.

## Included in one app
- **Arabic OCR**: searchable PDF + extracted TXT
- **PDF tools**: merge, split, delete pages, rotate, reorder
- **Arabic word cloud**: from OCR text, pasted text, TXT, or Excel
- **Templates**: ready-made text starters for surveys, feedback, and workshops

Think of it as a lightweight **Arabic PDF suite**.

---

## Product goals
- one repo
- one app
- no signup
- no saved user data
- easy for non-technical users
- one-click local run
- one-click hosted deployment

---

## Tech choice
This is intentionally built as a **single Streamlit app** because it is:
- fast to ship
- easy to maintain
- easy to package
- easy to self-host
- good enough for a public utility tool

For OCR, the app uses system tools:
- **Tesseract OCR**
- **Ghostscript**

That means:
- **great for Docker/self-host/VPS/Railway/Render/Fly**
- **not a good fit for Vercel OCR**

Vercel can host the frontend of a fancier future version, but not this full OCR stack cleanly.

---

## Features

### 1) OCR Arabic PDF
Upload a PDF and get:
- searchable PDF
- extracted UTF-8 text
- text ready for the Word Cloud tab

### 2) PDF Tools
- merge PDFs
- split PDF by page ranges
- delete selected pages
- rotate selected pages
- reorder pages

### 3) Word Cloud
Generate Arabic word clouds from:
- pasted text
- TXT files
- Excel files
- OCR output from uploaded PDF

### 4) Templates
Use simple text templates for:
- workshop feedback
- employee comments
- student feedback
- customer feedback

---

## Local run in one click

### Windows
Double-click:
- `run.bat`

### macOS / Linux
Run:
```bash
chmod +x run.sh
./run.sh
```

---

## Manual local setup

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

### 2) Python dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Run
```bash
streamlit run app.py
```

---

## Docker

### One command
```bash
docker compose up --build
```

Then open:
- <http://localhost:8501>

You can also use plain Docker:
```bash
docker build -t arabic-pdf-suite .
docker run --rm -p 8501:8501 arabic-pdf-suite
```

---

## One-click deployment
This repo is designed to be deployable to platforms that support Docker.

Best options:
- Railway
- Render
- Fly.io
- VPS with Docker

If you want, the next step is adding:
- `railway.json`
- `render.yaml`
- deployment badges/buttons in README

---

## Privacy
Recommended product promise:
- no signup
- no permanent file storage
- files processed temporarily and deleted

For true maximum privacy, run locally or self-host.

---

## Repo structure
```text
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.bat
├── run.sh
├── .gitignore
└── src/
    ├── ocr_service.py
    ├── pdf_tools.py
    └── text_utils.py
```

---

## Roadmap

### Phase 1
- merge your two repos into one app ✅
- add PDF tools ✅
- add one-click local launch ✅
- add Docker deploy ✅

### Phase 2
- better Arabic UI polish
- drag-and-drop page reordering
- PDF compression improvements
- more templates
- better mobile layout

### Phase 3
- desktop installer build
- hosted public deployment
- ads placement
- analytics
- optional premium limits later

---

## Suggested final repo name
- `arabic-pdf-suite`

That’s the cleanest name. Short, clear, useful.
