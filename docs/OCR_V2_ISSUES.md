# OCR V2 Prioritized Tickets

These tickets are written for the **current arabic-pdf-suite repo**, not for some imaginary greenfield rewrite.

Current state to keep in mind:
- `backend/main.py` is monolithic
- `src/ocr_service.py` is Tesseract/OCRmyPDF-first
- frontend currently targets the legacy OCR flow
- deployment docs already assume Docker/Railway/Render/Vercel split options

Use this file either as:
- a GitHub issue drafting source, or
- a local implementation backlog

---

## P0 — must ship first

### Issue 1 — Refactor OCR endpoints out of `backend/main.py`
**Priority:** P0  
**Type:** backend / architecture

#### Problem
OCR work is currently hard-wired into `backend/main.py`. Adding fast/deep/camera/searchable routes there will turn the file into a maintenance landfill.

#### Scope
- create `backend/api/ocr_routes.py`
- create `backend/api/pdf_routes.py`
- register routers from `backend/main.py`
- move existing `/api/ocr` into OCR routes without changing public behavior yet

#### Acceptance criteria
- `backend/main.py` is reduced to app setup + router registration
- legacy endpoints still work
- OCR-specific imports no longer live in the main bootstrap file

#### Notes
Do this before adding more OCR modes. Otherwise every next ticket gets uglier.

---

### Issue 2 — Create `src/ocr/` package and compatibility wrapper
**Priority:** P0  
**Type:** backend / architecture

#### Problem
Current OCR logic sits in `src/ocr_service.py` as a single implementation. There is no clean place to add routers, engines, preprocessing, or confidence logic.

#### Scope
- add `src/ocr/` package skeleton
- add `src/ocr/service.py`
- add `src/ocr/schemas.py`
- convert `src/ocr_service.py` into a thin compatibility wrapper that delegates to the new service

#### Acceptance criteria
- new OCR package exists with clean import boundaries
- old imports still function
- no duplicated OCR orchestration logic

---

### Issue 3 — Add native PDF text extraction fast path with `pdfplumber`
**Priority:** P0  
**Type:** backend / OCR quality

#### Problem
The repo OCRs PDFs even when they already contain selectable Arabic text. That is slower and often worse.

#### Scope
- add `src/ocr/engines/pdf_text_engine.py`
- add `src/ocr/pdf/classifier.py`
- use `pdfplumber` to detect meaningful embedded text
- return page-level extraction metrics

#### Acceptance criteria
- born-digital PDFs can bypass OCR
- mixed PDFs are detected as mixed, not blindly treated as scans
- add `POST /api/ocr/extract-text`

#### API
- `POST /api/ocr/extract-text`
- multipart input: `file`, optional `normalize_arabic`, `strip_diacritics`

---

### Issue 4 — Integrate PaddleOCR as the primary Arabic OCR engine
**Priority:** P0  
**Type:** backend / OCR quality

#### Problem
The repo is still Tesseract-first. That does not match the roadmap or the product positioning.

#### Scope
- add `src/ocr/engines/base.py`
- add `src/ocr/engines/paddle_engine.py`
- load Paddle lazily
- support Arabic and Arabic+English mixed mode
- return page confidence and bounding box metadata

#### Acceptance criteria
- Paddle is the default OCR engine in fast mode
- engine can process both images and rasterized PDF pages
- environment variables control CPU/GPU and model paths

#### Dependencies
- `paddleocr`
- model/runtime documentation update

---

### Issue 5 — Implement OCR document classifier and routing service
**Priority:** P0  
**Type:** backend / architecture

#### Problem
There is no ingestion router. Every file takes the same OCR tunnel.

#### Scope
- add `src/ocr/service.py`
- add `src/ocr/router.py` or equivalent dispatch logic
- classify uploads into `digital_pdf`, `scanned_pdf`, `mixed_pdf`, `image`, `unknown`
- route to extract-text vs OCR path appropriately

#### Acceptance criteria
- service chooses route without endpoint-specific hacks
- classification result is returned in OCR JSON response
- fallback chain is logged in response metadata

---

### Issue 6 — Ship `POST /api/ocr/fast` as the new default OCR endpoint
**Priority:** P0  
**Type:** backend / API

#### Problem
There is no V2-ready OCR endpoint. The current `/api/ocr` returns a text file and hides useful metadata.

#### Scope
- add `src/ocr/pipelines/fast_pipeline.py`
- wire up `POST /api/ocr/fast`
- return structured JSON response
- include raw text, normalized text, confidence, timings, and artifact metadata

