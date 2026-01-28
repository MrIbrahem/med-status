"""Unit tests for utility functions."""

import pytest
import os
import tempfile

from src.utils import is_ip_address, escape_title, format_number, ensure_directory


@pytest.mark.unit
class TestUtils:
    """Test utility functions."""

    @pytest.mark.parametrize(
        "ip,expected",
        [
            ("192.168.1.1", True),
            ("255.255.255.255", True),
            ("Username123", False),
            ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", True),
            ("NotAnIP", False),
        ],
    )
    def test_is_ip_address(self, ip, expected):
        """Test IP address detection."""
        assert is_ip_address(ip) == expected

    def test_escape_title(self):
        """Test SQL title escaping."""
        # Test with apostrophe
        assert "\\'" in escape_title("O'Reilly")
        # Test normal title
        assert escape_title("Normal_Title") == "Normal_Title"

    @pytest.mark.parametrize(
        "num,expected",
        [
            (1234, "1,234"),
            (1234567, "1,234,567"),
            (0, "0"),
            (1000, "1,000"),
        ],
    )
    def test_format_number(self, num, expected):
        """Test number formatting."""
        assert format_number(num) == expected

    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "test_subdir")
            ensure_directory(test_dir)
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)
