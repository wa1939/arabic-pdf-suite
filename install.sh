#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${1:-arabic-pdf-suite}
if [ ! -d "$APP_DIR" ]; then
  git clone https://github.com/wa1939/arabic-pdf-suite.git "$APP_DIR"
fi
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
exec streamlit run app.py --server.address 0.0.0.0 --server.port 3000