#### Acceptance criteria
- `/api/ocr/fast` works for scanned PDFs and images
- digital PDFs use extraction route instead of forced OCR when applicable
- legacy `/api/ocr` remains available for now

---

## P1 — core quality lift

### Issue 7 — Add OpenCV preprocessing utilities for scan cleanup
**Priority:** P1  
**Type:** backend / OCR quality

#### Problem
The repo lacks a reusable preprocessing layer for deskewing, denoising, thresholding, and border cleanup.

#### Scope
- add `src/ocr/preprocess/image_quality.py`
- add `src/ocr/preprocess/opencv_pipeline.py`
- implement skew, blur, contrast, and noise heuristics
- apply transforms conditionally, not blindly

#### Acceptance criteria
- preprocessing can be invoked by fast/deep/camera pipelines
- quality scorecard is exposed internally
- ugly scans improve without degrading clean scans by default

---

### Issue 8 — Add confidence scoring and fallback policy
**Priority:** P1  
**Type:** backend / OCR quality

#### Problem
There is no systematic way to decide whether OCR output is good enough.

#### Scope
- add `src/ocr/confidence.py`
- compute page/document confidence
- define thresholds for accept / retry / fallback
- log which pages retried and why

#### Acceptance criteria
- low-confidence pages trigger retry rules
- response includes confidence summary and fallback metadata
- thresholds are configurable by environment variable or settings module

---

### Issue 9 — Implement `POST /api/ocr/deep`
**Priority:** P1  
**Type:** backend / API

#### Problem
The roadmap calls for a deeper OCR mode, but the repo has only one generic path.

#### Scope
- add `src/ocr/pipelines/deep_pipeline.py`
- use stronger preprocessing + higher DPI rasterization
- allow fallback to Tesseract for very low-confidence cases

#### Acceptance criteria
- deep mode is separate from fast mode
- response shows retry/fallback chain
- docs explain latency tradeoff clearly

---

### Issue 10 — Add Arabic normalization module with raw/normalized output split
**Priority:** P1  
**Type:** backend / text processing

#### Problem
OCR output needs Arabic cleanup, but the raw OCR result must remain preserved.

#### Scope
- add `src/ocr/normalizer.py`
- normalize Alef variants
- normalize Ya/Alif Maqsura policy
- optional diacritic stripping
- whitespace and line cleanup

#### Acceptance criteria
- responses include both `raw_text` and `normalized_text`
- normalization can be toggled per request
- defaults are documented for Arabic search/export behavior

---

### Issue 11 — Add searchable PDF pipeline and endpoint
**Priority:** P1  
**Type:** backend / API

#### Problem
Searchable PDF is a roadmap promise but not a first-class V2 endpoint.

#### Scope
- add `src/ocr/pdf/searchable_pdf.py`
- add `src/ocr/pipelines/searchable_pdf_pipeline.py`
- add `POST /api/ocr/searchable-pdf`
- preserve original visuals while embedding searchable text layer

#### Acceptance criteria
- endpoint returns searchable PDF artifact
- OCRmyPDF/Tesseract dependency availability is reported via capabilities endpoint
- searchable PDF success rate is benchmarked

---

### Issue 12 — Add OCR capabilities endpoint for frontend/runtime awareness
**Priority:** P1  
**Type:** backend / API / ops

#### Problem
The frontend cannot currently tell which OCR modes or engines are available in the running deployment.

#### Scope
- add `GET /api/ocr/capabilities`
- return engine availability, hosting mode, supported routes, and system dependency status

#### Acceptance criteria
- endpoint reports Paddle/Tesseract/OCRmyPDF/Ghostscript availability
- frontend can hide or disable unsupported modes

---

## P2 — product polish and delivery

### Issue 13 — Update frontend OCR selector to expose Fast / Deep / Camera / Searchable PDF
**Priority:** P2  
**Type:** frontend

#### Problem
Frontend currently exposes OCR as one generic tool. That will not communicate the product upgrade.

#### Scope
- update OCR upload UI in `frontend/`
- add mode selector
- add brief mode descriptions and warnings about speed/quality tradeoffs
- wire to new OCR endpoints

#### Acceptance criteria
- users can select Fast, Deep, Camera, Searchable PDF
- frontend consumes structured OCR JSON response
- legacy behavior remains available during migration if needed

---

### Issue 14 — Add benchmark dataset manifest and runner
**Priority:** P2  
**Type:** backend / QA

