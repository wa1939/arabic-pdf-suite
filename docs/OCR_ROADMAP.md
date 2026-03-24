# Arabic PDF Suite — OCR Roadmap

## Positioning

Arabic PDF Suite should not compete as a generic PDF utility.

It should win as **the best Arabic document intelligence suite**:
- best Arabic OCR
- best Arabic PDF workflows
- best Arabic scan recovery
- best Arabic document extraction

That is the moat.

---

## North Star

Make Arabic PDF Suite the default tool for:
- Arabic printed text OCR
- Arabic scanned PDFs
- Arabic camera photos
- Arabic low-quality documents
- Arabic tables, invoices, forms, IDs
- Arabic handwriting (beta → mature)

---

## Recommended OCR Stack

### Core stack
- **PaddleOCR** → primary OCR engine
- **OCRmyPDF** → searchable PDF output
- **pdfplumber** → born-digital PDF extraction before OCR
- **Camelot** → native table extraction from digital PDFs
- **OpenCV** → preprocessing (deskew, denoise, thresholding, perspective fix)
- **CAMeL Tools** → Arabic normalization/post-processing

### Heavy path stack
- **Real-ESRGAN** → selective enhancement for ugly scans/photos
- **PP-StructureV3** → layout, tables, structured docs
- **PP-ChatOCRv4** → receipts/forms/invoices field extraction
- **Arabic-GLM-OCR-v1** or custom TrOCR-style Arabic model → handwriting / low-confidence heavy route

---

## Product Architecture

### 1. Ingestion Router
Every input should be classified into one of these lanes:
- Born-digital PDF
- Scanned PDF
- Camera photo/image
- Structured document (invoice/form/receipt/ID)
- Handwriting-likely document

### 2. Fast Path
Use this for speed and cost efficiency:
- born-digital PDF → `pdfplumber`
- clean image/PDF → `PaddleOCR`
- searchable PDF → `OCRmyPDF`
- native tables → `Camelot`

### 3. Heavy Path
Use this only when confidence is low or doc type demands it:
- camera photos → `OpenCV + Paddle`
- ugly scans → `OpenCV + optional Real-ESRGAN + Paddle`
- invoices/forms/IDs → `PP-StructureV3 + PP-ChatOCRv4`
- handwriting → `Arabic-GLM-OCR-v1` or custom handwriting model

### 4. Arabic Cleanup Layer
After OCR:
- normalize Alef variants
- normalize Ya / Ta Marbuta where needed
- optional diacritic stripping for search
- preserve original output separately
- confidence-aware cleanup and correction hooks

### 5. Output Layer
Every OCR route should support:
- Plain text
- Markdown
- JSON
- Searchable PDF
- Excel/CSV for tables
- confidence metadata

---

## Roadmap

## V2 — OCR That Actually Wins

### Goal
Beat Tesseract-first Arabic OCR tools decisively.

### Build
- Replace Tesseract-first with **PaddleOCR-first**
- Add document type router
- Add camera image OCR mode
- Add searchable PDF mode using OCRmyPDF
- Add confidence score + fallback retry
- Add born-digital no-OCR path with pdfplumber
- Add Arabic normalization cleanup

### Product changes
New OCR modes:
- Fast OCR
- Deep OCR
- Searchable PDF
- Camera OCR

### API endpoints to add
- `POST /api/ocr/fast`
- `POST /api/ocr/deep`
- `POST /api/ocr/camera`
- `POST /api/ocr/searchable-pdf`
- `POST /api/ocr/extract-text`

### Success criteria
- better Arabic text extraction quality on clean and medium-quality docs
- searchable PDFs generated reliably
- faster path for native PDFs without unnecessary OCR

---

## V3 — Arabic Document Intelligence

### Goal
Go beyond OCR into structured extraction.

### Build
- PP-StructureV3 integration
- invoice extraction
- receipt extraction
- form extraction
- ID extraction
- table extraction to Excel/CSV/JSON
- section/reading order recovery
- confidence review UI

### Product additions
- Arabic Invoice Extractor
- Arabic Receipt Scanner
- Arabic ID Reader
- Arabic Table Extractor
- Arabic Form Parser

### API endpoints to add
- `POST /api/extract/invoice`
- `POST /api/extract/receipt`
- `POST /api/extract/id`
- `POST /api/extract/form`
- `POST /api/extract/table`

### Success criteria
- field-level extraction for semi-structured Arabic docs
- meaningful exports to Excel/JSON
- clear confidence scores for extracted fields

---

## V4 — The Arabic Moat

### Goal
Own ugly Arabic documents that competitors fail on.

### Build
- handwriting OCR beta
- low-quality scan rescue mode
- page-level ensemble routing
- user correction loop for active learning
- domain packs: legal, education, government, receipts
- smart correction suggestions

### Product additions
- Handwritten Arabic OCR
- Low-Quality Scan Rescue
- Smart Review Mode
- Arabic Doc Intelligence Pro

### Success criteria
- usable handwriting extraction on real Arabic samples
- materially better recovery on blurry/noisy Arabic images
- benchmark improvements on hard documents

---

## Immediate Tickets

### OCR v2 Implementation Tickets
1. Add `services/paddle_ocr.py`
2. Add OCR router service for doc classification
3. Add `pdfplumber` path for native PDFs
4. Add searchable PDF generation pipeline with OCRmyPDF
5. Add Arabic text normalization module
6. Add OpenCV preprocessing utilities
7. Add confidence-based retry/fallback logic
8. Add frontend OCR mode selector
9. Add benchmark dataset folder + evaluation script
10. Keep Tesseract only as fallback

### Structured Extraction Tickets
1. Add `services/layout_analysis.py`
2. Add `services/field_extraction.py`
3. Add invoice/receipt/form/ID schemas
4. Add table extraction export helpers
5. Add structured JSON response format

### Handwriting Tickets
1. Benchmark Arabic-GLM-OCR-v1 on real Arabic handwriting samples
2. Define handwriting test dataset
3. Add handwriting-specific inference endpoint
4. Add beta label in UI

---

## Benchmarking Plan

Create a private benchmark set with at least:
- 100 clean printed Arabic pages
- 100 low-quality scanned Arabic pages
- 100 Arabic camera photos
- 50 Arabic invoices/receipts/forms
- 50 Arabic table-heavy docs
- 50 Arabic handwriting samples

Track:
- CER / WER
- field extraction accuracy
- table extraction accuracy
- searchable PDF success rate
- latency per route

---

## Risks

### 1. Handwriting is hard
There is no guaranteed production-perfect Arabic handwriting model yet. Treat it as beta first.

### 2. GPU helps a lot
Heavy OCR, layout, restoration, and handwriting are much better with GPU.

### 3. Image enhancement can backfire
Do not apply enhancement blindly. Route by quality heuristics.

### 4. Tesseract cannot be the hero
It can remain as fallback, not as the flagship engine.

---

## Product Messaging

### Wrong
- Arabic PDF tools
- OCR + merge PDF

### Right
- **Arabic document intelligence**
- **The best Arabic OCR and Arabic PDF suite**
- **From ugly scan to searchable, structured Arabic data**

---

## Final Recommendation

Build the moat in this order:
1. **PaddleOCR-first OCR v2**
2. **searchable PDF + native PDF extraction**
3. **structured Arabic doc extraction**
4. **handwriting + ugly-doc rescue**

That gives Arabic PDF Suite a real category, not just another toolbox.
