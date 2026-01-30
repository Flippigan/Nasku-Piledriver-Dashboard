# -*- mode: python ; coding: utf-8 -*-

import streamlit
import os

streamlit_path = os.path.dirname(streamlit.__file__)

a = Analysis(
    ['src/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        (streamlit_path, 'streamlit'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.runtime.scriptrunner',
        'supabase',
        'pandas',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='InverterTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
