# Dependency Architecture - Commerzbank FinTS Payout Automator

## Dependency Overview

The Commerzbank FinTS Payout Automator follows a **layered dependency model** with clear separation between external libraries, internal modules, and system dependencies. The architecture emphasizes minimal external dependencies while maintaining comprehensive banking protocol support.

### Dependency Hierarchy

```
Application Layer (CommerzbankFinTSApp)
    ↓ depends on
Integration Layer (FinTSWorker)
    ↓ depends on  
Protocol Layer (python-fints)
    ↓ depends on
System Layer (Python Standard Library, Qt6, Network)
```

## External Dependencies

### Runtime Dependencies

#### 1. PyQt6 (Qt6 Python Bindings)

**Package**: `PyQt6`  
**Version**: Latest stable (6.x series)  
**Purpose**: Cross-platform GUI framework with threading support  
**Installation**: `pip install PyQt6`

**Key Components Used**:
```python
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup,
    QPlainTextEdit, QInputDialog, QMessageBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
```

**Dependency Usage**:
- **GUI Components**: QMainWindow, QWidget, QTableWidget for interface
- **Threading**: QThread for background worker, pyqtSignal/pyqtSlot for communication
- **Styling**: QColor, QPalette for dark theme implementation
- **Event Handling**: Qt signals and slots for thread-safe communication

**Architecture Impact**:
- Enables event-driven threaded architecture
- Provides signal-slot mechanism for thread safety
- Supports responsive UI during blocking operations
- Cross-platform deployment (Windows, macOS, Linux)

**Critical Features**:
- **Thread-Safe Signals**: Automatic queuing of cross-thread communication
- **Event Loop**: Non-blocking UI operations during network calls
- **Rich Widget Set**: Table widgets, input dialogs, message boxes
- **CSS Styling**: Modern UI design with QSS (Qt Style Sheets)

---

#### 2. python-fints (FinTS/HBCI Banking Protocol)

**Package**: `fints`  
**Version**: Latest stable (maintained for German banking compatibility)  
**Purpose**: Open-source German banking protocol implementation  
**Installation**: `pip install fints`

**Key Components Used**:
```python
from fints.client import FinTS3PinTanClient
from fints.models import SEPATransferOrder
from fints.exceptions import FinTSClientPINError, FinTSClientError
from fints.dialog import NeedTANResponse
```

**Dependency Usage**:
- **FinTS3PinTanClient**: Main client for PIN/TAN authentication
- **SEPATransferOrder**: SEPA message formatting for transfers
- **FinTS Exceptions**: Specialized error handling for banking operations
- **NeedTANResponse**: PhotoTAN challenge detection and handling

**Architecture Impact**:
- **Protocol Layer**: Abstracts FinTS/HBCI protocol complexity
- **Network Management**: SSL/TLS connections to banking servers
- **Message Formatting**: SEPA credit transfer standard compliance
- **Authentication**: PhotoTAN challenge-response coordination

**Critical Features**:
- **SSL/TLS**: Secure communication with banking servers
- **SEPA Support**: Full SEPA credit transfer implementation
- **PhotoTAN**: Modern authentication method support
- **Error Handling**: Specialized exceptions for banking failures

**Banking Server Integration**:
```python
client = FinTS3PinTanClient(
    bank_identifier=self.blz,                    # German bank code
    user_id=self.user_id,                        # Online banking ID
    pin=self.pin,                                # User PIN
    server="https://fints.commerzbank.de/fints", # Commerzbank endpoint
    product_id="9A5B7C218E1D5FA0B0"             # FinTS client identification
)
```

---

### Standard Library Dependencies

#### 3. Threading Module

**Module**: `threading`  
**Purpose**: Thread-safe event coordination for photoTAN challenges

**Usage**:
```python
import threading

class FinTSWorker(QThread):
    def __init__(self):
        self.tan_event = threading.Event()  # Coordination primitive
        self.submitted_tan = ""
        self.is_cancelled = False
    
    def handle_tan_challenge_loop(self, client, response):
        while isinstance(res, NeedTANResponse):
            self.tan_event.clear()           # Reset coordination state
            self.request_tan_signal.emit()    # Request GUI interaction
            self.tan_event.wait()            # Block for user input
            # Process user response
```

