# Architecture Codemaps - Commerzbank FinTS Payout Automator

This directory contains comprehensive architecture documentation for the Commerzbank FinTS Payout Automator project, focusing on the event-driven threaded architecture implemented in a single-file desktop application.

## Document Structure

### 1. overview.md (266 lines)
**Purpose**: High-level architectural summary and design patterns

**Contents**:
- Event-Driven Threaded Architecture overview
- System boundaries (external, internal thread, user interaction)
- Key design patterns (Worker Thread, Signal-Slot, Interactive Coordination, Embedded Validation)
- Architecture constraints and trade-offs
- Technology alignment rationale
- Compliance and security architecture

**When to read**: First document to read for understanding the overall system architecture

### 2. modules.md (460 lines)
**Purpose**: Module definitions and responsibilities within the single-file architecture

**Contents**:
- Module hierarchy based on class boundaries
- FinTSWorker module (background banking operations)
- CommerzbankFinTSApp module (UI management)
- Cross-cutting concerns (thread safety, error handling, logging)
- Module dependencies graph
- Module interaction patterns

**When to read**: For understanding how code is organized and what each class is responsible for

### 3. dependencies.md (562 lines)
**Purpose**: External and internal dependency relationships

**Contents**:
- External dependencies (PyQt6, python-fints, standard library)
- Internal module dependencies
- Dependency characteristics and stability
- Dependency management and security
- Performance characteristics
- Dependency alternatives and evolution

**When to read**: For understanding what libraries the project uses and how they interact

### 4. entry-points.md (671 lines)
**Purpose**: Application initialization and execution flow

**Contents**:
- Primary entry point (main application startup)
- Initialization phases (Qt setup, UI construction, worker coordination)
- Secondary entry points (user-initiated methods)
- Thread entry points (worker thread execution)
- Initialization timing diagram
- Entry point security and error handling

**When to read**: For understanding how the application starts up and what happens during initialization

### 5. data-flow.md (846 lines)
**Purpose**: Data flow paths and state management

**Contents**:
- High-level data flow architecture
- Primary data flow paths (user input, banking operations, authentication, validation)
- Thread state management
- Cross-thread data transfer
- Error handling in data flows
- Performance characteristics
- Security aspects of data flow

**When to read**: For understanding how data moves through the system and how threads coordinate

## Architecture Highlights

### Event-Driven Threaded Architecture
The application implements a sophisticated two-thread architecture:
- **GUI Thread**: Handles all user interaction and display updates
- **Worker Thread**: Executes blocking network banking operations
- **Coordination**: Qt signals and threading events for thread-safe communication

### Key Design Patterns
1. **Worker Thread Pattern**: Background execution of blocking operations
2. **Signal-Slot Communication**: Thread-safe inter-thread communication
3. **Interactive Thread Coordination**: Background thread halts for user input
4. **Embedded Validation**: Real-time validation integrated into UI class

### Single-File Architecture
All functionality is contained within a single 689-line Python file, with clear separation of concerns achieved through class boundaries rather than file boundaries.

### Technology Stack
- **Language**: Python 3.14+
- **GUI Framework**: PyQt6 (Qt6 Python bindings)
- **Banking Protocol**: python-fints (FinTS/HBCI implementation)
- **Architecture Pattern**: Event-Driven Threaded Architecture

## Usage Guide

### For New Developers
1. Start with `overview.md` to understand the system architecture
2. Read `modules.md` to understand code organization
3. Study `entry-points.md` to understand initialization flow
4. Review `data-flow.md` to understand thread coordination

### For Architects
1. Review `overview.md` for design patterns and constraints
2. Study `dependencies.md` for technology choices and trade-offs
3. Analyze `data-flow.md` for thread safety and coordination patterns
4. Reference `entry-points.md` for initialization and lifecycle management

### For Maintainers
1. Quick reference: `overview.md` for architecture patterns
2. Dependency updates: `dependencies.md` for version management
3. Debugging flows: `entry-points.md` and `data-flow.md` for execution paths
4. Code changes: `modules.md` for class responsibilities

## Architecture Diagrams

Each document contains detailed ASCII diagrams illustrating:
- Thread architecture and communication
- Module dependencies and interactions
- Initialization sequences and timing
- Data flow paths and transformations
- State management and coordination

## Key Concepts

### Thread Safety
- All GUI operations happen in the main thread
- All network operations happen in the worker thread
- Qt signals provide thread-safe communication
- Threading events coordinate user interaction

### PhotoTAN Coordination
The most complex data flow involves photoTAN authentication:
1. Worker thread detects challenge from bank
2. Worker thread blocks on threading event
3. GUI thread displays dialog and collects input
4. GUI thread signals worker to continue
5. Worker thread submits TAN to bank

### Validation Strategy
- Real-time IBAN validation using MOD-97 algorithm
- Embedded in UI class for immediate feedback
- No network calls for validation (cost reduction)
- Mathematical certainty of IBAN validity

## Document Conventions

### Code References
Code references are provided as:
- **Line Numbers**: Specific locations in commerzbank_fints_qt_desktop_app.py
- **Method Names**: Specific methods within classes
- **File Paths**: Full paths to files (single file in this case)

### Diagram Conventions
- **Arrows (↓)**: Data flow or execution flow
- **Boxes**: Modules, components, or data structures
- **Dashed Lines**: Signal-slot connections
- **Bold Text**: Key components or concepts

### Performance Notes
Performance characteristics are marked as:
- **Estimated**: Theoretical estimates (not measured)
- **Measured**: Actual measured values
- **Variable**: Network-dependent or user-dependent

## Version Information

- **Version**: 1.0.0
- **Last Updated**: 2025-01-20
- **Architecture**: Event-Driven Threaded Architecture (Single-File Pattern)
- **Python Version**: 3.14+
- **Qt Version**: PyQt6 (6.x series)

## Related Documentation

### Project Documentation
- **Product Overview**: `.moai/project/product.md`
- **Technical Stack**: `.moai/project/tech.md`
- **Project Structure**: `.moai/project/structure.md`

### Design Documentation
- **Design Specification**: `.moai/design/spec.md`
- **System Architecture**: `.moai/design/system.md`
- **Research Notes**: `.moai/design/research.md`

### Code Documentation
- **Main Application**: `commerzbank_fints_qt_desktop_app.py` (689 lines)
- **Class Documentation**: Embedded docstrings in Python code

## Contribution Guidelines

When updating these documents:
1. Maintain consistency in formatting and structure
2. Update version information and date
3. Ensure code references remain accurate
4. Keep diagrams synchronized with text descriptions
5. Cross-reference related sections within and between documents

## License and Compliance

These documents describe architecture for a banking application that:
- Complies with German banking regulations (FinTS/HBCI protocol)
- Implements PSD2 Strong Customer Authentication (SCA)
- Uses SSL/TLS for all network communication
- Maintains no credential persistence (security by design)

---

**Generated**: 2025-01-20  
**Architecture Pattern**: Event-Driven Threaded Architecture  
**Project Type**: Desktop Banking Automation Application
