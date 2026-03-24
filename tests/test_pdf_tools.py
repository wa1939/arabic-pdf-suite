from io import BytesIO
from zipfile import ZipFile

from pypdf import PdfReader
from reportlab.pdfgen import canvas

from src.pdf_tools import compress_pdf, merge_pdfs, parse_page_list, pdf_to_excel, pdf_to_word


class Upload:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data
        self._offset = 0

    def seek(self, pos: int, whence: int = 0):
        self._offset = pos

    def read(self, *args, **kwargs):
        return self._data

    def getvalue(self):
        return self._data


def make_pdf(label: str) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 700, label)
    c.showPage()
    c.save()
    return buf.getvalue()


def test_parse_page_list():
    assert parse_page_list('1-3,5') == [1, 2, 3, 5]


def test_merge_pdfs():
    a = Upload('a.pdf', make_pdf('A'))
    b = Upload('b.pdf', make_pdf('B'))
    result = merge_pdfs([a, b])
    assert len(PdfReader(BytesIO(result.data)).pages) == 2


def test_compress_pdf_roundtrip():
    file = Upload('sample.pdf', make_pdf('Hello'))
    result = compress_pdf(file)
    assert len(PdfReader(BytesIO(result.data)).pages) == 1


def test_pdf_to_excel_and_word():
    file = Upload('sample.pdf', make_pdf('Hello World'))
    xlsx = pdf_to_excel(file)
    assert xlsx.filename.endswith('.xlsx')
    word = pdf_to_word(file)
    assert word.filename.endswith(('.docx', '.txt'))
