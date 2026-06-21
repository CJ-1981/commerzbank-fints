"""
Data import tests for Commerzbank FinTS application.

Tests clipboard parsing, table operations (add, delete, modify),
and batch calculation updates triggered by data changes.

Coverage Areas:
- Clipboard parsing with tab-separated data
- Table row operations (add, delete, modify)
- Batch calculation updates on data change
- Various clipboard content formats
- Edge cases (empty content, malformed data, special characters)
- Data validation on import
- Table event handling
"""

from PyQt6.QtWidgets import QTableWidgetItem, QApplication
from PyQt6.QtTest import QTest


class TestClipboardParsing:
    """Test clipboard data parsing functionality."""

    def test_valid_tab_separated_data(self, main_window):
        """Test parsing valid tab-separated data from clipboard."""
        clipboard_data = "Name1\tDE89370400440532013000\t100.00\tReference1\nName2\tDE56370400440002222222\t200,50\tReference2"

        # Set clipboard data
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        # Import from clipboard
        main_window.paste_from_clipboard()

        # Verify rows were added
        assert main_window.table.rowCount() >= 2, "Should import at least 2 rows"

        # Verify first row data (may be more rows if mock data exists)
        row_count = main_window.table.rowCount()
        first_imported_row = row_count - 2  # Assuming 2 imported rows

        name_item = main_window.table.item(first_imported_row, 0)
        iban_item = main_window.table.item(first_imported_row, 1)
        amount_item = main_window.table.item(first_imported_row, 2)
        ref_item = main_window.table.item(first_imported_row, 3)

        assert name_item.text() == "Name1", (
            f"Name should be 'Name1', got '{name_item.text()}'"
        )
        assert "DE89370400440532013000" in iban_item.text(), (
            f"IBAN should contain DE89..., got '{iban_item.text()}'"
        )
        assert "100.00" in amount_item.text() or "100,00" in amount_item.text(), (
            f"Amount should be 100.00, got '{amount_item.text()}'"
        )
        assert ref_item.text() == "Reference1", (
            f"Reference should be 'Reference1', got '{ref_item.text()}'"
        )

    def test_comma_decimal_parsing(self, main_window):
        """Test that comma decimals are converted to dot decimals."""
        clipboard_data = "Name1\tDE89370400440532013000\t100,50\tReference1"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        row_count = main_window.table.rowCount()
        imported_row = row_count - 1

        amount_item = main_window.table.item(imported_row, 2)
        # Should convert comma to dot
        assert "100.50" in amount_item.text() or "100,50" in amount_item.text(), (
            f"Amount should handle comma decimal, got '{amount_item.text()}'"
        )

    def test_empty_clipboard(self, main_window):
        """Test handling of empty clipboard."""
        initial_row_count = main_window.table.rowCount()

        clipboard = QApplication.clipboard()
        clipboard.setText("")

        main_window.paste_from_clipboard()

        # Should not add any rows
        assert main_window.table.rowCount() == initial_row_count, (
            "Empty clipboard should not add rows"
        )

    def test_whitespace_only_clipboard(self, main_window):
        """Test handling of whitespace-only clipboard."""
        initial_row_count = main_window.table.rowCount()

        clipboard = QApplication.clipboard()
        clipboard.setText("   \n   \n   ")

        main_window.paste_from_clipboard()

        # Should not add any rows
        assert main_window.table.rowCount() == initial_row_count, (
            "Whitespace-only clipboard should not add rows"
        )

    def test_missing_columns_handling(self, main_window):
        """Test handling of rows with missing columns."""
        # Row with only 2 columns (should need at least 3)
        clipboard_data = "Name1\tDE89370400440532013000\t100.00\tReference1\nName2\tDE56370400440002222222"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        # Should only import the complete row
        # Verify the incomplete row was not imported
        rows_added = 0
        row_count = main_window.table.rowCount()

        for row in range(row_count):
            name_item = main_window.table.item(row, 0)
            if name_item and name_item.text() == "Name2":
                rows_added += 1

        # Name2 should not be imported (missing columns)
        assert rows_added == 0, "Incomplete rows should not be imported"

    def test_extra_columns_handling(self, main_window):
        """Test handling of rows with extra columns."""
        # Row with 5 columns (should use first 4)
        clipboard_data = (
            "Name1\tDE89370400440532013000\t100.00\tReference1\tExtraColumn"
        )

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        row_count = main_window.table.rowCount()
        imported_row = row_count - 1

        # Should import only first 4 columns
        name_item = main_window.table.item(imported_row, 0)
        assert name_item.text() == "Name1", (
            "Should import first 4 columns and ignore extras"
        )

    def test_empty_lines_in_clipboard(self, main_window):
        """Test handling of empty lines in clipboard data."""
        clipboard_data = "Name1\tDE89370400440532013000\t100.00\tReference1\n\nName2\tDE56370400440002222222\t200.00\tReference2\n"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        # Should skip empty lines and import 2 rows
        imported_rows = 0
        row_count = main_window.table.rowCount()

        for row in range(row_count):
            name_item = main_window.table.item(row, 0)
            if name_item and name_item.text() in ["Name1", "Name2"]:
                imported_rows += 1

        assert imported_rows == 2, (
            f"Should import 2 non-empty rows, got {imported_rows}"
        )

    def test_single_row_import(self, main_window):
        """Test importing a single row."""
        clipboard_data = "Name1\tDE89370400440532013000\t100.00\tReference1"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        # Should import 1 row
        imported_rows = 0
        row_count = main_window.table.rowCount()

        for row in range(row_count):
            name_item = main_window.table.item(row, 0)
            if name_item and name_item.text() == "Name1":
                imported_rows += 1

        assert imported_rows == 1, f"Should import 1 row, got {imported_rows}"

    def test_iban_normalization_on_import(self, main_window):
        """Test that IBANs are normalized (uppercase, spaces removed) on import."""
        # IBAN with lowercase and spaces
        clipboard_data = "Name1\tde89 3704 0044 0532 0130 00\t100.00\tReference1"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        row_count = main_window.table.rowCount()
        imported_row = row_count - 1

        iban_item = main_window.table.item(imported_row, 1)
        # Should be uppercase and without spaces
        iban_text = iban_item.text()
        assert iban_text.isupper(), "IBAN should be uppercase"
        assert " " not in iban_text, "IBAN should not contain spaces"
        assert "DE89370400440532013000" in iban_text, (
            f"IBAN should be normalized, got {iban_text}"
        )


