"""
Error handling tests for Commerzbank FinTS application.

Tests exception handling, input validation, network failure scenarios,
and graceful error recovery throughout the application.

Coverage Areas:
- FinTS library exception handling
- Invalid input validation
- Network failure simulation
- Authentication error handling
- Thread error propagation
- GUI error display
- Graceful degradation
"""

from unittest.mock import MagicMock, patch
from commerzbank_fints_qt_desktop_app import FinTSWorker


class TestFinTSLibraryExceptions:
    """Test handling of FinTS library exceptions."""

    def test_fints_library_not_available(self, main_window):
        """Test behavior when FinTS library is not installed."""
        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Track finished signal
        finished_calls = []

        def track_finished(success, message):
            finished_calls.append((success, message))

        worker.finished_signal.connect(track_finished)

        # Mock FinTS as unavailable
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', False):
            worker.run()

            # Should emit finished_signal with error
            assert len(finished_calls) == 1, "Should emit finished signal"
            assert finished_calls[0][0] is False, "Should indicate failure"
            assert "Missing dependencies" in finished_calls[0][1], "Should report missing dependencies"

    def test_pin_error_handling(self, main_window):
        """Test handling of invalid PIN authentication."""
        from fints.exceptions import FinTSClientPINError

        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="wrongpin",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Track finished signal
        finished_calls = []

        def track_finished(success, message):
            finished_calls.append((success, message))

        worker.finished_signal.connect(track_finished)

        # Mock FinTS client to raise PIN error
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientPINError("Invalid PIN")
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.run()
                worker.wait(2000)

                # Should handle PIN error gracefully
                assert len(finished_calls) > 0, "Should emit finished signal"
                assert finished_calls[0][0] is False, "Should indicate failure"
                assert "Invalid PIN" in finished_calls[0][1], "Should report invalid PIN"

    def test_general_finTS_error_handling(self, main_window):
        """Test handling of general FinTS exceptions."""
        from fints.exceptions import FinTSClientError

        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Track finished signal
        finished_calls = []

        def track_finished(success, message):
            finished_calls.append((success, message))

        worker.finished_signal.connect(track_finished)

        # Mock FinTS client to raise general error
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientError("Network error")
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.run()
                worker.wait(2000)

                # Should handle general error gracefully
                assert len(finished_calls) > 0, "Should emit finished signal"
                assert finished_calls[0][0] is False, "Should indicate failure"


class TestInputValidation:
    """Test input validation and error detection."""

    def test_empty_pin_validation(self, main_window):
        """Test that empty PIN is rejected before execution."""
        # Clear PIN field
        main_window.pin_input.setText("")

        # Mock table with data
        main_window.table.setRowCount(1)
        from PyQt6.QtWidgets import QTableWidgetItem
        main_window.table.setItem(0, 0, QTableWidgetItem("Test"))
        main_window.table.setItem(0, 1, QTableWidgetItem("DE89370400440532013000"))
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(0, 3, QTableWidgetItem("Ref"))

        # Try to execute with empty PIN
        # This should show a QMessageBox.error and not start worker
        # Since we can't easily test QMessageBox in unit tests, we verify worker is not created

        # Clear worker to test validation
        main_window.worker = None

        # This will fail validation and show error dialog
        main_window.start_batch_execution()

        # Worker should still be None (validation failed)
        assert main_window.worker is None, "Worker should not be created with empty PIN"

    def test_incomplete_table_data_validation(self, main_window):
        """Test that incomplete table data is detected."""
        # Set PIN
        main_window.pin_input.setText("test1234")

        # Add incomplete row (missing name)
        main_window.table.setRowCount(1)
        from PyQt6.QtWidgets import QTableWidgetItem
        main_window.table.setItem(0, 0, QTableWidgetItem(""))  # Empty name
        main_window.table.setItem(0, 1, QTableWidgetItem("DE89370400440532013000"))
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(0, 3, QTableWidgetItem("Ref"))

        # Try to execute with incomplete data
        main_window.start_batch_execution()

        # Should show error and not start worker
        # Worker should be None or not running
        if main_window.worker:
            assert not main_window.worker.isRunning(), "Worker should not start with incomplete data"

    def test_empty_payout_list_validation(self, main_window):
        """Test that empty payout list is detected."""
        # Set PIN
        main_window.pin_input.setText("test1234")

        # Clear table
        main_window.table.setRowCount(0)

        # Try to execute with no payouts
        main_window.start_batch_execution()

        # Should show error and not start worker
        if main_window.worker:
            assert not main_window.worker.isRunning(), "Worker should not start with empty payout list"


