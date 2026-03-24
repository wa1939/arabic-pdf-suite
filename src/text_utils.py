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

DEFAULT_STOPWORDS = {
    "و", "في", "على", "من", "او", "أو", "بشكل", "طلب", "مع", "خلال", "بين", "الذي",
    "عدم", "ذلك", "التأكيد", "القطاع", "جدا", "لكن", "ما", "الى", "إلى", "بالنسبة",
    "شي", "ولكن", "العمل", "المكان", "مكان", "لا", "يوجد", "المكتب", "يؤدي", "عن",
    "أن", "إن", "كان", "كانت", "هذا", "هذه", "هناك", "تم", "كما", "كل", "قد", "أي",
}

ARABIC_RE = re.compile(r"[\u0600-\u06FF]+")


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper RTL display in word clouds."""
    text = (text or "").strip()
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def normalize_text(text: str) -> str:
    text = (text or "").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


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
    stop = set(stopwords or DEFAULT_STOPWORDS)
    words = ARABIC_RE.findall(normalize_text(text))
    return [w for w in words if len(w) > 1 and w not in stop]


def top_terms(text: str, limit: int = 20) -> list[tuple[str, int]]:
    counts = Counter(tokenize_arabic(text))
    return counts.most_common(limit)


# Available Arabic fonts
ARABIC_FONTS = {
    "DIN Next Arabic": "assets/DIN Next LT Arabic Regular.ttf",
    "Arial": "assets/arial.ttf",
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


def get_available_fonts() -> dict[str, str]:
    """Return available fonts that exist on the system."""
    available = {}
    for name, path in ARABIC_FONTS.items():
        if Path(path).exists():
            available[name] = path
    return available


def pick_font(font_name: str | None = None) -> str | None:
    """Pick a font, preferring the specified one or falling back to defaults."""
    if font_name and font_name in ARABIC_FONTS:
        path = Path(ARABIC_FONTS[font_name])
        if path.exists():
            return str(path)
    
    # Fallback order (DIN first as it's the original)
    for name in ["DIN Next Arabic", "Arial", "Noto Naskh Arabic", "Noto Sans Arabic", "Amiri"]:
        if name in ARABIC_FONTS:
            path = Path(ARABIC_FONTS[name])
            if path.exists():
                return str(path)
    return None


def make_color_func(colors: list[str]):
    """Create a color function for wordcloud using the original approach."""
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
) -> Image.Image:
    """
    Generate a word cloud with customizable options.
    
    Uses the original ArabicWordCloudGenerator approach:
    - Reshapes Arabic text properly with arabic_reshaper + bidi
    - Supports transparent background (mode='RGBA')
    - Custom color functions
    """
    tokens = tokenize_arabic(text)
    source = " ".join(tokens) if tokens else normalize_text(text)
    
    # Reshape Arabic text for proper display (original approach)
    shaped = reshape_arabic(source) if source else reshape_arabic("لا توجد بيانات كافية")
    
    # Get colors for the scheme
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["ELM Brand"])
    color_func = make_color_func(colors)
    
    font_path = pick_font(font_name)
    
    # Use original approach: transparent background with RGBA mode
    if transparent or background_color is None:
        wc = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            background_color=None,
            mode='RGBA',
            collocations=False,
            prefer_horizontal=prefer_horizontal,
            color_func=color_func,
            max_words=max_words,
        ).generate(shaped)
    else:
        wc = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            background_color=background_color,
            collocations=False,
            prefer_horizontal=prefer_horizontal,
            color_func=color_func,
            max_words=max_words,
        ).generate(shaped)
    
    return wc.to_image()
