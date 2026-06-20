# Commerzbank FinTS Payout Automator

> A modern Qt6 desktop application for automating SEPA bank transfers through Commerzbank's FinTS interface with photoTAN authentication.

![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-Latest-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
[![CI Status](https://github.com/CJ-1981/commerzbank-fints/actions/workflows/ci.yml/badge.svg)](https://github.com/CJ-1981/commerzbank-fints/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25%2B-brightgreen)](https://github.com/CJ-1981/commerzbank-fints/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-113%20passing-success)](https://github.com/CJ-1981/commerzbank-fints/actions/workflows/ci.yml)

## 📸 Screenshot

![Application Screenshot](screenshots/app-screenshot.png)

## ✨ Features

- 🔐 **Secure FinTS Connection** - SSL/TLS encrypted communication with Commerzbank
- 📊 **Batch Payout Management** - Interactive table for managing multiple SEPA transfers
- ✅ **Real-time IBAN Validation** - MOD-97 checksum validation with visual feedback
- 📱 **photoTAN Integration** - Interactive challenge-response authentication
- 🔄 **Transfer Strategy Selection** - Collective batch or individual transfer modes
- 📋 **Clipboard Import** - Quick data import from spreadsheet applications
- 💻 **Terminal Logging** - Real-time operation feedback with color-coded messages
- ⚡ **Non-blocking Operations** - Background thread handling prevents UI freezing

## 🎯 Use Cases

### For Small Business Owners
Process bulk vendor payments efficiently with single photoTAN authentication for multiple transfers.

### For Accounting Departments  
Automate recurring payout operations with comprehensive audit trails and validation.

### For Finance Teams
Execute secure bank transfers with granular approval workflow and real-time monitoring.

## 🚀 Installation

### Option 1: Standalone Windows Executable (Recommended)

Download the pre-built Windows executable from the [Releases](https://github.com/CJ-1981/commerzbank-fints/releases) page:

1. Navigate to the latest release
2. Download `CommerzbankFinTS_Payout_Automator-Windows-vX.X.X.zip`
3. Extract the ZIP file
4. Run `CommerzbankFinTS_Payout_Automator.exe`

**No Python installation required!**

### Option 2: Build from Source

#### Prerequisites
- Python 3.11 or higher
- Stable internet connection
- Commerzbank online banking with photoTAN access

#### Quick Start

```bash
# Clone the repository
git clone https://github.com/CJ-1981/commerzbank-fints.git
cd commerzbank-fints

# Install dependencies
pip install -r requirements.txt

# Run the application
python commerzbank_fints_qt_desktop_app.py
```

#### Building Windows Executable

```bash
# Install build dependencies
pip install -r requirements.txt pyinstaller

# Build with PyInstaller
pyinstaller commerzbank_fints.spec --clean --noconfirm

# Find the executable in dist/CommerzbankFinTS_Payout_Automator.exe
```

## 📖 Usage

### First Time Setup

1. **Launch the application** - Start `commerzbank_fints_qt_desktop_app.py`
2. **Enter credentials** - Provide your Commerzbank online banking details
3. **Verify connection** - Application retrieves your account information
4. **Configure settings** - Set up default transfer preferences

### Creating a Batch Transfer

1. **Add payout rows** - Enter recipient details (name, IBAN, amount, purpose)
2. **Validate IBANs** - Automatic MOD-97 checksum validation with color feedback
3. **Import data** (optional) - Paste tab-separated data from spreadsheet
4. **Review totals** - Check batch summary and calculated sums
5. **Choose strategy** - Select collective batch (single photoTAN) or individual transfers
6. **Execute** - Start batch processing
7. **Authenticate** - Respond to photoTAN prompts on your smartphone
8. **Monitor progress** - Real-time status updates in terminal log

## 🔒 Security

- **PIN Protection** - Never stored in memory or configuration files
- **Two-Factor Authentication** - photoTAN required for all transfers
- **Encrypted Communication** - SSL/TLS connections to FinTS servers
- **No Credential Persistence** - Fresh authentication each session
- **Thread-Safe Operations** - Secure cross-thread data handling

## 🏗️ Technical Architecture

- **Language**: Python 3.14+
- **GUI Framework**: PyQt6 (Qt6)
- **Banking Protocol**: python-fints (FinTS/HBCI)
- **Architecture**: Event-driven threaded design
- **Thread Safety**: Signal-slot pattern for UI/worker coordination

### Architecture Highlights

- **UI Thread**: Responsive Qt6 interface with real-time updates
- **Worker Thread**: Background FinTS operations without blocking
- **Thread Coordination**: Event-based synchronization for photoTAN handling
- **Validation Layer**: Embedded MOD-97 IBAN checking for immediate feedback

## 📋 System Requirements

- **Operating System**: Windows 10+, macOS 11+, or modern Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Display**: 1024x768 minimum (1100x750 optimized)
- **Network**: Stable internet connection required

## 🛠️ Development

### Building Executables

#### GitHub Actions Build Pipeline

The project includes comprehensive CI/CD pipelines:

### CI/CD Pipeline

- **CI Testing**: Multi-platform automated testing (113 tests across 6 files)
- **Quality Gates**: Code quality, security scanning, coverage ≥85%
- **Build**: Cross-platform executable creation (Windows, macOS, Linux)
- **Release**: Automated GitHub releases with artifacts

#### CI/CD Workflows

- **CI Pipeline**: Comprehensive testing with quality gates
- **Test Reports**: Detailed test results and coverage reports
- **Merge Protection**: Branch protection and approval workflows
- **Notifications**: Automatic alerts on failures

For detailed CI/CD documentation, see [CI-CD Guide](docs/CI-CD-GUIDE.md) and [Quick Start](docs/CI-CD-QUICKSTART.md).

#### Build from Source

```bash
# Install build dependencies
pip install -r requirements.txt pyinstaller

# Build with PyInstaller spec file
pyinstaller commerzbank_fints.spec --clean --noconfirm

# The executable will be created at:
# dist/CommerzbankFinTS_Payout_Automator.exe
```

#### Build from Source

```bash
# Install build dependencies
pip install -r requirements.txt pyinstaller

# Build with PyInstaller spec file
pyinstaller commerzbank_fints.spec --clean --noconfirm

# The executable will be created at:
# dist/CommerzbankFinTS_Payout_Automator.exe
```

### Project Structure
```
commerzbank-fints/
├── commerzbank_fints_qt_desktop_app.py  # Main application
├── commerzbank_fints.spec               # PyInstaller build configuration
├── requirements.txt                      # Production dependencies
├── requirements-test.txt                 # Test dependencies
├── .github/workflows/build-windows.yml   # GitHub Actions build pipeline
├── build-assets/                         # Build resources (icons, version info)
├── tests/                               # Test suite
├── .moai/                               # Project documentation
├── .claude/                             # Development framework
└── README.md                            # This file
```

### Key Technologies
- **PyQt6**: Modern Qt6 Python bindings for desktop GUI
- **python-fints**: Open-source FinTS/HBCI implementation
- **threading**: Background operation management
- **decimal**: Precise financial calculations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is provided as-is for educational and personal use. The authors are not responsible for any financial losses or damages resulting from its use. Always verify transactions through your official banking channels.

## 🔗 Resources

- [FinTS Protocol Documentation](https://www.hbci-zka.de/)
- [python-fints Library](https://github.com/phython/python-fints)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

## 📞 Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/CJ-1981/commerzbank-fints).

### Testing

The project includes a comprehensive test suite:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=commerzbank_fints_qt_desktop_app --cov-report=html

# Run specific test
pytest tests/test_app_startup.py -v
```

See [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md) for detailed testing instructions.

---

**Made with ❤️ for automated banking workflows**
