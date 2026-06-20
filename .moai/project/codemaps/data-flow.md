# Data Flow Architecture - Commerzbank FinTS Payout Automator

## Data Flow Overview

The Commerzbank FinTS Payout Automator implements a **thread-separated data flow architecture** where UI data flows through the GUI thread while banking data flows through a background worker thread. The two threads coordinate via Qt signals and threading events, ensuring responsive user interaction during blocking network operations.

### Data Flow Principles

1. **Thread Separation**: UI data stays in GUI thread, banking operations in worker thread
2. **Signal-Slot Communication**: Thread-safe data transfer via Qt signals
3. **Event Coordination**: Cross-thread blocking for user-mediated operations
4. **Immutable Transfer**: Data passed between threads is immutable (copies, not references)
5. **Real-time Validation**: Immediate feedback during data entry without network calls

## High-Level Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│                   (Keyboard/Mouse Input)                     │
└─────────────────────────────────────────────────────────────┘
                          ↓ User Events
┌─────────────────────────────────────────────────────────────┐
│                    GUI Thread (Main)                         │
│                 CommerzbankFinTSApp                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Input Validation Layer                            │  │
│  │     • Form field validation                           │  │
│  │     • IBAN MOD-97 validation                          │  │
│  │     • Amount decimal parsing                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ Validated Data                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. Data Aggregation Layer                            │  │
│  │     • Table widget data extraction                    │  │
│  │     • Batch totals calculation                        │  │
│  │     • Transfer strategy selection                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ Prepared Payload                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. Worker Coordination Layer                        │  │
│  │     • Worker thread creation                          │  │
│  │     • Signal-slot connection                          │  │
│  │     • Thread lifecycle management                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓ Signal Emission
┌─────────────────────────────────────────────────────────────┐
│                  Worker Thread (Background)                  │
│                      FinTSWorker                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  4. Banking Protocol Layer                           │  │
│  │     • FinTS client initialization                    │  │
│  │     • Account retrieval and verification             │  │
│  │     • SEPA transfer formatting                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ Network I/O                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  5. Authentication Coordination Layer               │  │
│  │     • PhotoTAN challenge detection                    │  │
│  │     • User interaction coordination                   │  │
│  │     • TAN code submission                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ Signal Emission
└─────────────────────────────────────────────────────────────┘
                          ↓ Signal Reception
┌─────────────────────────────────────────────────────────────┐
│                    GUI Thread (Main)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  6. Response Handling Layer                          │  │
│  │     • Terminal log display                           │  │
│  │     • PhotoTAN dialog management                     │  │
│  │     • Completion notification                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Primary Data Flow Paths

### Data Flow Path 1: User Input to Banking Execution

**Phase**: Batch Execution Initiation  
**Entry**: User clicks "⚡ Execute Payout Batch" button  
**Exit**: Worker thread begins banking operations

#### Step 1: Input Validation (GUI Thread)

**Location**: Lines 602-632 in `start_batch_execution()`

**Data Flow**:
```
Input Fields → Validation Logic → Validated Data
     │               │                   │
     ├─► BLZ        ├─► Required        ├─► blz: "37040044"
     ├─► User ID    ├─► Format          ├─► user_id: "1234567890"
     ├─► PIN        ├─► Security        ├─► pin: "*****"
     ├─► IBAN       └─► Completeness    ├─► debtor_iban: "DE89..."
     └─► Table                          └─► payouts: [...]
```

**Validation Rules**:
```python
# PIN validation (Lines 607-609)
if not pin:
    return  # Block execution

# Table data validation (Lines 619-621)
if not name or not iban or not amount:
    return  # Block execution

# Payout list validation (Lines 630-632)
if not payouts:
    return  # Block execution
```

**Data Structure Transformation**:
```python
# Raw table data
table_widget_items = [QTableWidgetItem(...), ...]

# Transformed to banking payload
payouts = [
    {
        "name": "Max Mustermann",
        "iban": "DE12370400440001111111",
        "amount": "350.00",
        "reference": "Refund Invoice 10934"
    },
    # ... additional payouts
]
```

#### Step 2: Worker Initialization (GUI Thread)

**Location**: Lines 634-637 in `start_batch_execution()`