class TestNetworkFailureSimulation:
    """Test handling of network failures and timeouts."""

    def test_connection_timeout(self, main_window):
        """Test handling of connection timeout."""
        from fints.exceptions import FinTSClientError

        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Track finished signal
        finished_calls = []

        def track_finished(success, message):
            finished_calls.append((success, message))

        worker.finished_signal.connect(track_finished)

        # Mock network timeout
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientError("Connection timeout")
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.run()
                worker.wait(2000)

                # Should handle timeout gracefully
                assert len(finished_calls) > 0, "Should emit finished signal"
                assert finished_calls[0][0] is False, "Should indicate failure"
                assert "timeout" in finished_calls[0][1].lower() or "Connection" in finished_calls[0][1], \
                    "Should mention connection issue"

    def test_network_unreachable(self, main_window):
        """Test handling of unreachable network."""
        from fints.exceptions import FinTSClientError

        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Track finished signal
        finished_calls = []

        def track_finished(success, message):
            finished_calls.append((success, message))

        worker.finished_signal.connect(track_finished)

        # Mock network unreachable
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientError("Network unreachable")
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.run()
                worker.wait(2000)

                # Should handle network error gracefully
                assert len(finished_calls) > 0, "Should emit finished signal"
                assert finished_calls[0][0] is False, "Should indicate failure"


class TestThreadErrorPropagation:
    """Test error propagation from worker thread to GUI thread."""

    def test_worker_error_signal_emission(self, main_window):
        """Test that worker emits error signals correctly."""
        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Track log signals (including error logs)
        log_calls = []

        def track_log(message, color):
            log_calls.append((message, color))

        worker.log_signal.connect(track_log)

        # Log an error
        worker.log("Test error message", "error")

        # Should emit error log with red color
        assert len(log_calls) == 1, "Should emit error log"
        assert log_calls[0][0] == "Test error message", "Error message should match"
        assert log_calls[0][1] == "#f87171", "Error should have red color"

    def test_worker_finished_signal_on_error(self, main_window):
        """Test that worker emits finished_signal on error."""
        from fints.exceptions import FinTSClientError

        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Track finished signal
        finished_calls = []

        def track_finished(success, message):
            finished_calls.append((success, message))

        worker.finished_signal.connect(track_finished)

        # Mock FinTS client to raise error
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientError("Test error")
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.run()
                worker.wait(2000)

                # Should emit finished_signal with error
                assert len(finished_calls) > 0, "Should emit finished signal"
                assert finished_calls[0][0] is False, "Should indicate failure"


