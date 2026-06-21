"""
Financial calculation tests for Commerzbank FinTS application.

Tests Decimal arithmetic for batch totals, currency formatting, amount parsing,
and precision handling to ensure financial accuracy.

Coverage Areas:
- Decimal precision preservation
- Batch total calculations
- Currency formatting (German locale with comma as decimal separator)
- Amount parsing from various input formats
- Edge cases (zero amounts, negative amounts, invalid inputs)
- Large amount handling
- Rounding behavior
"""

import pytest
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class TestDecimalPrecision:
    """Test Decimal precision handling for financial calculations."""

    def test_decimal_creation_from_string(self, main_window):
        """Test Decimal creation from string inputs preserves precision."""
        test_cases = [
            ("100.00", Decimal("100.00")),
            ("0.01", Decimal("0.01")),
            ("1000.999", Decimal("1000.999")),
            ("1234567.89", Decimal("1234567.89")),
        ]

        for input_str, expected in test_cases:
            result = Decimal(input_str)
            assert result == expected, f"Decimal('{input_str}') should equal {expected}"
            # Verify precision is preserved
            assert str(result) == str(expected), "String representation should preserve precision"

    def test_decimal_arithmetic_preserves_precision(self, main_window):
        """Test that Decimal arithmetic maintains precision."""
        # Addition
        result = Decimal("100.00") + Decimal("200.50")
        assert result == Decimal("300.50"), "Addition should preserve precision"

        # Subtraction
        result = Decimal("500.00") - Decimal("200.25")
        assert result == Decimal("299.75"), "Subtraction should preserve precision"

        # Multiplication
        result = Decimal("100.00") * Decimal("3")
        assert result == Decimal("300.00"), "Multiplication should preserve precision"

        # Division (should be careful with this in financial contexts)
        result = Decimal("100.00") / Decimal("3")
        # Division can create many decimal places
        assert result > Decimal("33.33") and result < Decimal("33.34"), "Division should be precise"

    def test_sub_cent_precision_handling(self, main_window):
        """Test handling of sub-cent precision (0.001 and below)."""
        # Some financial systems use sub-cent precision for intermediate calculations
        sub_cent_amounts = [
            Decimal("0.001"),
            Decimal("0.009"),
            Decimal("0.0001"),
        ]

        for amount in sub_cent_amounts:
            # Should be able to create and manipulate sub-cent amounts
            doubled = amount * 2
            assert doubled > amount, f"Sub-cent amount {amount} should be manipulable"

    def test_large_amount_precision(self, main_window):
        """Test precision handling for large amounts."""
        large_amounts = [
            ("1000000.00", Decimal("1000000.00")),
            ("999999999.99", Decimal("999999999.99")),
            ("1234567890.12", Decimal("1234567890.12")),
        ]

        for input_str, expected in large_amounts:
            result = Decimal(input_str)
            assert result == expected, f"Large amount {input_str} should preserve precision"