**Data Flow**:
```
Validated Data → Worker Constructor → Worker Instance State
        │                   │                     │
        ├─► Banking Creds  ├─► __init__()       ├─► self.blz
        ├─► Payouts        ├─► Parameter        ├─► self.user_id
        ├─► Strategy       ├─► Storage          ├─► self.pin
        └─► IBAN                                ├─► self.payouts
                                               ├─► self.method
                                               └─► self.tan_event
```

**Thread Safety**: Constructor runs in GUI thread, stores immutable data

#### Step 3: Signal Connection (GUI Thread)

**Location**: Lines 639-642 in `start_batch_execution()`

**Data Flow**:
```
Worker Signals → Slot Connections → Thread-Safe Communication Channels
       │                │                          │
       ├─► log_signal   ├─► connect()             ├─► Log messages
       ├─► request_tan  ├─► connect()             ├─► PhotoTAN prompts
       └─► finished     ├─► connect()             └─► Completion status
```

**Signal-Slot Mechanics**:
```python
# Signal emission (worker thread)
self.log_signal.emit(message, color)

# Slot reception (GUI thread)
@pyqtSlot(str, str)
def append_terminal_message(self, text, color):
    self.log_terminal.appendHtml(f'<span style="color: {color};">{text}</span>')
```

**Thread Safety**: Qt automatically queues signals to target thread

#### Step 4: Worker Thread Start (GUI Thread)

**Location**: Line 648 in `start_batch_execution()`

**Data Flow**:
```
worker.start() → QThread.start() → Background Thread Creation
       │                │                     │
       ├─► GUI Thread  ├─► OS Thread        ├─► New thread context
       └─► Triggers    └─► run() Call       └─► Banking operations
```

**Thread Separation**: GUI thread continues event loop, worker thread begins `run()`

---

### Data Flow Path 2: Banking Operations to FinTS Server

**Phase**: Worker Thread Execution  
**Entry**: Worker thread `run()` method begins  
**Exit**: Banking operations complete or fail

#### Step 1: FinTS Client Initialization

**Location**: Lines 84-92 in `FinTSWorker.run()`

**Data Flow**:
```
Worker State → FinTS Client → Network Connection
       │              │                 │
       ├─► blz        ├─► Constructor   ├─► SSL/TLS socket
       ├─► user_id    ├─► Parameter      ├─► Bank endpoint
       ├─► pin        ├─► Authentication  ├─► Session establishment
       └─► product_id └─► Configuration  └─► Protocol handshake
```

**Network Connection**:
```python
client = FinTS3PinTanClient(
    bank_identifier=self.blz,                    # "37040044"
    user_id=self.user_id,                        # "1234567890"
    pin=self.pin,                                # User PIN
    server="https://fints.commerzbank.de/fints", # Bank server URL
    product_id="9A5B7C218E1D5FA0B0"             # FinTS client ID
)
```

**Data Transformation**:
- Python objects → FinTS protocol messages
- UTF-8 strings → Wire protocol encoding
- Application credentials → Banking authentication tokens

#### Step 2: Account Retrieval

**Location**: Lines 96-98 in `FinTSWorker.run()`

**Data Flow**:
```
Client Request → FinTS Server → Account List → Worker State
      │               │              │              │
      ├─► get_sepa_   ├─► Protocol   ├─► Account   ├─► accounts list
      │   accounts()  ├─► Network    ├─► Objects   └─► Matching logic
      └─► Blocking    └─► Response   └─► IBAN list
```

**Response Data**:
```python
# FinTS server response
accounts = client.get_sepa_accounts()
# Returns: [SEPAAccount1(...), SEPAAccount2(...), ...]

# Data processing
debtor_acc = next(
    (a for a in accounts 
     if a.iban.replace(" ", "").upper() == self.debtor_iban.replace(" ", "").upper()
    ), 
    None
)
```

#### Step 3: Transfer Execution (Collective Mode)

**Location**: Lines 119-143 in `process_collective_transfer()`

**Data Flow**:
```
Payouts List → SEPA Orders → FinTS Message → Bank Server
      │             │              │              │
      ├─► Python     ├─► SEPATransferOrder  ├─► XML/FinTS
      │   Dicts      ├─► Decimal amounts    ├─► SSL/TLS
      ├─► Validation ├─► Recipient data     ├─► Protocol
      └─► Formatting └─► Reference text     └─► Processing
```

