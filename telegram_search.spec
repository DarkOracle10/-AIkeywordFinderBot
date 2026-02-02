# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Telegram Keyword Search Desktop App.

Build command:
    pyinstaller telegram_search.spec

This will create a single executable file in the standalone-app/ folder.
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all telethon submodules
hiddenimports = collect_submodules('telethon')

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env.example', '.'),
    ],
    hiddenimports=hiddenimports + [
        'telethon',
        'telethon.sync',
        'telethon.tl',
        'telethon.tl.types',
        'telethon.tl.functions',
        'telethon.errors',
        'telethon.sessions',
        'telethon.crypto',
        'telethon.network',
        'dotenv',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TelegramKeywordSearch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add your icon path here: 'icon.ico'
)