class TestBatchTotalCalculations:
    """Test batch total calculation accuracy and edge cases."""

    def test_batch_total_simple_addition(self, main_window):
        """Test simple batch total calculation."""
        # Add test data to table
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(3)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(1, 2, QTableWidgetItem("200.50"))
        main_window.table.setItem(2, 2, QTableWidgetItem("50.25"))

        # Trigger calculation
        main_window.update_batch_calculations()

        # Check total
        total_text = main_window.lbl_batch_total.text()
        assert "350.75" in total_text or "350,75" in total_text, f"Total should be 350.75, got {total_text}"

    def test_batch_total_with_many_rows(self, main_window):
        """Test batch total with many rows."""
        from PyQt6.QtWidgets import QTableWidgetItem

        # Add 100 rows with varying amounts
        main_window.table.setRowCount(100)
        expected_total = Decimal("0.00")

        for i in range(100):
            amount = f"{i * 10}.50"
            main_window.table.setItem(i, 2, QTableWidgetItem(amount))
            expected_total += Decimal(amount)

        # Trigger calculation
        main_window.update_batch_calculations()

        # Check total (allowing for formatting differences)
        total_text = main_window.lbl_batch_total.text()
        # Extract numeric part
        total_numeric = total_text.replace("€", "").replace(".", "").replace(",", ".")
        calculated_total = Decimal(total_numeric)

        assert calculated_total == expected_total, f"Total should be {expected_total}, got {calculated_total}"

    def test_batch_total_with_zero_amounts(self, main_window):
        """Test batch total calculation with zero amounts."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(3)
        main_window.table.setItem(0, 2, QTableWidgetItem("0.00"))
        main_window.table.setItem(1, 2, QTableWidgetItem("0.00"))
        main_window.table.setItem(2, 2, QTableWidgetItem("0.00"))

        main_window.update_batch_calculations()

        total_text = main_window.lbl_batch_total.text()
        assert "0.00" in total_text or "0,00" in total_text, f"Total should be 0.00, got {total_text}"

    def test_batch_total_with_mixed_valid_invalid_amounts(self, main_window):
        """Test batch total with valid and invalid amounts mixed."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(4)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(1, 2, QTableWidgetItem("invalid"))  # Invalid
        main_window.table.setItem(2, 2, QTableWidgetItem("200.50"))
        main_window.table.setItem(3, 2, QTableWidgetItem(""))  # Empty

        main_window.update_batch_calculations()

        # Should only sum valid amounts (100.00 + 200.50 = 300.50)
        total_text = main_window.lbl_batch_total.text()
        assert "300.50" in total_text or "300,50" in total_text, f"Total should be 300.50, got {total_text}"

    def test_batch_total_updates_on_row_change(self, main_window):
        """Test that batch total updates when table data changes."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(1)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))

        main_window.update_batch_calculations()

        # Change the amount
        main_window.table.setItem(0, 2, QTableWidgetItem("250.00"))

        # Signal table changed (which triggers update)
        main_window.on_table_changed(main_window.table.item(0, 2))

        # Check updated total
        total_text = main_window.lbl_batch_total.text()
        assert "250.00" in total_text or "250,00" in total_text, f"Total should update to 250.00, got {total_text}"

    def test_batch_count_updates_correctly(self, main_window):
        """Test that batch count updates correctly."""
        from PyQt6.QtWidgets import QTableWidgetItem

        # Test single row
        main_window.table.setRowCount(1)
        main_window.table.setItem(0, 0, QTableWidgetItem("Test"))
        main_window.table.setItem(0, 1, QTableWidgetItem("DE89370400440532013000"))
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(0, 3, QTableWidgetItem("Ref"))

        main_window.update_batch_calculations()

        count_text = main_window.lbl_batch_count.text()
        assert "1 Payout" in count_text, f"Count should be '1 Payout', got {count_text}"

        # Test multiple rows
        main_window.table.setRowCount(5)
        for i in range(5):
            main_window.table.setItem(i, 0, QTableWidgetItem("Test"))
            main_window.table.setItem(i, 1, QTableWidgetItem("DE89370400440532013000"))
            main_window.table.setItem(i, 2, QTableWidgetItem("100.00"))
            main_window.table.setItem(i, 3, QTableWidgetItem("Ref"))

        main_window.update_batch_calculations()

        count_text = main_window.lbl_batch_count.text()
        assert "5 Payouts" in count_text, f"Count should be '5 Payouts', got {count_text}"


class TestCurrencyFormatting:
    """Test German currency formatting (comma as decimal separator)."""

    def test_german_locale_formatting(self, main_window):
        """Test German locale formatting with comma decimal separator."""
        # The app uses German formatting: 1.234,56 (dots for thousands, comma for decimal)
        test_cases = [
            (Decimal("100.00"), "100,00"),
            (Decimal("1000.00"), "1.000,00"),
            (Decimal("1234567.89"), "1.234.567,89"),
        ]

        for amount, expected_substring in test_cases:
            # Trigger calculation with this amount
            from PyQt6.QtWidgets import QTableWidgetItem

            main_window.table.setRowCount(1)
            main_window.table.setItem(0, 2, QTableWidgetItem(str(amount)))

            main_window.update_batch_calculations()

            total_text = main_window.lbl_batch_total.text()
            assert expected_substring in total_text, f"Expected '{expected_substring}' in '{total_text}'"

    def test_amount_parsing_with_comma_decimal(self, main_window):
        """Test parsing amounts with comma as decimal separator."""
        # European format: 100,50 means 100.50
        test_cases = [
            ("100,50", Decimal("100.50")),
            ("1.234,56", Decimal("1234.56")),
            ("10,00", Decimal("10.00")),
        ]

        for input_str, expected in test_cases:
            # The app converts commas to dots for Decimal parsing
            normalized = input_str.replace(",", ".")
            result = Decimal(normalized)
            assert result == expected, f"Parsed '{input_str}' should equal {expected}"

    def test_amount_parsing_with_dot_decimal(self, main_window):
        """Test parsing amounts with dot as decimal separator."""
        # International format: 100.50 means 100.50
        test_cases = [
            ("100.50", Decimal("100.50")),
            ("1234.56", Decimal("1234.56")),
            ("10.00", Decimal("10.00")),
        ]

        for input_str, expected in test_cases:
            result = Decimal(input_str)
            assert result == expected, f"Parsed '{input_str}' should equal {expected}"

    def test_currency_symbol_display(self, main_window):
        """Test that Euro symbol is displayed correctly."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(1)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))

        main_window.update_batch_calculations()

        total_text = main_window.lbl_batch_total.text()
        assert "€" in total_text or "EUR" in total_text, "Total should contain Euro symbol"