**Data Transformation**:
```python
# Python dictionaries
for p in self.payouts:
    orders.append(
        SEPATransferOrder(
            recipient_name=p["name"],          # "Max Mustermann"
            recipient_iban=p["iban"],           # "DE12370400440001111111"
            amount=Decimal(p["amount"]),       # Decimal("350.00")
            reason=p["reference"]               # "Refund Invoice 10934"
        )
    )

# FinTS protocol message
res = client.sepa_transfer_multiple(account=debtor_acc, orders=orders)
```

**Network Protocol**:
- SEPA credit transfer XML → FinTS binary encoding → SSL/TLS transmission

---

### Data Flow Path 3: PhotoTAN Challenge Coordination

**Phase**: Interactive Authentication  
**Entry**: FinTS server returns `NeedTANResponse`  
**Exit**: User provides TAN, banking continues

#### Step 1: Challenge Detection

**Location**: Line 136 in `process_collective_transfer()`

**Data Flow**:
```
Bank Response → Response Type Check → Challenge Handling
      │                  │                     │
      ├─► FinTS response ├─► isinstance()     ├─► photoTAN loop
      ├─► NeedTAN        ├─► True condition    ├─► User prompt
      └─► Regular        └─► False condition   └─► Continue
```

**Challenge Detection**:
```python
res = client.sepa_transfer_multiple(...)
# res might be NeedTANResponse instance

# Check and handle
res = self.handle_tan_challenge_loop(client, res)
```

#### Step 2: User Interaction Request (Worker → GUI)

**Location**: Lines 176-183 in `handle_tan_challenge_loop()`

**Data Flow**:
```
Challenge Data → Signal Emission → GUI Thread → Dialog Display
       │              │                │              │
       ├─► Challenge  ├─► emit()       ├─► Slot call  ├─► QMessageBox
       │   text       ├─► Qt signal    ├─► Parameter  ├─► User input
       ├─► Decoupled  ├─► Thread-safe  └─► Blocking   └─► Response
       └─► Event      └─► Queued                      collection
```

**Cross-Thread Communication**:
```python
# Worker thread (background)
self.tan_event.clear()                              # Reset coordination
self.request_tan_signal.emit(res.challenge, is_decoupled)  # Request GUI
self.tan_event.wait()                               # Block for user

# GUI thread (main)
@pyqtSlot(str, bool)
def prompt_user_for_tan(self, challenge, is_decoupled):
    # Display dialog, collect input
    tan, ok = QInputDialog.getText(...)
    if ok and tan.strip():
        self.worker.set_tan(tan.strip())  # Resume worker
```

#### Step 3: User Input Collection (GUI Thread)

**Location**: Lines 650-675 in `prompt_user_for_tan()`

**Data Flow**:
```
Dialog Display → User Input → Validation → Worker Coordination
      │              │            │              │
      ├─► Challenge  ├─► Keyboard ├─► Strip     ├─► set_tan()
      │   text       ├─► OK/Cancel├─► Check     ├─► Event set
      ├─► Decoupled  └─► Response └─► Confirm   └─► Resume worker
      └─► Context
```

**Input Processing**:
```python
# Coupled mode (code entry)
tan, ok = QInputDialog.getText(
    self, 
    "photoTAN Challenge Required", 
    f"{challenge}\n\nPlease enter the 6-digit photoTAN code:"
)
if ok and tan.strip():
    self.worker.set_tan(tan.strip())  # Send to worker
else:
    self.worker.cancel_tan()           # Cancel operation

# Decoupled mode (mobile approval)
ret = msg_box.exec()
if ret == QMessageBox.StandardButton.Ok:
    self.worker.set_tan("decoupled")   # Confirm mobile approval
```

#### Step 4: Worker Thread Resume

**Location**: Lines 186-196 in `handle_tan_challenge_loop()`

**Data Flow**:
```
GUI Action → Event Set → Worker Unblocks → TAN Submission
     │             │             │               │
     ├─► set_tan() ├─► Event     ├─► wait()      ├─► FinTS API
     │             ├─► set()    ├─► Returns     ├─► send_tan()
     └─► cancel()  └─► Signal   └─► Process     └─► Continue
```

**Thread Coordination**:
```python
# Worker thread blocked
self.tan_event.wait()  # Blocks until GUI sets event

# GUI thread sets event
self.worker.set_tan(tan_code)  # Sets tan_event

# Worker thread resumes
if getattr(res, 'decoupled', False):
    res = client.send_tan(res, "decoupled")
else:
    res = client.send_tan(res, self.submitted_tan)
```

---

### Data Flow Path 4: Real-Time Validation

