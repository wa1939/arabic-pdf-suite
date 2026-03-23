from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter


@dataclass
class PDFBytesResult:
    data: bytes
    filename: str


def _read(uploaded_file) -> PdfReader:
    uploaded_file.seek(0)
    return PdfReader(uploaded_file)


def merge_pdfs(files: list) -> PDFBytesResult:
    writer = PdfWriter()
    for file in files:
        reader = _read(file)
        for page in reader.pages:
            writer.add_page(page)
    buffer = BytesIO()
    writer.write(buffer)
    return PDFBytesResult(buffer.getvalue(), "merged.pdf")


def split_pdf(file, page_ranges: str) -> list[PDFBytesResult]:
    reader = _read(file)
    results: list[PDFBytesResult] = []
    for idx, chunk in enumerate(page_ranges.split(","), start=1):
        chunk = chunk.strip()
        if not chunk:
            continue
        writer = PdfWriter()
        if "-" in chunk:
            start_s, end_s = chunk.split("-", 1)
            start, end = int(start_s), int(end_s)
            for page_num in range(start - 1, min(end, len(reader.pages))):
                writer.add_page(reader.pages[page_num])
        else:
            page_num = int(chunk) - 1
            writer.add_page(reader.pages[page_num])
        buf = BytesIO()
        writer.write(buf)
        results.append(PDFBytesResult(buf.getvalue(), f"split_{idx}.pdf"))
    return results


def delete_pages(file, pages_to_delete: Iterable[int]) -> PDFBytesResult:
    reader = _read(file)
    writer = PdfWriter()
    drop = {p - 1 for p in pages_to_delete}
    for i, page in enumerate(reader.pages):
        if i not in drop:
            writer.add_page(page)
    buf = BytesIO()
    writer.write(buf)
    return PDFBytesResult(buf.getvalue(), "pages_deleted.pdf")


def rotate_pdf(file, pages: Iterable[int], angle: int) -> PDFBytesResult:
    reader = _read(file)
    writer = PdfWriter()
    targets = set(p - 1 for p in pages)
    for i, page in enumerate(reader.pages):
        if i in targets:
            page.rotate(angle)
        writer.add_page(page)
    buf = BytesIO()
    writer.write(buf)
    return PDFBytesResult(buf.getvalue(), "rotated.pdf")


def reorder_pdf(file, order: list[int]) -> PDFBytesResult:
    reader = _read(file)
    writer = PdfWriter()
    for page_number in order:
        writer.add_page(reader.pages[page_number - 1])
    buf = BytesIO()
    writer.write(buf)
    return PDFBytesResult(buf.getvalue(), "reordered.pdf")


def page_count(file) -> int:
    return len(_read(file).pages)
