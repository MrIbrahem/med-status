"""Unit tests for database module."""

from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from src.services.database import Database, DatabaseUtils


@pytest.mark.unit
class TestDatabase:
    """Test Database class."""

    def test_database_init(self):
        """Test database initialization."""
        db = Database("localhost", "test")
        assert db.host == "localhost"
        assert db.database == "testwiki_p"
        assert db.port == 3306

    def test_load_credentials(self):
        """Test credential loading."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=testuser\npassword=testpass\n")):
                db = Database("localhost", "test")
                creds = db._load_credentials()
                assert creds["user"] == "testuser"
                assert creds["password"] == "testpass"

    def test_context_manager(self):
        """Test database context manager."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                with patch("src.services.database.pymysql.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    with Database("localhost", "test") as db:
                        assert db.connection == mock_conn

                    mock_conn.close.assert_called_once()

    def test_execute_query(self):
        """Test query execution."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                with patch("src.services.database.pymysql.connect") as mock_connect:
                    mock_cursor = MagicMock()
                    mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
                    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
                    mock_cursor.__exit__ = Mock(return_value=False)

                    mock_conn = Mock()
                    mock_conn.cursor.return_value = mock_cursor
                    mock_connect.return_value = mock_conn

                    with Database("localhost", "test") as db:
                        results = db.execute("SELECT * FROM test")
                        assert len(results) == 1
                        assert results[0]["id"] == 1


@pytest.mark.unit
class TestDatabaseUtils:
    """Test DatabaseUtils class."""

    def test_check_database_name(self):
        """Test getting database name for language."""
        db_utils = DatabaseUtils()
        db_name = db_utils._check_database_name("en")
        assert db_name == "enwiki_p"

        db_name = db_utils._check_database_name("enwiki")
        assert db_name == "enwiki_p"

        db_name = db_utils._check_database_name("enwiki_p")
        assert db_name == "enwiki_p"

        db_name = db_utils._check_database_name("de")
        assert db_name == "dewiki_p"

    def test_check_database_name_special_cases(self):
        """Test getting database name for language."""
        db_utils = DatabaseUtils()
        db_name = db_utils._check_database_name("vro")
        assert db_name == "fiu_vrowiki_p"

        db_name = db_utils._check_database_name("vrowiki_p")
        assert db_name == "fiu_vrowiki_p"

    def test_check_database_name_special_cases_gsw(self):
        db_utils = DatabaseUtils()
        db_name1 = db_utils._check_database_name("gsw")
        db_name2 = db_utils._check_database_name("gswwiki")
        db_name3 = db_utils._check_database_name("gswwiki_p")

        assert db_name1 == "alswiki_p"
        assert db_name1 == db_name2 == db_name3