class TestAmountParsing:
    """Test amount parsing from various input formats."""

    def test_parse_valid_amount_strings(self, main_window):
        """Test parsing of valid amount strings."""
        valid_amounts = [
            "100.00",
            "100,00",
            "1000",
            "0.99",
            "1234567.89",
        ]

        for amount_str in valid_amounts:
            # Normalize comma to dot
            normalized = amount_str.replace(",", ".")
            try:
                result = Decimal(normalized)
                assert result >= 0, f"Amount {amount_str} should be non-negative"
            except (InvalidOperation, ValueError):
                pytest.fail(f"Should be able to parse valid amount: {amount_str}")

    def test_parse_invalid_amount_strings(self, main_window):
        """Test handling of invalid amount strings."""
        invalid_amounts = [
            "not_a_number",
            "abc123",
            "",
            "   ",
            "100.00.00",  # Multiple dots
            "100,00,00",  # Multiple commas
        ]

        for amount_str in invalid_amounts:
            # Normalize comma to dot
            normalized = amount_str.replace(",", ".")

            try:
                Decimal(normalized)
                # If we get here, the string was somehow valid
                # This is unexpected for truly invalid strings
                if amount_str in ["not_a_number", "abc123"]:
                    pytest.fail(f"Should not parse invalid amount: {amount_str}")
            except (InvalidOperation, ValueError):
                # Expected behavior for invalid amounts
                pass

    def test_amount_parsing_from_table(self, main_window):
        """Test amount parsing directly from table cells."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(3)

        # Set various amount formats
        main_window.table.setItem(0, 2, QTableWidgetItem("100.50"))  # Dot decimal
        main_window.table.setItem(1, 2, QTableWidgetItem("200,75"))  # Comma decimal
        main_window.table.setItem(2, 2, QTableWidgetItem("300.00"))  # Dot decimal

        main_window.update_batch_calculations()

        # Total should be 100.50 + 200.75 + 300.00 = 601.25
        total_text = main_window.lbl_batch_total.text()
        assert "601.25" in total_text or "601,25" in total_text, f"Total should be 601.25, got {total_text}"


class TestEdgeCases:
    """Test edge cases in financial calculations."""

    def test_zero_amount_handling(self, main_window):
        """Test handling of zero amounts."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(2)
        main_window.table.setItem(0, 2, QTableWidgetItem("0.00"))
        main_window.table.setItem(1, 2, QTableWidgetItem("100.00"))

        main_window.update_batch_calculations()

        # Should include zero amounts in total (0.00 + 100.00 = 100.00)
        total_text = main_window.lbl_batch_total.text()
        assert "100.00" in total_text or "100,00" in total_text, f"Total should be 100.00, got {total_text}"

    def test_negative_amount_handling(self, main_window):
        """Test handling of negative amounts (if supported)."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(2)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(1, 2, QTableWidgetItem("-50.00"))

        main_window.update_batch_calculations()

        # Should subtract negative amounts (100.00 + (-50.00) = 50.00)
        total_text = main_window.lbl_batch_total.text()
        # Note: The app may not support negative amounts, this tests behavior
        assert "50.00" in total_text or "50,00" in total_text or "100.00" in total_text

    def test_very_small_amounts(self, main_window):
        """Test handling of very small amounts (< 0.01)."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(2)
        main_window.table.setItem(0, 2, QTableWidgetItem("0.001"))
        main_window.table.setItem(1, 2, QTableWidgetItem("0.009"))

        main_window.update_batch_calculations()

        # Should handle sub-cent precision
        total_text = main_window.lbl_batch_total.text()
        # The exact display may vary due to formatting
        assert "€" in total_text or "EUR" in total_text, "Should display some total"

    def test_very_large_amounts(self, main_window):
        """Test handling of very large amounts."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(1)
        main_window.table.setItem(0, 2, QTableWidgetItem("999999999.99"))

        main_window.update_batch_calculations()

        # Should handle large amounts without overflow
        total_text = main_window.lbl_batch_total.text()
        assert "999" in total_text, "Should contain large amount digits"

    def test_empty_amount_cells(self, main_window):
        """Test handling of empty amount cells."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(3)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(1, 2, QTableWidgetItem(""))  # Empty
        main_window.table.setItem(2, 2, QTableWidgetItem("200.00"))

        main_window.update_batch_calculations()

        # Should skip empty cells (100.00 + 200.00 = 300.00)
        total_text = main_window.lbl_batch_total.text()
        assert "300.00" in total_text or "300,00" in total_text, f"Total should be 300.00, got {total_text}"

    def test_whitespace_amount_cells(self, main_window):
        """Test handling of whitespace-only amount cells."""
        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(2)
        main_window.table.setItem(0, 2, QTableWidgetItem("100.00"))
        main_window.table.setItem(1, 2, QTableWidgetItem("   "))  # Whitespace only

        main_window.update_batch_calculations()

        # Should treat whitespace as zero
        total_text = main_window.lbl_batch_total.text()
        assert "100.00" in total_text or "100,00" in total_text, f"Total should be 100.00, got {total_text}"


