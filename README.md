# Arabic PDF Suite

A single lightweight app that merges your existing projects into one Arabic-first document tool.

## Included in one app
- **Arabic OCR**: searchable PDF + extracted TXT
- **PDF tools**: merge, split, delete pages, rotate, reorder
- **Arabic word cloud**: from OCR text, pasted text, TXT, or Excel
- **Templates**: ready-made text starters for surveys, feedback, and workshops

Think of it as a lightweight **Arabic PDF suite**.

---

## What makes this useful
- one repo
- one app
- no signup
- no permanent file storage
- easy for non-technical users
- one-click local run
- one-click hosted deployment on Docker-friendly platforms

---

## Quick start

### One click local run
#### Windows
Double-click:
- `run.bat`

#### macOS / Linux
```bash
chmod +x run.sh
./run.sh
```

### One command Docker run
```bash
docker compose up --build
```

Open:
- <http://localhost:8501>

---

## Hosted deployment
This repo is prepared for Docker-based hosting.

### Deploy to Railway
1. Create a new project in Railway
2. Connect this repo
3. Railway will detect `railway.json` + `Dockerfile`
4. Deploy

### Deploy to Render
1. Create a new Web Service from this repo
2. Render will detect `render.yaml`
3. Deploy

### Deploy anywhere with Docker
```bash
docker build -t arabic-pdf-suite .
docker run --rm -p 8501:8501 arabic-pdf-suite
```

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

## Why this stack
This is intentionally a **single Streamlit app** because it is:
- fast to ship
- simple to maintain
- easy to package
- easy to self-host
- good enough for a public utility tool

For OCR, the app uses system tools:
- **Tesseract OCR**
- **Ghostscript**

That means:
- great for Docker/self-host/VPS/Railway/Render/Fly
- not a clean fit for Vercel OCR

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

## Privacy
Recommended product promise:
- no signup
- no permanent file storage
- files processed temporarily and deleted

For maximum privacy, run locally or self-host.

---

## Repo structure
```text
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── railway.json
├── render.yaml
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

### Done
- merge your two repos into one app
- add PDF tools
- add one-click local launch
- add Docker deploy
- prepare Railway/Render deployment config

### Next
- stronger Arabic UI polish
- drag-and-drop page reordering
- better PDF compression
- more templates
- release packaging for desktop download
- hosted public instance
- ads layout

---

## Suggested final repo name
- `arabic-pdf-suite`

Short, clear, useful.
