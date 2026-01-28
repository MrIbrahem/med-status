"""
Step 1: Retrieve medicine titles
"""

from typing import Dict, List

from ..config import OUTPUT_DIRS
from ..logging_config import get_logger
from ..services.database import Database
from ..services.queries import QueryBuilder
from ..utils import save_language_titles

logger = get_logger(__name__)


def _organize_titles_by_language(results: List[Dict]) -> Dict[str, List[str]]:
    """Organize query results by language."""
    titles_by_language: Dict[str, List[str]] = {}

    # Process langlinks
    for row in results:
        lang = row.get("ll_lang", "")
        title = row.get("ll_title", "")

        if lang and title:
            if lang not in titles_by_language:
                titles_by_language[lang] = []
            titles_by_language[lang].append(title)

    # Add English titles
    for row in results:
        en_title = row.get("page_title", "")
        if en_title:
            if "en" not in titles_by_language:
                titles_by_language["en"] = []
            if en_title not in titles_by_language["en"]:
                titles_by_language["en"].append(en_title)

    return titles_by_language


def _save_language_files(titles_by_language: Dict[str, List[str]]) -> None:
    """Save title lists to language files."""
    for lang, titles in titles_by_language.items():
        save_language_titles(lang, titles, OUTPUT_DIRS["languages"])


def retrieve_medicine_titles(host: str = "analytics.db.svc.wikimedia.cloud") -> Dict[str, List[str]]:
    """
    Retrieve Medicine project articles with langlinks from enwiki.

    Returns:
        Dictionary mapping language codes to lists of article titles

    Example:
        >>> orchestrator = WorkflowOrchestrator()
        >>> titles = orchestrator.retrieve_medicine_titles()
        >>> # Returns: {"en": ["Medicine"], "fr": ["Médecine"], ...}
    """
    logger.info("=" * 60)
    logger.info("Step 1: Retrieving Medicine articles from enwiki")
    logger.info("=" * 60)
    query_builder = QueryBuilder()
    try:
        query = query_builder.get_medicine_titles()

        with Database(host, "enwiki_p") as db:
            results = db.execute(query)
            logger.info("Retrieved %d article-language pairs", len(results))

            titles_by_language = _organize_titles_by_language(results)
            _save_language_files(titles_by_language)

            logger.info("✓ Found %d languages with %d total articles", len(titles_by_language), len(results))

    except Exception as e:
        logger.error("Failed to retrieve medicine titles: %s", str(e), exc_info=True)
        raise

    return titles_by_language


__all__ = [
    "retrieve_medicine_titles",
]
