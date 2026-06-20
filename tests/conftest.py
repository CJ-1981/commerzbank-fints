"""
Test configuration and fixtures for Commerzbank FinTS application tests.

Provides mock objects, test data, and Qt6 application fixtures for comprehensive testing.
"""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QThread
import sys
import threading


# @MX:NOTE: [AUTO] Fixture factory pattern for test data generation
# @MX:REASON: Centralized test data management ensures consistency across test suite


@pytest.fixture
def app_instance():
    """
    Qt6 QApplication instance for GUI testing.

    Creates a singleton QApplication instance required for Qt widget testing.
    Uses QApplication.instance() to avoid multiple instantiation issues.
    """
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    # Cleanup handled by Qt garbage collection


@pytest.fixture
def main_window(app_instance):
    """
    Main application window fixture.

    Provides the CommerzbankFinTSApp instance for GUI testing.
    Imports the actual application class to test real functionality.
    """
    # Import here to avoid import side effects
    from commerzbank_fints_qt_desktop_app import CommerzbankFinTSApp

    window = CommerzbankFinTSApp()
    yield window
    # Cleanup
    window.close()


@pytest.fixture
def valid_iban_data():
    """
    Valid IBAN test data for comprehensive validation testing.

    Provides various valid IBAN formats including:
    - German IBANs (DE) with different banks
    - Valid checksums verified by MOD-97 algorithm
    """
    return {
        "german_valid": [
            "DE89370400440532013000",  # Commerzbank
            "DE12370400440001111111",  # Test IBAN from app
            "DE56370400440002222222",  # Test IBAN from app
            "DE78370400440003333333",  # Test IBAN from app
            "DE75512108001234567890",  # Another German bank
        ],
        "checksum_validated": [
            "DE89370400440532013000",  # Known valid checksum
            "DE12500105170648489890",  # Deutsche Bank valid
        ]
    }


@pytest.fixture
def invalid_iban_data():
    """
    Invalid IBAN test data for error case testing.

    Provides various invalid IBAN formats:
    - Wrong checksums
    - Invalid lengths
    - Invalid characters
    - Empty/short strings
    """
    return {
        "wrong_checksum": [
            "DE89370400440532013001",  # Last digit changed (invalid checksum)
            "DE12370400440001111112",  # Invalid checksum
        ],
        "invalid_length": [
            "DE123",  # Too short
            "DE12345678901234",  # Still too short (needs 22 chars for DE)
            "",  # Empty string
            "   ",  # Whitespace only
        ],
        "invalid_characters": [
            "DE89@370400440532013000",  # Invalid character @
            "DE89 3704 0044 0532 01300!",  # Special characters
            "DE89-3704-0044-0532-013000",  # Hyphens (spaces ok, hyphens not)
            "1234567890123456789012",  # No country code
        ],
        "malformed": [
            None,  # None value
            "DE",  # Country code only
            "XXXXXXXXXXXXXXXXXXXXXXXX",  # All Xs
        ]
    }


@pytest.fixture
def payout_test_data():
    """
    Payout test data for table operations and batch calculations.

    Provides realistic payout data in various formats:
    - Dictionary format for internal processing
    - Tab-separated format for clipboard import
    - Edge cases for validation testing
    """
    return {
        "valid_payouts": [
            {
                "name": "Max Mustermann",
                "iban": "DE89370400440532013000",
                "amount": "350.00",
                "reference": "Refund Invoice 10934"
            },
            {
                "name": "Acme Components GmbH",
                "iban": "DE56370400440002222222",
                "amount": "1280.50",
                "reference": "Supplies Batch 81A"
            },
            {
                "name": "Web Hosting Services Ltd",
                "iban": "DE78370400440003333333",
                "amount": "49.99",
                "reference": "SaaS Cloud Base"
            }
        ],
        "clipboard_tab_separated": """Max Mustermann\tDE89370400440532013000\t350.00\tRefund Invoice 10934
Acme Components GmbH\tDE56370400440002222222\t1280,50\tSupplies Batch 81A
Web Hosting Services Ltd\tDE78370400440003333333\t49.99\tSaaS Cloud Base""",
        "edge_cases": [
            {
                "name": "",  # Empty name
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test"
            },
            {
                "name": "Test User",
                "iban": "",  # Empty IBAN
                "amount": "100.00",
                "reference": "Test"
            },
            {
                "name": "Test User",
                "iban": "DE89370400440532013000",
                "amount": "",  # Empty amount
                "reference": "Test"
            },
            {
                "name": "Test User",
                "iban": "DE89370400440532013000",
                "amount": "invalid",  # Invalid amount
                "reference": "Test"
            },
            {
                "name": "Test User",
                "iban": "DE89370400440532013000",
                "amount": "0.00",  # Zero amount
                "reference": "Test"
            }
        ]
    }


