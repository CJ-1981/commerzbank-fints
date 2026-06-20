# Module Definitions - Commerzbank FinTS Payout Automator

## Module Organization Overview

The application follows a **single-file architecture** where module boundaries are defined by class responsibilities rather than file boundaries. This architecture provides clear separation of concerns while maintaining deployment simplicity.

### Module Hierarchy

```
commerzbank_fints_qt_desktop_app.py
├── FinTSWorker Module (Background Operations)
│   ├── FinTS Protocol Management
│   ├── SEPA Transfer Processing
│   ├── PhotoTAN Authentication Coordination
│   └── Thread-Safe Event Coordination
└── CommerzbankFinTSApp Module (UI Management)
    ├── User Interface Construction
    ├── Input Validation and Processing
    ├── Table Widget Management
    ├── Terminal Log Display
    └── Background Worker Coordination
```

## Core Modules

### Module 1: FinTSWorker (Background Banking Operations)

**Module Type**: Thread Worker Class  
**Base Class**: `QThread`  
**Location**: Lines 35-198 (164 lines)  
**Thread Execution**: Background thread for blocking network operations

#### Responsibilities

1. **FinTS Client Management**
   - Initialize `FinTS3PinTanClient` with banking credentials
   - Establish SSL/TLS connections to Commerzbank server
   - Manage session lifecycle and authentication state
   - Handle connection errors and retry logic

2. **SEPA Account Operations**
   - Retrieve authorized SEPA accounts from bank
   - Match debtor IBAN against authorized accounts
   - Validate account access permissions
   - Handle account retrieval failures

3. **Payment Processing**
   - **Collective Mode**: Execute Sammelüberweisung (batch transfer)
   - **Individual Mode**: Sequential single payment execution
   - Format SEPA transfer orders with proper metadata
   - Handle partial success/failure scenarios

4. **PhotoTAN Authentication Coordination**
   - Detect photoTAN challenges from FinTS responses
   - Coordinate with GUI thread for user interaction
   - Handle both coupled (code entry) and decoupled (mobile approval) methods
   - Manage authentication timeout and cancellation scenarios

5. **Thread-Safe Communication**
   - Emit Qt signals for status updates and log messages
   - Manage event-based blocking for user coordination
   - Handle thread interruption and cancellation
   - Ensure clean thread shutdown and resource cleanup

#### Public Interface

**Constructor**:
```python
def __init__(self, blz, user_id, pin, debtor_iban, payouts, method)
```
- **Parameters**: Banking credentials, payment data, transfer strategy
- **Purpose**: Initialize worker with execution context
- **Thread Safety**: Constructor runs in GUI thread, worker runs in background

**Main Entry Point**:
```python
def run(self)
```
- **Purpose**: QThread entry point for background operations
- **Execution**: Runs in background thread context
- **Signals**: Emits log_signal, request_tan_signal, finished_signal

**TAN Coordination Methods**:
```python
def set_tan(self, tan_code)      # Called by GUI thread with user input
def cancel_tan(self)             # Called by GUI thread on user cancellation
```

**Processing Methods**:
```python
def process_collective_transfer(self, client, debtor_acc)    # Batch processing
def process_individual_transfers(self, client, debtor_acc)   # Sequential processing
def handle_tan_challenge_loop(self, client, response)       # Authentication coordination
```

#### Signal Interface

**log_signal(str, str)**: Terminal logging with color coding
- **Signal Signature**: `(message: str, color: str)`
- **Purpose**: Update terminal display with operation progress
- **Colors**: slate-200 (info), red-400 (error), emerald-400 (success), amber-400 (warning)
- **Thread Safety**: Automatically queued to GUI thread

**request_tan_signal(str, bool)**: PhotoTAN challenge prompt request
- **Signal Signature**: `(challenge_text: str, is_decoupled: bool)`
- **Purpose**: Request GUI to display photoTAN input dialog
- **Challenge Context**: Banking server challenge text for user display
- **Decoupled Mode**: Flag indicates mobile app approval vs code entry

