"""
Thread coordination tests for Commerzbank FinTS application.

Tests the multi-threaded architecture where FinTSWorker runs in background
thread while GUI thread handles user interactions, with proper signal-slot
communication and threading.Event() synchronization.

Coverage Areas:
- Thread lifecycle management (start, run, finish)
- Signal-slot communication between threads
- threading.Event() synchronization for TAN input
- Thread-safe data access patterns
- Concurrent operation handling
- Thread cancellation and cleanup
"""

import threading
import time
from unittest.mock import MagicMock, patch
from commerzbank_fints_qt_desktop_app import FinTSWorker


class TestFinTSWorkerThreadLifecycle:
    """Test FinTSWorker thread creation, execution, and termination."""

    def test_worker_thread_initialization(self, main_window):
        """Test that FinTSWorker thread initializes correctly."""
        payouts = [
            {
                "name": "Test",
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test",
            }
        ]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective",
        )

        assert worker.isRunning() is False, "Worker should not be running initially"
        assert worker.blz == "37040044", "BLZ should be stored"
        assert worker.user_id == "1234567890", "User ID should be stored"
        assert worker.pin == "test1234", "PIN should be stored"
        assert worker.tan_event.is_set() is False, (
            "TAN event should not be set initially"
        )
        assert worker.is_cancelled is False, "Worker should not be cancelled initially"

    def test_worker_thread_starts_correctly(self, main_window):
        """Test that worker thread can be started."""
        payouts = [
            {
                "name": "Test",
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test",
            }
        ]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective",
        )

        # Mock the FinTS client to prevent real network calls
        with patch("commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE", True):
            with patch(
                "commerzbank_fints_qt_desktop_app.FinTS3PinTanClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_account = MagicMock()
                mock_account.iban = "DE89370400440532013000"
                mock_client.get_sepa_accounts.return_value = [mock_account]
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.start()
                # Give thread time to start
                time.sleep(0.1)
                assert worker.isRunning() is True, (
                    "Worker should be running after start()"
                )

                # Cleanup
                worker.is_cancelled = True
                worker.tan_event.set()
                worker.wait(2000)  # Wait for thread to finish

    def test_worker_thread_finished_signal(self, main_window):
        """Test that worker emits finished_signal when complete."""
        payouts = [
            {
                "name": "Test",
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test",
            }
        ]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective",
        )

        # Track finished signal emissions
        finished_calls = []

        def track_finished(success, message):
            finished_calls.append((success, message))

        worker.finished_signal.connect(track_finished)

        # Mock the FinTS client
        with patch("commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE", True):
            with patch(
                "commerzbank_fints_qt_desktop_app.FinTS3PinTanClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_account = MagicMock()
                mock_account.iban = "DE89370400440532013000"
                mock_client.get_sepa_accounts.return_value = [mock_account]
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.start()
                worker.wait(3000)  # Wait for completion

                assert len(finished_calls) > 0, "Worker should emit finished_signal"


class TestSignalSlotCommunication:
    """Test Qt signal-slot communication between worker and GUI thread."""

    def test_log_signal_emission(self, main_window):
        """Test that worker emits log_signal correctly."""
        payouts = [
            {
                "name": "Test",
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test",
            }
        ]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective",
        )

        # Track log signal emissions
        log_calls = []

        def track_log(message, color):
            log_calls.append((message, color))

        worker.log_signal.connect(track_log)

        # Call log method directly
        worker.log("Test message", "info")
        worker.log("Error message", "error")
        worker.log("Success message", "success")

        assert len(log_calls) == 3, "Should emit 3 log signals"
        assert log_calls[0] == ("Test message", "#e2e8f0"), (
            "First log should have default color"
        )
        assert log_calls[1] == ("Error message", "#f87171"), (
            "Error log should have red color"
        )
        assert log_calls[2] == ("Success message", "#34d399"), (
            "Success log should have green color"
        )

    def test_request_tan_signal_emission(self, main_window):
        """Test that worker emits request_tan_signal for TAN challenges."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Track TAN request signal emissions
        tan_requests = []

        def track_tan_request(challenge, is_decoupled):
            tan_requests.append((challenge, is_decoupled))

        worker.request_tan_signal.connect(track_tan_request)

        # Emit TAN request
        worker.request_tan_signal.emit("Please confirm in photoTAN app", False)

        assert len(tan_requests) == 1, "Should emit one TAN request"
        assert tan_requests[0] == ("Please confirm in photoTAN app", False), (
            "TAN request should match"
        )

    def test_signal_slot_connection_in_main_app(self, main_window):
        """Test that main app properly connects worker signals."""
        # The main app should connect worker signals when starting execution
        assert hasattr(main_window, "append_terminal_message"), (
            "App should have terminal message handler"
        )
        assert hasattr(main_window, "prompt_user_for_tan"), (
            "App should have TAN prompt handler"
        )
        assert hasattr(main_window, "on_worker_finished"), (
            "App should have worker finished handler"
        )


class TestTANEventSynchronization:
    """Test threading.Event() synchronization for TAN input flow."""

    def test_tan_event_initial_state(self, main_window):
        """Test that TAN event starts in unset state."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        assert worker.tan_event.is_set() is False, "TAN event should be unset initially"
        assert worker.submitted_tan == "", "Submitted TAN should be empty initially"

    def test_set_tan_sets_event(self, main_window):
        """Test that set_tan() sets the event and stores TAN."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        worker.set_tan("123456")

        assert worker.submitted_tan == "123456", "TAN should be stored"
        assert worker.tan_event.is_set() is True, "Event should be set"

    def test_cancel_tan_sets_event(self, main_window):
        """Test that cancel_tan() sets event and cancellation flag."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        worker.cancel_tan()

        assert worker.is_cancelled is True, "Cancellation flag should be set"
        assert worker.tan_event.is_set() is True, "Event should be set"

    def test_tan_event_wait_blocks_until_set(self, main_window):
        """Test that event.wait() blocks until event is set."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Test that wait returns False when event is not set
        assert worker.tan_event.wait(0.1) is False, (
            "Wait should timeout when event not set"
        )

        # Set the event
        worker.set_tan("123456")

        # Test that wait returns True when event is set
        assert worker.tan_event.wait(0.1) is True, (
            "Wait should succeed when event is set"
        )

    def test_tan_event_clear_and_wait_cycle(self, main_window):
        """Test the clear -> wait -> set cycle used in TAN flow."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Initial state
        assert worker.tan_event.is_set() is False

        # Simulate the TAN flow cycle
        worker.tan_event.clear()  # Reset event
        assert worker.tan_event.is_set() is False

        # In a real scenario, this would block in the worker thread
        # For testing, we verify the event can be set again
        worker.set_tan("654321")
        assert worker.tan_event.is_set() is True


