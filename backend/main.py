"""
Arabic PDF Suite - FastAPI Backend
Production-grade PDF processing API
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import tempfile
import uuid
import os
import sys
from typing import List, Optional
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

app = FastAPI(
    title="Arabic PDF Suite API",
    description="Production-grade PDF processing with Arabic OCR support",
    version="2.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp directory for file processing
TEMP_DIR = Path(tempfile.gettempdir()) / "arabic-pdf-suite"
TEMP_DIR.mkdir(exist_ok=True)

# Import PDF tools
try:
    from pdf_tools import (
        merge_pdfs, split_pdf, compress_pdf,
        pdf_to_images, images_to_pdf,
        word_to_pdf, pdf_to_word,
        add_watermark, rotate_pages,
        delete_pages, reorder_pages,
        pdf_to_excel, excel_to_pdf
    )
    from ocr_service import extract_text_from_file
    PDF_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PDF tools import failed: {e}")
    PDF_TOOLS_AVAILABLE = False


def cleanup_file(filepath: Path, delay: int = 60):
    """Delete file after delay"""
    async def _cleanup():
        await asyncio.sleep(delay)
        try:
            if filepath.exists():
                filepath.unlink()
        except:
            pass
    asyncio.create_task(_cleanup())


@app.get("/")
async def root():
    return {
        "name": "Arabic PDF Suite API",
        "version": "2.0.0",
        "status": "running",
        "tools_available": PDF_TOOLS_AVAILABLE
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/merge")
async def api_merge_pdfs(files: List[UploadFile] = File(...)):
    """Merge multiple PDFs into one"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        # Save uploaded files
        pdf_paths = []
        for i, file in enumerate(files):
            file_path = job_dir / f"input_{i}.pdf"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            pdf_paths.append(str(file_path))
        
        # Merge
        output_path = job_dir / "merged.pdf"
        merge_pdfs(pdf_paths, str(output_path))
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="merged.pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/split")
async def api_split_pdf(
    file: UploadFile = File(...),
    mode: str = Form("all"),  # "all", "range", "extract"
    start: Optional[int] = Form(None),
    end: Optional[int] = Form(None),
    pages: Optional[str] = Form(None)  # e.g., "1,3,5-7"
):
    """Split PDF into multiple files or extract pages"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        # Save uploaded file
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_dir = job_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Split
        if mode == "all":
            result = split_pdf(str(input_path), str(output_dir))
        else:
            page_list = parse_page_range(pages) if pages else list(range(start or 1, (end or 1) + 1))
            result = split_pdf(str(input_path), str(output_dir), pages=page_list)
        
        # Return first file or zip
        output_files = list(output_dir.glob("*.pdf"))
        if len(output_files) == 1:
            cleanup_file(output_files[0], delay=120)
            return FileResponse(
                path=str(output_files[0]),
                media_type="application/pdf",
                filename=output_files[0].name
            )
        else:
            # Create zip
            import zipfile
            zip_path = job_dir / "split_files.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                for pdf_file in output_files:
                    zf.write(pdf_file, pdf_file.name)
            
            cleanup_file(zip_path, delay=120)
            return FileResponse(
                path=str(zip_path),
                media_type="application/zip",
                filename="split_files.zip"
            )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compress")
async def api_compress_pdf(
    file: UploadFile = File(...),
    quality: str = Form("medium")  # "low", "medium", "high"
):
    """Compress PDF file size"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "compressed.pdf"
        compress_pdf(str(input_path), str(output_path), quality=quality)
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="compressed.pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pdf-to-images")
async def api_pdf_to_images(
    file: UploadFile = File(...),
    format: str = Form("png"),  # "png", "jpg"
    dpi: int = Form(150)
):
    """Convert PDF pages to images"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_dir = job_dir / "images"
        output_dir.mkdir(exist_ok=True)
        
        pdf_to_images(str(input_path), str(output_dir), format=format, dpi=dpi)
        
        # Create zip of images
        import zipfile
        zip_path = job_dir / "images.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for img_file in output_dir.glob("*"):
                zf.write(img_file, img_file.name)
        
        cleanup_file(zip_path, delay=120)
        
        return FileResponse(
            path=str(zip_path),
            media_type="application/zip",
            filename="images.zip"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/images-to-pdf")
async def api_images_to_pdf(files: List[UploadFile] = File(...)):
    """Convert images to PDF"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        image_paths = []
        for i, file in enumerate(files):
            ext = Path(file.filename).suffix or ".png"
            file_path = job_dir / f"image_{i}{ext}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            image_paths.append(str(file_path))
        
        output_path = job_dir / "output.pdf"
        images_to_pdf(image_paths, str(output_path))
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="images.pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/word-to-pdf")
async def api_word_to_pdf(file: UploadFile = File(...)):
    """Convert Word document to PDF"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        ext = Path(file.filename).suffix
        input_path = job_dir / f"input{ext}"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "output.pdf"
        word_to_pdf(str(input_path), str(output_path))
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename=Path(file.filename).stem + ".pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pdf-to-word")
async def api_pdf_to_word(file: UploadFile = File(...)):
    """Convert PDF to Word document"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "output.docx"
        pdf_to_word(str(input_path), str(output_path))
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=Path(file.filename).stem + ".docx"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/watermark")
async def api_add_watermark(
    file: UploadFile = File(...),
    text: str = Form(...),
    opacity: float = Form(0.3),
    position: str = Form("center")  # "center", "diagonal"
):
    """Add watermark to PDF"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "watermarked.pdf"
        add_watermark(str(input_path), str(output_path), text, opacity=opacity, position=position)
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="watermarked.pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rotate")
async def api_rotate_pages(
    file: UploadFile = File(...),
    degrees: int = Form(90),
    pages: Optional[str] = Form(None)  # e.g., "1,3,5-7" or None for all
):
    """Rotate PDF pages"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "rotated.pdf"
        page_list = parse_page_range(pages) if pages else None
        rotate_pages(str(input_path), str(output_path), degrees=degrees, pages=page_list)
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="rotated.pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/delete-pages")
async def api_delete_pages(
    file: UploadFile = File(...),
    pages: str = Form(...)  # e.g., "1,3,5-7"
):
    """Delete pages from PDF"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "output.pdf"
        page_list = parse_page_range(pages)
        delete_pages(str(input_path), str(output_path), pages=page_list)
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="modified.pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reorder")
async def api_reorder_pages(
    file: UploadFile = File(...),
    order: str = Form(...)  # e.g., "3,1,2,4"
):
    """Reorder PDF pages"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "reordered.pdf"
        page_order = [int(x.strip()) for x in order.split(",")]
        reorder_pages(str(input_path), str(output_path), order=page_order)
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="reordered.pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ocr")
async def api_ocr(
    file: UploadFile = File(...),
    language: str = Form("ara+eng")  # Arabic + English by default
):
    """Extract text from PDF using OCR"""
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        ext = Path(file.filename).suffix
        input_path = job_dir / f"input{ext}"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Use OCR service
        text = extract_text_from_file(str(input_path), languages=language.split("+"))
        
        # Return as text file
        output_path = job_dir / "extracted_text.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="text/plain",
            filename="extracted_text.txt"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wordcloud")
