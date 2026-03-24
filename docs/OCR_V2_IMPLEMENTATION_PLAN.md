# OCR V2 Implementation Plan

## Why this plan exists

`docs/OCR_ROADMAP.md` sets the product direction, but the repo still ships a **Tesseract-first OCR path**:
- `backend/main.py` exposes a single `POST /api/ocr` endpoint
- `src/ocr_service.py` is built around `ocrmypdf` + Tesseract + Ghostscript
- there is no ingestion router, no native PDF fast path, no confidence-based fallback, and no OCR-specific benchmark harness

This document converts the roadmap into a **repo-specific execution plan** for the current codebase.

---

## Current repo baseline

### Current OCR-related files
- `backend/main.py` — monolithic FastAPI app with all endpoints
- `src/ocr_service.py` — current OCR wrapper around OCRmyPDF/Tesseract
- `src/pdf_tools.py` — existing PDF transformations
- `src/text_utils.py` — existing text helpers (non-OCR architecture)
- `backend/requirements.txt` and `requirements.txt` — dependency split is inconsistent today

### Current product gap
The app already has generic PDF tools, but OCR is still a single legacy lane:
- no distinction between born-digital vs scanned PDFs
- no Arabic-first OCR engine abstraction
- no clean way to add PaddleOCR / OpenCV preprocessing / PP-Structure later
- no structured OCR JSON response contract
- no benchmark harness to prove Arabic quality gains

---

## V2 objective

Ship an OCR stack that is:
- **PaddleOCR-first** for Arabic printed text
- **fast-path aware** for born-digital PDFs
- **searchable-PDF capable** via OCRmyPDF/Tesseract as a packaging backend, not the flagship recognizer
- **router-driven** so future V3/V4 additions do not turn `backend/main.py` into spaghetti

---

## Target backend architecture

## Directory changes

Add these modules under `src/`:

```text
src/
  ocr/
    __init__.py
    schemas.py
    router.py
    confidence.py
    normalizer.py
    result_builder.py
    service.py
    engines/
      __init__.py
      base.py
      paddle_engine.py
      tesseract_engine.py
      pdf_text_engine.py
    pipelines/
      __init__.py
      fast_pipeline.py
      deep_pipeline.py
      camera_pipeline.py
      searchable_pdf_pipeline.py
    preprocess/
      __init__.py
      image_quality.py
      opencv_pipeline.py
      page_rasterizer.py
    pdf/
      __init__.py
      classifier.py
      extractor.py
      searchable_pdf.py
  benchmarks/
    __init__.py
    dataset_manifest.py
    evaluator.py
    runners/
      run_ocr_benchmark.py
```

### Keep but deprecate
- `src/ocr_service.py`
  - keep temporarily as a compatibility wrapper
  - reimplement it to call the new `src/ocr/service.py`
  - remove direct OCR business logic from it after frontend migration

---

## Exact modules to add

## 1) `src/ocr/schemas.py`
Define the request/response contracts used by FastAPI.

### Add models for:
- `OCRMode` enum: `fast`, `deep`, `camera`, `searchable_pdf`, `extract_text`
- `DocumentKind` enum: `digital_pdf`, `scanned_pdf`, `image`, `mixed_pdf`, `unknown`
- `OCRRequestOptions`
- `OCRPageResult`
- `OCRArtifact`
- `OCRResponse`

### Response shape
Every OCR endpoint should return structured JSON first, not raw text files by default:
- job id
- selected mode
- selected engine
- detected document kind
- per-page confidence
- normalized text
- raw text
- output artifacts (txt/json/pdf/markdown)
- timings
- fallback chain used

This lets the frontend grow later without breaking contracts.

---

## 2) `src/ocr/engines/base.py`
Shared OCR engine contract.

### Add abstract interface:
- `supports(file_type, options) -> bool`
- `ocr_image(image_path, lang_config) -> EngineResult`
- `ocr_pdf(pdf_path, lang_config) -> EngineResult`
- `name` property

This prevents route handlers from knowing engine details.

---

## 3) `src/ocr/engines/paddle_engine.py`
Primary Arabic OCR engine.

### Responsibilities
- initialize PaddleOCR lazily
- support Arabic + English mixed recognition
- OCR rasterized PDF pages and standalone images
- return text lines, boxes, confidence scores, and page aggregates

