from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import ocrmypdf


@dataclass
class OCRResult:
    pdf_path: Path
    txt_path: Path


def system_ready() -> tuple[bool, list[str]]:
    missing = []
    for cmd in ("tesseract", "gs"):
        if shutil.which(cmd) is None:
            missing.append(cmd)
    return (len(missing) == 0, missing)


def run_ocr(input_pdf: bytes, filename: str, language: str = "ara") -> OCRResult:
    ready, missing = system_ready()
    if not ready:
        raise RuntimeError(
            "Missing system packages: " + ", ".join(missing) + ". Install Tesseract + Ghostscript or use Docker."
        )

    safe_name = Path(filename).stem or "document"
    out_dir = Path(tempfile.mkdtemp(prefix="arabic-suite-"))
    input_path = out_dir / f"{safe_name}.pdf"
    output_pdf = out_dir / f"{safe_name}_ocr.pdf"
    output_txt = out_dir / f"{safe_name}_ocr.txt"
    input_path.write_bytes(input_pdf)

    try:
        ocrmypdf.ocr(
            str(input_path),
            str(output_pdf),
            language=language,
            rotate_pages=True,
            deskew=True,
            clean=True,
            remove_background=True,
            optimize=1,
            output_type="pdf",
            pdf_renderer="hocr",
            tesseract_oem=1,
            tesseract_pagesegmode=3,
            sidecar=str(output_txt),
            jobs=max(1, (os.cpu_count() or 2) - 1),
            force_ocr=False,
            redo_ocr=True,
            skip_text=False,
        )
    except Exception as exc:
        raise RuntimeError(f"OCR failed: {exc}") from exc

    if not output_txt.exists():
        output_txt.write_text("", encoding="utf-8")

    return OCRResult(pdf_path=output_pdf, txt_path=output_txt)


def vercel_friendly_note() -> str:
    return (
        "Vercel is fine for the text/word-cloud UI, but full OCR is not reliable there because it needs "
        "Tesseract + Ghostscript system binaries. For public deployment, use Docker, a VPS, Railway, Render, "
        "Fly.io, or self-host."
    )
