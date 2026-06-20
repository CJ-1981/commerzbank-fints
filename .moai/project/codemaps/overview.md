# Architecture Overview - Commerzbank FinTS Payout Automator

## High-Level Architecture

The Commerzbank FinTS Payout Automator implements an **Event-Driven Threaded Architecture** specifically designed for responsive desktop banking applications. The architecture follows a **single-file modular pattern** where clear separation of concerns is maintained through class boundaries rather than file boundaries.

### Core Design Principles

1. **Thread Safety First**: Network-blocking operations never impact UI responsiveness
2. **Signal-Slot Communication**: Qt's proven mechanism for thread-safe inter-thread communication
3. **Embedded Validation**: Real-time validation integrated into user interaction flow
4. **Interactive Authentication**: Background thread coordination for user-mediated photoTAN challenges
5. **Desktop-First Design**: Native Qt6 GUI optimized for local execution

## Architectural Pattern

### Event-Driven Threaded Architecture

The application implements a specialized variant of the **Worker Thread Pattern** optimized for banking operations:

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Thread (GUI)                        │
│                  CommerzbankFinTSApp                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Qt Event Loop                                      │   │
│  │  • User Input Handling                               │   │
│  │  • Real-time Validation                              │   │
│  │  • Terminal Log Display                              │   │
│  │  • photoTAN Dialog Coordination                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↕ Qt Signals
┌─────────────────────────────────────────────────────────────┐
│                  Worker Thread (FinTS)                      │
│                     FinTSWorker                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Network Operations (Blocking)                    │   │
│  │  • FinTS Protocol Management                          │   │
│  │  • SEPA Transfer Execution                            │   │
│  │  • photoTAN Challenge Handling                       │   │
│  │  • Thread-Safe Event Coordination                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↕ API Calls
┌─────────────────────────────────────────────────────────────┐
│              External Integration Layer                      │
│                 python-fints Library                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • FinTS/HBCI Protocol Implementation                 │   │
│  │  • SSL/TLS Network Communication                     │   │
│  │  • SEPA Message Formatting                           │   │
│  │  • photoTAN Challenge Processing                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## System Boundaries

### External System Boundary

**Commerzbank FinTS Server**
- **Endpoint**: `https://fints.commerzbank.de/fints` (hardcoded)
- **Protocol**: FinTS/HBCI over SSL/TLS
- **Authentication**: PIN/TAN with photoTAN Strong Customer Authentication (SCA)
- **Operations**: SEPA account retrieval, transfer execution, status queries

**Boundary Characteristics**:
- **Security**: Encrypted communication with certificate validation
- **Latency**: Network-dependent with potential timeout considerations
- **Reliability**: Dependent on banking server availability and maintenance windows
- **Compliance**: German banking regulations and PSD2 requirements

### Internal Thread Boundaries

**GUI Thread Boundary (CommerzbankFinTSApp)**
- **Responsibility**: User interaction, display updates, input validation
- **Constraint**: Must never perform blocking I/O operations
- **Communication**: Emits signals to worker thread, receives status via slots
- **State Management**: UI state, user input, terminal log content

**Worker Thread Boundary (FinTSWorker)**
- **Responsibility**: Network operations, FinTS protocol, banking logic
- **Constraint**: Must never directly access Qt GUI components
- **Communication**: Emits status signals, waits for GUI thread coordination
- **State Management**: Banking client state, photoTAN challenge state, operation progress

### User Interaction Boundary

**PhotoTAN Authentication Boundary**
- **Special Coordination**: Background thread suspends while GUI thread prompts user
- **Event-Based Blocking**: `threading.Event` coordinates cross-thread interaction
- **Two-Mode Support**: Coupled (code entry) and decoupled (mobile approval) methods
- **Security Context**: Time-sensitive challenges requiring user mediation

## Key Design Patterns

### 1. Worker Thread Pattern (QThread)

**Implementation**: `FinTSWorker` extends `QThread` for background operations

**Benefits**:
- UI responsiveness during network operations
- Clear separation of UI and business logic
- Thread-safe communication via Qt signals
- Simplified error handling in dedicated context

**Pattern Structure**:
```python
class FinTSWorker(QThread):
    # Signal definitions for thread-safe communication
    log_signal = pyqtSignal(str, str)
    request_tan_signal = pyqtSignal(str, bool)
    finished_signal = pyqtSignal(bool, str)
    
    def run(self):
        # Banking operations executed in background thread
        # All GUI communication via signal emission
```

### 2. Signal-Slot Communication Pattern

**Implementation**: Qt signals for inter-thread coordination

