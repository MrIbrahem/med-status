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

    def test_check_database_name_special_cases_under(self):
        db_utils = DatabaseUtils()
        db_name1 = db_utils._check_database_name("be-x-old")
        db_name2 = db_utils._check_database_name("be-x-oldwiki")
        db_name3 = db_utils._check_database_name("be-x-oldwiki_p")

        assert db_name1 == "be_x_oldwiki_p"
        assert db_name1 == db_name2 == db_name3

    def test_resolve_bytes_with_bytes(self):
        """Test resolve_bytes with bytes input."""
        db_utils = DatabaseUtils()
        result = db_utils.resolve_bytes(b"test string")
        assert result == "test string"

    def test_resolve_bytes_with_bytes_invalid_utf8(self):
        """Test resolve_bytes with invalid UTF-8 bytes."""
        db_utils = DatabaseUtils()
        # Invalid UTF-8 sequence
        result = db_utils.resolve_bytes(b"\xff\xfe")
        assert isinstance(result, str)

    def test_resolve_bytes_with_dict(self):
        """Test resolve_bytes with dict containing bytes."""
        db_utils = DatabaseUtils()
        result = db_utils.resolve_bytes({"key": b"value", "num": 42})
        assert result["key"] == "value"
        assert result["num"] == 42

    def test_resolve_bytes_with_list(self):
        """Test resolve_bytes with list containing bytes."""
        db_utils = DatabaseUtils()
        result = db_utils.resolve_bytes([b"item1", b"item2", "regular"])
        assert result == ["item1", "item2", "regular"]

    def test_resolve_bytes_with_nested_structure(self):
        """Test resolve_bytes with nested structure."""
        db_utils = DatabaseUtils()
        result = db_utils.resolve_bytes({"list": [b"item"], "dict": {b"key": b"value"}})
        assert result["list"] == ["item"]
        assert result["dict"]["key"] == "value"


@pytest.mark.unit
class TestDatabaseEdgeCases:
    """Test Database edge cases and error handling."""

    def test_exit_without_connection(self):
        """Test __exit__ when connection is None."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                db = Database("localhost", "test")
                # Don't enter context, so connection remains None
                db.__exit__(None, None, None)
                assert db.connection is None

    def test_load_credentials_file_not_found(self):
        """Test _load_credentials when credential file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            db = Database("localhost", "test")
            with pytest.raises(FileNotFoundError, match="Credential file not found"):
                db._load_credentials()

    def test_load_credentials_malformed_missing_user(self):
        """Test _load_credentials when user is missing."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="password=pass\n")):
                db = Database("localhost", "test")
                with pytest.raises(ValueError, match="Invalid credential file format"):
                    db._load_credentials()

    def test_load_credentials_malformed_missing_password(self):
        """Test _load_credentials when password is missing."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\n")):
                db = Database("localhost", "test")
                with pytest.raises(ValueError, match="Invalid credential file format"):
                    db._load_credentials()

    def test_load_credentials_empty_lines(self):
        """Test _load_credentials with empty lines."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="\nuser=test\n\npassword=pass\n")):
                db = Database("localhost", "test")
                creds = db._load_credentials()
                assert creds["user"] == "test"
                assert creds["password"] == "pass"

    def test_load_credentials_with_comments(self):
        """Test _load_credentials ignores lines that don't start with user/password."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="# comment\nuser=test\npassword=pass\n")):
                db = Database("localhost", "test")
                creds = db._load_credentials()
                assert creds["user"] == "test"
                assert creds["password"] == "pass"

    def test_connect_with_retry_success(self, mocker):
        """Test _connect with retry on first failure, success on second."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                import pymysql

                mock_conn = Mock()
                # First call fails, second succeeds
                mocker.patch.object(
                    pymysql,
                    "connect",
                    side_effect=[
                        pymysql.err.OperationalError(1205, "Lock wait timeout"),
                        mock_conn,
                    ],
                )

                db = Database("localhost", "test")
                mocker.patch("time.sleep")  # Skip actual sleep

                db._connect()
                assert db.connection == mock_conn

    def test_connect_with_retry_exhausted(self, mocker):
        """Test _connect when all retries are exhausted."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                import pymysql

                mocker.patch.object(
                    pymysql,
                    "connect",
                    side_effect=pymysql.err.OperationalError(1205, "Lock wait timeout"),
                )

                db = Database("localhost", "test")
                mocker.patch("time.sleep")  # Skip actual sleep

                with pytest.raises(pymysql.err.OperationalError):
                    db._connect()

    def test_execute_without_connection(self):
        """Test execute when connection is not established."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                db = Database("localhost", "test")
                # Don't enter context, connection remains None
                with pytest.raises(RuntimeError, match="Database connection not established"):
                    db.execute("SELECT * FROM test")

    def test_execute_with_programming_error(self):
        """Test execute with SQL syntax error."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                import pymysql

                mock_cursor = MagicMock()
                mock_cursor.execute.side_effect = pymysql.err.ProgrammingError(1064, "syntax error")
                mock_cursor.__enter__ = Mock(return_value=mock_cursor)
                mock_cursor.__exit__ = Mock(return_value=False)

                mock_conn = Mock()
                mock_conn.cursor.return_value = mock_cursor

                with patch("src.services.database.pymysql.connect", return_value=mock_conn):
                    with Database("localhost", "test") as db:
                        with pytest.raises(pymysql.err.ProgrammingError):
                            db.execute("INVALID SQL")

    def test_execute_with_operational_error(self):
        """Test execute with operational error during query execution."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                import pymysql

                mock_cursor = MagicMock()
                mock_cursor.execute.side_effect = pymysql.err.OperationalError(2002, "Connection lost")
                mock_cursor.__enter__ = Mock(return_value=mock_cursor)
                mock_cursor.__exit__ = Mock(return_value=False)

                mock_conn = Mock()
                mock_conn.cursor.return_value = mock_cursor

                with patch("src.services.database.pymysql.connect", return_value=mock_conn):
                    with Database("localhost", "test") as db:
                        with pytest.raises(pymysql.err.OperationalError):
                            db.execute("SELECT * FROM test")

    def test_connect_port_from_database_config(self, mocker):
        """Test that port from DATABASE_CONFIG is properly handled."""
        # Import the actual DATABASE_CONFIG which contains a port
        from src.config import DATABASE_CONFIG

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                mock_conn = Mock()

                # Use side_effect to verify connection params include the port
                original_connect = mocker.patch("src.services.database.pymysql.connect", return_value=mock_conn)

                db = Database("localhost", "test", port=9999)  # Different port
                db._connect()

                # The DATABASE_CONFIG port should override the initial port
                assert db.port == DATABASE_CONFIG.get("port", 3306)
                # Verify connect was called
                original_connect.assert_called_once()

    def test_connect_without_port_in_database_config(self, mocker):
        """Test connect when DATABASE_CONFIG has no port (uses initial port)."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="user=test\npassword=pass\n")):
                mock_conn = Mock()
                mocker.patch("src.services.database.pymysql.connect", return_value=mock_conn)

                # Patch DATABASE_CONFIG without a port
                mocker.patch("src.services.database.DATABASE_CONFIG", {})

                db = Database("localhost", "test", port=3307)
                db._connect()

                # The initial port should be preserved
                assert db.port == 3307