**finished_signal(bool, str)**: Operation completion notification
- **Signal Signature**: `(success: bool, status_message: str)`
- **Purpose**: Notify GUI thread of worker completion
- **Success State**: True if all operations completed successfully
- **Status Message**: Human-readable completion status

#### Internal State

**Thread Coordination State**:
```python
self.tan_event = threading.Event()    # Event for blocking during photoTAN input
self.submitted_tan = ""               # User-provided TAN code
self.is_cancelled = False             # Cancellation flag for graceful shutdown
```

**Banking Operation State**:
```python
self.blz = bank_code                 # German bank code (Bankleitzahl)
self.user_id = login_id              # Online banking user identifier
self.pin = secure_pin                # User PIN (never persisted)
self.debtor_iban = account_iban      # Source account IBAN
self.payouts = payment_list          # List of payment dictionaries
self.method = transfer_strategy      # "collective" or "individual"
```

#### Dependencies

**External Libraries**:
- `fints.client.FinTS3PinTanClient`: FinTS protocol client
- `fints.models.SEPATransferOrder`: SEPA transfer message formatting
- `fints.exceptions`: FinTS-specific exception handling
- `fints.dialog.NeedTANResponse`: PhotoTAN challenge response type

**Standard Library**:
- `threading.Event`: Thread-safe coordination primitive
- `decimal.Decimal`: Precise financial calculations

#### Error Handling

**Exception Types Handled**:
- `FinTSClientPINError`: Invalid PIN authentication failure
- `FinTSClientError`: General FinTS protocol errors
- `Exception`: Unexpected errors with logging

**Error Recovery**:
- PIN errors trigger user-friendly error messages
- Network errors result in clean failure notifications
- User cancellation results in graceful thread termination

#### Thread Safety Guarantees

**Thread-Affinity Rules**:
- **Constructor**: Runs in GUI thread during initialization
- **run()**: Executes entirely in background worker thread
- **Signal Emission**: Thread-safe, automatically queued to GUI thread
- **Event Blocking**: Safe for background thread to wait on GUI thread coordination

**Shared State Protection**:
- `submitted_tan`: Set by GUI thread, read by worker thread (string is atomic)
- `is_cancelled`: Set by GUI thread, read by worker thread (boolean is atomic)
- `tan_event`: Thread-safe coordination primitive

---

### Module 2: CommerzbankFinTSApp (Main GUI Window)

**Module Type**: Qt Main Window Class  
**Base Class**: `QMainWindow`  
**Location**: Lines 201-684 (484 lines)  
**Thread Execution**: Main GUI thread

#### Responsibilities

1. **User Interface Construction**
   - Build complete Qt6 widget layout with splitter-based design
   - Implement responsive dashboard interface with modern styling
   - Create configuration panel with input fields for banking credentials
   - Design payout table with real-time validation and feedback
   - Implement terminal log display with color-coded messages

2. **Input Validation and Processing**
   - **IBAN Validation**: MOD-97 checksum validation (lines 548-564)
   - **Form Validation**: Empty field checking and data completeness
   - **Real-time Feedback**: Visual validation during data entry
   - **Clipboard Import**: Tab-separated spreadsheet data parsing
   - **Amount Validation**: Decimal parsing and formatting

3. **Table Widget Management**
   - Dynamic row addition and deletion
   - Cell change detection and validation triggers
   - Batch totals calculation and display updates
   - Selection management for bulk operations
   - IBAN validation feedback with color coding

4. **Background Worker Coordination**
   - Worker thread initialization with validated parameters
   - Signal-slot connection for thread-safe communication
   - PhotoTAN dialog display and user input collection
   - Operation completion handling with user notifications
   - Thread lifecycle management and cleanup

