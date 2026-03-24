from __future__ import annotations

import random
import re
from collections import Counter
from io import BytesIO
from pathlib import Path
from typing import Iterable

import arabic_reshaper
import pandas as pd
from bidi.algorithm import get_display
from PIL import Image
from wordcloud import WordCloud

# Get the project root directory (where assets/ folder is)
_PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Exact base list from the original ArabicWordCloudGenerator/app.py
ORIGINAL_STOPWORDS = [
    "و", "في", "على", "من", "او", "أو", "بشكل", "طلب", "مع", "خلال", "بين", "الذي", "عدم", "ذلك",
    "و ", "التأكيد", "القطاع", "جدا", "المكاتب", "لكن", "ما", "الى", "بالنسبة", "شي", "ولكن",
    "العمل", "المكان", "مكان", "لا", "يوجد", "المكتب", "يؤدي",
]

# Extended defaults used by the suite, while keeping the original list intact.
DEFAULT_STOPWORDS = ORIGINAL_STOPWORDS + [
    "عن", "أن", "إن", "كان", "كانت", "هذا", "هذه", "هناك", "تم", "كما", "كل", "قد", "أي", "إلى",
    "هو", "هي", "هم", "هن", "نحن", "أنا", "أنت", "أنتم", "أنتما", "أنتن", "التي", "الذين", "اللتي",
    "اللتان", "اللواتي", "اللائي", "الذى", "الذيان",
]

ARABIC_RE = re.compile(r"[\u0600-\u06FF]+")
TOKEN_SPLIT_RE = re.compile(r"[^\u0600-\u06FF]+")


# Available Arabic fonts (using absolute paths)
ARABIC_FONTS = {
    "DIN Next Arabic": str(_PROJECT_ROOT / "assets" / "DIN Next LT Arabic Regular.ttf"),
    "Arial": str(_PROJECT_ROOT / "assets" / "arial.ttf"),
    "Noto Naskh Arabic": "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
    "Noto Sans Arabic": "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "Amiri": "/usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Regular.ttf",
}

# Color schemes (as hex colors)
COLOR_SCHEMES = {
    "ELM Brand": ["#808285", "#2A6EBB", "#952D98", "#44C8F5", "#722EA5", "#1E1656"],
    "Blue Ocean": ["#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8", "#03045E"],
    "Sunset": ["#FF6B6B", "#FEC89A", "#FFD93D", "#6BCB77", "#4D96FF"],
    "Forest": ["#2D6A4F", "#40916C", "#52B788", "#74C69D", "#95D5B2"],
    "Purple Dream": ["#7B2CBF", "#9D4EDD", "#C77DFF", "#E0AAFF", "#5A189A"],
    "Warm Earth": ["#BC6C25", "#DDA15E", "#FEFAE0", "#606C38", "#283618"],
    "Monochrome": ["#212529", "#495057", "#6C757D", "#ADB5BD", "#DEE2E6"],
    "Saudi Green": ["#006C35", "#008C45", "#004D25", "#00A84A", "#005A2B"],
    "Candy": ["#FF69B4", "#FF1493", "#DB7093", "#FFB6C1", "#FFC0CB"],
}


def normalize_text(text: str) -> str:
    text = str(text or "").replace("\ufeff", " ")
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _pad_text(text: str) -> str:
    text = normalize_text(text)
    return f" {text} " if text else ""


def remove_stopwords(text: str, stopwords: Iterable[str]) -> str:
    """Match the original app.py approach exactly: raw string replacement on padded text."""
    result = _pad_text(text)
    for word in stopwords:
        result = result.replace(f" {word} ", " ")
    return normalize_text(result)


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper RTL display using the original arabic_reshaper + bidi flow."""
    source = normalize_text(text)
    if not source:
        return ""
    reshaped_text = arabic_reshaper.reshape(source)
    return get_display(reshaped_text)


def extract_text_from_txt(file_bytes: bytes) -> str:
    return normalize_text(file_bytes.decode("utf-8", errors="ignore"))


def extract_text_from_excel(file_bytes: bytes, preferred_column: str | None = None) -> str:
    df = pd.read_excel(BytesIO(file_bytes))
    if df.empty:
        return ""

    if preferred_column and preferred_column in df.columns:
        series = df[preferred_column]
    else:
        object_cols = [c for c in df.columns if df[c].dtype == object]
        series = df[object_cols[0]] if object_cols else df.iloc[:, 0]

    return normalize_text(" ".join(series.fillna("").astype(str).tolist()))


def tokenize_arabic(text: str, stopwords: Iterable[str] | None = None) -> list[str]:
    stop = {normalize_text(w) for w in (stopwords or DEFAULT_STOPWORDS)}
    cleaned = remove_stopwords(text, stop)
    tokens = [tok for tok in TOKEN_SPLIT_RE.split(cleaned) if tok]
    return [tok for tok in tokens if len(tok) > 1 and ARABIC_RE.fullmatch(tok)]


def top_terms(text: str, limit: int = 20, stopwords: Iterable[str] | None = None) -> list[tuple[str, int]]:
    counts = Counter(tokenize_arabic(text, stopwords=stopwords))
    return counts.most_common(limit)


def get_available_fonts() -> dict[str, str]:
    available = {}
    for name, path in ARABIC_FONTS.items():
        if Path(path).exists():
            available[name] = path
    return available


def pick_font(font_name: str | None = None) -> str | None:
    if font_name and font_name in ARABIC_FONTS:
        path = Path(ARABIC_FONTS[font_name])
        if path.exists():
            return str(path)

    for name in ["DIN Next Arabic", "Arial", "Noto Naskh Arabic", "Noto Sans Arabic", "Amiri"]:
        path = Path(ARABIC_FONTS[name])
        if path.exists():
            return str(path)
    return None


def make_color_func(colors: list[str]):
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return random.choice(colors)

    return color_func


def make_wordcloud(
    text: str,
    width: int = 800,
    height: int = 800,
    font_name: str | None = None,
    color_scheme: str = "ELM Brand",
    background_color: str | None = None,
    max_words: int = 200,
    prefer_horizontal: float = 0.9,
    transparent: bool = True,
    extra_stopwords: list[str] | None = None,
    exclude_stopwords: list[str] | None = None,
) -> Image.Image:
    """Generate a word cloud using the original Arabic RTL rendering pipeline."""
    stopwords = list(DEFAULT_STOPWORDS)
    if extra_stopwords:
        stopwords.extend(normalize_text(w) for w in extra_stopwords if normalize_text(w))
    if exclude_stopwords:
        excluded = {normalize_text(w) for w in exclude_stopwords if normalize_text(w)}
        stopwords = [w for w in stopwords if normalize_text(w) not in excluded]

    source = remove_stopwords(text, stopwords)
    shaped = reshape_arabic(source) if source else reshape_arabic("لا توجد بيانات كافية")
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["ELM Brand"])
    font_path = pick_font(font_name)

    kwargs = dict(
        font_path=font_path,
        width=width,
        height=height,
        collocations=False,
        prefer_horizontal=prefer_horizontal,
        color_func=make_color_func(colors),
        max_words=max_words,
    )

    if transparent or background_color is None:
        kwargs.update(background_color=None, mode="RGBA")
    else:
        kwargs.update(background_color=background_color)

    return WordCloud(**kwargs).generate(shaped).to_image()
