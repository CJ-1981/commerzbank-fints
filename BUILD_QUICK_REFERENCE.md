# Build System Quick Reference

Quick reference for building and releasing Commerzbank FinTS Payout Automator executables.

## 🚀 Quick Start

### Automated Build (Recommended)

```bash
# Tag a new release
git tag v1.0.0
git push origin v1.0.0

# Wait for GitHub Actions to complete
# Download from Releases section
```

### Local Build

```bash
# Install dependencies
pip install -r requirements.txt pyinstaller

# Build executable
pyinstaller commerzbank_fints.spec --clean --noconfirm

# Test the build
cd dist
./CommerzbankFinTS_Payout_Automator.exe
```

## 📁 Build Artifacts

### Windows Build

- **Location**: `dist/CommerzbankFinTS_Payout_Automator.exe`
- **Size**: ~80-120 MB
- **Dependencies**: Bundled (standalone)

### macOS Build

- **Location**: `dist/CommerzbankFinTS_Payout_Automator.app`
- **Size**: ~100-150 MB
- **Dependencies**: Bundled (standalone)

### Linux Build

- **Location**: `dist/CommerzbankFinTS_Payout_Automator`
- **Size**: ~80-120 MB
- **Dependencies**: Bundled (standalone)

## 🔧 Build Options

### Debug Build

```python
# In commerzbank_fints.spec
console = True  # Show console for debugging
debug = True    # Include debug symbols
upx = False     # Disable compression
```

### Release Build

```python
# In commerzbank_fints.spec
console = False  # Hide console window
debug = False    # Optimized build
upx = True       # Enable compression
```

### Minimal Build

```python
# Add to excludes list
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
    'PIL',           # Exclude if not using Pillow
    'email',         # Exclude if not using email
]
```

## 🎯 Common Tasks

### Run Tests Before Build

```bash
pip install -r requirements-test.txt
pytest tests/ -v --cov=commerzbank_fints_qt_desktop_app
```

### Build with Clean Output

```bash
# Remove previous builds
pyinstaller commerzbank_fints.spec --clean --noconfirm

# Or manually remove build directories
rm -rf build dist *.spec
```

### Verify Build

```bash
# Windows
if exist "dist\CommerzbankFinTS_Payout_Automator.exe" (
    echo Build successful!
)

# macOS/Linux
if [ -f "dist/CommerzbankFinTS_Payout_Automator" ]; then
    echo Build successful!
fi
```

### Package for Distribution

```bash
# Windows
mkdir installer
copy dist\CommerzbankFinTS_Payout_Automator.exe installer\
copy README.md installer\
Compress-Archive -Path installer\* -DestinationPath "CommerzbankFinTS_Payout_Automator.zip"

# macOS/Linux
mkdir -p installer
cp -R dist/* installer/
cp README.md LICENSE installer/
tar -czf CommerzbankFinTS_Payout_Automator.tar.gz installer/
```

## 🏗️ GitHub Actions Workflows

### Build Windows Executable

**Trigger**: Push to main, tag, manual dispatch

**File**: `.github/workflows/build-windows.yml`

**Features**:
- Automated testing before build
- PyInstaller spec file execution
- Artifact storage (30 days retention)
- Automatic release on tag push
- Manual release creation option

### Build Cross-Platform Executables

**Trigger**: Tag push, manual dispatch

**File**: `.github/workflows/build-cross-platform.yml`

**Platforms**:
- Windows 10/11
- macOS 11+
- Ubuntu Linux

**Features**:
- Matrix build for all platforms
- Platform-specific packaging
- Unified release creation

## 🔍 Troubleshooting

### Build Fails

1. **Check Python version**: Must be 3.11+
2. **Verify dependencies**: `pip install -r requirements.txt`
3. **Run tests**: `pytest tests/ -v`
4. **Check PyInstaller version**: `pip install pyinstaller>=6.0.0`
5. **Review build logs**: Look for missing imports or dependencies

### Executable Won't Run

1. **Enable console**: Set `console = True` in spec file
2. **Check dependencies**: Verify all imports are bundled
3. **Test on clean machine**: No Python installation required
4. **Check antivirus**: May flag unsigned executables

### Missing DLL Errors

1. **Install Visual C++ Redistributable**: [Download](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. **Verify Qt plugins**: PyQt6 plugins must be bundled
3. **Check PATH**: Windows system paths must include required DLLs

## 📝 Release Checklist

### Pre-Release

- [ ] Update version in `commerzbank_fints.spec`
- [ ] Update version in `build-assets/version_info.txt`
- [ ] Update `CHANGELOG.md`
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Test executable on clean Windows machine
- [ ] Verify all features work correctly

### Release

- [ ] Commit all changes
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Wait for GitHub Actions build
- [ ] Download and test artifacts
- [ ] Verify release was created
- [ ] Test executable from release

### Post-Release

- [ ] Monitor GitHub Issues for bug reports
- [ ] Update documentation if needed
- [ ] Archive release artifacts
- [ ] Prepare for next version

## 📚 Documentation

- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Comprehensive build guide
- [README.md](README.md) - Installation and usage
- [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md) - Testing guide
- [GitHub Actions](.github/workflows/) - Build automation

## 🔗 Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Last Updated**: June 2024
**Maintained By**: CJ-1981
