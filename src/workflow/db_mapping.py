"""

"""
import functools
import json
from pathlib import Path
from typing import Dict
from ..config import HOST, OUTPUT_DIRS
from ..logging_config import get_logger
from ..services.database import Database
from ..services.queries import QueryBuilder

logger = get_logger(__name__)

query_builder = QueryBuilder()


def save_db_mapping(mapping_list: Dict[str, str]) -> None:
    """
    Save database mapping to JSON file.
    """
    output_file = Path(OUTPUT_DIRS["sqlresults"]) / "db_mapping.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(mapping_list, f, ensure_ascii=False, indent=2)

    logger.debug("Saved %d mappings to %s", len(mapping_list), output_file)


def load_db_mapping() -> Dict[str, str]:
    """
    Load database mapping from JSON file.

    Returns:
        List of database mappings
    """
    input_file = Path(OUTPUT_DIRS["sqlresults"]) / "db_mapping.json"

    if not input_file.exists():
        return {}

    with open(input_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    logger.debug("Loaded %d mappings from %s", len(mapping), input_file)
    return mapping


def fetch_database_mapping() -> Dict[str, str]:
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
            url = row.get("url", "")
            lang = row.get("lang", "")
            dbname = row.get("dbname", "")
            if not dbname:
                continue
            if lang:
                mapping[lang] = dbname
            if url:
                url_lang = url.split(".")[0].replace("https://", "")
                mapping[url_lang] = dbname

        logger.info("✓ Retrieved mappings for %d languages", len(mapping))

    return mapping


@functools.lru_cache(maxsize=1)
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

    mapping: Dict[str, str] = load_db_mapping()
    if not mapping:
        mapping = fetch_database_mapping()
        save_db_mapping(mapping)

    return mapping