@pytest.fixture
def mock_fints_client():
    """
    Mock FinTS client for testing without real banking operations.

    Prevents actual banking calls during testing while providing
    realistic API responses for success and failure cases.
    """
    mock_client = MagicMock()

    # Mock successful account retrieval
    mock_account = MagicMock()
    mock_account.iban = "DE89370400440532013000"
    mock_client.get_sepa_accounts.return_value = [mock_account]

    # Mock successful transfer responses
    mock_response = MagicMock()
    mock_response.challenge = "Please confirm in your photoTAN app"
    mock_response.decoupled = False
    mock_client.sepa_transfer_multiple.return_value = mock_response
    mock_client.simple_sepa_transfer.return_value = mock_response

    # Mock TAN submission
    mock_client.send_tan.return_value = True  # Success after TAN

    return mock_client


@pytest.fixture
def mock_fints_worker():
    """
    Mock FinTSWorker for thread coordination testing.

    Provides controlled worker behavior for testing thread
    synchronization, signal emission, and error handling.
    """
    from unittest.mock import Mock
    from PyQt6.QtCore import QObject, pyqtSignal

    # Create a mock worker with signal tracking
    worker = Mock()
    worker.log_signal = pyqtSignal(str, str)
    worker.request_tan_signal = pyqtSignal(str, bool)
    worker.finished_signal = pyqtSignal(bool, str)

    # Track signal emissions
    worker.log_calls = []
    worker.tan_requests = []
    worker.finished_calls = []

    def mock_log(message, color):
        worker.log_calls.append((message, color))

    def mock_request_tan(challenge, is_decoupled):
        worker.tan_requests.append((challenge, is_decoupled))

    def mock_finished(success, message):
        worker.finished_calls.append((success, message))

    # Connect mock functions
    worker.log_signal.connect(mock_log)
    worker.request_tan_signal.connect(mock_request_tan)
    worker.finished_signal.connect(mock_finished)

    return worker


@pytest.fixture
def thread_coordinator():
    """
    Thread coordination fixture for testing multi-threaded interactions.

    Provides synchronization primitives for testing thread-safe operations
    between GUI thread and FinTSWorker background thread.
    """
    coordinator = {
        'events': {},
        'locks': {},
        'timeouts': {}
    }

    def create_event(name):
        coordinator['events'][name] = threading.Event()
        return coordinator['events'][name]

    def create_lock(name):
        coordinator['locks'][name] = threading.Lock()
        return coordinator['locks'][name]

    def wait_for_event(event_name, timeout=5.0):
        """Wait for a thread event with timeout."""
        if event_name not in coordinator['events']:
            return False
        return coordinator['events'][event_name].wait(timeout=timeout)

    def set_event(event_name):
        """Set a thread event."""
        if event_name in coordinator['events']:
            coordinator['events'][event_name].set()

    coordinator['create_event'] = create_event
    coordinator['create_lock'] = create_lock
    coordinator['wait'] = wait_for_event
    coordinator['set'] = set_event

    return coordinator


@pytest.fixture
def decimal_test_cases():
    """
    Decimal precision test cases for financial calculations.

    Tests edge cases in Decimal arithmetic:
    - Rounding behavior
    - Precision preservation
    - Currency formatting
    - Large amounts
    """
    return {
        "precision_cases": [
            ("0.01", Decimal("0.01")),
            ("0.001", Decimal("0.001")),  # Sub-cent precision
            ("1000.999", Decimal("1000.999")),
            ("999999.99", Decimal("999999.99")),  # Large amount
        ],
        "formatting_cases": [
            (Decimal("1000.00"), "1,000.00"),
            (Decimal("1234567.89"), "1,234,567.89"),
            (Decimal("0.01"), "0.01"),
            (Decimal("1000000.00"), "1,000,000.00"),
        ],
        "calculation_cases": [
            ([Decimal("100.00"), Decimal("200.00"), Decimal("50.00")], Decimal("350.00")),
            ([Decimal("0.01"), Decimal("0.02"), Decimal("0.03")], Decimal("0.06")),
            ([Decimal("1000.00"), Decimal("2000.00")], Decimal("3000.00")),
        ],
        "edge_cases": [
            ("0.00", Decimal("0.00")),  # Zero amount
            ("-100.00", Decimal("-100.00")),  # Negative amount
            ("invalid", None),  # Invalid input
            ("", None),  # Empty input
        ]
    }


