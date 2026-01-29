""" """

from typing import Optional

from ..logging_config import get_logger
from .database import Database
from .db_mapping import get_database_name_for_language

logger = get_logger(__name__)


class DatabaseAnalytics:
    """
    Context manager for analytics database connections.

    Simplifies connecting to Wikimedia Toolforge analytics databases.

    Example:
        >>> with DatabaseAnalytics("en") as db:
        ...     results = db.execute("SELECT * FROM page LIMIT 10")
    """

    def __init__(self, site_code: str, timeout: Optional[float] = None) -> None:
        """
        Initialize analytics database connection parameters.

        Args:
            site_code: Language code (e.g., "en", "fr", "ar")
            timeout: Connection timeout in seconds
        """
        database, host = self.get_database_info(site_code)
        self.timeout = timeout
        self.database = database
        self.host = host
        self.db = None

    def get_database_info(self, site_code: str) -> tuple[str, str]:
        pre_defined_db_mapping = {
            "meta": ("meta_p", "s7.analytics.db.svc.wikimedia.cloud"),
        }

        if site_code in pre_defined_db_mapping:
            return pre_defined_db_mapping[site_code]

        site_code = site_code.replace("-", "_")
        site_code = site_code.lower().removesuffix("wiki")

        database = get_database_name_for_language(site_code) or f"{site_code}wiki_p"

        host_name = database.removesuffix("_p")
        host = f"{host_name}.analytics.db.svc.wikimedia.cloud"
        return database, host

    def __enter__(self) -> Database:
        """
        Enter context manager - establish connection.

        Returns:
            Database instance
        """
        self.db = Database(self.host, self.database, timeout=self.timeout)
        return self.db.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager - close connection."""
        self.db.__exit__(exc_type, exc_val, exc_tb)