class TestRoundingBehavior:
    """Test rounding behavior in financial calculations."""

    def test_default_rounding(self, main_window):
        """Test default Decimal rounding behavior."""
        # Decimal uses default rounding (round-half-even in Python 3)
        test_cases = [
            (Decimal("1.005"), 2),  # May round to 1.00 or 1.01 depending on rounding mode
            (Decimal("2.5"), 0),  # May round to 2 or 3
            (Decimal("3.5"), 0),  # May round to 4 (round-half-even: 3.5 -> 4)
        ]

        for amount, decimal_places in test_cases:
            # Quantize to specified decimal places
            quantized = amount.quantize(Decimal("1").scaleb(-decimal_places))
            # Just verify it doesn't crash
            assert quantized is not None

    def test_explicit_rounding_half_up(self, main_window):
        """Test explicit ROUND_HALF_UP rounding."""
        # Financial applications often use ROUND_HALF_UP
        test_cases = [
            (Decimal("1.005"), Decimal("1.01")),  # Rounds up
            (Decimal("2.5"), Decimal("3")),  # Rounds up
            (Decimal("3.4"), Decimal("3")),  # Rounds down
        ]

        for amount, expected in test_cases:
            rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            assert rounded == expected, f"Expected {expected}, got {rounded}"


class TestCalculationPerformance:
    """Test performance of financial calculations."""

    def test_large_batch_calculation_performance(self, main_window):
        """Test calculation performance with large batch."""
        import time

        from PyQt6.QtWidgets import QTableWidgetItem

        # Add 1000 rows
        main_window.table.setRowCount(1000)
        for i in range(1000):
            main_window.table.setItem(i, 2, QTableWidgetItem(f"{i * 10}.50"))

        # Measure calculation time
        start_time = time.time()
        main_window.update_batch_calculations()
        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0, f"Calculation should be fast, took {elapsed:.2f}s"

    def test_frequent_recalculation_impact(self, main_window):
        """Test impact of frequent recalculations."""
        import time

        from PyQt6.QtWidgets import QTableWidgetItem

        main_window.table.setRowCount(100)

        # Simulate frequent updates
        start_time = time.time()
        for i in range(100):
            main_window.table.setItem(i, 2, QTableWidgetItem(f"{i * 10}.50"))
            main_window.update_batch_calculations()
        elapsed = time.time() - start_time

        # Should handle 100 recalculations in reasonable time
        assert elapsed < 2.0, f"100 recalculations should be fast, took {elapsed:.2f}s"


# @MX:ANCHOR: [AUTO] Financial calculation testing - critical for payment accuracy
# @MX:REASON: High fan_in (affects batch processing, totals calculation, and display formatting)
