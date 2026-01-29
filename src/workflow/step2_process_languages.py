"""
Step 2: Process languages
"""

from typing import Dict, List, Optional

from tqdm import tqdm

from ..config import BATCH_SIZE, OUTPUT_DIRS
from ..logging_config import get_logger
from ..services import EditorProcessor, QueryBuilder, ReportGenerator
from ..utils import get_available_languages, load_language_titles_safe

logger = get_logger(__name__)

processor = EditorProcessor()
query_builder = QueryBuilder()


def _get_languages_to_process(languages: Optional[List[str]]) -> List[str]:
    """Determine which languages to process."""
    available_languages = get_available_languages(OUTPUT_DIRS["languages"])

    if languages:
        languages_to_process = [lang for lang in languages if lang in available_languages]
        if len(languages_to_process) < len(languages):
            missing = set(languages) - set(languages_to_process)
            logger.warning("Requested languages not found: %s", missing)
        return languages_to_process
    else:
        return available_languages


def _process_single_language(
    lang: str,
    year: str,
    batch_size: int,
    titles: List[str],
) -> Dict[str, int]:
    """Process a single language."""
    report_generator = ReportGenerator()

    editors = _process_titles_for_language(lang, titles, year, batch_size)

    if editors:
        report_generator.save_editors_json(lang, editors)
        report_generator.generate_language_report(lang, editors, year)

    logger.info("✓ Language '%s' complete: %d editors, %d edits", lang, len(editors), sum(editors.values()))
    return editors


def _process_titles_for_language(
    lang: str,
    titles: List[str],
    year: str,
    batch_size: int,
) -> Dict[str, int]:
    """Process titles for a language, with batching if needed."""
    if len(titles) <= batch_size:
        return processor.process_language(lang, titles, year)

    logger.info("Processing %d titles in batches of %d", len(titles), batch_size)
    editors: Dict[str, int] = {}

    for batch_num in range(0, len(titles), batch_size):
        batch = titles[batch_num : batch_num + batch_size]
        logger.debug("Processing batch %d-%d", batch_num, batch_num + len(batch))

        batch_editors = processor.process_language(lang, batch, year)

        # Merge batch results
        for editor, count in batch_editors.items():
            if editor in editors:
                editors[editor] += count
            else:
                editors[editor] = count

    return editors


def gather_language_titles(languages_to_process: List[str], sort_descending: bool = False) -> dict[str, list[str]]:
    """
    Gather titles for all languages to process.

    Args:
        languages_to_process: List of language codes to process

    Returns:
        Dictionary mapping language codes to their article titles
    """
    languages_titles: dict[str, list[str]] = {}
    for lang in tqdm(languages_to_process, desc="Loading language titles"):
        titles: List[str] = load_language_titles_safe(lang, OUTPUT_DIRS["languages"])
        languages_titles[lang] = titles

    languages_titles = dict(sorted(languages_titles.items(), key=lambda item: len(item[1]), reverse=sort_descending))

    return languages_titles


def process_languages(
    year: str,
    languages: Optional[List[str]] = None,
    batch_size: int = BATCH_SIZE,
    sort_descending: bool = False,
) -> Dict[str, Dict[str, int]]:
    """
    Process editor statistics for all or specified languages.

    Args:
        year: Year to analyze (e.g., "2024")
        languages: Optional list of specific languages to process
        batch_size: Batch size for processing titles (default: from config)

    Returns:
        Dictionary mapping language codes to editor statistics

    Example:
        >>> all_editors = orchestrator.process_languages("2024", ["en", "fr"])
    """
    logger.info("=" * 60)
    logger.info("Step 2: Processing editor statistics by language")
    logger.info("=" * 60)

    languages_to_process: List[str] = _get_languages_to_process(languages)

    logger.info("Processing %d languages", len(languages_to_process))

    languages_titles: dict[str, list[str]] = gather_language_titles(
        languages_to_process, sort_descending=sort_descending
    )

    all_editors: Dict[str, Dict[str, int]] = {}

    for i, (lang, titles) in enumerate(languages_titles.items(), 1):
        logger.info("-" * 60)
        logger.info("Language %d/%d: %s", i, len(languages_titles), lang)
        logger.info("-" * 60)
        lang_editors = _process_single_language(lang, year, batch_size, titles)
        if lang_editors:
            all_editors[lang] = lang_editors

    logger.info("")
    logger.info("✓ Step 2 complete: %d languages processed", len(all_editors))

    return all_editors


__all__ = [
    "process_languages",
]