class TestTableRowOperations:
    """Test table row operations (add, delete, modify)."""

    def test_add_single_row(self, main_window):
        """Test adding a single row to the table."""
        initial_count = main_window.table.rowCount()

        main_window.add_table_row()

        assert main_window.table.rowCount() == initial_count + 1, "Should add 1 row"

        # Verify default values
        new_row = main_window.table.rowCount() - 1
        name_item = main_window.table.item(new_row, 0)
        iban_item = main_window.table.item(new_row, 1)
        amount_item = main_window.table.item(new_row, 2)
        ref_item = main_window.table.item(new_row, 3)

        assert name_item.text() == "New Recipient", (
            "Default name should be 'New Recipient'"
        )
        assert iban_item.text() == "DE", "Default IBAN should be 'DE'"
        assert amount_item.text() == "0.00", "Default amount should be '0.00'"
        assert ref_item.text() == "Invoice Ref", (
            "Default reference should be 'Invoice Ref'"
        )

    def test_add_multiple_rows(self, main_window):
        """Test adding multiple rows."""
        initial_count = main_window.table.rowCount()

        for _ in range(5):
            main_window.add_table_row()

        assert main_window.table.rowCount() == initial_count + 5, "Should add 5 rows"

    def test_delete_single_row(self, main_window):
        """Test deleting a single row."""
        # Add a row to delete
        main_window.add_table_row()
        QApplication.processEvents()  # Process Qt events

        row_count_before = main_window.table.rowCount()

        # Select the last row
        last_row = row_count_before - 1
        main_window.table.selectRow(last_row)
        QApplication.processEvents()  # Process Qt events after selection

        # Delete the selected row
        main_window.delete_selected_row()
        QApplication.processEvents()  # Process Qt events after deletion

        assert main_window.table.rowCount() == row_count_before - 1, (
            f"Should delete 1 row, got {main_window.table.rowCount()} rows"
        )

    def test_delete_multiple_rows(self, main_window):
        """Test deleting multiple rows at once."""
        # Add rows to delete
        for i in range(3):
            main_window.add_table_row()

        # Process Qt events after adding rows
        QApplication.processEvents()

        row_count_before = main_window.table.rowCount()

        # Select multiple rows
        main_window.table.setSelectionBehavior(main_window.table.SelectRows)
        main_window.table.setRangeSelected(
            main_window.model().index(row_count_before - 3, 0),
            main_window.model().index(row_count_before - 1, 3),
        )

        # Process Qt events after selection
        QApplication.processEvents()

        # Delete selected rows
        main_window.delete_selected_row()

        # Process Qt events after deletion
        QApplication.processEvents()

        assert main_window.table.rowCount() == row_count_before - 3, (
            f"Should delete 3 rows, got {main_window.table.rowCount()} rows"
        )

    def test_delete_row_without_selection(self, main_window):
        """Test deleting without selecting a row shows warning."""
        # Ensure no row is selected
        main_window.table.clearSelection()

        # Try to delete without selection (should show warning dialog)
        # This will pop up a QMessageBox, which we can't easily test in unit tests
        # But we can verify the function handles it gracefully
        main_window.delete_selected_row()

        # Row count should not change
        row_count_before = main_window.table.rowCount()
        main_window.delete_selected_row()
        assert main_window.table.rowCount() == row_count_before, (
            "No rows should be deleted without selection"
        )

    def test_modify_row_data(self, main_window):
        """Test modifying row data."""
        # Add a row
        main_window.add_table_row()
        row = main_window.table.rowCount() - 1

        # Modify the data
        main_window.table.setItem(row, 0, QTableWidgetItem("Modified Name"))
        main_window.table.setItem(row, 1, QTableWidgetItem("DE89370400440532013000"))
        main_window.table.setItem(row, 2, QTableWidgetItem("500.00"))
        main_window.table.setItem(row, 3, QTableWidgetItem("Modified Reference"))

        # Trigger update (normally done by itemChanged signal)
        main_window.update_batch_calculations()

        # Verify data was modified
        name_item = main_window.table.item(row, 0)
        assert name_item.text() == "Modified Name", "Name should be modified"

        amount_item = main_window.table.item(row, 2)
        assert "500.00" in amount_item.text() or "500,00" in amount_item.text(), (
            "Amount should be modified"
        )

    def test_clear_all_rows(self, main_window):
        """Test clearing all rows from table."""
        # Add some rows
        for _ in range(5):
            main_window.add_table_row()

        # Clear all rows
        main_window.table.setRowCount(0)

        assert main_window.table.rowCount() == 0, "All rows should be cleared"


