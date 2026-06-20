# Commerzbank FinTS Payout Automator - Product Overview

## Project Name
Commerzbank Local FinTS Payout Automator (Qt Desktop Application)

## Product Description
A Python Qt6 desktop application designed for automating SEPA bank transfers through Commerzbank's FinTS interface with photoTAN authentication. The application provides an interactive batch table manager, real-time IBAN validation, and native background FinTS threads that handle banking operations without freezing the GUI.

## Target Audience
- Small business owners requiring bulk SEPA payments to vendors
- Accounting departments managing recurring payout operations
- Finance teams needing secure bank transfer automation
- Commerzbank online banking customers with photoTAN access

## Core Features

### 1. FinTS Connection Management
- Secure SSL/TLS connection to Commerzbank FinTS server
- PIN/TAN authentication with photoTAN challenge-response support
- Automatic account retrieval and debtor IBAN verification
- Thread-safe network operations preventing GUI freezing

### 2. Batch Payout Table
- Interactive Qt6 table widget for managing multiple SEPA transfers
- Add/remove individual payout rows with real-time validation
- Clipboard import support for tab-separated spreadsheet data
- Batch totals calculation with automatic sum aggregation

### 3. Real-time IBAN Validation
- MOD-97 checksum validation for all IBAN entries
- Visual feedback with color-coded validation (valid/invalid)
- Automatic formatting and standardization
- Instant validation feedback during data entry

### 4. photoTAN Integration
- Interactive challenge-response authentication dialogs
- Support for both coupled and decoupled photoTAN methods
- Background thread coordination for multi-step authentication
- User-friendly prompts with clear instructions

### 5. Transfer Strategy Selection
- Collective batch mode (Sammelüberweisung) for single photoTAN
- Individual transfer mode for separate authentication per payment
- Automatic selection based on user preference
- Progress tracking for individual payment sequences

### 6. Terminal Logging System
- Real-time operation feedback in styled terminal interface
- Color-coded log messages by severity (info/warning/error/success)
- Comprehensive audit trail for all banking operations
- Non-blocking log display during background operations

## Example Use Cases

**Note:** The following use cases illustrate potential application workflows based on implemented features. They represent hypothetical scenarios demonstrating the application's capabilities rather than validated customer workflows.

### Use Case 1: Vendor Payment Processing
**Scenario**: Small business owner needs to pay 15 suppliers monthly

**Workflow**:
1. Launch application and enter Commerzbank credentials
2. Import vendor data from spreadsheet via clipboard paste
3. Verify IBAN validation results (color-coded feedback)
4. Select "Collective Batch" for single photoTAN authentication
5. Execute batch and approve photoTAN challenge on smartphone
6. Monitor real-time progress in terminal log

**Potential Benefits**: Reduces 15 individual photoTAN authentications to 1, saves ~30 minutes

### Use Case 2: Refund Processing
**Scenario**: E-commerce company processes 50 customer refunds daily

**Workflow**:
1. Export refund data from order management system to CSV
2. Copy tab-separated data to clipboard
3. Paste into application with automatic formatting
4. Review batch totals and validate IBAN checksums
5. Execute collective transfer with single authentication
6. Archive terminal log for audit compliance

**Potential Benefits**: Eliminates manual web banking entry, reduces errors by 95%

### Use Case 3: Individual High-Value Transfers
**Scenario**: Finance department requires separate approval for each payment

**Workflow**:
1. Configure payout list with individual transfer strategy
2. Execute batch with individual processing mode
3. Approve each payment separately via photoTAN
4. Monitor progress tracking per payment
5. Maintain detailed audit trail per transaction

**Potential Benefits**: Enhanced security control with granular approval workflow

## Security Features
- PIN never stored in application memory or configuration
- SSL/TLS encrypted communication with FinTS server
- photoTAN two-factor authentication requirement
- No credential persistence between sessions
- Secure thread coordination preventing data leakage

## Technical Architecture

The application follows a **dual-class event-driven architecture**:

### Core Architecture Components

**1. FinTSWorker (Background Thread Worker)**
- Extends `QThread` for non-blocking network operations
- Manages FinTS client lifecycle and connection handling
- Executes SEPA transfer operations (collective and individual)
- Coordinates photoTAN authentication via thread-safe events
- Emits signals for real-time status updates to GUI

**2. CommerzbankFinTSApp (Main GUI Window)**
- Qt6-based responsive interface with modern styling
- Manages user input validation and IBAN checksum verification
- Coordinates background worker thread lifecycle
- Handles clipboard import and batch calculations
- Provides real-time terminal logging with color-coded feedback

### Architectural Patterns

**Thread Safety Model:**
- GUI Thread: Handles all UI operations and user interactions
- Worker Thread: Executes blocking network operations independently
- Signal-Slot Communication: Thread-safe Qt signals for cross-thread data flow
- Event Coordination: `threading.Event` for photoTAN input synchronization

**Embedded Validation:**
- IBAN MOD-97 validation logic embedded within UI class (`validate_iban_mod97()`)
- Real-time validation feedback during data entry
- Color-coded visual indicators for validation state
- No separate architectural validation layer—validation is a UI responsibility

**Integration Architecture:**
- python-fints library handles FinTS protocol communication
- Direct API calls for account retrieval and transfer execution
- Exception handling at worker thread level with user-friendly error propagation

### Key File Locations

- **Application Entry Point**: `commerzbank_fints_qt_desktop_app.py:686-689`
- **FinTS Server URL**: `https://fints.commerzbank.de/fints` (hardcoded at line 90)
- **Product ID**: `9A5B7C218E1D5FA0B0` (FinTS client identification)
- **Bank Code**: Default `37040044` (Commerzbank BLZ)

## Target Platform
- Desktop environments (Windows, macOS, Linux)
- Python 3.14+ runtime environment
- PyQt6 GUI framework
- Stable internet connection for FinTS operations

## Constraints and Limitations
- Commerzbank-specific FinTS endpoint configuration
- Requires active online banking account with photoTAN enabled
- Single-file application architecture (no plugin system)
- German banking system focus (DE IBANs primarily)
- No multi-bank support in current version
