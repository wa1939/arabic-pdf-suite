#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

python3 -m PyInstaller --noconfirm packaging/pyinstaller.spec

mkdir -p release
ARCHIVE="release/ArabicPDFSuite-linux-${RUNNER_ARCH:-$(uname -m)}.tar.gz"
tar -C dist -czf "$ARCHIVE" ArabicPDFSuite

echo "Created $ARCHIVE"