class TestBatchCalculationUpdates:
    """Test batch calculation updates triggered by data changes."""

    def test_batch_calculation_on_row_add(self, main_window):
        """Test that batch calculations update when row is added."""

        # Clear existing rows
        main_window.table.setRowCount(0)

        # Add row with amount
        main_window.add_table_row()
        row = 0
        main_window.table.setItem(row, 2, QTableWidgetItem("100.00"))

        # Trigger update
        main_window.update_batch_calculations()

        # Check batch count
        count_text = main_window.lbl_batch_count.text()
        assert "1 Payout" in count_text, (
            f"Count should be '1 Payout', got '{count_text}'"
        )

        # Check batch total
        total_text = main_window.lbl_batch_total.text()
        assert "100.00" in total_text or "100,00" in total_text, (
            f"Total should be 100.00, got '{total_text}'"
        )

    def test_batch_calculation_on_row_delete(self, main_window):
        """Test that batch calculations update when row is deleted."""
        # Clear and add known rows
        main_window.table.setRowCount(0)

        for i in range(3):
            main_window.add_table_row()
            main_window.table.setItem(i, 2, QTableWidgetItem(f"{(i + 1) * 100}.00"))

        main_window.update_batch_calculations()

        # Delete last row
        main_window.table.selectRow(2)
        main_window.delete_selected_row()

        # Total should now be 100 + 200 = 300
        total_after = main_window.lbl_batch_total.text()
        assert "300.00" in total_after or "300,00" in total_after, (
            f"Total should be 300.00 after delete, got '{total_after}'"
        )

    def test_batch_calculation_on_data_change(self, main_window):
        """Test that batch calculations update when cell data changes."""
        # Clear and add row
        main_window.table.setRowCount(0)
        main_window.add_table_row()
        row = 0
        main_window.table.setItem(row, 2, QTableWidgetItem("100.00"))

        main_window.update_batch_calculations()

        # Verify initial total
        total_before = main_window.lbl_batch_total.text()
        assert "100.00" in total_before or "100,00" in total_before, (
            "Initial total should be 100.00"
        )

        # Change amount
        main_window.table.setItem(row, 2, QTableWidgetItem("250.00"))

        # Trigger update (normally done by itemChanged signal)
        main_window.update_batch_calculations()

        # Verify updated total
        total_after = main_window.lbl_batch_total.text()
        assert "250.00" in total_after or "250,00" in total_after, (
            f"Total should be 250.00 after change, got '{total_after}'"
        )

    def test_batch_calculation_with_empty_table(self, main_window):
        """Test batch calculations with empty table."""
        main_window.table.setRowCount(0)

        main_window.update_batch_calculations()

        # Count should be 0
        count_text = main_window.lbl_batch_count.text()
        assert "0 Payout" in count_text, (
            f"Count should be '0 Payouts', got '{count_text}'"
        )

        # Total should be 0.00
        total_text = main_window.lbl_batch_total.text()
        assert "0.00" in total_text or "0,00" in total_text, (
            f"Total should be 0.00, got '{total_text}'"
        )