5. **Terminal Log Display**
   - Real-time message display with HTML formatting
   - Color-coded log levels (info, warning, success, error)
   - Auto-scrolling to latest messages
   - Message persistence during operation execution

#### Public Interface

**Constructor**:
```python
def __init__(self)
```
- **Purpose**: Initialize main window and construct UI
- **Execution**: Runs in GUI thread during application startup

**UI Construction Methods**:
```python
def init_ui(self)                              # Build complete interface
def setup_dark_palette(self)                   # Apply CSS styling
def load_mock_data(self)                       # Load example payment data
```

**Table Management Methods**:
```python
def add_table_row(self)                       # Add new empty row
def delete_selected_row(self)                  # Remove selected rows
def paste_from_clipboard(self)                 # Import spreadsheet data
def on_table_changed(self, item)               # Handle cell edits
def update_batch_calculations(self)            # Recalculate totals
```

**Validation Methods**:
```python
def validate_iban_mod97(self, iban)            # MOD-97 checksum validation
```

**Worker Coordination Methods**:
```python
def start_batch_execution(self)                # Launch background worker
def prompt_user_for_tan(self, challenge, is_decoupled)  # Display photoTAN dialog
def on_worker_finished(self, success, message)         # Handle completion
```

**Log Display Methods**:
```python
def append_terminal_message(self, text, color)  # Add formatted message
```

#### Slot Interface

**@pyqtSlot(str, str) append_terminal_message**:
- **Purpose**: Receive log messages from worker thread
- **Parameters**: (message_text: str, color_hex: str)
- **Execution**: Runs in GUI thread via Qt signal-slot mechanism

**@pyqtSlot(str, bool) prompt_user_for_tan**:
- **Purpose**: Display photoTAN input dialog
- **Parameters**: (challenge_text: str, is_decoupled: bool)
- **Execution**: Blocks background thread until user responds

**@pyqtSlot(bool, str) on_worker_finished**:
- **Purpose**: Handle worker completion
- **Parameters**: (success: bool, status_message: str)
- **Execution**: Re-enables execute button and shows completion dialog

#### UI Components

**Left Panel (Configuration and Data)**:
```python
self.blz_input = QLineEdit()              # Bank code input
self.user_id_input = QLineEdit()          # Online banking ID
self.pin_input = QLineEdit()              # PIN entry (password mode)
self.debtor_iban_input = QLineEdit()      # Source account IBAN
self.radio_collective = QRadioButton()    # Batch transfer mode
self.radio_individual = QRadioButton()    # Individual transfer mode
self.table = QTableWidget()               # Payment data table
self.lbl_batch_count = QLabel()           # Row count display
self.lbl_batch_total = QLabel()           # Total sum display
```

**Right Panel (Execution and Logs)**:
```python
self.log_terminal = QPlainTextEdit()      # Terminal message display
self.btn_execute = QPushButton()          # Batch execution trigger
```

#### Internal State

**Worker Reference**:
```python
self.worker = None  # FinTSWorker instance (None when not running)
```

**UI State**:
- Table content and selection state
- Form input values (not persisted)
- Radio button selection for transfer strategy
- Terminal log content

#### Validation Logic

**IBAN MOD-97 Validation** (Lines 548-564):
```python
def validate_iban_mod97(self, iban):
    """Mathematical validation of IBAN checksum using MOD-97 algorithm"""
    # 1. Remove spaces and convert to uppercase
    # 2. Rearrange: Move first 4 characters to end
    # 3. Convert letters to numbers (A=10, B=11, ..., Z=35)
    # 4. Calculate MOD-97 and verify result equals 1
    return int(numeric_iban) % 97 == 1
```

