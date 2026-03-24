# Arabic PDF Suite

![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

**Like ILovePDF, but built for Arabic documents.**

Professional PDF tools with full Arabic OCR support. Merge, split, compress, convert, OCR, watermark, and more. Modern Next.js frontend with Python FastAPI backend.

[**Live Demo**](#) • [**Deploy Your Own**](#-deploy-in-3-minutes) • [**Documentation**](#documentation)

---

## Why Arabic PDF Suite?

Most PDF tools treat Arabic as an afterthought. This one doesn't.

| Feature | ILovePDF | SmallPDF | **Arabic PDF Suite** |
|---------|----------|----------|---------------------|
| Arabic OCR | ❌ | ❌ | ✅ Full support |
| RTL Interface | ❌ | ❌ | ✅ Built-in |
| Self-host | ❌ | ❌ | ✅ Your server |
| Free forever | ❌ | ❌ | ✅ Open source |
| Privacy | ⚠️ Cloud | ⚠️ Cloud | ✅ 100% local |

---

## ✨ Features

### 📄 PDF Tools (15 tools)
- **Merge PDF** - Combine multiple PDFs into one
- **Split PDF** - Split into multiple files or extract pages
- **Compress PDF** - Reduce file size intelligently
- **PDF ↔ Images** - Convert both ways
- **PDF ↔ Word** - Full document conversion
- **PDF ↔ Excel** - Table extraction and conversion
- **Add Watermark** - Custom text watermarks
- **Rotate Pages** - 90°, 180°, 270° rotation
- **Delete Pages** - Remove unwanted pages
- **Reorder Pages** - Drag to rearrange
- **OCR** - Arabic + English text extraction
- **Arabic Word Cloud** - Beautiful visualizations

### 🌐 Modern Stack
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **Backend**: Python 3.11 + FastAPI
- **Architecture**: Microservices with REST API
- **Deploy**: Docker Compose, Vercel + Railway, or bare metal

### 🔒 Privacy First
- Files processed locally on your server
- Automatic cleanup after processing
- No external API calls
- No tracking, no analytics, no BS

---

## 🚀 Deploy in 3 Minutes

### Option 1: Docker Compose (Recommended)

```bash
# Clone and run
git clone https://github.com/wa1939/arabic-pdf-suite.git
cd arabic-pdf-suite
docker compose up --build
```

Open http://localhost

### Option 2: Vercel + Railway

**Frontend (Vercel):**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fwa1939%2Farabic-pdf-suite&env=NEXT_PUBLIC_API_URL)

**Backend (Railway):**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/arabic-pdf-suite)

### Option 3: One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/wa1939/arabic-pdf-suite/main/install.sh | bash
```

---

## 📸 Screenshots

### Home Page
![Home](docs/screenshots/home.png)

### Tool Interface
![Tool](docs/screenshots/tool.png)

### Dark Mode
![Dark](docs/screenshots/dark.png)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **PDF Engine** | PyPDF2, pdf2image, ReportLab |
| **OCR** | Tesseract (Arabic + English) |
| **Office** | python-docx, openpyxl, LibreOffice |
| **Deployment** | Docker, Docker Compose, Nginx |

---

## 📁 Project Structure

```
arabic-pdf-suite/
├── frontend/              # Next.js app
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities
│   └── public/           # Static assets
├── backend/              # FastAPI app
│   ├── main.py          # API routes
│   └── requirements.txt
├── src/                  # Shared Python modules
│   ├── pdf_tools.py     # PDF operations
│   ├── ocr_service.py   # OCR logic
│   └── text_utils.py    # Arabic text handling
├── docker-compose.yml
├── Dockerfile.backend
├── nginx.conf
└── README.md
```

---

## 🔧 Local Development

### Prerequisites

- Node.js 20+
- Python 3.11+
- Tesseract OCR with Arabic language pack

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-ara tesseract-ocr-eng \
    ghostscript qpdf poppler-utils libreoffice-writer libreoffice-calc

# Run backend
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Run development server
npm run dev
```

Open http://localhost:3000

---

## 🌍 Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)

```env
# No required env vars for basic setup
# Optional: configure CORS, rate limiting, etc.
```

---

## 📖 API Reference

### Health Check
```
GET /health
```

### Merge PDFs
```
POST /api/merge
Content-Type: multipart/form-data

files: [PDF files]
```

### Split PDF
```
POST /api/split
Content-Type: multipart/form-data

file: PDF file
mode: "all" | "range" | "extract"
pages: "1,3,5-7" (optional)
```

### Compress PDF
```
POST /api/compress
Content-Type: multipart/form-data

file: PDF file
quality: "low" | "medium" | "high"
```

### OCR
```
POST /api/ocr
Content-Type: multipart/form-data

file: PDF or image
language: "ara+eng" (default)
```

[View full API docs →](docs/API.md)

---

## 🗺️ Roadmap

- [ ] Drag-and-drop page reordering
- [ ] PDF signing
- [ ] PDF password protection
- [ ] Batch processing
- [ ] Arabic handwriting OCR
- [ ] Browser extension
- [ ] Desktop apps (Electron)

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [PyPDF2](https://github.com/py-pdf/pypdf) - PDF manipulation
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API framework
- [Next.js](https://nextjs.org/) - React framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS

---

<div align="center">

**Made with ❤️ by [Waleed Alhamed](https://walhamed.com)**

[Website](https://walhamed.com) • [GitHub](https://github.com/wa1939) • [Twitter](https://twitter.com/wa1939)

</div>