**Signal Types**:
- **Log Signal**: Terminal message updates with color coding
- **TAN Request Signal**: PhotoTAN challenge prompts with context
- **Finished Signal**: Completion notification with status

**Benefits**:
- Thread-safe communication without manual locking
- Type-safe parameter passing
- Automatic thread affinity management
- Decoupled communication architecture

### 3. Interactive Thread Coordination Pattern

**Implementation**: Event-based blocking for user-mediated authentication

**Pattern Structure**:
```python
def handle_tan_challenge_loop(self, client, response):
    while isinstance(res, NeedTANResponse) and not self.is_cancelled:
        self.tan_event.clear()                    # Reset coordination event
        self.request_tan_signal.emit(challenge)    # Request GUI interaction
        self.tan_event.wait()                      # Block until user responds
        # Process user response and continue
```

**Benefits**:
- Natural user interaction flow during background operations
- Thread-safe coordination without polling
- Clean separation of user interaction from business logic
- Support for cancellation and timeout scenarios

### 4. Embedded Validation Pattern

**Implementation**: Real-time validation within UI class

**Pattern Structure**:
```python
class CommerzbankFinTSApp(QMainWindow):
    def validate_iban_mod97(self, iban):
        # MOD-97 checksum validation
        # Called during table edit events
        # Provides immediate visual feedback
```

**Benefits**:
- Immediate user feedback during data entry
- No API calls for validation (cost reduction)
- Mathematical certainty of IBAN validity
- Integrated into natural user workflow

## Architecture Constraints and Limitations

### Current Constraints

1. **Single-File Architecture**: All code in one file limits modular testing and deployment
2. **Hardcoded Configuration**: Commerzbank endpoint prevents multi-bank support
3. **German Banking Focus**: Limited internationalization and SEPA zone support
4. **No Configuration Files**: All settings must be entered per session
5. **Embedded Validation**: Validation logic not modularized for reuse

### Design Trade-offs

**Simplicity vs. Extensibility**: Chose single-file architecture for development simplicity and deployment ease over plugin extensibility

**Performance vs. Security**: Direct credential entry per session prioritizes security over convenience of stored credentials

**Responsiveness vs. Complexity**: Two-thread architecture provides optimal responsiveness without complex multi-threaded concurrency

**Validation Strategy**: Embedded validation provides immediate feedback but limits validation logic reuse

## Technology Alignment

### Framework Choices Rationale

**PyQt6**: Most mature Python GUI framework with excellent threading support
- **Signal-Slot Architecture**: Perfect for thread-safe communication
- **Cross-Platform**: Windows, macOS, Linux support
- **Mature Ecosystem**: Extensive documentation and community support

**python-fints**: Comprehensive German banking protocol implementation
- **FinTS/HBCI Support**: Complete protocol coverage for German banks
- **photoTAN Handling**: Built-in support for modern authentication
- **Active Maintenance**: Regular updates for banking protocol changes
- **Open Source**: Transparent implementation with community support

**Python 3.14+**: Modern Python runtime with enhanced capabilities
- **Type Hints**: Improved code documentation and IDE support
- **Decimal Precision**: Native support for financial calculations
- **Threading**: Enhanced threading capabilities for worker pattern

## Architecture Evolution Path

### Current State (Single-File Desktop App)
- Focused scope with clear class boundaries
- Direct Python execution for deployment
- Embedded validation and configuration

### Near-Term Evolution (Configuration Enhancement)
- Configuration file support for bank settings
- Persistent credential storage with OS keychain
- Extracted validation module for reuse

### Medium-Term Evolution (Modular Architecture)
- Separate modules for UI, business logic, and validation
- Plugin system for multi-bank support
- Internationalization and multi-language support

### Long-Term Evolution (Enterprise Features)
- Cloud-based configuration synchronization
- Advanced authentication methods
- Mobile application companion
- Enterprise deployment with centralized management

## Compliance and Security Architecture

### Banking Compliance

**German Banking Regulations**:
- FinTS/HBCI protocol compliance
- PSD2 Strong Customer Authentication (SCA) requirements
- SEPA credit transfer standards
- Data protection and privacy regulations

**Security Architecture**:
- SSL/TLS encrypted communication
- Certificate validation for server authentication
- No plaintext credential storage
- Time-sensitive photoTAN challenges

### Data Protection

**Privacy by Design**:
- No credential persistence (user-controlled security)
- No logging of sensitive authentication data
- Minimal data retention (session-only)
- User-mediated authentication for all operations

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Architecture**: Event-Driven Threaded Architecture (Single-File Pattern)