#### Problem
Without benchmarks, “better Arabic OCR” is just marketing perfume.

#### Scope
- add `src/benchmarks/dataset_manifest.py`
- add `src/benchmarks/evaluator.py`
- add `src/benchmarks/runners/run_ocr_benchmark.py`
- create `benchmarks/manifest.json`

#### Acceptance criteria
- benchmark runner compares current Tesseract baseline vs V2 pipelines
- outputs JSON and Markdown summary
- can run locally and in CI/manual QA

---

### Issue 15 — Create initial private benchmark fixture set
**Priority:** P2  
**Type:** QA / data

#### Problem
There is no curated Arabic OCR test set in the repo workflow.

#### Scope
- gather at minimum:
  - 30 clean printed Arabic pages
  - 30 low-quality scans
  - 20 camera photos
  - 20 born-digital PDFs
  - 10 mixed PDFs
- add ground truth and manifest references

#### Acceptance criteria
- fixtures are categorized consistently
- legal/privacy-safe storage plan is documented
- benchmark runner can iterate through all fixtures automatically

---

### Issue 16 — Add OCR artifact builder for txt/json/md outputs
**Priority:** P2  
**Type:** backend / output

#### Problem
Current OCR endpoint emits a text file only. That is too thin for downstream use.

#### Scope
- add `src/ocr/result_builder.py`
- build txt/json/md outputs from one canonical OCR result object
- support optional zipped multi-artifact response later

#### Acceptance criteria
- OCR responses can expose artifact metadata consistently
- outputs are generated from a single source of truth

---

### Issue 17 — Unify OCR dependency documentation and install profiles
**Priority:** P2  
**Type:** docs / devex / ops

#### Problem
Dependencies are currently split between root and backend requirements in a way that will get messier once Paddle/OpenCV/pdfplumber are added.

#### Scope
- document which file is authoritative
- optionally create an OCR-heavy dependency file
- update Docker/Render/Railway deployment notes

#### Acceptance criteria
- a new contributor can install the OCR stack without guessing
- docs explain free/basic/heavy deployment profiles clearly

---

### Issue 18 — Repoint legacy `POST /api/ocr` to the fast pipeline
**Priority:** P2  
**Type:** backend / compatibility

#### Problem
Clients may still use `/api/ocr`, but maintaining separate OCR behavior is pointless.

#### Scope
- keep `/api/ocr` as compatibility route
- make it call the fast pipeline internally
- optionally preserve text-file response shape only when a legacy flag is requested

#### Acceptance criteria
- old clients do not break immediately
- code path is shared with V2 fast mode
- old Tesseract-first logic is no longer the default path

---

## Stretch / after V2 core

### Issue 19 — Add mixed-PDF page-level routing
**Priority:** Stretch  
**Type:** backend / OCR quality

#### Scope
- process text-layer pages with extraction engine
- OCR only image-only pages
- merge outputs into one page-ordered result

#### Why later
Useful and smart, but V2 can ship without perfect per-page routing on day one.

---

### Issue 20 — Prepare extension points for V3 structured extraction
**Priority:** Stretch  
**Type:** architecture

#### Scope
- reserve `src/ocr/layout/` or `src/extract/` namespace
- define response compatibility expectations for PP-Structure phase

#### Why later
Do not bloat V2 with invoice/form/ID logic yet.

---

## Suggested GitHub milestone grouping

### Milestone: OCR V2 Foundation
- Issue 1
- Issue 2
- Issue 3
- Issue 4
- Issue 5
- Issue 6

### Milestone: OCR V2 Quality
- Issue 7
- Issue 8
- Issue 9
- Issue 10
- Issue 11
- Issue 12

### Milestone: OCR V2 Delivery
- Issue 13
- Issue 14
- Issue 15
- Issue 16
- Issue 17
- Issue 18

---

## Recommended execution order

If I were running implementation this week, I’d do it in this order:
1. Issue 1 — route refactor
2. Issue 2 — `src/ocr/` package skeleton
3. Issue 3 — native PDF extraction
4. Issue 4 — Paddle engine
5. Issue 5 — routing service
6. Issue 6 — fast endpoint
7. Issue 7 — preprocessing
8. Issue 8 — confidence/fallback
9. Issue 9 — deep endpoint
10. Issue 10 — normalization
11. Issue 11 — searchable PDF
12. Issue 12 — capabilities endpoint
13. Issue 13+ — frontend and benchmark work

That sequence gets the architecture right first, then ships user-visible wins without building on mud.