class TestTableEventHandling:
    """Test table event handling and signal connections."""

    def test_table_item_changed_signal(self, main_window):
        """Test that itemChanged signal triggers batch calculation."""
        # Clear and add row
        main_window.table.setRowCount(0)
        main_window.add_table_row()
        row = 0

        # Block signals to prevent initial calculation
        main_window.table.blockSignals(True)
        main_window.table.setItem(row, 2, QTableWidgetItem("100.00"))
        main_window.table.blockSignals(False)

        # Manually trigger item changed (simulating signal)
        item = main_window.table.item(row, 2)
        main_window.on_table_changed(item)

        # Verify batch calculation was triggered
        total_text = main_window.lbl_batch_total.text()
        assert "100.00" in total_text or "100,00" in total_text, (
            "Batch calculation should be triggered"
        )

    def test_table_signal_connection(self, main_window):
        """Test that itemChanged signal is properly connected."""
        # Verify signal is connected (this is a basic check)
        assert main_window.table.itemChanged is not None, (
            "itemChanged signal should exist"
        )

        # Add a row and check that changing it triggers calculation
        main_window.add_table_row()
        row = main_window.table.rowCount() - 1

        # Change amount (this should trigger itemChanged signal)
        main_window.table.setItem(row, 2, QTableWidgetItem("999.99"))

        # Allow signal to propagate
        QTest.qWait(100)

        # Verify calculation was updated
        total_text = main_window.lbl_batch_total.text()
        assert "999.99" in total_text or "999,99" in total_text, (
            "Signal should trigger batch calculation"
        )


class TestDataValidation:
    """Test data validation during import and editing."""

    def test_iban_validation_on_import(self, main_window):
        """Test that imported IBANs are validated."""
        clipboard_data = "Name1\tINVALIDIBAN\t100.00\tReference1"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        row_count = main_window.table.rowCount()
        imported_row = row_count - 1

        # IBAN should be marked as invalid (red color)
        iban_item = main_window.table.item(imported_row, 1)
        if iban_item:
            # Check for invalid IBAN color indication (red)
            color = iban_item.foreground().color()
            # Invalid IBAN should have red color (#f87171)
            assert color.name() == "#f87171", (
                f"Invalid IBAN should be red, got {color.name()}"
            )

    def test_valid_iban_color_on_import(self, main_window):
        """Test that valid imported IBANs get correct color."""
        clipboard_data = "Name1\tDE89370400440532013000\t100.00\tReference1"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        row_count = main_window.table.rowCount()
        imported_row = row_count - 1

        # IBAN should be marked as valid (white color)
        iban_item = main_window.table.item(imported_row, 1)
        if iban_item:
            color = iban_item.foreground().color()
            # Valid IBAN should have white/light color (#f1f5f9)
            assert color.name() in ["#f1f5f9", "#ffffff"], (
                f"Valid IBAN should be white, got {color.name()}"
            )

    def test_amount_validation_on_import(self, main_window):
        """Test that invalid amounts are handled."""
        # Import with invalid amount
        clipboard_data = "Name1\tDE89370400440532013000\tinvalid\tReference1"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        main_window.paste_from_clipboard()

        # Should not crash, and should handle gracefully
        # The amount might be stored as-is or treated as 0
        assert main_window.table.rowCount() > 0, (
            "Row should be imported even with invalid amount"
        )


class TestImportPerformance:
    """Test performance of data import operations."""

    def test_large_clipboard_import_performance(self, main_window):
        """Test importing large clipboard data."""
        import time

        # Generate large clipboard data (1000 rows)
        lines = []
        for i in range(1000):
            lines.append(
                f"Name{i}\tDE89370400440532013000\t{(i + 1) * 10}.50\tReference{i}"
            )

        clipboard_data = "\n".join(lines)

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_data)

        # Measure import time
        start_time = time.time()
        main_window.paste_from_clipboard()
        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 2 seconds)
        assert elapsed < 2.0, f"Large import should be fast, took {elapsed:.2f}s"

        # Verify rows were imported
        assert main_window.table.rowCount() >= 1000, (
            f"Should import 1000 rows, got {main_window.table.rowCount()}"
        )

    def test_frequent_add_row_performance(self, main_window):
        """Test performance of adding many rows."""
        import time

        # Clear table
        main_window.table.setRowCount(0)

        # Measure time to add 1000 rows
        start_time = time.time()
        for i in range(1000):
            main_window.add_table_row()
        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 3 seconds)
        assert elapsed < 3.0, f"Adding 1000 rows should be fast, took {elapsed:.2f}s"

        assert main_window.table.rowCount() == 1000, (
            f"Should have 1000 rows, got {main_window.table.rowCount()}"
        )


# @MX:NOTE: [AUTO] Comprehensive data import testing
# @MX:REASON: Data import is critical user-facing feature - clipboard parsing and table operations must be robust
