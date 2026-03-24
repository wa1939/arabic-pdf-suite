# Windows Desktop Build Guide - Arabic PDF Suite

## Quick Start

1. Install PyInstaller:
   ```bash
   pip install -r requirements.txt pyinstaller
   ```

2. Build the portable app from the repo root:
   ```bash
   pyinstaller --noconfirm packaging/pyinstaller.spec
   ```

3. Find your app:
   - Main launcher: `dist/ArabicPDFSuite/ArabicPDFSuite.exe`
   - CI archive: `release/ArabicPDFSuite-windows.zip`

4. Test it:
   - Open `ArabicPDFSuite.exe`
   - Keep the rest of the generated `dist/ArabicPDFSuite/` folder beside it

## What this build is
- Portable Windows desktop artifact
- No installer wizard
- Better for CI because it is much less fragile than maintaining a separate MSI/EXE packaging path

## Distribution
Zip the full `dist/ArabicPDFSuite/` folder or use the GitHub Actions artifact.

## Important limits
- This does **not** bundle Tesseract / Ghostscript / LibreOffice.
- OCR and some conversions still depend on those tools being installed on the target machine.
- If you want a polished signed installer later, do it after CI is green and stable.
