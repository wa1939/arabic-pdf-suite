# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

PROJECT_ROOT = Path.cwd().resolve()
APP_FILE = PROJECT_ROOT / 'app.py'
ASSETS_DIR = PROJECT_ROOT / 'assets'


datas = []
if ASSETS_DIR.exists():
    datas.append((str(ASSETS_DIR), 'assets'))

datas += collect_data_files('streamlit', include_py_files=True)

hiddenimports = [
    'bidi.algorithm',
    'arabic_reshaper',
    'pymupdf',
]


a = Analysis(
    [str(APP_FILE)],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ArabicPDFSuite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ArabicPDFSuite',
)
