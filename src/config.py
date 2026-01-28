"""
Application configuration.

All configuration constants for the Wikipedia Medicine project.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Years (dynamically calculated)
LAST_YEAR: str = str(datetime.now().year - 1)

# Processing
BATCH_SIZE: int = 100
MAX_CONNECTIONS: int = 5
QUERY_TIMEOUT: int = 60
MAX_RETRIES: int = 3

# Database
DATABASE_CHARSET: str = "utf8mb4"

CREDENTIAL_FILE: str = os.getenv("CREDENTIAL_FILE", "~/replica.my.cnf")
CREDENTIAL_FILE = os.path.expanduser(CREDENTIAL_FILE)

HOST: str = os.getenv("DB_HOST", "analytics.db.svc.wikimedia.cloud")
DATABASE_PORT: int = int(os.getenv("DB_PORT", 3306))

DATA_DIR = os.getenv("DATA_DIR", "~/data")
DATA_DIR = Path(DATA_DIR).expanduser()

# Output directories
OUTPUT_DIRS: Dict[str, Path] = {
    "languages": DATA_DIR / "languages",
    "editors": DATA_DIR / "editors",
    "reports": DATA_DIR / "reports",
}

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
