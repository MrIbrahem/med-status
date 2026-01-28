"""
Application configuration.

All configuration constants for the Wikipedia Medicine project.
"""

from datetime import datetime
from typing import Dict, Any

# Years (dynamically calculated)
CURRENT_YEAR: str = str(datetime.now().year)
LAST_YEAR: str = str(datetime.now().year - 1)

# Processing
BATCH_SIZE: int = 100
MAX_CONNECTIONS: int = 5
QUERY_TIMEOUT: int = 60
MAX_RETRIES: int = 3

# Database
CREDENTIAL_FILE: str = "~/replica.my.cnf"
DATABASE_PORT: int = 3306
DATABASE_CHARSET: str = "utf8mb4"

# Output directories
OUTPUT_DIRS: Dict[str, str] = {"languages": "languages", "editors": "editors", "reports": "reports"}

# Logging
LOG_LEVEL: str = "INFO"
LOG_FILE: str = None
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# Database connection parameters
DATABASE_CONFIG: Dict[str, Any] = {
    "port": DATABASE_PORT,
    "charset": DATABASE_CHARSET,
    "connect_timeout": 30,
    "read_timeout": QUERY_TIMEOUT,
    "autocommit": True,
}
