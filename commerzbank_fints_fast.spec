# -*- mode: python ; coding: utf-8 -*-
"""
Fast build spec for Commerzbank FinTS Payout Automator
Simplified configuration to prevent hanging - creates directory distribution
"""

import sys
import os

# Application metadata
app_name = 'CommerzbankFinTS_Payout_Automator'
main_script = 'commerzbank_fints_qt_desktop_app.py'

# Minimal hidden imports for fast analysis
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'fints',
    'typing_extensions',
]

# Exclude non-essential modules
excludes = [
    'tkinter', 'matplotlib', 'pandas', 'numpy', 'scipy',
    'IPython', 'jupyter', 'pytest', 'test', 'tests',
    'sphinx', 'pylint', 'mypy',
]

a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Simplified build - no UPX compression
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name + '.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # CRITICAL: Disabled to prevent hanging
    console=True,  # Enable console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # CRITICAL: Disabled to prevent hanging
    upx_exclude=[],
    name=app_name,
)
