# -*- mode: python ; coding: utf-8 -*-
"""
Compatibility wrapper.

We no longer maintain a separate Windows-only PyInstaller recipe because it kept
breaking in CI. Use the shared cross-platform spec instead:

    pyinstaller --noconfirm packaging/pyinstaller.spec
"""

from pathlib import Path

SHARED_SPEC = Path(SPECPATH).resolve().parent / 'pyinstaller.spec'
exec(compile(SHARED_SPEC.read_text(), str(SHARED_SPEC), 'exec'))
