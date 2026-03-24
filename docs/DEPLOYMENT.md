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

## Desktop packages
- Windows: `pyinstaller packaging/pyinstaller.spec`
- macOS: `bash packaging/build-macos-app.sh`
- Linux: `bash packaging/build-linux-appimage.sh` or `snapcraft`