class TestGUIErrorDisplay:
    """Test error display in GUI components."""

    def test_error_message_in_terminal(self, main_window):
        """Test that error messages appear in terminal log."""
        # Append an error message
        main_window.append_terminal_message("Test error", "#f87171")

        # Verify error message is displayed
        terminal_text = main_window.log_terminal.toPlainText()
        assert "Test error" in terminal_text, "Error message should appear in terminal"

    def test_error_dialog_on_worker_failure(self, main_window):
        """Test that error dialog is shown when worker fails."""
        # Set up worker that will fail
        from fints.exceptions import FinTSClientError

        # Set PIN and add table data
        main_window.pin_input.setText("test1234")
        main_window.table.setRowCount(1)
        from PyQt6.QtWidgets import QTableWidgetItem
        main_window.table.setItem(0, 0, QTableWidgetItem("Test"))
        main_window.table.setItem(0, 1, QTableWidgetItem("DE89370400440532013000"))
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(0, 3, QTableWidgetItem("Ref"))

        # Mock FinTS client to raise error
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientError("Test error")
                mock_account = MagicMock()
                mock_account.iban = "DE89370400440532013000"
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                # Start execution
                main_window.start_batch_execution()

                # Wait for worker to complete
                if main_window.worker:
                    main_window.worker.wait(3000)

                    # Error dialog should be shown (we can't easily test QMessageBox, but we can verify terminal has error)
                    terminal_text = main_window.log_terminal.toPlainText()
                    # Some error message should appear in terminal
                    assert len(terminal_text) > 0, "Terminal should have content after error"

    def test_execute_button_state_after_error(self, main_window):
        """Test that execute button is re-enabled after error."""
        # Initially enabled
        assert main_window.btn_execute.isEnabled(), "Button should be enabled initially"

        # Set up scenario that will fail
        from fints.exceptions import FinTSClientError

        main_window.pin_input.setText("test1234")
        main_window.table.setRowCount(1)
        from PyQt6.QtWidgets import QTableWidgetItem
        main_window.table.setItem(0, 0, QTableWidgetItem("Test"))
        main_window.table.setItem(0, 1, QTableWidgetItem("DE89370400440532013000"))
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(0, 3, QTableWidgetItem("Ref"))

        # Mock FinTS client to raise error
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientError("Test error")
                mock_account = MagicMock()
                mock_account.iban = "DE89370400440532013000"
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                # Start execution
                main_window.start_batch_execution()

                # Button should be disabled during execution
                assert not main_window.btn_execute.isEnabled(), "Button should be disabled during execution"

                # Wait for completion
                if main_window.worker:
                    main_window.worker.wait(3000)

                    # Button should be re-enabled after error
                    assert main_window.btn_execute.isEnabled(), "Button should be re-enabled after error"


class TestGracefulDegradation:
    """Test graceful degradation when components fail."""

    def test_table_calculation_with_invalid_data(self, main_window):
        """Test that batch calculations continue with invalid data."""
        from PyQt6.QtWidgets import QTableWidgetItem

        # Add mix of valid and invalid data
        main_window.table.setRowCount(3)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))  # Valid
        main_window.table.setItem(1, 2, QTableWidgetItem("invalid"))  # Invalid
        main_window.table.setItem(2, 2, QTableWidgetItem("200.00"))  # Valid

        # Should not crash, should sum valid amounts
        main_window.update_batch_calculations()

        total_text = main_window.lbl_batch_total.text()
        # Should be 100 + 200 = 300 (invalid skipped)
        assert "300.00" in total_text or "300,00" in total_text, f"Should handle invalid data gracefully, got {total_text}"

    def test_iban_validation_with_malformed_input(self, main_window):
        """Test that IBAN validation handles malformed input gracefully."""
        # Test various malformed inputs
        malformed_inputs = [
            None,
            "",
            "   ",
            "INVALID",
            "12345678901234567890",
            "DE@370400440532013000",
        ]

        for malformed_input in malformed_inputs:
            # Should not crash
            result = main_window.validate_iban_mod97(malformed_input)
            # Should return False for all malformed inputs
            assert result is False, f"Should return False for malformed input: {malformed_input}"

    def test_worker_cleanup_after_error(self, main_window):
        """Test that worker resources are cleaned up after error."""
        from fints.exceptions import FinTSClientError

        payouts = [{"name": "Test", "iban": "DE89370400440532013000", "amount": "100.00", "reference": "Test"}]

        worker = FinTSWorker(
            blz="37040044",
            user_id="1234567890",
            pin="test1234",
            debtor_iban="DE89370400440532013000",
            payouts=payouts,
            method="collective"
        )

        # Mock FinTS client to raise error
        with patch('commerzbank_fints_qt_desktop_app.FINTS_AVAILABLE', True):
            with patch('commerzbank_fints_qt_desktop_app.FinTS3PinTanClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_sepa_accounts.side_effect = FinTSClientError("Test error")
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client_class.return_value = mock_client

                worker.run()
                worker.wait(2000)

                # Worker should be finished (not running)
                assert not worker.isRunning(), "Worker should be finished after error"

                # Resources should be cleaned up
                assert worker.isFinished(), "Worker should be in finished state"


# @MX:NOTE: [AUTO] Comprehensive error handling testing
# @MX:REASON: Error handling is critical for application stability and user experience