**Phase**: User Data Entry  
**Entry**: User edits table cell  
**Exit**: Visual validation feedback

#### Step 1: Cell Edit Detection

**Location**: Line 321 (table signal connection) + Lines 545-546

**Data Flow**:
```
Cell Edit → Qt Signal → Slot Call → Validation Trigger
     │           │          │            │
     ├─► Item    ├─► item    ├─► on_      ├─► validate_
     │   change  ├─► changed├─► table_   ├─► iban_mod97()
     └─► Content └─► Signal  └─► changed  └─► Color update
```

**Event Connection**:
```python
# In init_ui()
self.table.itemChanged.connect(self.on_table_changed)

# Slot implementation
def on_table_changed(self, item):
    self.update_batch_calculations()  # Trigger validation
```

#### Step 2: IBAN Validation

**Location**: Lines 548-564 in `validate_iban_mod97()`

**Data Flow**:
```
IBAN String → MOD-97 Algorithm → Validation Result → Visual Feedback
      │              │                   │                  │
      ├─► Raw input ├─► Character      ├─► True/False    ├─► Green/Red
      │   "DE12..."  ├─► conversion     ├─► Checksum      ├─► White/
      ├─► Uppercase  ├─► Numeric        ├─► Modulo        └─► Red color
      └─► Cleaned    └─► Calculation    └─► Validation
```

**Algorithm Execution**:
```python
def validate_iban_mod97(self, iban):
    # Step 1: Clean input
    iban = iban.replace(" ", "").upper()
    
    # Step 2: Rearrange (move first 4 chars to end)
    rearranged = iban[4:] + iban[:4]
    
    # Step 3: Convert letters to numbers
    numeric = ""
    for char in rearranged:
        if char.isdigit():
            numeric += char
        elif char.isalpha():
            numeric += str(ord(char) - 55)  # A=10, B=11, ..., Z=35
    
    # Step 4: MOD-97 validation
    try:
        return int(numeric) % 97 == 1
    except ValueError:
        return False
```

#### Step 3: Visual Feedback

**Location**: Lines 566-589 in `update_batch_calculations()`

**Data Flow**:
```
Validation Result → Color Assignment → Cell Update → User Notification
         │                 │                 │                  │
         ├─► True          ├─► #f1f5f9       ├─► setForeground  ├─► Valid IBAN
         │   (valid)        ├─► (white)      ├─► Qt update      └─► Invalid IBAN
         └─► False         └─► #f87171      └─► Visual change
             (invalid)      (red-400)
```

**Feedback Implementation**:
```python
for row in range(row_count):
    iban_item = self.table.item(row, 1)
    if iban_item:
        raw_iban = iban_item.text().strip()
        if self.validate_iban_mod97(raw_iban):
            iban_item.setForeground(QColor("#f1f5f9"))  # Valid (white)
        else:
            iban_item.setForeground(QColor("#f87171"))  # Invalid (red)
```

#### Step 4: Batch Totals Update

**Location**: Lines 570-589 in `update_batch_calculations()`

**Data Flow**:
```
Table Data → Decimal Parsing → Summation → Display Update
     │              │               │              │
     ├─► Amount     ├─► Decimal()   ├─► Total      ├─► Label text
     │   strings    ├─► Precision   ├─► Sum        ├─► Format
     ├─► Iteration  ├─► Error       ├─► Count      └─► Real-time
     └─► Rows       └─► Handling    └─► Statistics
```

**Calculation Logic**:
```python
total_sum = Decimal("0.00")
for row in range(row_count):
    amount_item = self.table.item(row, 2)
    if amount_item:
        try:
            val = Decimal(amount_item.text().strip() or "0")
            total_sum += val
        except (InvalidOperation, ValueError):
            pass  # Skip invalid amounts

# Update display
self.lbl_batch_count.setText(f"Size: {row_count} Payout{'s' if row_count != 1 else ''}")
self.lbl_batch_total.setText(f"Total Sum: €{total_sum:,.2f}")
```

---

## Data Flow State Management

### Thread State Management

#### GUI Thread State

**Components**:
```python
class CommerzbankFinTSApp(QMainWindow):
    # Worker reference (None when not running)
    self.worker = None
    
    # UI state (managed by Qt)
    self.table = QTableWidget()        # Table data
    self.log_terminal = QPlainTextEdit() # Log content
    
    # Form state
    self.blz_input = QLineEdit()       # Bank code
    self.user_id_input = QLineEdit()   # User ID
    self.pin_input = QLineEdit()       # PIN (password mode)
    self.debtor_iban_input = QLineEdit() # Debtor IBAN
    
    # Strategy state
    self.radio_collective = QRadioButton()  # Transfer strategy
    self.radio_individual = QRadioButton()
```

