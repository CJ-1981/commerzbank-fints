# -*- mode: python ; coding: utf-8 -*-
"""
Minimal PyInstaller spec file for Commerzbank FinTS Payout Automator
Uses auto-discovery for Qt plugins
"""

import sys
import os

block_cipher = None
app_name = 'CommerzbankFinTS_Payout_Automator'

a = Analysis(
    ['commerzbank_fints_qt_desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'fints.client',
        'fints.exceptions',
        'mt940',
        'sepaxml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'pandas',
        'numpy',
        'pytest',
        'test',
        'tests',
    ],
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
    name=app_name + '.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
