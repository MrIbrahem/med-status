"""
Step 3: Generate global reports
"""

from typing import Dict

from ..config import OUTPUT_DIRS
from ..logging_config import get_logger
from ..services import ReportGenerator
from ..utils import get_available_languages

logger = get_logger(__name__)


def generate_reports(all_editors: Dict[str, Dict[str, int]], year: str) -> None:
    """
    Generate global summary report.

    Args:
        all_editors: Dictionary mapping language codes to editor statistics
        year: Year of the report

    Example:
        >>> orchestrator.generate_reports(all_editors, "2024")
    """
    report_generator = ReportGenerator()
    logger.info("")
    logger.info("=" * 60)
    logger.info("Step 3: Generating global summary report")
    logger.info("=" * 60)

    # ignore all_editors and load from files
    for lang, editors in all_editors.items():
        report_generator.generate_language_report(lang, editors, year)

    report_generator.generate_global_report(all_editors, year)
    logger.info("✓ Step 3 complete")


def generate_reports_from_files(year: str) -> Dict[str, Dict[str, int]]:
    """
    Generate global summary report.

    Args:
        year: Year of the report

    Example:
        >>> orchestrator.generate_reports("2024")
    """
    report_generator = ReportGenerator()
    logger.info("")
    logger.info("=" * 60)
    logger.info("Step 3: Generating summaries reports")
    logger.info("=" * 60)
    langs = get_available_languages(OUTPUT_DIRS["editors"])
    all_editors: Dict[str, Dict[str, int]] = {}

    for lang in langs:
        editors = report_generator.load_editors_json(lang)
        all_editors[lang] = editors
        report_generator.generate_language_report(lang, editors, year)

    logger.info("✓ Step 3 complete")

    logger.info("=" * 60)
    logger.info("Step 4: Generating global summary report")
    logger.info("=" * 60)

    report_generator.generate_global_report(all_editors, year)
    logger.info("✓ Step 4 complete")
    return all_editors


__all__ = [
    "generate_reports",
    "generate_reports_from_files",
]