**Architecture Role**:
- **Cross-Thread Coordination**: Safe blocking mechanism for user interaction
- **Event Synchronization**: Background thread waits for GUI thread input
- **Cancellation Support**: Clean shutdown during user cancellation

**Thread Safety**:
- `threading.Event` is a thread-safe synchronization primitive
- Provides explicit `set()` and `wait()` methods for coordination
- No manual locking required, avoiding deadlock risks

---

#### 4. Decimal Module

**Module**: `decimal`  
**Purpose**: Precise financial calculations for amounts and totals

**Usage**:
```python
from decimal import Decimal, InvalidOperation

# SEPA transfer order creation
SEPATransferOrder(
    recipient_name=p["name"],
    recipient_iban=p["iban"],
    amount=Decimal(p["amount"]),  # Precise decimal conversion
    reason=p["reference"]
)

# Batch totals calculation
total_sum = Decimal("0.00")
for row in range(row_count):
    val = Decimal(amount_item.text().strip() or "0")
    total_sum += val
```

**Architecture Role**:
- **Financial Precision**: Avoids floating-point rounding errors
- **SEPA Compliance**: Precise decimal representation for banking transfers
- **Validation**: Exact decimal parsing for amount validation

**Critical for Banking**:
- SEPA transfers require exact decimal amounts
- Floating-point arithmetic introduces rounding errors
- `Decimal` provides mathematical exactness for financial calculations

---

#### 5. Logging Module

**Module**: `logging`  
**Purpose**: Standard Python logging infrastructure  
**Current Usage**: Imported but primarily using custom terminal logging

**Potential Enhancement**:
```python
import logging

# Future integration for file-based logging
logging.basicConfig(
    filename='commerzbank_fints.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

#### 6. System Module

**Module**: `sys`  
**Purpose**: Application lifecycle management and exit handling

**Usage**:
```python
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommerzbankFinTSApp()
    window.show()
    sys.exit(app.exec())  # Clean Qt application exit
```

---

## Internal Module Dependencies

### Class-Level Dependency Graph

```
CommerzbankFinTSApp (GUI Thread)
    │
    ├── Creates Instance ──► FinTSWorker (Background Thread)
    │                           │
    │                           ├── Uses ──► threading.Event
    │                           ├── Uses ──► decimal.Decimal
    │                           └── Depends On ──► python-fints
    │                                               │
    │                                               └── Network Calls ──► Commerzbank Server
    │
    └── Uses ──► PyQt6 Components
                    │
                    ├── QWidget, QMainWindow (UI Structure)
                    ├── QTableWidget (Data Display)
                    ├── QThread (Worker Threading)
                    ├── pyqtSignal/pyqtSlot (Communication)
                    └── QColor, QFont (Styling)
```

### Method-Level Dependencies

#### CommerzbankFinTSApp Method Dependencies

```python
# UI Construction (depends on PyQt6)
def init_ui(self):
    # Depends on: QWidget, QVBoxLayout, QTableWidget, etc.
    
# Validation (depends on standard library)
def validate_iban_mod97(self, iban):
    # Depends on: string operations, int conversion
    # Independent of Qt or FinTS libraries

# Table Management (depends on PyQt6)
def update_batch_calculations(self):
    # Depends on: QTableWidget, Decimal
    # Calls: validate_iban_mod97()

# Worker Coordination (depends on PyQt6 and custom class)
def start_batch_execution(self):
    # Depends on: FinTSWorker, PyQt6 signals
    # Creates: FinTSWorker instance
    # Connects: Signal-slot connections
```

#### FinTSWorker Method Dependencies

```python
# Main Entry Point (depends on python-fints)
def run(self):
    # Depends on: FinTS3PinTanClient, fints exceptions
    # Creates: FinTS client instance
    # Calls: process_collective_transfer() or process_individual_transfers()