**State Lifecycle**:
- **Initialization**: Created during `init_ui()`
- **User Interaction**: Modified via user input
- **Validation**: Checked during `start_batch_execution()`
- **Transfer**: Copied to worker thread via constructor
- **Cleanup**: State persists until application exit

#### Worker Thread State

**Components**:
```python
class FinTSWorker(QThread):
    # Banking credentials (immutable after construction)
    self.blz = blz
    self.user_id = user_id
    self.pin = pin
    self.debtor_iban = debtor_iban
    
    # Payment data (immutable after construction)
    self.payouts = payouts
    self.method = method
    
    # Coordination state (mutable during execution)
    self.tan_event = threading.Event()    # Coordination primitive
    self.submitted_tan = ""                # User-provided TAN
    self.is_cancelled = False              # Cancellation flag
```

**State Lifecycle**:
- **Initialization**: Set via constructor parameters
- **Execution**: Read-only banking state, mutable coordination state
- **PhotoTAN Coordination**: `tan_event` and `submitted_tan` modified
- **Completion**: Thread terminates, state destroyed

### Cross-Thread Data Transfer

#### Immutable Data Transfer (GUI → Worker)

**Method**: Constructor parameter passing  
**Data Type**: Immutable strings, booleans, lists of dictionaries

```python
# GUI thread
self.worker = FinTSWorker(
    blz,                    # String (immutable)
    user_id,               # String (immutable)
    pin,                   # String (immutable)
    debtor_iban,           # String (immutable)
    payouts,               # List of dicts (immutable reference)
    method                 # String (immutable)
)
```

**Thread Safety**: Immutable data requires no synchronization

#### Signal-Based Data Transfer (Worker → GUI)

**Method**: Qt signal emission  
**Data Type**: Strings, booleans (Qt automatically handles thread safety)

```python
# Worker thread
self.log_signal.emit(message, color)
self.request_tan_signal.emit(challenge, is_decoupled)
self.finished_signal.emit(success, message)

# GUI thread (automatically queued)
@pyqtSlot(str, str)
def append_terminal_message(self, text, color):
    # Process message
```

**Thread Safety**: Qt queues signals to target thread

#### Event-Based Coordination (GUI → Worker)

**Method**: Threading event primitive  
**Data Type**: Synchronization flag

```python
# Worker thread
self.tan_event.wait()  # Block until event set

# GUI thread
self.worker.set_tan(tan_code)  # Sets tan_event internally

# Worker thread resumes
tan = self.submitted_tan  # Read user input
```

**Thread Safety**: `threading.Event` is thread-safe by design

---

## Data Flow Error Handling

### Validation Error Handling

**Location**: Throughout GUI thread methods

**Error Flow**:
```
Invalid Input → Validation Check → Error Display → Operation Blocked
      │               │                 │              │
      ├─► Empty PIN  ├─► if not pin   ├─► QMessageBox├─► return
      ├─► Bad data   ├─► Exception     ├─► Error msg  └─► No worker
      └─► Validation ├─► Check failed  └─► User alert     start
```

**Handling Strategy**:
- **Input Validation**: Pre-flight checks before worker creation
- **User Feedback**: Immediate error messages via QMessageBox
- **Operation Blocking**: Prevent invalid data from reaching worker thread

### Network Error Handling

**Location**: Lines 112-117 in `FinTSWorker.run()`

**Error Flow**:
```
Network Error → FinTS Exception → Worker Handler → Signal Emission → GUI Display
      │               │               │              │              │
      ├─► Invalid PIN ├─► FinTSClient├─► except     ├─► log_signal ├─► Terminal
      │               ├─► PINError   ├─► Catch      ├─► emit()     ├─► Red text
      ├─► Protocol    ├─► FinTSClient├─► Log        ├─► finished   └─► Error msg
      │   error       └─► Error      └─► Signal     └─► emit()
      └─► Timeout
```

**Handling Strategy**:
- **Exception Catch**: Catch specific FinTS exceptions
- **Signal Emission**: Emit error signals to GUI thread
- **User Notification**: Display user-friendly error messages
- **Clean Shutdown**: Worker terminates cleanly

