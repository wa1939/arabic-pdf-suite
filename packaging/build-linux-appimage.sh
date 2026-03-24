#!/usr/bin/env bash
set -euo pipefail
echo 'Build the portable folder with PyInstaller first, then package it with appimagetool.'
pyinstaller --noconfirm --name ArabicPDFSuite --add-data 'assets:assets' app.py
