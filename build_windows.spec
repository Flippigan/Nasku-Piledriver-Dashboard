# -*- mode: python ; coding: utf-8 -*-
# Windows build spec for Inverter Tracker

import streamlit
import os
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata

streamlit_path = os.path.dirname(streamlit.__file__)

# Collect metadata for packages that use importlib.metadata.version()
metadata_datas = []
metadata_datas += copy_metadata('streamlit')
metadata_datas += copy_metadata('pydantic')
metadata_datas += copy_metadata('altair')

# Collect all src files
src_files = []
src_dir = Path('src')
for f in src_dir.rglob('*.py'):
    src_files.append((str(f), str(f.parent)))

a = Analysis(
    ['src/launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        (streamlit_path, 'streamlit'),
        ('src', 'src'),
        ('.env', '.'),
    ] + metadata_datas,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.scriptrunner.script_runner',
        'supabase',
        'postgrest',
        'gotrue',
        'realtime',
        'storage3',
        'pandas',
        'pandas._libs.tslibs.timedeltas',
        'pydantic',
        'pydantic_core',
        'dotenv',
        'altair',
        'pyarrow',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest_cov',
    ],
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
    console=False,  # Hide console window for end users
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
