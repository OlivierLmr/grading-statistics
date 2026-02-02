"""
Unit tests for utility functions.

Tests the round_up() function and other utilities.
"""
import pytest
import math
from grading import round_up


@pytest.mark.unit
class TestRoundUp:
    """Tests for the round_up() function."""

    def test_round_up_no_rounding_needed(self):
        """Test round_up when no rounding is needed."""
        assert round_up(1.1, 1) == 1.1
        assert round_up(2.5, 1) == 2.5
        assert round_up(3.0, 1) == 3.0

    def test_round_up_rounds_up(self):
        """Test round_up actually rounds up."""
        assert round_up(1.11, 1) == 1.2
        assert round_up(1.15, 1) == 1.2
        assert round_up(1.19, 1) == 1.2
        assert round_up(2.01, 1) == 2.1

    def test_round_up_zero(self):
        """Test round_up with zero."""
        assert round_up(0.0, 1) == 0.0
        assert round_up(0.01, 1) == 0.1

    def test_round_up_negative_numbers(self):
        """Test round_up with negative numbers."""
        assert round_up(-1.1, 1) == -1.1
        assert round_up(-1.15, 1) == -1.1
        assert round_up(-2.01, 1) == -2.0

    def test_round_up_large_numbers(self):
        """Test round_up with large numbers."""
        assert round_up(999.99, 1) == 1000.0
        assert round_up(1234.567, 1) == 1234.6

    def test_round_up_different_precision(self):
        """Test round_up with different precision values."""
        # 2 decimal places
        assert round_up(1.111, 2) == 1.12
        assert round_up(1.119, 2) == 1.12

        # 0 decimal places (whole numbers)
        assert round_up(1.1, 0) == 2.0
        assert round_up(1.9, 0) == 2.0
        assert round_up(2.0, 0) == 2.0

    def test_round_up_edge_cases(self):
        """Test round_up edge cases."""
        # Already at precision boundary
        assert round_up(1.2, 1) == 1.2
        assert round_up(1.5, 1) == 1.5

        # Very small increments
        assert round_up(1.000001, 1) == 1.1

        # Multiple of precision
        assert round_up(5.0, 1) == 5.0
        assert round_up(5.5, 1) == 5.5

    @pytest.mark.parametrize("value,digits,expected", [
        (1.1, 1, 1.1),
        (1.11, 1, 1.2),
        (1.15, 1, 1.2),
        (1.19, 1, 1.2),
        (2.01, 1, 2.1),
        (5.91, 1, 6.0),
        (0.01, 1, 0.1),
        (1.111, 2, 1.12),
        (1.115, 2, 1.12),
    ])
    def test_round_up_parametrized(self, value, digits, expected):
        """Parametrized tests for round_up."""
        result = round_up(value, digits)
        assert result == pytest.approx(expected, abs=1e-10)

    def test_round_up_consistency_with_ceil(self):
        """Test that round_up behaves like ceil at the appropriate scale."""
        # round_up should be equivalent to scaling, ceiling, and scaling back
        for value in [1.11, 1.15, 1.19, 2.01, 3.456]:
            result = round_up(value, 1)
            expected = math.ceil(value * 10) / 10
            assert result == pytest.approx(expected, abs=1e-10)
