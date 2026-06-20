# Changelog

All notable changes to Commerzbank FinTS Payout Automator and its build system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflow for automated Windows executable builds
- PyInstaller spec file for cross-platform builds
- Comprehensive build documentation and guides
- Automated testing integration with pytest
- Build artifact storage and release automation
- Issue templates for build bug reports and feature requests

### Changed
- Updated README with installation options (standalone vs. source)
- Restructured project documentation for better organization
- Improved build configuration with platform detection

### Fixed
- PyInstaller dependency collection for PyQt6 and fints libraries
- Cross-platform compatibility for macOS and Linux builds

## [1.0.0] - 2024-06-20

### Added
- Initial release of Commerzbank FinTS Payout Automator
- Qt6 desktop application with modern GUI
- FinTS banking protocol integration with python-fints
- photoTAN authentication support
- Batch SEPA transfer management
- Real-time IBAN validation with MOD-97 checksum
- Interactive payout table with clipboard import
- Terminal logging with color-coded messages
- Background thread handling for non-blocking operations
- Comprehensive test suite with 85%+ coverage
- Detailed documentation and guides

### Security Features
- No PIN storage (fresh authentication each session)
- Encrypted SSL/TLS communication
- Thread-safe operations
- Two-factor authentication with photoTAN

### System Requirements
- Python 3.11+ or standalone Windows executable
- Windows 10+, macOS 11+, or Linux
- 4GB RAM minimum (8GB recommended)
- Stable internet connection
- Commerzbank online banking with photoTAN access

---

## Release Notes Format

### [Version] - Date

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Features to be removed in future versions

### Removed
- Features removed in this version

### Fixed
- Bug fixes

### Security
- Security vulnerability fixes or enhancements

---

**Note**: This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality additions
- PATCH version for backwards-compatible bug fixes
