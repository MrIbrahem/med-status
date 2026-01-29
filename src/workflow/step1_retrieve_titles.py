"""
Step 1: Retrieve medicine titles
"""

from typing import Any, Dict, List

from tqdm import tqdm

from ..config import OUTPUT_DIRS
from ..logging_config import get_logger
from ..services import DatabaseAnalytics, QueryBuilder
from ..utils import save_language_titles, save_titles_sql_results

logger = get_logger(__name__)


def _organize_titles_by_language(results: List[Dict]) -> Dict[str, List[str]]:
    en_titles = set()
    titles_by_language = {"en": []}

    for x in tqdm(results, desc="Organizing titles by language", unit="rows"):
        lang = x.get("ll_lang", "")
        title = x.get("ll_title", "")

        if lang and title:
            titles_by_language.setdefault(lang, []).append(title)

        en_titles.add(x.get("page_title", ""))

    titles_by_language["en"] = list(en_titles)

    return titles_by_language


def _save_language_summary_report(titles_by_language: Dict[str, List[str]]) -> None:
    """
    Save summary report of titles by language.
    """
    data = {lang: len(titles) for lang, titles in titles_by_language.items()}
    data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    output_file = OUTPUT_DIRS["reports"] / "language_titles_summary.wiki"

    wiki_text = "Language Titles Summary:\n"
    wiki_text += '{| class="wikitable"\n! Language !! Number of Titles\n'
    for lang, count in data.items():
        wiki_text += f"|-\n| [https://{lang}.wikipedia.org/wiki/ {lang}] || {count}\n"
    wiki_text += "|}\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(wiki_text)
    logger.info(" ✓ Saved language titles summary report to %s", output_file.name)


def _save_language_files(titles_by_language: Dict[str, List[str]]) -> None:
    """Save title lists to language files."""
    for lang, titles in titles_by_language.items():
        save_language_titles(lang, titles, OUTPUT_DIRS["languages"])


def fetch_medicine_titles() -> List[Dict[str, Any]]:
    """
    Retrieve Medicine project articles with langlinks from enwiki.
    """
    query_builder = QueryBuilder()
    query = query_builder.get_medicine_titles()
    results = []

    try:
        with DatabaseAnalytics("en") as db:
            results = db.execute(query)
    except Exception as e:
        logger.error("Failed to retrieve medicine titles: %s", str(e), exc_info=True)

    if results:
        save_titles_sql_results(results, OUTPUT_DIRS["sqlresults"])

    return results


def download_medicine_titles() -> None:
    """
    Retrieve Medicine project articles with langlinks from enwiki.

    Returns:
        Dictionary mapping language codes to lists of article titles

    Example:
        >>> orchestrator = WorkflowOrchestrator()
        >>> titles = orchestrator.download_medicine_titles()
        >>> # Returns: {"en": ["Medicine"], "fr": ["Médecine"], ...}
    """
    logger.info("=" * 60)
    logger.info("Step 1: Retrieving Medicine articles from enwiki")
    logger.info("=" * 60)

    results = fetch_medicine_titles()
    logger.info("Retrieved %d article-language pairs", len(results))

    titles_by_language = _organize_titles_by_language(results)
    _save_language_files(titles_by_language)
    _save_language_summary_report(titles_by_language)

    logger.info("✓ Found %d languages with %d total articles", len(titles_by_language), len(results))


__all__ = [
    "download_medicine_titles",
]
