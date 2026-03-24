from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile

import pikepdf
from pypdf import PdfReader, PdfWriter


@dataclass
class PDFBytesResult:
    data: bytes
    filename: str


def _read(uploaded_file) -> PdfReader:
    uploaded_file.seek(0)
    return PdfReader(uploaded_file)


def _read_bytes(uploaded_file) -> bytes:
    uploaded_file.seek(0)
    return uploaded_file.read()


def parse_page_list(raw: str) -> list[int]:
    pages: list[int] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_s, end_s = chunk.split("-", 1)
            start, end = int(start_s), int(end_s)
            if start <= 0 or end <= 0 or end < start:
                raise ValueError(f"Invalid page range: {chunk}")
            pages.extend(range(start, end + 1))
        else:
            value = int(chunk)
            if value <= 0:
                raise ValueError(f"Invalid page number: {chunk}")
            pages.append(value)
    return pages


def parse_page_ranges(raw: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_s, end_s = chunk.split("-", 1)
            start, end = int(start_s), int(end_s)
        else:
            start = end = int(chunk)
        if start <= 0 or end <= 0 or end < start:
            raise ValueError(f"Invalid page range: {chunk}")
        ranges.append((start, end))
    return ranges


def merge_pdfs(files: list) -> PDFBytesResult:
    writer = PdfWriter()
    for file in files:
        reader = _read(file)
        for page in reader.pages:
            writer.add_page(page)
    buffer = BytesIO()
    writer.write(buffer)
    return PDFBytesResult(buffer.getvalue(), "merged.pdf")


def split_pdf(file, page_ranges: str) -> bytes:
    reader = _read(file)
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zf:
        for idx, (start, end) in enumerate(parse_page_ranges(page_ranges), start=1):
            writer = PdfWriter()
            for page_num in range(start - 1, min(end, len(reader.pages))):
                writer.add_page(reader.pages[page_num])
            buf = BytesIO()
            writer.write(buf)
            zf.writestr(f"split_{idx}_{start}-{end}.pdf", buf.getvalue())
    return zip_buffer.getvalue()


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
    targets = {p - 1 for p in pages}
    for i, page in enumerate(reader.pages):
        if i in targets:
            page.rotate(angle)
        writer.add_page(page)
    buf = BytesIO()
    writer.write(buf)
    return PDFBytesResult(buf.getvalue(), "rotated.pdf")


def reorder_pdf(file, order: list[int]) -> PDFBytesResult:
    reader = _read(file)
    total = len(reader.pages)
    if sorted(order) != list(range(1, total + 1)):
        raise ValueError("Page order must include every page exactly once.")
    writer = PdfWriter()
    for page_number in order:
        writer.add_page(reader.pages[page_number - 1])
    buf = BytesIO()
    writer.write(buf)
    return PDFBytesResult(buf.getvalue(), "reordered.pdf")


def compress_pdf(file) -> PDFBytesResult:
    source = _read_bytes(file)
    input_buffer = BytesIO(source)
    output_buffer = BytesIO()

    with pikepdf.open(input_buffer) as pdf:
        for page in pdf.pages:
            try:
                page_contents = page.obj.get("/Contents")
                if page_contents is not None:
                    page_contents = page_contents.read_bytes()
            except Exception:
                pass

        pdf.remove_unreferenced_resources()
        pdf.save(
            output_buffer,
            compress_streams=True,
            recompress_flate=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            linearize=True,
        )

    result = output_buffer.getvalue()
    if len(result) >= len(source):
        result = source
    return PDFBytesResult(result, "compressed.pdf")


def page_count(file) -> int:
    return len(_read(file).pages)
