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

from src.config import DATABASE_CONFIG, CREDENTIAL_FILE, MAX_RETRIES
from src.logging_config import get_logger

logger = get_logger(__name__)


class Database:
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

    def __init__(self, host: str, database: str, port: int = 3306):
        """
        Initialize database connection parameters.

        Args:
            host: Database host (e.g., "enwiki.analytics.db.svc.wikimedia.cloud")
            database: Database name (e.g., "enwiki_p")
            port: Database port (default: 3306)
        """
        self.host = host
        self.database = database
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
        cred_file = os.path.expanduser(CREDENTIAL_FILE)

        if not os.path.exists(cred_file):
            logger.critical("Credential file not found: %s", cred_file)
            raise FileNotFoundError(f"Credential file not found: {cred_file}")

        credentials = {}
        with open(cred_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("user"):
                    credentials["user"] = line.split("=")[1].strip()
                elif line.startswith("password"):
                    credentials["password"] = line.split("=")[1].strip()

        if "user" not in credentials or "password" not in credentials:
            raise ValueError("Invalid credential file format")

        logger.debug("Credentials loaded from %s", cred_file)
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
                connect_params.pop("port", None)  # Remove port from config if present

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
                return results

        except pymysql.err.ProgrammingError as e:
            logger.error("Query syntax error: %s\nQuery: %s", str(e), query[:200])
            raise

        except pymysql.err.OperationalError as e:
            logger.error("Query execution error: %s", str(e))
            raise
