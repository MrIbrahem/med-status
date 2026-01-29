""" """

import functools
import json
from pathlib import Path
from typing import Dict

from ..config import OUTPUT_DIRS
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
    Get mapping of language codes to database names from meta database.

    Returns:
        Dictionary mapping language codes to database names

    Example:
        >>> orchestrator = WorkflowOrchestrator()
        >>> mapping = orchestrator.get_database_mapping()
        >>> # Returns: {"en": "enwiki", "fr": "frwiki", ...}
    """
    logger.info("Retrieving database name mappings from meta database")

    mapping: Dict[str, str] = {}

    query = query_builder.get_database_mapping()

    with Database("s7.analytics.db.svc.wikimedia.cloud", "meta_p") as db:
        results = db.execute(query)

        for row in results:
            url = row.get("url", "")
            lang = row.get("lang", "")
            dbname = row.get("dbname", "")
            url_lang = url.split(".")[0].replace("https://", "")

            if not dbname:
                continue
            if lang:
                mapping[lang] = dbname
            if url:
                mapping[url_lang] = dbname

        logger.info("✓ Retrieved mappings for %d languages", len(mapping))

    # Ensure English value to avoid ("en", "testwiki", "https://test.wikipedia.org") entry
    mapping["en"] = "enwiki"
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


def get_database_name_for_language(language: str) -> str:
    """
    Get the database name for a specific language code.
    Args:
        language (str): The language code to look up.
    Returns:
        str: The corresponding database name, or an empty string if not found.
    Example:
        >>> db_name = get_database_name_for_language("en")
        >>> print(db_name)
        "enwiki_p"
    """
    pre_defined_db_mapping = {
        "gsw": "alswiki",
        "sgs": "bat_smgwiki",
        "bat-smg": "bat_smgwiki",
        "be-tarask": "be_x_oldwiki",
        "bho": "bhwiki",
        "cbk": "cbk_zamwiki",
        "cbk-zam": "cbk_zamwiki",
        "vro": "fiu_vrowiki",
        "fiu-vro": "fiu_vrowiki",
        "map-bms": "map_bmswiki",
        "nds-nl": "nds_nlwiki",
        "nb": "nowiki",
        "rup": "roa_rupwiki",
        "roa-rup": "roa_rupwiki",
        "roa-tara": "roa_tarawiki",
        "lzh": "zh_classicalwiki",
        "zh-classical": "zh_classicalwiki",
        "nan": "zh_min_nanwiki",
        "zh-min-nan": "zh_min_nanwiki",
        "yue": "zh_yuewiki",
        "zh-yue": "zh_yuewiki",
    }

    if language in pre_defined_db_mapping:
        return pre_defined_db_mapping[language]

    mapping: Dict[str, str] = get_database_mapping()

    return mapping.get(language, "")
