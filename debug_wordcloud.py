from __future__ import annotations

import json
from pathlib import Path

from src.text_utils import build_wordcloud_debug_report, get_available_fonts, make_wordcloud

SAMPLE_TEXT = "مرحبا بالعالم هذا نص تجريبي للتحقق من العمل والنجاح والتقدم المستمر وتطوير الخدمات وتحسين تجربة المستخدم"


def main() -> None:
    out_dir = Path("debug_output")
    out_dir.mkdir(exist_ok=True)

    report = build_wordcloud_debug_report(SAMPLE_TEXT)
    (out_dir / "wordcloud_debug_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for font_name in get_available_fonts():
        image = make_wordcloud(SAMPLE_TEXT, font_name=font_name, width=1200, height=800)
        image.save(out_dir / f"wordcloud_{font_name.replace(' ', '_')}.png")
        print(f"saved debug_output/wordcloud_{font_name.replace(' ', '_')}.png")

    print("saved debug_output/wordcloud_debug_report.json")


if __name__ == "__main__":
    main()
