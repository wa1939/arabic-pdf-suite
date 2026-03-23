from __future__ import annotations

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
    text = (text or "").strip()
    if not text:
        return ""
    return get_display(arabic_reshaper.reshape(text))


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


def pick_font() -> str | None:
    candidates = [
        Path("assets/NotoNaskhArabic-Regular.ttf"),
        Path("DIN Next LT Arabic Regular.ttf"),
        Path("arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def make_wordcloud(text: str, width: int = 1400, height: int = 800) -> Image.Image:
    tokens = tokenize_arabic(text)
    source = " ".join(tokens) if tokens else normalize_text(text)
    shaped = reshape_arabic(source)
    wc = WordCloud(
        font_path=pick_font(),
        width=width,
        height=height,
        background_color="white",
        collocations=False,
        prefer_horizontal=0.9,
        regexp=r"[^\s]+",
        color_func=lambda *args, **kwargs: "#4493F8",
    ).generate(shaped or "لا توجد بيانات كافية")
    return wc.to_image()
