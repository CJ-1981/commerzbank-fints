# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Commerzbank FinTS Payout Automator
Creates a standalone Windows executable with all dependencies bundled
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Application metadata
block_cipher = None
app_name = 'CommerzbankFinTS_Payout_Automator'
app_version = '1.0.0'

# Main application script
main_script = 'commerzbank_fints_qt_desktop_app.py'

# Platform-specific settings
is_windows = sys.platform == 'win32'
is_macos = sys.platform == 'darwin'
is_linux = sys.platform.startswith('linux')

# Data files and assets
datas = []
binaries = []

# Collect PyQt6 data files
try:
    datas += collect_data_files('PyQt6', include_pyds=False, subdir='PyQt6')
except:
    pass

# Collect fints library data
try:
    datas += collect_data_files('fints', include_pyds=True, subdir='fints')
except:
    pass

# Additional hidden imports
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'fints.client',
    'fints.models',
    'fints.dialog',
    'fints.exceptions',
    'fints.form',
    'fints.parser',
    'typing_extensions',
]

# Exclude modules to reduce size
excludes = [
    'tkinter',
    'matplotlib',
    'pandas',
    'numpy',
    'scipy',
    'IPython',
    'jupyter',
    'pytest',
    'test',
    'tests',
    'sphinx',
    'pylint',
    'mypy',
]

a = Analysis(
    [main_script],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out unnecessary files
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific executable configuration
if is_windows:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name + '.exe',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # Set to True for debugging
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,  # Add icon file: 'build-assets/icon.ico'
        version_file=None,  # Add version info: 'build-assets/version_info.txt'
    )
elif is_macos:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
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
        icon=None,  # Add icon file: 'build-assets/icon.icns'
    )
else:  # Linux
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
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
    upx=True,
    upx_exclude=[],
    name=app_name,
)
