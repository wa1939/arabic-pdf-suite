from pathlib import Path

out = Path('docs/screenshots')
out.mkdir(parents=True, exist_ok=True)
(out / 'README.txt').write_text('Run the app on localhost:3000, then use browser automation or manual capture to replace placeholder screenshots.', encoding='utf-8')
print(f'Screenshot placeholder prepared at {out}')
