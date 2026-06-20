# Windows Build Guide

Comprehensive guide for building Windows executables for the Commerzbank FinTS Payout Automator.

## Table of Contents

1. [Automated Builds (GitHub Actions)](#automated-builds-github-actions)
2. [Local Build Instructions](#local-build-instructions)
3. [Build Configuration](#build-configuration)
4. [Troubleshooting](#troubleshooting)
5. [Release Process](#release-process)

---

## Automated Builds (GitHub Actions)

### Overview

The project uses GitHub Actions for automated Windows executable builds. The pipeline handles testing, building, and packaging in a single workflow.

### Triggers

The build workflow triggers on:

- **Push to main branch**: Development builds
- **Tag push (v*)**: Production releases
- **Pull requests**: Validation builds
- **Manual dispatch**: On-demand builds with release creation

### Workflow Steps

1. **Setup**: Checkout code, install Python 3.11, cache dependencies
2. **Install**: Production and build dependencies (PyQt6, fints, PyInstaller)
3. **Test**: Run pytest suite with coverage reporting
4. **Build**: Execute PyInstaller with spec file
5. **Package**: Create ZIP archive with README and license
6. **Release**: Upload to GitHub Releases (tagged versions only)

### Manual Build with Release

1. Navigate to **Actions** tab in GitHub
2. Select **Build Windows Executable** workflow
3. Click **Run workflow**
4. Select **Create GitHub Release** option
5. Enter release tag (e.g., `v1.0.0`)
6. Click **Run workflow**
7. Wait for build completion (5-10 minutes)
8. Find the release in **Releases** section

### Artifact Download

1. Navigate to **Actions** tab
2. Select the completed workflow run
3. Scroll to **Artifacts** section
4. Download `windows-exe` artifact
5. Extract ZIP file to access the executable

---

## Local Build Instructions

### Prerequisites

- Windows 10 or 11 (64-bit)
- Python 3.11 or higher
- Administrator rights (for some build operations)

### Step 1: Install Python

```powershell
# Check Python version (must be 3.11+)
python --version

# If not installed, download from:
# https://www.python.org/downloads/
```

### Step 2: Clone Repository

```powershell
git clone https://github.com/CJ-1981/commerzbank-fints.git
cd commerzbank-fints
```

### Step 3: Create Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies

```powershell
# Install production dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller>=6.0.0
```

### Step 5: Run Tests (Optional)

```powershell
# Install test dependencies
pip install -r requirements-test.txt

# Run test suite
pytest tests/ -v
```

### Step 6: Build Executable

```powershell
# Build with PyInstaller
pyinstaller commerzbank_fints.spec --clean --noconfirm
```

### Step 7: Test Executable

```powershell
# Navigate to build output
cd dist

# Run the executable
.\CommerzbankFinTS_Payout_Automator.exe
```

### Step 8: Distribute

The executable is self-contained and can be copied to any Windows machine.

---

## Build Configuration

### PyInstaller Spec File

The `commerzbank_fints.spec` file contains all build configuration:

```python
# Key settings
app_name = 'CommerzbankFinTS_Payout_Automator'
console = False  # Hide console window (set to True for debugging)
upx = True      # Use UPX compression (reduces size by 50%)
```

### Customization Options

#### Add Application Icon

1. Create icon file: `build-assets/icon.ico` (256x256 pixels)
2. Update spec file:
   ```python
   icon='build-assets/icon.ico'
   ```

#### Add Version Information

1. Create version file from template:
   ```powershell
   # Edit build-assets/version_info.txt with your details
   ```

2. Update spec file:
   ```python
   version_file='build-assets/version_info.txt'
   ```

#### Include Additional Files

```python
datas = [
    ('config.ini', '.'),          # Include config file
    ('README.md', '.'),           # Include documentation
]

a = Analysis(
    [main_script],
    datas=datas,
    # ... other settings
)
```

---

## Troubleshooting

### Common Build Issues

#### Issue: PyInstaller Fails with Import Errors

**Symptom**: Build fails with `ModuleNotFoundError`

**Solution**:
```powershell
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt

# Verify imports work in Python
python -c "from PyQt6.QtWidgets import QApplication; print('OK')"
```

#### Issue: Antivirus Flags Executable

**Symptom**: Windows Defender or other antivirus blocks the executable

**Solution**:
- Add exception for the build directory
- Sign the executable with code signing certificate
- Submit to Microsoft SmartScreen for whitelist

#### Issue: Missing DLL Errors

**Symptom**: Executable runs but fails with DLL not found

**Solution**:
```powershell
# Rebuild with --debug option for detailed logs
pyinstaller commerzbank_fints.spec --debug --clean --noconfirm

# Check for missing Visual C++ Redistributable
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

#### Issue: Executable Size Too Large

**Symptom**: Generated .exe file is >200MB

**Solution**:
```python
# In spec file, exclude more modules
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
]

# Disable UPX compression if it causes issues
upx = False
```

#### Issue: Application Fails to Start

**Symptom**: Double-clicking .exe does nothing

**Solution**:
```powershell
# Enable console to see error messages
# In spec file:
console = True

# Rebuild and run from command line
cd dist
.\CommerzbankFinTS_Payout_Automator.exe
```

---

## Release Process

### Creating a New Release

#### 1. Update Version Numbers

Edit `commerzbank_fints.spec`:
```python
app_version = '1.1.0'  # Increment version
```

Edit `build-assets/version_info.txt`:
```python
StringStruct(u'FileVersion', u'1.1.0.0'),
StringStruct(u'ProductVersion', u'1.1.0.0'),
```

#### 2. Update Changelog

Create or update `CHANGELOG.md`:
```markdown
## [1.1.0] - 2024-XX-XX

### Added
- New feature description

### Fixed
- Bug fix description

### Changed
- Change description
```

#### 3. Commit and Tag

```bash
# Commit changes
git add .
git commit -m "Release v1.1.0"

# Create and push tag
git tag v1.1.0
git push origin v1.1.0
```

#### 4. Verify Build

1. Navigate to GitHub Actions
2. Wait for "Build Windows Executable" workflow to complete
3. Download and test the artifact
4. Verify the release was created in Releases section

#### 5. Manual Testing Checklist

- [ ] Executable starts without errors
- [ ] Application connects to Commerzbank successfully
- [ ] Batch transfer operations work correctly
- [ ] PhotoTAN authentication functions properly
- [ ] IBAN validation works as expected
- [ ] Data import/export features functional
- [ ] No memory leaks or crashes during extended use

---

## Advanced Topics

### Code Signing

If you have a code signing certificate, sign the executable:

```powershell
# Install SignTool (part of Windows SDK)
# Sign the executable
signtool sign /f certificate.pfx /p password ^
  /t http://timestamp.digicert.com ^
  /fd sha256 ^
  dist/CommerzbankFinTS_Payout_Automator.exe
```

### Multi-Version Builds

Create separate build configurations for different scenarios:

- **Debug Build**: Include console, disable optimization
- **Release Build**: No console, UPX compression enabled
- **Portable Build**: All dependencies in single directory

### Cross-Platform Builds

For macOS and Linux, use platform-specific build scripts:

```bash
# macOS build
pyinstaller commerzbank_fints.spec --clean --noconfirm

# Linux build
pyinstaller commerzbank_fints.spec --clean --noconfirm
```

---

## Support and Feedback

For build issues or questions:

1. Check existing [GitHub Issues](https://github.com/CJ-1981/commerzbank-fints/issues)
2. Create a new issue with build logs and error messages
3. Include your Windows version and Python version
4. Attach the PyInstaller build output if possible

---

**Last Updated**: June 2024
**Build System**: PyInstaller 6.0+ with GitHub Actions
**Target Platform**: Windows 10/11 64-bit