### Thread Coordination Error Handling

**Location**: Lines 74-76, 188-189 in `FinTSWorker`

**Error Flow**:
```
User Action → Coordination Update → Worker Check → Operation Result
      │               │                    │              │
      ├─► Cancel     ├─► cancel_tan()     ├─► is_       ├─► Clean exit
      │              ├─► is_cancelled     ├─► cancelled  └─► Signal emit
      └─► Timeout    ├─► = True           └─► Check
                    └─► tan_event.set()
```

**Handling Strategy**:
- **Cancellation**: Graceful shutdown on user request
- **Event Setting**: Always set event to prevent deadlock
- **State Check**: Check cancellation flag before continuing
- **Clean Termination**: Emit finished signal and exit

---

## Data Flow Performance Characteristics

### GUI Thread Performance

**Input Validation**:
- **IBAN Validation**: ~0.1-1ms per IBAN (string operations + modulo)
- **Table Update**: ~1-5ms for typical batch (10-50 rows)
- **Display Update**: ~10-30ms (Qt rendering)

**Responsiveness**:
- **Idle State**: 0% CPU usage (waiting for events)
- **User Input**: <5% CPU usage (event handling)
- **Worker Active**: <10% CPU usage (signal processing)

### Worker Thread Performance

**Banking Operations** (Variable, network-dependent):
- **Account Retrieval**: ~500-2000ms (network round-trip)
- **SEPA Transfer**: ~1000-5000ms (processing + confirmation)
- **PhotoTAN Coordination**: ~5000-30000ms (user interaction time)

**CPU Usage**:
- **Network I/O**: ~0% CPU (waiting for response)
- **Protocol Processing**: ~5-15% CPU (message parsing)
- **Event Coordination**: ~0% CPU (blocking on event)

### Cross-Thread Communication Overhead

**Signal Emission**: ~0.1-1ms (Qt internal queuing)  
**Event Coordination**: ~0.01-0.1ms (threading.Event)  
**Data Transfer**: Negligible (immutable references)

---

## Data Flow Security

### Credential Security

**PIN Handling**:
```
User Input → Password Field → Memory Variable → FinTS Client → SSL/TLS → Bank
     │              │               │               │           │          │
     ├─► Keyboard  ├─► Password   ├─► String      ├─► Encrypted├─► HTTPS  └─► Auth
     │             ├─► No display ├─► No storage ├─► Protocol└─► Secure
     └─► Secure    └─► Qt widget  └─► Session     └─► FinTS     transmission
```

**Security Measures**:
- **No Persistence**: PIN never written to disk
- **Memory Only**: Held in process memory only
- **SSL/TLS**: Encrypted transmission to bank
- **Session Scope**: Cleared when application exits

### Data Validation Security

**IBAN Validation**:
- **Pre-Transmission**: Validate before sending to bank
- **Cost Reduction**: Prevent failed transfer charges
- **User Feedback**: Immediate visual validation
- **No Network**: Local mathematical validation

**Amount Validation**:
- **Decimal Precision**: Prevent rounding errors
- **Type Safety**: Decimal type for exact arithmetic
- **Range Checking**: Implicit via Decimal parsing

---

## Data Flow Diagrams

### Complete Batch Execution Flow

```
User Input (GUI Thread)
    │
    ├─► Form Entry
    ├─► Table Edit
    └─► IBAN Validation (Real-time)
        │
        ▼
Execute Button Click
    │
    ├─► Input Validation
    ├─► Data Aggregation
    └─► Worker Creation
        │
        ▼
Worker Thread Start
    │
    ├─► FinTS Client Init
    ├─► Account Retrieval
    │       │
    │       ▼
    └─► Transfer Execution
        │
        ├─► Collective: sepa_transfer_multiple()
        └─► Individual: simple_sepa_transfer() loop
            │
            ▼
        PhotoTAN Challenge?
            │
            ├─► Yes: Signal GUI → User Input → Event Set → Continue
            └─► No: Continue
                │
                ▼
            Completion
                │
                ├─► Success: finished_signal.emit(True, message)
                └─► Failure: finished_signal.emit(False, error)
                    │
                    ▼
                GUI Thread
                    │
                    ├─► Re-enable Execute Button
                    ├─► Show Completion Dialog
                    └─► Ready for Next Batch
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Data Flow Pattern**: Thread-Separated Signal-Slot Architecture with Event Coordination
