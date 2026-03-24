#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install pyinstaller -r requirements.txt
pyinstaller --noconfirm --windowed --name ArabicPDFSuite --add-data 'assets:assets' app.py
