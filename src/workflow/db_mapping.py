"""

"""

from typing import Dict
from ..config import HOST
from ..logging_config import get_logger
from ..services.database import Database
from ..services.queries import QueryBuilder

logger = get_logger(__name__)

query_builder = QueryBuilder()


def get_database_mapping() -> Dict[str, str]:
    """
    Get mapping of language codes to database names from meta_p.

    Returns:
        Dictionary mapping language codes to database names

    Example:
        >>> orchestrator = WorkflowOrchestrator()
        >>> mapping = orchestrator.get_database_mapping()
        >>> # Returns: {"en": "enwiki_p", "fr": "frwiki_p", ...}
    """
    logger.info("Retrieving database name mappings from meta_p")

    mapping: Dict[str, str] = {}

    query = query_builder.get_database_mapping()

    with Database(HOST, "meta_p") as db:
        results = db.execute(query)

        for row in results:
            lang = row.get("lang", "")
            dbname = row.get("dbname", "")

            if lang and dbname:
                mapping[lang] = dbname

        logger.info("✓ Retrieved mappings for %d languages", len(mapping))

    return mapping
