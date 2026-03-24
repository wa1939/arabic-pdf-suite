# -*- mode: python ; coding: utf-8 -*-
"""
Arabic PDF Suite - Windows Installer Spec
Build with: pyinstaller packaging/windows_installer.spec
"""

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('backend', 'backend'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'streamlit',
        'pypdf2',
        'pdf2image',
        'PIL',
        'pytesseract',
        'docx',
        'openpyxl',
        'reportlab',
        'wordcloud',
        'arabic_reshaper',
        'bidi',
    ],
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
    name='Arabic-Pdf-Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Arabic-Pdf-Suite',
)