**Validation Integration**:
- Called during `update_batch_calculations()` for every table row
- Invalid IBANs displayed in red color (#f87171)
- Valid IBANs displayed in white color (#f1f5f9)
- Provides immediate visual feedback during data entry

#### Dependencies

**Qt6 Framework**:
- `PyQt6.QtWidgets`: GUI components and layouts
- `PyQt6.QtCore`: Core Qt functionality including signals and threading
- `PyQt6.QtGui`: Fonts, colors, and styling

**Standard Library**:
- `decimal.Decimal`: Precise financial calculations for totals

#### Thread Safety Guarantees

**GUI Thread Constraints**:
- All methods run in GUI thread context
- Never performs blocking I/O operations
- All worker communication via signal-slot mechanism
- Worker methods called via signal emission, not direct invocation

**Thread Coordination**:
- PhotoTAN input collected in GUI thread, passed to worker via `worker.set_tan()`
- Worker thread blocked on `threading.Event` during user interaction
- Clean separation ensures no race conditions or data corruption

---

## Cross-Cutting Concerns

### Thread Safety

**Coordination Mechanism**: Qt signals and threading events provide thread-safe communication without manual locking

**Signal Emission**: All worker-to-GUI communication via Qt signals (thread-safe by design)
**Event Blocking**: `threading.Event` for GUI-to-worker coordination (thread-safe primitive)
**State Protection**: Atomic operations for shared boolean/string state

### Error Handling Strategy

**Worker Thread**: Catches exceptions, emits error signals, never crashes GUI
**GUI Thread**: User-friendly error messages, never propagates exceptions to user
**Network Errors**: Graceful degradation with clear error messages
**Validation Errors**: Real-time feedback prevents invalid data submission

### Logging Strategy

**Worker Thread**: Color-coded log messages via signal emission
**GUI Thread**: HTML-formatted terminal display with auto-scroll
**Log Levels**: info, warning, success, error with visual color coding
**Message Content**: Operation progress, authentication challenges, completion status

---

## Module Dependencies Graph

```
┌─────────────────────────────────────────────────────────┐
│                 CommerzbankFinTSApp                      │
│                   (GUI Thread)                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Dependencies:                                    │  │
│  │  • PyQt6 (QtWidgets, QtCore, QtGui)              │  │
│  │  • decimal.Decimal                               │  │
│  │  • threading.Event (for coordination)            │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ Signal-Slot Connection
                          │ (Thread-Safe Communication)
                          │
┌─────────────────────────────────────────────────────────┐
│                    FinTSWorker                           │
│                 (Background Thread)                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Dependencies:                                    │  │
│  │  • fints.client.FinTS3PinTanClient              │  │
│  │  • fints.models.SEPATransferOrder                │  │
│  │  • fints.dialog.NeedTANResponse                 │  │
│  │  • fints.exceptions                               │  │
│  │  • threading.Event                               │  │
│  │  • decimal.Decimal                               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ Direct API Calls
                          │ (Same Thread Context)
                          │
┌─────────────────────────────────────────────────────────┐
│                  python-fints Library                    │
│              (External Integration)                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Provides:                                        │  │
│  │  • FinTS/HBCI Protocol Implementation            │  │
│  │  • SSL/TLS Network Communication                 │  │
│  │  • SEPA Message Formatting                       │  │
│  │  • PhotoTAN Challenge Processing                  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Module Interaction Patterns

### Pattern 1: User Initiates Batch Execution

```
User Action → GUI Thread → Worker Thread → Bank Server
     │            │             │              │
     └──── Button Click ──► Validation ──► Signal Connect ──► FinTS API
                          └─► Worker Start ──► Network Call
```

### Pattern 2: PhotoTAN Challenge Response

```
Bank Server → Worker Thread → GUI Thread → User → GUI Thread → Worker Thread
     │            │              │         │          │              │
     └─► Challenge ──► Signal Emit ──► Dialog ──► Input ──► Event Set ──► Send TAN
```

### Pattern 3: Real-time Validation

```
User Input → Table Edit → Validation Method → Visual Feedback
     │            │              │                 │
     └─► Cell Change ──► IBAN Validate ──► Color Update
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Module Pattern**: Single-File Class-Based Architecture
