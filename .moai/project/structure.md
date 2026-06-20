# Commerzbank FinTS Payout Automator - Project Structure

## Directory Tree

```
commerzbank_fints/
├── commerzbank_fints_qt_desktop_app.py    # Single-file application (689 lines)
├── .moai/                                  # MoAI-ADK framework configuration
│   ├── config/                            # Project configuration files
│   │   ├── sections/                      # Configuration sections
│   │   │   ├── user.yaml                  # User metadata
│   │   │   ├── language.yaml              # Language settings
│   │   │   ├── design.yaml                # Design system config
│   │   │   └── harness.yaml               # Quality gate settings
│   │   ├── evaluator-profiles/            # Evaluation scoring profiles
│   │   └── astgrep-rules/                 # AST grep pattern rules
│   ├── design/                            # Design artifacts and assets
│   │   ├── screenshots/                   # UI screenshots
│   │   └── wireframes/                    # Interface wireframes
│   ├── docs/                              # Generated documentation
│   ├── evolution/                         # Evolution and learning data
│   │   ├── learnings/                     # Acquired learnings
│   │   ├── new-skills/                     # New skill definitions
│   │   └── telemetry/                      # Usage telemetry
│   ├── learning/                          # Learning and observation data
│   ├── logs/                              # Application logs
│   ├── project/                           # Project documentation
│   │   ├── brand/                         # Brand assets and identity
│   │   └── db/                            # Database schemas
│   ├── reports/                           # Generated reports
│   │   └── plan-audit/                     # SPEC review reports
│   └── state/                             # State checkpoints
├── .claude/                               # Claude Code framework configuration
│   ├── rules/                            # MoAI-ADK rules and guidelines
│   │   └── moai/                         # Core MoAI framework rules
│   │       ├── core/                     # Core constitutional rules
│   │       ├── workflow/                 # Workflow-specific rules
│   │       ├── development/              # Development guidelines
│   │       └── languages/                # Language-specific rules
│   ├── skills/                           # Skill definitions
│   │   └── moai-*/                       # Various MoAI skills
│   ├── agents/                           # Agent definitions (if any)
│   └── commands/                         # Command definitions
└── README.md                             # Project readme
```

## Module Organization

### Single-File Architecture
The application follows a single-file architecture pattern where all components are contained within `commerzbank_fints_qt_desktop_app.py`. This architecture is suitable for:

- Desktop applications with focused scope
- Rapid prototyping and deployment
- Simplified distribution and execution
- Educational clarity for codebase understanding

### Class-Level Module Boundaries

#### 1. FinTSWorker (Background Thread Worker)
**Purpose**: Handles network-blocking banking operations in background thread

**Responsibilities**:
- FinTS client initialization and connection management
- SEPA account retrieval and verification
- Collective batch transfer processing
- Individual payment sequence execution
- photoTAN challenge-response coordination
- Thread-safe event coordination with GUI

**Key Methods**:
- `run()`: Main thread entry point for banking operations
- `process_collective_transfer()`: Handles Sammelüberweisung logic
- `process_individual_transfers()`: Sequential payment processing
- `handle_tan_challenge_loop()`: Interactive photoTAN coordination

**Signal Interface**:
- `log_signal(str, str)`: Terminal logging with color coding
- `request_tan_signal(str, bool)`: photoTAN prompt requests
- `finished_signal(bool, str)`: Completion notification

#### 2. CommerzbankFinTSApp (Main GUI Window)
**Purpose**: Qt6 main window with responsive dashboard interface

**Responsibilities**:
- UI layout construction and styling
- User input handling and validation
- Table widget management and updates
- Clipboard import processing
- **IBAN validation logic (embedded within UI class)**
- Background worker coordination
- Terminal log display management

**Key Methods**:
- `init_ui()`: Constructs complete interface layout
- `setup_dark_palette()`: Applies modern CSS styling
- `validate_iban_mod97()`: IBAN checksum validation (lines 548-564)
- `update_batch_calculations()`: Real-time totals calculation
- `start_batch_execution()`: Launches background worker
- `prompt_user_for_tan()`: photoTAN dialog coordination

**UI Components**:
- Left Panel: Configuration, strategy selection, payout table
- Right Panel: Terminal logs and execution controls
- Splitter: Resizable horizontal layout divider

## Layer Architecture

The application implements a **simplified two-layer architecture** with embedded validation:

### UI Layer (CommerzbankFinTSApp)
- Qt6 widget management and event handling
- User input validation and processing
- **Embedded IBAN validation via `validate_iban_mod97()` method**
- Visual feedback and terminal logging
- Background worker lifecycle management

**Interface Contract**: All UI operations must be thread-safe and use Qt signals for cross-thread communication