# Collective Transfer (depends on python-fints)
def process_collective_transfer(self, client, debtor_acc):
    # Depends on: SEPATransferOrder, Decimal
    # Calls: client.sepa_transfer_multiple()
    # Uses: handle_tan_challenge_loop()

# PhotoTAN Coordination (cross-thread dependency)
def handle_tan_challenge_loop(self, client, response):
    # Depends on: threading.Event, NeedTANResponse
    # Coordinates: GUI thread via signals
    # Uses: client.send_tan()
```

---

## Dependency Characteristics

### Dependency Types

**Build-Time Dependencies**:
- None (single-file Python script)

**Runtime Dependencies**:
- PyQt6 (GUI framework)
- python-fints (banking protocol)
- Python standard library (threading, decimal, sys, logging)

**Development Dependencies** (Future):
- pytest (testing framework)
- ruff (code quality tool)
- mypy (type checking)

### Dependency Stability

**Stable Dependencies**:
- **Python Standard Library**: Extremely stable, backward compatible
- **PyQt6**: Mature framework, stable API
- **decimal module**: Core Python feature, mathematical exactness guaranteed

**External Dependency Risks**:
- **python-fints**: Active development, potential API changes
  - **Mitigation**: Version pinning in requirements.txt
  - **Monitoring**: Track library updates for breaking changes
- **Commerzbank FinTS Server**: External service dependency
  - **Mitigation**: Error handling for network failures
  - **Monitoring**: Track bank maintenance windows

---

## Dependency Management

### Installation Requirements

**Minimum Installation**:
```bash
# Python 3.14+ required
pip install PyQt6 fints
```

**Recommended Installation** (Future):
```bash
# Virtual environment setup
python3.14 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Dependency installation
pip install PyQt6 fints

# Development dependencies (future)
pip install pytest ruff mypy
```

### Dependency Versioning

**Current Strategy**: Latest stable versions
```bash
# No version constraints currently applied
pip install PyQt6 fints
```

**Recommended Strategy** (Production):
```bash
# Pin specific versions for stability
pip install PyQt6==6.7.0 fints==2.3

