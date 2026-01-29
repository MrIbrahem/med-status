"""
Database connection management.

This module provides the Database class for managing connections to
Wikimedia Toolforge databases with connection pooling and retry logic.

See .claude/context/architecture.md for design details.
"""

import os
import time
from typing import Any, Dict, List, Optional

import pymysql
import pymysql.cursors

from ..config import CREDENTIAL_FILE, DATABASE_CONFIG, MAX_RETRIES
from ..logging_config import get_logger

logger = get_logger(__name__)


class DatabaseUtils:
    def __init__(self) -> None:
        pass

    def _check_database_name(self, dbname: str) -> str:
        """
        Ensure database name ends with '_p'.

        Args:
            dbname: Original database name

        Returns:
            Validated database name
        """
        pre_defined_db_mapping = {
            "gsw": "alswiki_p",
            "sgs": "bat_smgwiki_p",
            "bat-smg": "bat_smgwiki_p",
            "be-tarask": "be_x_oldwiki_p",
            "bho": "bhwiki_p",
            "cbk": "cbk_zamwiki_p",
            "cbk-zam": "cbk_zamwiki_p",
            "vro": "fiu_vrowiki_p",
            "fiu-vro": "fiu_vrowiki_p",
            "map-bms": "map_bmswiki_p",
            "nds-nl": "nds_nlwiki_p",
            "nb": "nowiki_p",
            "rup": "roa_rupwiki_p",
            "roa-rup": "roa_rupwiki_p",
            "roa-tara": "roa_tarawiki_p",
            "lzh": "zh_classicalwiki_p",
            "zh-classical": "zh_classicalwiki_p",
            "nan": "zh_min_nanwiki_p",
            "zh-min-nan": "zh_min_nanwiki_p",
            "yue": "zh_yuewiki_p",
            "zh-yue": "zh_yuewiki_p",
        }
        dbname = dbname.replace("-", "_")
        dbname_normalized = dbname.strip().lower().removesuffix("_p").removesuffix("wiki")
        if dbname_normalized in pre_defined_db_mapping:
            return pre_defined_db_mapping[dbname_normalized]

        if dbname_normalized == dbname.lower():
            # logger.warning("Database name '%s' missing 'wiki' suffix. Appending suffix.", dbname)
            return f"{dbname}wiki_p"

        if not dbname.endswith("_p"):
            # logger.warning("Database name '%s' does not end with '_p'. Appending suffix.", dbname)
            dbname += "_p"
        return dbname

    def resolve_bytes(self, data: Any) -> Any:
        """
        Recursively convert bytes in data structures to strings.

        Args:
            data: Input data (could be dict, list, bytes, or other types)

        Returns:
            The input data with all byte strings converted to regular strings
        """
        if isinstance(data, dict):
            return {self.resolve_bytes(key): self.resolve_bytes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.resolve_bytes(item) for item in data]
        elif isinstance(data, bytes):
            return data.decode("utf-8", errors="replace")
        return data


class Database(DatabaseUtils):
    """
    Context manager for database connections.

    Manages connections to Wikimedia Toolforge databases with:
    - Automatic credential loading from ~/replica.my.cnf
    - Connection retry logic with exponential backoff
    - Proper resource cleanup via context manager

    Attributes:
        host: Database host
        database: Database name
        port: Database port (default: 3306)

    Example:
        >>> with Database("enwiki.analytics.db.svc.wikimedia.cloud", "enwiki_p") as db:
        ...     results = db.execute("SELECT * FROM page LIMIT 10")
    """

    def __init__(self, host: str, database: str, port: int = 3306, timeout: Optional[float] = None) -> None:
        """
        Initialize database connection parameters.

        Args:
            host: Database host (e.g., "enwiki.analytics.db.svc.wikimedia.cloud")
            database: Database name (e.g., "enwiki_p")
            port: Database port (default: 3306)
            timeout: Connection timeout in seconds (default: None)
        """
        self.timeout = timeout
        self.host = host
        self.database = self._check_database_name(database)
        self.port = port
        self.connection: Optional[pymysql.connections.Connection] = None

        logger.debug("Database initialized: %s/%s", host, database)

    def __enter__(self) -> "Database":
        """
        Enter context manager - establish connection.

        Returns:
            self

        Raises:
            pymysql.err.OperationalError: If connection fails after retries
        """
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager - close connection."""
        if self.connection:
            self.connection.close()
            logger.debug("Connection closed: %s/%s", self.host, self.database)
            self.connection = None

    def _load_credentials(self) -> Dict[str, str]:
        """
        Load database credentials from ~/replica.my.cnf.

        Returns:
            Dictionary with 'user' and 'password'

        Raises:
            FileNotFoundError: If credential file doesn't exist
            ValueError: If credentials are malformed
        """

        if not os.path.exists(CREDENTIAL_FILE):
            logger.critical("Credential file not found: %s", CREDENTIAL_FILE)
            raise FileNotFoundError(f"Credential file not found: {CREDENTIAL_FILE}")

        credentials = {}
        with open(CREDENTIAL_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("user"):
                    credentials["user"] = line.split("=")[1].strip()
                elif line.startswith("password"):
                    credentials["password"] = line.split("=")[1].strip()

        if "user" not in credentials or "password" not in credentials:
            raise ValueError("Invalid credential file format")

        logger.debug("Credentials loaded from %s", CREDENTIAL_FILE)
        return credentials

    def _connect(self) -> None:
        """
        Establish database connection with retry logic.

        Raises:
            pymysql.err.OperationalError: If connection fails after max retries
        """
        credentials = self._load_credentials()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug("Connecting to %s/%s (attempt %d/%d)", self.host, self.database, attempt, MAX_RETRIES)

                # Merge config with connection parameters, avoiding duplicate port
                connect_params = DATABASE_CONFIG.copy()

                if connect_params.get("port"):
                    self.port = connect_params["port"]
                    connect_params.pop("port", None)  # Remove port from config if present

                if self.timeout is not None:
                    connect_params["connect_timeout"] = self.timeout

                logger.info(f"Connecting to database {self.database} at host {self.host}:{self.port}")

                self.connection = pymysql.connect(
                    host=self.host,
                    database=self.database,
                    port=self.port,
                    user=credentials["user"],
                    password=credentials["password"],
                    cursorclass=pymysql.cursors.DictCursor,
                    **connect_params,
                )

                logger.info("✓ Connected to %s/%s", self.host, self.database)
                return

            except pymysql.err.OperationalError as e:
                logger.warning("Connection failed (attempt %d/%d): %s", attempt, MAX_RETRIES, str(e))

                if attempt < MAX_RETRIES:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.info("Retrying in %d seconds...", wait_time)
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to connect after %d attempts", MAX_RETRIES)
                    raise

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries

        Raises:
            pymysql.err.ProgrammingError: If query has syntax errors
            pymysql.err.OperationalError: If query execution fails

        Example:
            >>> results = db.execute("SELECT page_title FROM page LIMIT 10")
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")

        try:
            with self.connection.cursor() as cursor:
                logger.debug("Executing query: %s...", query[:100])
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.debug("Query returned %d rows", len(results))
                return self.resolve_bytes(results)

        except pymysql.err.ProgrammingError as e:
            logger.error("Query syntax error: %s\nQuery: %s", str(e), query[:200])
            raise

        except pymysql.err.OperationalError as e:
            logger.error("Query execution error: %s", str(e))
            raise