@pytest.fixture
def clipboard_test_data():
    """
    Clipboard test data for import functionality testing.

    Provides various clipboard content formats:
    - Valid tab-separated data
    - Malformed data
    - Empty content
    - Different delimiters
    """
    return {
        "valid_tab_separated": """Name1\tDE89370400440532013000\t100.00\tReference1
Name2\tDE56370400440002222222\t200,50\tReference2
Name3\tDE78370400440003333333\t300.00\tReference3""",
        "missing_columns": """Name1\tDE89370400440532013000\t100.00
Name2\tDE56370400440002222222\t200,50""",
        "extra_columns": """Name1\tDE89370400440532013000\t100.00\tReference1\tExtraColumn
Name2\tDE56370400440002222222\t200,50\tReference2\tExtraColumn2""",
        "empty_lines": """Name1\tDE89370400440532013000\t100.00\tReference1

Name2\tDE56370400440002222222\t200,50\tReference2

""",
        "comma_decimals": """Name1\tDE89370400440532013000\t100,50\tReference1
Name2\tDE56370400440002222222\t200,00\tReference2""",
        "empty": "",
        "whitespace_only": "   \n   \n   ",
        "single_row": "Name1\tDE89370400440532013000\t100.00\tReference1"
    }


@pytest.fixture
def error_test_scenarios():
    """
    Error scenario test data for exception handling validation.

    Provides comprehensive error cases:
    - Network failures
    - Authentication errors
    - Invalid input scenarios
    - Thread coordination failures
    """
    return {
        "network_errors": [
            "Connection timeout",
            "Network unreachable",
            "SSL handshake failed",
            "DNS resolution failed",
        ],
        "auth_errors": [
            "Invalid PIN",
            "Account locked",
            "Authentication failed",
            "Session expired",
        ],
        "validation_errors": [
            "Invalid IBAN format",
            "Insufficient funds",
            "Recipient account not found",
            "Amount exceeds daily limit",
        ],
        "thread_errors": [
            "Worker thread crashed",
            "TAN event timeout",
            "Signal slot disconnected",
            "Worker already running",
        ]
    }


# @MX:ANCHOR: [AUTO] Test fixture factory - centralized test data management
# @MX:REASON: High fan_in (15+ test files use these fixtures) ensures consistency and reduces duplication


@pytest.fixture
def fints_not_available():
    """
    Mock FinTS library unavailable scenario.

    Tests application behavior when fints library is not installed.
    """
    with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', False):
        yield


@pytest.fixture
def mock_tan_challenge():
    """
    Mock photoTAN challenge response for testing TAN flow.

    Simulates the NeedTANResponse object from the FinTS library
    for testing user interaction scenarios.
    """
    from fints.dialog import NeedTANResponse

    # Create a mock NeedTANResponse
    mock_response = MagicMock(spec=NeedTANResponse)
    mock_response.challenge = "Please confirm in your photoTAN app"
    mock_response.decoupled = False
    mock_response.tan_media = "photoTAN"

    return mock_response


@pytest.fixture
def test_timeouts():
    """
    Timeout configurations for different test scenarios.

    Provides appropriate timeout values for:
    - Thread synchronization
    - Network operations
    - GUI event processing
    """
    return {
        "thread_sync": 5.0,  # Thread coordination timeout
        "network": 10.0,  # Network operation timeout
        "gui_event": 2.0,  # GUI event processing timeout
        "tan_response": 30.0,  # TAN user input timeout
    }


@pytest.fixture
def signal_tracker():
    """
    Signal emission tracker for testing Qt signals.

    Provides a mechanism to track and verify Qt signal emissions
    during testing of thread coordination and GUI events.
    """
    tracker = {
        'signals': {},
        'count': {}
    }

    def track(signal_name, *args):
        if signal_name not in tracker['signals']:
            tracker['signals'][signal_name] = []
            tracker['count'][signal_name] = 0
        tracker['signals'][signal_name].append(args)
        tracker['count'][signal_name] += 1

    def get_count(signal_name):
        return tracker['count'].get(signal_name, 0)

    def get_calls(signal_name):
        return tracker['signals'].get(signal_name, [])

    def reset():
        tracker['signals'] = {}
        tracker['count'] = {}

    tracker['track'] = track
    tracker['get_count'] = get_count
    tracker['get_calls'] = get_calls
    tracker['reset'] = reset

    return tracker
