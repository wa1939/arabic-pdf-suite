#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

python3 -m PyInstaller --noconfirm packaging/pyinstaller.spec

mkdir -p release
APP_PATH="dist/ArabicPDFSuite"
ARCHIVE="release/ArabicPDFSuite-macos.zip"

/usr/bin/ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ARCHIVE"

echo "Created $ARCHIVE"