async def api_wordcloud(
    file: UploadFile = File(...),
    width: int = Form(800),
    height: int = Form(400)
):
    """Generate Arabic word cloud from document"""
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        ext = Path(file.filename).suffix
        input_path = job_dir / f"input{ext}"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Extract text first
        text = extract_text_from_file(str(input_path), languages=["ara", "eng"])
        
        # Generate word cloud
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        
        # Use Arabic-compatible font
        font_path = find_arabic_font()
        
        wc = WordCloud(
            width=width,
            height=height,
            font_path=font_path,
            background_color='white',
            colormap='viridis'
        ).generate(text)
        
        output_path = job_dir / "wordcloud.png"
        wc.to_file(str(output_path))
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="image/png",
            filename="wordcloud.png"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pdf-to-excel")
async def api_pdf_to_excel(file: UploadFile = File(...)):
    """Convert PDF to Excel"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        input_path = job_dir / "input.pdf"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "output.xlsx"
        pdf_to_excel(str(input_path), str(output_path))
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=Path(file.filename).stem + ".xlsx"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/excel-to-pdf")
async def api_excel_to_pdf(file: UploadFile = File(...)):
    """Convert Excel to PDF"""
    if not PDF_TOOLS_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF tools not available")
    
    job_id = str(uuid.uuid4())
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        ext = Path(file.filename).suffix
        input_path = job_dir / f"input{ext}"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        output_path = job_dir / "output.pdf"
        excel_to_pdf(str(input_path), str(output_path))
        
        cleanup_file(output_path, delay=120)
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename=Path(file.filename).stem + ".pdf"
        )
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


def parse_page_range(page_str: str) -> List[int]:
    """Parse page range string like '1,3,5-7' into list of page numbers"""
    pages = []
    for part in page_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))
    return pages


def find_arabic_font():
    """Find an Arabic-compatible font on the system"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/System/Library/Fonts/GeezaPro.ttc",  # macOS
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows
    ]
    for path in font_paths:
        if Path(path).exists():
            return path
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
