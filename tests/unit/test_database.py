"""Unit tests for database module."""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock

from src.database import Database


@pytest.mark.unit
class TestDatabase:
    """Test Database class."""

    def test_database_init(self):
        """Test database initialization."""
        db = Database("localhost", "test_db")
        assert db.host == "localhost"
        assert db.database == "test_db"
        assert db.port == 3306

    def test_load_credentials(self):
        """Test credential loading."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=testuser\npassword=testpass\n")):
                db = Database("localhost", "test_db")
                creds = db._load_credentials()
                assert creds["user"] == "testuser"
                assert creds["password"] == "testpass"

    def test_context_manager(self):
        """Test database context manager."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                with patch("src.database.pymysql.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    with Database("localhost", "test_db") as db:
                        assert db.connection == mock_conn

                    mock_conn.close.assert_called_once()

    def test_execute_query(self):
        """Test query execution."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                with patch("src.database.pymysql.connect") as mock_connect:
                    mock_cursor = MagicMock()
                    mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
                    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
                    mock_cursor.__exit__ = Mock(return_value=False)

                    mock_conn = Mock()
                    mock_conn.cursor.return_value = mock_cursor
                    mock_connect.return_value = mock_conn

                    with Database("localhost", "test_db") as db:
                        results = db.execute("SELECT * FROM test")
                        assert len(results) == 1
                        assert results[0]["id"] == 1
