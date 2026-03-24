# Arabic PDF Suite

![Deploy](https://img.shields.io/badge/Deploy-Free-success) ![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js) ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![License](https://img.shields.io/badge/License-MIT-green)

**Like ILovePDF, but for Arabic documents. 100% free. 100% private.**

Professional PDF tools with full Arabic OCR support. No registration. No data saved. Browser-only.

---

## 🚀 Deploy in 1 Minute (FREE)

### Option 1: Railway (Recommended - Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/arabic-pdf-suite)

1. Click the button above
2. Sign in with GitHub
3. Done! You get a free URL like `your-app.railway.app`

**Free tier includes:** 500 hours/month, 512MB RAM, 1GB storage

---

### Option 2: Render (Free Forever)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/wa1939/arabic-pdf-suite)

1. Click button → Connect GitHub
2. Create free account
3. Get URL like `your-app.onrender.com`

**Free tier:** 750 hours/month, auto-sleeps after 15 min inactivity

---

### Option 3: Vercel + Railway (Split Deployment)

**Frontend (Vercel - Free):**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fwa1939%2Farabic-pdf-suite&root-directory=frontend)

**Backend (Railway - Free):**

[![Deploy Backend on Railway](https://railway.app/button.svg)](https://railway.app/template/arabic-pdf-backend)

---

### Option 4: Docker (Any Cloud)

```bash
# One command
docker run -p 80:80 wa1939/arabic-pdf-suite
```

Works on: AWS, GCP, Azure, DigitalOcean, any VPS

---

## 📸 What You Get

**Single Page - All 15 Tools Visible:**
- Merge PDF
- Split PDF
- Compress PDF
- PDF to Images
- Images to PDF
- Word to PDF
- PDF to Word
- Add Watermark
- Rotate Pages
- Delete Pages
- Reorder Pages
- OCR (Arabic + English)
- Arabic Word Cloud
- PDF to Excel
- Excel to PDF

**3 Ad Placements:**
- Top banner
- Sidebar
- Bottom banner

**Your Branding:**
- "Built by [Your Name]" in footer
- Add your website link

**Privacy First:**
- "No data saved, 100% private, browser-only" messaging
- Files processed and deleted immediately
- No tracking, no analytics

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14.2, React 18, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, Tesseract OCR |
| OCR | Arabic + English support |
| Deploy | Docker, Railway, Render, Vercel |

---

## 🏃 Local Development

```bash
# Clone
git clone https://github.com/wa1939/arabic-pdf-suite.git
cd arabic-pdf-suite

# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## 🧠 OCR Vision & Roadmap

The long-term play is bigger than PDF utilities.

Arabic PDF Suite is becoming **Arabic document intelligence**:
- better Arabic OCR
- searchable PDFs
- low-quality scan recovery
- forms / invoices / ID extraction
- handwriting OCR roadmap

Read the roadmap here:
- [docs/OCR_ROADMAP.md](docs/OCR_ROADMAP.md)

## 🤖 Desktop Build Automation

GitHub Actions now builds portable desktop artifacts automatically for:
- Windows portable folder zipped as `ArabicPDFSuite-windows.zip`
- macOS portable archive as `ArabicPDFSuite-macos.zip`
- Linux portable archive as `ArabicPDFSuite-linux-<arch>.tar.gz`

Run it from the repo Actions tab:
- **Actions → Build Desktop Apps → Run workflow**

The workflow runs tests first, then builds each OS artifact with one shared PyInstaller spec. That is less glamorous than “native installers,” but it is a hell of a lot more reliable.

## 📝 License

MIT - Use it, fork it, sell it, whatever. Just keep the "Built by" credit.

---

## 🙏 Credits

Built by [Waleed Alhamed](https://walhamed.com) • [GitHub](https://github.com/wa1939) • [Twitter](https://twitter.com/wa1939)

---

**Star ⭐ this repo if it helped you!**