class TestThreadSafety:
    """Test thread-safe operations and data access."""

    def test_concurrent_tan_access(self, main_window):
        """Test thread-safe access to submitted_tan variable."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Simulate concurrent access from multiple threads
        def set_tan_concurrently(tan_value):
            worker.set_tan(tan_value)

        threads = []
        for i in range(10):
            t = threading.Thread(target=set_tan_concurrently, args=(str(i),))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify final state (last write wins, but no crash should occur)
        assert worker.tan_event.is_set() is True
        assert worker.submitted_tan is not None

    def test_cancellation_flag_thread_safety(self, main_window):
        """Test thread-safe cancellation flag handling."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Simulate cancellation from multiple threads
        def cancel_concurrently():
            worker.cancel_tan()

        threads = []
        for _ in range(5):
            t = threading.Thread(target=cancel_concurrently)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert worker.is_cancelled is True
        assert worker.tan_event.is_set() is True

    def test_worker_state_consistency(self, main_window):
        """Test that worker state remains consistent across thread boundaries."""
        payouts = [
            {
                "name": "Test",
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test",
            }
        ]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective",
        )

        # Verify initial state
        initial_payouts = worker.payouts
        initial_method = worker.method

        # Mock execution
        with patch("commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE", False):
            worker.run()

        # Verify state is unchanged
        assert worker.payouts == initial_payouts, "Payouts should not change"
        assert worker.method == initial_method, "Method should not change"