### Notes for this repo
- use PaddleOCR for recognition quality
- do **not** make `backend/main.py` talk to Paddle directly
- load model path/config through environment variables so Docker/Railway can choose lighter or heavier variants

### Environment variables to support
- `OCR_PRIMARY_ENGINE=paddle`
- `PADDLE_DEVICE=cpu|gpu`
- `PADDLE_LANG=ar`
- `PADDLE_DET_MODEL_DIR`
- `PADDLE_REC_MODEL_DIR`
- `PADDLE_CLS_MODEL_DIR`

---

## 4) `src/ocr/engines/tesseract_engine.py`
Fallback engine and searchable PDF sidecar helper.

### Responsibilities
- keep the current Tesseract/OCRmyPDF path available
- run when Paddle is unavailable or confidence is below threshold
- serve searchable PDF generation pipeline when text layer embedding is required

### Important product stance
Tesseract stays in the repo because it is useful operationally, but it is no longer the default hero path.

---

## 5) `src/ocr/engines/pdf_text_engine.py`
Native text extraction path for born-digital PDFs.

### Responsibilities
- extract text without OCR using `pdfplumber` first
- inspect whether the PDF already contains a usable text layer
- return page text, character counts, and extraction quality heuristics

### Why this matters here
This repo currently OCRs everything like it’s 2017. That wastes time and hurts quality on real digital PDFs.

---

## 6) `src/ocr/pdf/classifier.py`
Document router / classifier.

### Responsibilities
- determine whether input is:
  - born-digital PDF
  - scanned PDF
  - mixed PDF
  - image/photo
- compute routing hints:
  - pages with embedded text
  - page image density
  - likely camera capture / perspective distortion
  - low-quality scan heuristics

