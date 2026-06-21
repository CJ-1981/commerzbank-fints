#!/usr/bin/env python3
"""
PyInstaller diagnostic tool to identify hanging issues
Tests PyInstaller analysis and build process step by step
"""

import sys
import subprocess
import time
import os

def test_step(name, command, timeout=60):
    """Test a single build step with timeout"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")

    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ SUCCESS in {elapsed:.1f}s")
            return True
        else:
            print(f"❌ FAILED in {elapsed:.1f}s")
            print(f"Error: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("PyInstaller Hanging Diagnostic Tool")
    print("=" * 60)

    # Test 1: Basic Python environment
    if not test_step(
        "Python Environment",
        "python --version"
    ):
        return 1

    # Test 2: PyInstaller installation
    if not test_step(
        "PyInstaller Version",
        "pyinstaller --version"
    ):
        return 1

    # Test 3: Module imports
    if not test_step(
        "Import PyQt6",
        "python -c \"from PyQt6.QtWidgets import QApplication\""
    ):
        return 1

    if not test_step(
        "Import fints",
        "python -c \"import fints\""
    ):
        return 1

    # Test 4: Application syntax check
    if not test_step(
        "Application Syntax",
        "python -m py_compile commerzbank_fints_qt_desktop_app.py"
    ):
        return 1

    # Test 5: PyInstaller analysis only
    print("\n" + "=" * 60)
    print("Testing: PyInstaller Analysis (this is where hanging often occurs)")
    print("=" * 60)

    start_time = time.time()
    try:
        result = subprocess.run(
            "pyinstaller commerzbank_fints.spec --clean --noconfirm --log-level=DEBUG",
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ BUILD SUCCESS in {elapsed:.1f}s")
            print(f"Executable should be in dist/")
            return 0
        else:
            print(f"❌ BUILD FAILED in {elapsed:.1f}s")
            print(f"Last 1000 chars of stderr:")
            print(result.stderr[-1000:])
            return 1
    except subprocess.TimeoutExpired:
        print(f"⏰ BUILD TIMEOUT after 10 minutes")
        print("\nMost likely causes:")
        print("1. UPX compression hanging (fixed by setting upx=False)")
        print("2. Missing hidden imports causing circular dependency loops")
        print("3. PyQt6 plugin collection issues")
        print("4. Anti-virus interference")
        print("\nTry the commerzbank_fints_fast.spec file for a simpler build.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