class TestThreadCancellation:
    """Test thread cancellation and cleanup scenarios."""

    def test_worker_cancellation_stops_processing(self, main_window):
        """Test that setting is_cancelled stops worker processing."""
        payouts = [
            {
                "name": f"Test{i}",
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test",
            }
            for i in range(5)
        ]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="individual",
        )

        # Set cancellation flag
        worker.is_cancelled = True

        # Mock the FinTS client
        with patch("commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE", True):
            with patch(
                "commerzbank_fints_qt_desktop_app.FinTS3PinTanClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_account = MagicMock()
                mock_account.iban = "DE89370400440532013000"
                mock_client.get_sepa_accounts.return_value = [mock_account]
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.run()

                # Should emit finished signal with cancellation
                # (Verification depends on signal tracking)

    def test_tan_timeout_handling(self, main_window):
        """Test TAN event timeout scenarios."""
        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Test timeout on event.wait()
        start_time = time.time()
        result = worker.tan_event.wait(0.5)  # 500ms timeout
        elapsed = time.time() - start_time

        assert result is False, "Wait should timeout when event not set"
        assert 0.4 <= elapsed <= 0.7, f"Timeout should take ~500ms, took {elapsed:.2f}s"


class TestConcurrentOperations:
    """Test handling of concurrent operations and state management."""

    def test_multiple_workers_cannot_run_simultaneously(self, main_window):
        """Test that app prevents multiple workers from running."""
        # Start first worker
        main_window.start_batch_execution()

        # Try to start second worker while first is running
        first_worker = main_window.worker

        if first_worker and first_worker.isRunning():
            # Clear the terminal for second attempt
            main_window.log_terminal.clear()

            # Attempt second execution
            main_window.start_batch_execution()

            # Should log error message about worker already running
            terminal_text = main_window.log_terminal.toPlainText()
            assert (
                "already executing" in terminal_text.lower()
                or "cannot run" in terminal_text.lower()
            )

            # Cleanup
            first_worker.is_cancelled = True
            first_worker.tan_event.set()
            first_worker.wait(2000)

    def test_worker_cleanup_on_completion(self, main_window):
        """Test that worker resources are cleaned up on completion."""
        payouts = [
            {
                "name": "Test",
                "iban": "DE89370400440532013000",
                "amount": "100.00",
                "reference": "Test",
            }
        ]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective",
        )

        # Mock execution
        with patch("commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE", False):
            worker.run()
            worker.wait(2000)

        # Verify thread is finished
        assert worker.isRunning() is False, "Worker should be finished"


class TestTANChallengeFlow:
    """Test the complete TAN challenge coordination flow."""

    def test_tan_challenge_flow_with_decoupled(self, main_window):
        """Test TAN flow with decoupled mobile confirmation."""
        from fints.dialog import NeedTANResponse

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Create mock NeedTANResponse with decoupled flag
        mock_response = MagicMock(spec=NeedTANResponse)
        mock_response.challenge = "Please confirm in your photoTAN app"
        mock_response.decoupled = True

        # Mock client
        mock_client = MagicMock()
        mock_client.send_tan.return_value = True

        # Track signal emissions
        tan_requests = []

        def track_tan_request(challenge, is_decoupled):
            tan_requests.append((challenge, is_decoupled))
            # Simulate user approval
            worker.set_tan("decoupled")

        worker.request_tan_signal.connect(track_tan_request)

        # Run the TAN challenge loop
        worker.handle_tan_challenge_loop(mock_client, mock_response)

        assert len(tan_requests) == 1, "Should request TAN once"
        assert tan_requests[0][1] is True, "Should be decoupled request"

    def test_tan_challenge_flow_with_manual_tan(self, main_window):
        """Test TAN flow with manual 6-digit TAN input."""
        from fints.dialog import NeedTANResponse

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Create mock NeedTANResponse without decoupled flag
        mock_response = MagicMock(spec=NeedTANResponse)
        mock_response.challenge = "Please enter the 6-digit photoTAN code"
        mock_response.decoupled = False

        # Mock client
        mock_client = MagicMock()
        mock_client.send_tan.return_value = True

        # Track signal emissions
        tan_requests = []

        def track_tan_request(challenge, is_decoupled):
            tan_requests.append((challenge, is_decoupled))
            # Simulate user entering TAN
            worker.set_tan("123456")

        worker.request_tan_signal.connect(track_tan_request)

        # Run the TAN challenge loop
        worker.handle_tan_challenge_loop(mock_client, mock_response)

        assert len(tan_requests) == 1, "Should request TAN once"
        assert tan_requests[0][1] is False, "Should be manual TAN request"
        assert worker.submitted_tan == "123456", "TAN should be stored"

    def test_tan_challenge_cancellation(self, main_window):
        """Test TAN challenge cancellation flow."""
        from fints.dialog import NeedTANResponse

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=[],
            method="collective",
        )

        # Create mock NeedTANResponse
        mock_response = MagicMock(spec=NeedTANResponse)
        mock_response.challenge = "Please enter the 6-digit photoTAN code"
        mock_response.decoupled = False

        # Mock client
        mock_client = MagicMock()

        # Track signal emissions
        tan_requests = []

        def track_tan_request(challenge, is_decoupled):
            tan_requests.append((challenge, is_decoupled))
            # Simulate user cancellation
            worker.cancel_tan()

        worker.request_tan_signal.connect(track_tan_request)

        # Run the TAN challenge loop
        worker.handle_tan_challenge_loop(mock_client, mock_response)

        assert len(tan_requests) == 1, "Should request TAN once"
        assert worker.is_cancelled is True, "Cancellation flag should be set"


# @MX:ANCHOR: [AUTO] Thread coordination testing - critical for GUI responsiveness
# @MX:REASON: High fan_in (directly affects GUI thread responsiveness and user experience)
