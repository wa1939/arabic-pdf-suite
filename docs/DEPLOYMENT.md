# Deployment Guide

## Vercel
Use for the lightweight UI only. Full OCR on Vercel is not recommended because Ghostscript and Tesseract are not a clean fit for serverless Python.

## Railway
- Connect the repo.
- Railway will use `Dockerfile`.
- Expose port `3000`.

## Docker
```bash
docker compose up --build
```

## One-command local run
```bash
bash install.sh
```

## Desktop artifacts
We now use one shared PyInstaller recipe across Windows, macOS, and Linux.
That is deliberate: one boring build that works beats three flaky “installer” paths.

Build from the repo root:

- Windows / generic: `pyinstaller --noconfirm packaging/pyinstaller.spec`
- macOS archive: `bash packaging/build-macos-app.sh`
- Linux archive: `bash packaging/build-linux-appimage.sh`

GitHub Actions uploads portable desktop artifacts in `release/`:
- Windows: `ArabicPDFSuite-windows.zip`
- macOS: `ArabicPDFSuite-macos.zip`
- Linux: `ArabicPDFSuite-linux-<arch>.tar.gz`

Notes:
- These are **portable desktop builds**, not signed installers.
- Real notarized macOS apps and MSI/DMG installers need platform-specific signing and runner validation.