### Initial heuristics
Start simple and deterministic:
- if `pdfplumber` extracts meaningful text on >70% of pages → `digital_pdf`
- if no usable text layer and pages render as image-heavy → `scanned_pdf`
- if mixed page outcomes → `mixed_pdf`
- if uploaded MIME is image/* → `image`

Do not block V2 on ML classification. Heuristics are enough.

---

## 7) `src/ocr/preprocess/image_quality.py`
Quality assessment used before expensive preprocessing.

### Responsibilities
- blur score
- skew estimate
- contrast score
- noise estimate
- resolution / DPI estimate
- edge crop / border detection

### Output
A small scorecard used by the router:
- `needs_deskew`
- `needs_thresholding`
- `needs_denoise`
- `needs_perspective_fix`
- `is_low_quality`

---

## 8) `src/ocr/preprocess/opencv_pipeline.py`
Image preprocessing for scans and camera photos.

### Responsibilities
- grayscale normalization
- deskew
- denoise
- adaptive thresholding
- border cleanup
- optional perspective correction for camera images

### Guardrail
Only apply transforms when heuristics say they are needed. Blind enhancement wrecks text surprisingly fast.

---

## 9) `src/ocr/preprocess/page_rasterizer.py`
Page rendering utility for PDFs.

### Responsibilities
- rasterize PDF pages at mode-specific DPI
- output temp images for Paddle pipeline
- expose page/image maps for mixed-mode documents

### Defaults
- fast path: 200 DPI
- deep path: 300 DPI
- camera/photo retry path: configurable

---

## 10) `src/ocr/confidence.py`
Confidence aggregation and fallback trigger logic.

### Responsibilities
- compute per-page and document confidence
- flag low-confidence pages
- trigger retry with preprocessing or fallback engine

### Initial thresholds
- `>= 0.88` accept page result
- `0.70 - 0.87` retry with preprocessing
- `< 0.70` escalate to fallback or deep mode

Thresholds should be benchmark-tuned, not guessed forever.

---

## 11) `src/ocr/normalizer.py`
Arabic cleanup layer.

### Responsibilities
- preserve raw OCR text
- produce normalized Arabic text for search/export
- normalize Alef variants
- normalize Ya / Alif Maqsura as configured
- optional diacritic stripping
- whitespace cleanup and line repair

### Output strategy
Return both:
- `raw_text`
- `normalized_text`

Never destroy the original OCR output.

---

## 12) `src/ocr/result_builder.py`
Artifact packaging.

### Responsibilities
- build `.txt`, `.md`, `.json` outputs
- unify page metadata and timing data
- optionally zip multi-artifact outputs

This keeps route handlers thin and consistent.

---

## 13) `src/ocr/pipelines/fast_pipeline.py`
Primary V2 path.

### Routing
- digital PDF → `pdf_text_engine`
- scanned PDF/image → light preprocessing + `paddle_engine`
- mixed PDF → page-level split between text extraction and OCR

### Target
Best speed/cost default for most users.

---

## 14) `src/ocr/pipelines/deep_pipeline.py`
Higher-accuracy route for ugly scans.

### Responsibilities
- stronger preprocessing
- higher DPI rasterization
- confidence-based retries
- fallback to Tesseract where Paddle fails badly

### Constraint
No PP-Structure or heavy restoration yet in V2 core. Keep this shippable.

---

## 15) `src/ocr/pipelines/camera_pipeline.py`
Photo-specific OCR route.

### Responsibilities
- detect perspective distortion
- crop document area if possible
- stronger denoise + deskew + thresholding
- run Paddle after camera-specific cleanup

This mode is product-facing and should map to the roadmap’s “Camera OCR”.

---

## 16) `src/ocr/pdf/searchable_pdf.py`
Searchable PDF assembly.

### Responsibilities
- take OCR output and generate searchable PDF artifact
- use OCRmyPDF/Tesseract path where operationally simplest
- preserve original page visuals while embedding searchable text layer

### Repo decision
For V2, searchable PDF generation can remain operationally tied to OCRmyPDF even if recognition is Paddle-first elsewhere.

That is pragmatic, not ideological.

---

## 17) `src/ocr/pipelines/searchable_pdf_pipeline.py`
End-to-end searchable PDF route.

### Responsibilities
- classify document
- decide whether OCR is needed
- produce searchable PDF
- return artifact metadata plus extracted text summary

---

## 18) `src/ocr/service.py`
Main orchestration service used by FastAPI.

### Responsibilities
- accept uploaded file + OCR mode
- call classifier
- dispatch pipeline
- build response
- handle temp directories and cleanup

### Public interface
Add one orchestration entry point:
- `process_document(file_path: str, filename: str, mode: OCRMode, options: OCRRequestOptions) -> OCRResponse`

---

## 19) `src/benchmarks/dataset_manifest.py`
Benchmark manifest definitions.

### Responsibilities
- define dataset schema
- support labels such as `clean_print`, `scan_low_quality`, `camera_photo`, `mixed_pdf`
- store ground-truth file paths and expected outputs

---

## 20) `src/benchmarks/evaluator.py`
Evaluation metrics.

### Responsibilities
- CER
- WER
- latency
- page success rate
- confidence calibration summary
- searchable PDF generation success

---

## 21) `src/benchmarks/runners/run_ocr_benchmark.py`
CLI benchmark runner.

### Responsibilities
- run fast/deep/camera/searchable modes against manifest
- output JSON + Markdown summary into `benchmark_results/`

---

## API endpoints to add

## Keep existing endpoint temporarily
- `POST /api/ocr`
  - mark as legacy in docs
  - internally route to `mode=fast` after the new service lands

## Add new V2 endpoints

### 1. `POST /api/ocr/fast`
Default OCR route.

**Use for:** scanned PDFs, mixed PDFs, images, most traffic.

**Returns:** JSON response with text + artifact references.

### 2. `POST /api/ocr/deep`
Higher-accuracy OCR route.

**Use for:** poor scans, denser docs, low-confidence retries.

### 3. `POST /api/ocr/camera`
Photo-specific OCR route.

**Use for:** mobile captures, perspective distortion, phone images.

### 4. `POST /api/ocr/searchable-pdf`
Generate searchable PDF output.

**Returns:** file artifact plus JSON metadata.

### 5. `POST /api/ocr/extract-text`
Digital-first text extraction route.

**Use for:** born-digital PDFs and mixed PDFs where OCR may be unnecessary.

### 6. `GET /api/ocr/capabilities`
Health/config inspection for frontend.

**Returns:**
- primary engine
- fallback engine
- whether Paddle is available
- whether OCRmyPDF/Tesseract/Ghostscript are available
- supported modes
- hosting mode

---

## Endpoint request contract

Use multipart upload consistently:
- `file`
- `output_formats` (`txt,json,md,pdf`)
- `normalize_arabic` (bool)
- `strip_diacritics` (bool)
- `force_ocr` (bool)
- `lang_hint` (`ar`, `ar+en`)
- `return_artifacts_inline` (bool, default false)

### Deep/camera-only extras
- `deskew` (bool)
- `denoise` (bool)
- `thresholding` (bool)
- `dpi` (int)

---

## FastAPI refactor plan in `backend/main.py`

`backend/main.py` is already overloaded. V2 should stop adding giant inline handlers.

## Refactor target
Create route modules:

```text
backend/
  api/
    __init__.py
    ocr_routes.py
    pdf_routes.py
```

### Plan
1. move current non-OCR endpoints into `pdf_routes.py`
2. implement new OCR endpoints in `ocr_routes.py`
3. keep `backend/main.py` as app bootstrap + router registration only

### Why
This repo will otherwise become a maintenance hostage by V3.

---

## Model / service split

## Service boundaries

### Product-facing service layer
- `src/ocr/service.py`
- `src/ocr/pipelines/*`
- `src/ocr/router.py` if you want a thin dispatch helper

### Model / engine layer
- `src/ocr/engines/paddle_engine.py`
- `src/ocr/engines/tesseract_engine.py`
- `src/ocr/engines/pdf_text_engine.py`

### Utility / infrastructure layer
- `src/ocr/preprocess/*`
- `src/ocr/pdf/*`
- `src/ocr/result_builder.py`
- `src/ocr/confidence.py`
- `src/ocr/normalizer.py`

## Rule
Route handlers should call the service layer.
The service layer should choose pipelines.
Pipelines should choose engines/utilities.
No endpoint should import OpenCV/Paddle/Tesseract logic directly.

---

## Hosting modes

The roadmap needs hosting guidance that matches this repo’s deployment reality.

## 1) Free mode
Best for GitHub users spinning this up cheaply.

### Platforms
- Railway free/basic
- Render free/basic
- self-hosted small VPS with CPU only

### Stack enabled
- digital PDF extraction (`pdfplumber`)
- PaddleOCR CPU fast mode
- lightweight OpenCV preprocessing
- searchable PDF generation only if system deps are present

### Constraints
- CPU only
- lower throughput
- deep mode may be slow
- camera mode works, but not blazing fast

### Recommended defaults
- `PADDLE_DEVICE=cpu`
- limit uploads/pages for public instances
- disable aggressive deep retries by default

---

## 2) Basic mode
Best default paid deployment.

### Platforms
- Railway paid
- Render paid instance
- Hetzner / DigitalOcean / generic VPS with 4–8 vCPU and enough RAM

### Stack enabled
- everything in Free mode
- deeper preprocessing enabled
- higher page count limits
- searchable PDF fully supported with OCRmyPDF + Ghostscript installed

### Recommended defaults
- fast mode is public default
- deep mode available for signed-in/admin or rate-limited users
- artifact retention short-lived only

---

## 3) Heavy mode
For the future Arabic document intelligence tier.

### Platforms
- GPU VM / dedicated box
- Docker deployment with optional CUDA image variant

### Stack enabled
- V2 fully unlocked
- staging ground for V3 features:
  - PP-Structure
  - document field extraction
  - restoration / super-resolution experiments
  - handwriting benchmarks

### Current repo stance
Do not require Heavy mode to ship V2. Design for it, but do not block on it.

---

## Dependency plan

## Add to Python dependencies
For V2 implementation branch, plan to add:
- `paddleocr`
- `opencv-python-headless`
- `pdfplumber`
- `rapidfuzz` (optional text alignment/helpers)
- `jiwer` (WER/CER evaluation) or custom metric util

### Keep
- `ocrmypdf`
- `pypdf` / `pikepdf`
- `PyMuPDF`

### Packaging note
Separate runtime profiles if needed:
- `requirements.txt` or `pyproject` base
- `requirements-ocr-heavy.txt` for larger deployments

Right now dependency management is split awkwardly between root and backend files. V2 should unify or document the split clearly.

---

## Benchmark plan

## Benchmark folder layout

```text
benchmarks/
  manifest.json
  clean_print/
  low_quality_scans/
  camera_photos/
  mixed_pdfs/
  searchable_pdf_checks/
  ground_truth/
benchmark_results/
```

## Dataset target for V2 gate
Start smaller than the roadmap’s full long-term benchmark, but real enough to matter.

### Minimum V2 benchmark set
- 30 clean printed Arabic pages
- 30 medium/low-quality scanned Arabic pages
- 20 Arabic camera photos
- 20 born-digital Arabic PDFs
- 10 mixed PDFs (text layer on some pages, scanned others)

Total initial benchmark: **110 documents/pagesets** minimum.

## Metrics to track
- CER by cohort
- WER by cohort
- extraction success rate
- searchable PDF success rate
- median latency per page
- fallback rate
- confidence vs actual accuracy correlation

## Baselines to compare
- current `src/ocr_service.py` Tesseract path
- new fast pipeline
- new deep pipeline
- camera pipeline on photo cohort

## Acceptance thresholds for V2 merge
- fast mode beats current Tesseract baseline on Arabic CER for clean and medium-quality scans
- extract-text route avoids unnecessary OCR on born-digital PDFs in >90% of benchmark cases
- searchable PDF generation succeeds on >95% of benchmark fixture set
- median fast-mode latency remains acceptable on CPU deployment

---

## Milestone checklist

## Milestone 0 — architecture prep
- [ ] create `src/ocr/` package skeleton
- [ ] create `backend/api/ocr_routes.py`
- [ ] move legacy OCR logic behind compatibility wrapper
- [ ] define OCR schemas and JSON response contract

## Milestone 1 — fast path
- [ ] add `pdf_text_engine.py` using `pdfplumber`
- [ ] add `classifier.py` for digital vs scanned routing
- [ ] add `paddle_engine.py`
- [ ] implement `fast_pipeline.py`
- [ ] add `POST /api/ocr/fast`
- [ ] add `POST /api/ocr/extract-text`

## Milestone 2 — preprocessing + fallback
- [ ] add `image_quality.py`
- [ ] add `opencv_pipeline.py`
- [ ] add `confidence.py`
- [ ] add `deep_pipeline.py`
- [ ] add `POST /api/ocr/deep`
- [ ] keep Tesseract fallback behind config flag

## Milestone 3 — camera mode
- [ ] add `camera_pipeline.py`
- [ ] add perspective correction / crop heuristics
- [ ] add `POST /api/ocr/camera`
- [ ] expose camera mode in frontend selector

## Milestone 4 — searchable PDF
- [ ] add `searchable_pdf.py`
- [ ] add `searchable_pdf_pipeline.py`
- [ ] add `POST /api/ocr/searchable-pdf`
- [ ] decide file vs JSON artifact response shape

## Milestone 5 — Arabic cleanup + artifacts
- [ ] add `normalizer.py`
- [ ] add `result_builder.py`
- [ ] support txt/md/json outputs
- [ ] preserve raw and normalized text in every response

## Milestone 6 — benchmark gate
- [ ] add benchmark manifest and runner
- [ ] collect baseline outputs from current OCR stack
- [ ] compare fast/deep/camera against baseline
- [ ] publish `benchmark_results/v2-baseline.md`

## Milestone 7 — legacy cleanup
- [ ] make `POST /api/ocr` call fast pipeline internally
- [ ] update README and deployment docs
- [ ] mark legacy Tesseract-first behavior deprecated

---

## Suggested implementation sequence

1. **Refactor routes first**
   - because adding more OCR logic to `backend/main.py` is asking for pain
2. **Ship digital-PDF extraction + fast pipeline**
   - fastest visible product improvement
3. **Add confidence/fallback + deep mode**
4. **Add camera mode**
5. **Add searchable PDF endpoint**
6. **Run benchmarks before calling V2 “done”**

That order gets real user value early without getting trapped in heavyweight experiments.

---

## Non-goals for V2

Do not cram these into V2 core:
- PP-StructureV3 field extraction
- invoices/receipts/forms/ID schemas
- handwriting OCR production promises
- Real-ESRGAN or restoration-first workflows
- GPU-only assumptions

Those belong to V3/V4. Keep V2 lean, measurable, and shippable.

---

## Definition of done for V2

V2 is done when this repo can honestly claim:
- Arabic OCR is **Paddle-first**, not Tesseract-first
- born-digital PDFs skip unnecessary OCR
- camera images have a dedicated OCR route
- searchable PDF generation is exposed as a first-class endpoint
- OCR responses are structured and confidence-aware
- a benchmark report proves quality gain over the current baseline

That is a real product step-up, not just another endpoint pile.