**Embedded Validation**: IBAN MOD-97 checksum validation is implemented directly within the UI class (lines 548-564), not as a separate architectural layer. This method provides real-time validation feedback during data entry.

### Business Logic Layer (FinTSWorker)
- FinTS protocol implementation via python-fints library
- Banking operation orchestration
- photoTAN authentication coordination
- Thread-safe event management

**Interface Contract**: Must emit signals for all state changes and wait for GUI thread coordination

### Integration Layer (python-fints)
- Third-party FinTS/HBCI client library
- Network communication with Commerzbank
- SEPA message formatting and parsing
- SSL/TLS connection management

**Interface Contract**: External library with documented API for client operations

**Architecture Note**: The application does NOT implement a separate "Validation Layer." IBAN validation logic is embedded within the UI class as a method (`validate_iban_mod97()`) that provides real-time feedback during user interaction.

## Key File Locations

### Application Entry Point
- **File**: `commerzbank_fints_qt_desktop_app.py:686-689`
- **Purpose**: Application initialization and main window display
- **Dependencies**: PyQt6, fints library

### Core Configuration
- **FinTS Server**: `https://fints.commerzbank.de/fints` (line 90, hardcoded)
- **Product ID**: `9A5B7C218E1D5FA0B0` (FinTS client identification)
- **Bank Code**: Default `37040044` (Commerzbank BLZ)

### MoAI Framework Configuration
- **User Settings**: `.moai/config/sections/user.yaml`
- **Language Settings**: `.moai/config/sections/language.yaml`
- **Design System**: `.moai/config/sections/design.yaml`
- **Quality Gates**: `.moai/config/sections/harness.yaml`
- **Evaluator Profiles**: `.moai/config/evaluator-profiles/`
- **AST Grep Rules**: `.moai/config/astgrep-rules/`

## Module Boundaries and Contracts

### Thread Safety Boundaries
- **GUI Thread**: Handles all UI operations and user interactions
- **Worker Thread**: Executes blocking network operations
- **Coordination**: `threading.Event` for blocking worker during photoTAN input
- **Signal-Slot**: Qt signals for thread-safe communication

### Data Flow Boundaries
1. **User Input → UI Layer**: Form validation and processing
2. **UI Layer → Worker Thread**: Signal-based parameter passing
3. **Worker Thread → FinTS Library**: Direct API calls
4. **FinTS Library → Worker Thread**: Response objects and exceptions
5. **Worker Thread → UI Layer**: Signal-based status updates

### Error Handling Boundaries
- **UI Layer**: Input validation and user-friendly error messages
- **Worker Thread**: FinTS exception handling and logging
- **Integration Layer**: Library-specific exception propagation

## Dependency Management

### Runtime Dependencies
- **PyQt6**: Qt6 Python bindings for GUI
- **fints**: python-fints library for FinTS/HBCI protocol

### Development Dependencies
- **Python 3.14+**: Required runtime environment
- **Standard Library**: threading, decimal, logging modules

### Framework Dependencies
- **MoAI-ADK**: AI-driven development framework configuration
- **Claude Code**: Development environment and agent coordination

## Configuration Architecture

### Application Configuration
- **Hardcoded Settings**: FinTS server URL, product ID
- **User Input**: Banking credentials, payment details
- **UI Preferences**: Transfer strategy selection

### Framework Configuration
- **Quality Gates**: TRUST 5 validation thresholds
- **Language Settings**: Multi-language support configuration
- **Design System**: UI/UX patterns and component standards

## Extension Points (Current Limitations)

### Current Architecture Constraints
- Single-file design limits plugin extensibility
- Hardcoded Commerzbank endpoint prevents multi-bank support
- No configuration file system for persistent settings
- Limited internationalization (German banking focus)
- Validation logic embedded in UI class (not modular)

### Potential Extension Areas
- Configuration file integration for bank settings
- Plugin architecture for multiple bank support
- Persistent credential storage (with proper security)
- International SEPA support beyond German IBANs
- Batch size optimization and chunking strategies
- Extraction of validation logic into separate module

## Documentation Structure

### Generated Documentation
- **Product Overview**: `.moai/project/product.md`
- **Technical Stack**: `.moai/project/tech.md`
- **Architecture**: `.moai/project/structure.md` (this file)

### Framework Documentation
- **Constitutional Rules**: `.claude/rules/moai/core/`
- **Workflow Guides**: `.claude/rules/moai/workflow/`
- **Language Guides**: `.claude/rules/moai/languages/`

### Design Artifacts
- **Screenshots**: `.moai/design/screenshots/`
- **Wireframes**: `.moai/design/wireframes/`
- **Brand Assets**: `.moai/project/brand/`
