"""
Step 3: Generate global reports
"""

from typing import Dict

from ..logging_config import get_logger
from ..services.reports import ReportGenerator

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

    report_generator.generate_global_report(all_editors, year)
    logger.info("✓ Step 3 complete")


__all__ = [
    "generate_reports",
]
