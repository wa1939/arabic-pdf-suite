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

# Exact stopwords from original ArabicWordCloudGenerator/app.py
ORIGINAL_STOPWORDS = [
    "و", "في", "على", "من", "او", "أو", "بشكل", "طلب", "مع", "خلال", "بين", "الذي", "عدم", "ذلك",
    "و ", "التأكيد", "القطاع", "جدا", "المكاتب", "لكن", "ما", "الى", "بالنسبة", "شي", "ولكن",
    "العمل", "المكان", "مكان", "لا", "يوجد", "المكتب", "يؤدي",
]

# Extended defaults
DEFAULT_STOPWORDS = list(ORIGINAL_STOPWORDS) + [
    "عن", "أن", "إن", "كان", "كانت", "هذا", "هذه", "هناك", "تم", "كما", "كل", "قد", "أي", "إلى",
    "هو", "هي", "هم", "هن", "نحن", "أنا", "أنت", "أنتم", "أنتما", "أنتن", "التي", "الذين",
]

ARABIC_RE = re.compile(r"[\u0600-\u06FF]+")

# Available Arabic fonts (using absolute paths)
ARABIC_FONTS = {
    "DIN Next Arabic": str(_PROJECT_ROOT / "assets" / "DIN Next LT Arabic Regular.ttf"),
    "Arial": str(_PROJECT_ROOT / "assets" / "arial.ttf"),
    "Noto Naskh Arabic": "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
    "Noto Sans Arabic": "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "Amiri": "/usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Regular.ttf",
}

# Color schemes
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
    """Normalize text for processing."""
    text = str(text or "").replace("\ufeff", " ")
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_stopwords(text: str, stopwords: Iterable[str]) -> str:
    """Remove stopwords from text - EXACT original approach."""
    result = f" {text} "
    for word in stopwords:
        result = result.replace(f" {word} ", " ")
    return normalize_text(result)


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper RTL display - EXACT original approach."""
    if not text or not text.strip():
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


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
    """Extract Arabic words for term counting."""
    stop = set(stopwords or DEFAULT_STOPWORDS)
    cleaned = remove_stopwords(text, stop)
    words = ARABIC_RE.findall(cleaned)
    return [w for w in words if len(w) > 1]


def top_terms(text: str, limit: int = 20, stopwords: Iterable[str] | None = None) -> list[tuple[str, int]]:
    """Get top terms for display."""
    counts = Counter(tokenize_arabic(text, stopwords=stopwords))
    return counts.most_common(limit)


def get_available_fonts() -> dict[str, str]:
    """Return available fonts that exist on the system."""
    available = {}
    for name, path in ARABIC_FONTS.items():
        if Path(path).exists():
            available[name] = path
    return available


def pick_font(font_name: str | None = None) -> str | None:
    """Pick a font, preferring the specified one."""
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
    """Create a color function - EXACT original approach."""
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
    """
    Generate a word cloud using the EXACT original ArabicWordCloudGenerator approach.
    
    This matches the original app.py:
    1. Remove stopwords from raw text
    2. Reshape the ENTIRE text with arabic_reshaper
    3. Apply bidi.get_display
    4. Pass to WordCloud.generate()
    """
    # Build stopwords list
    stopwords = list(DEFAULT_STOPWORDS)
    if extra_stopwords:
        stopwords.extend(extra_stopwords)
    if exclude_stopwords:
        exclude_set = set(exclude_stopwords)
        stopwords = [w for w in stopwords if w not in exclude_set]
    
    # Remove stopwords from text (original approach)
    cleaned = remove_stopwords(text, stopwords)
    
    # Reshape the ENTIRE text (original approach - not word by word)
    reshaped_text = arabic_reshaper.reshape(cleaned)
    bidi_text = get_display(reshaped_text)
    
    # Get colors
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["ELM Brand"])
    color_func = make_color_func(colors)
    
    # Get font
    font_path = pick_font(font_name)
    if not font_path:
        raise RuntimeError("No Arabic-capable font found")
    
    # Generate word cloud - EXACT original parameters
    if transparent or background_color is None:
        wc = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            background_color=None,
            mode='RGBA',
            color_func=color_func,
            max_words=max_words,
            prefer_horizontal=prefer_horizontal,
            collocations=False,
        ).generate(bidi_text)
    else:
        wc = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            background_color=background_color,
            color_func=color_func,
            max_words=max_words,
            prefer_horizontal=prefer_horizontal,
            collocations=False,
        ).generate(bidi_text)
    
    return wc.to_image()
