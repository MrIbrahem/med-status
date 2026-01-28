"""Unit tests for utility functions."""
import pytest

# Skip all tests until src.utils module is implemented
pytest.importorskip("src.utils")
from src.utils import is_ip_address, escape_title

@pytest.mark.unit
class TestUtils:
    """Test utility functions."""
    
    @pytest.mark.parametrize("ip,expected", [
        ("192.168.1.1", True),
        ("Username123", False),
        ("2001:0db8:85a3::8a2e:0370:7334", True),
        ("NotAnIP", False),
    ])
    def test_is_ip_address(self, ip, expected):
        """Test IP address detection."""
        assert is_ip_address(ip) == expected
    
    def test_escape_title(self):
        """Test SQL title escaping."""
        title = "Test'Title"
        escaped = escape_title(title)
        # Verify that apostrophes are properly escaped or replaced
        assert escaped == title.replace("'", "\\'") or escaped == title.replace("'", "''")