# Use requirements.txt for reproducibility
echo "PyQt6==6.7.0" > requirements.txt
echo "fints==2.3" >> requirements.txt
```

### Dependency Updates

**Update Policy**:
- **PyQt6**: Update for major bug fixes and security patches
- **python-fints**: Monitor for banking protocol changes and API updates
- **Python**: Track LTS releases and compatibility

**Testing Before Updates**:
1. Install updated dependency in virtual environment
2. Run application with test data (mock banking operations)
3. Verify all functionality: UI, validation, worker coordination
4. Test with actual Commerzbank sandbox environment

---

## Dependency Alternatives

### GUI Framework Alternatives

**Considered and Rejected**:
- **Tkinter**: Too limited for modern UI design, poor threading support
- **PySide6**: Alternative Qt6 binding, chose PyQt6 for maturity
- **Kivy**: Cross-platform focus not aligned with desktop-first design
- **wxPython**: Less mature than Qt6, smaller community

**PyQt6 Advantages**:
- Most mature Python Qt binding
- Excellent documentation and community support
- Proven track record in financial applications
- Superior threading support for background operations

### Banking Protocol Alternatives**

**Considered and Rejected**:
- **Direct FinTS Implementation**: Too complex, maintenance burden
- **Commercial Banking APIs**: Cost prohibitive, vendor lock-in
- **Web Scraping**: Fragile, violates terms of service, security risks

**python-fints Advantages**:
- Open-source and actively maintained
- Comprehensive German bank support
- Strong community for German banking protocols
- Regular updates for banking standard changes

---

## Dependency Security

### Security Considerations

**PyQt6 Security**:
- **Trust**:成熟 framework, 良好的安全记录
- **Updates**: 定期安全补丁
- **Network**: No direct network operations (security boundary clear)

**python-fints Security**:
- **Trust**: 活跃维护, 开源透明
- **Network**: SSL/TLS 加密通信
- **Credentials**: 无凭证存储, 传输加密
- **Compliance**: 符合德国银行安全标准

**Credential Security**:
- **No Persistence**: 用户凭证从不存储
- **Session-Only**: 凭证仅在会话期间有效
- **User Control**: 用户控制会话边界
- **Encryption**: SSL/TLS 加密所有 FinTS 通信

### Dependency Vulnerabilities

**Monitoring Strategy**:
- **PyQt6**: 追踪 Qt 安全公告
- **python-fints**: 监控 GitHub issues 和更新
- **Python**: 追踪 CPython 安全公告

**Response Process**:
1. 评估漏洞影响范围
2. 检查是否有可用的补丁版本
3. 在虚拟环境中测试更新
4. 部署更新并重新测试功能

---

## Dependency Performance

### PyQt6 Performance Characteristics

**Memory Usage**:
- **Base Overhead**: Qt 框架内存占用
- **Widget Memory**: 表格和输入组件内存
- **Event Loop**: 最小线程内存占用

**CPU Usage**:
- **Idle State**: 最小 CPU 使用（等待用户输入）
- **Worker Active**: 后台线程使用（网络操作）
- **UI Updates**: 事件驱动, 高效渲染

### python-fints Performance Characteristics

**Network Operations**:
- **Connection Setup**: SSL/TLS 握开销（一次性）
- **API Calls**: 每个操作的往返延迟
- **SEPA Transfers**: 取决于批量大小和网络条件

**Memory Usage**:
- **Client State**: FinTS 会话状态（小内存占用）
- **Message Buffers**: SEPA 消息格式化（临时分配）
- **Response Parsing**: FinTS 消息解析（临时分配）

---

## Dependency Evolution

### Current Dependency State

**Version Policy**: 使用最新稳定版本
**Update Frequency**: 按需更新（安全补丁, 主要版本）
**Testing**: 手动测试功能完整性

### Future Dependency Enhancements

**Planned Additions**:
- **pytest**: 单元测试框架
- **ruff**: 代码质量工具
- **mypy**: 类型检查工具
- **PyInstaller**: 独立可执行文件打包

**Potential Replacements**:
- **python-fints**: 监控替代方案（如果维护停止）
- **PyQt6**: 考虑 PySide6（如果许可证变更）

### Dependency Modernization

**Short-Term (6 months)**:
- 添加版本固定到 requirements.txt
- 实施自动化测试（pytest）
- 添加依赖安全扫描

**Medium-Term (12 months)**:
- 考虑 PyInstaller 用于独立分发
- 添加依赖更新监控
- 实施持续集成（CI）用于依赖兼容性测试

**Long-Term (24+ months)**:
- 评估模块化架构（影响依赖结构）
- 考虑插件系统（动态依赖加载）
- 监控 Python 版本演进和兼容性

---

## Dependency Compliance

### Banking Compliance

**python-fints Compliance**:
- **FinTS/HBCI Protocol**: 完整的德国银行协议实现
- **SEPA Standards**: 符合 SEPA 信用转账要求
- **PSD2 Regulation**: 强客户认证（SCA）支持
- **Data Protection**: 符合德国数据保护法规

### Open Source Licensing

**PyQt6 License**:
- **GPL v3**: 要求应用程序开源（如果静态链接）
- **Commercial License**: 专有软件的替代方案
- **Current Usage**: 直接 Python 执行（GPL 合规）

**python-fints License**:
- **MIT License**: 宽松的开源许可
- **Permissive**: 可以用于专有软件
- **No Restrictions**: 无商业使用限制

### Third-Party Dependencies

**Indirect Dependencies**:
- **PyQt6**: 依赖 Qt6 C++ 框架
- **python-fints**: 可能依赖额外的 Python 库
  - **mt-940**: MT-940 银行语句解析
  - **sepaxml**: SEPA XML 消息生成

**Transitive Dependency Management**:
```bash
# 检查完整依赖树
pip show PyQt6
pip show fints

# 查看间接依赖
pip list
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Dependency Strategy**: 最小外部依赖, 最大标准库使用
