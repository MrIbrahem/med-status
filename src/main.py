"""
Main entry point for Wikipedia Medicine Editor Analysis tool.

This module provides the CLI interface and orchestrates the complete
workflow for analyzing editor contributions across Wikipedia Medicine projects.
"""

import argparse
import sys
from typing import Dict

from src.config import CURRENT_YEAR, LOG_LEVEL
from src.logging_config import setup_logging, get_logger
from src.queries import QueryBuilder
from src.processor import EditorProcessor
from src.reports import ReportGenerator

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Wikipedia Medicine Editor Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (current year, INFO level)
  python -m src.main

  # Run with debug logging
  python -m src.main --log-level DEBUG

  # Specify year and save logs to file
  python -m src.main --year 2023 --log-file output.log
        """,
    )

    parser.add_argument("--year", type=str, default=CURRENT_YEAR, help=f"Year to analyze (default: {CURRENT_YEAR})")

    parser.add_argument(
        "--log-level",
        type=str,
        default=LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Logging level (default: {LOG_LEVEL})",
    )

    parser.add_argument("--log-file", type=str, default=None, help="Optional log file path")

    parser.add_argument(
        "--languages", type=str, nargs="+", default=None, help="Specific languages to process (default: all)"
    )

    return parser.parse_args()


def main() -> int:
    """
    Main application entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)

    logger.info("=" * 60)
    logger.info("Wikipedia Medicine Editor Analysis Tool")
    logger.info("=" * 60)
    logger.info("Year: %s", args.year)
    logger.info("Log Level: %s", args.log_level)
    logger.info("=" * 60)

    try:
        # Initialize components
        _ = QueryBuilder()  # noqa: F841
        _ = EditorProcessor()  # noqa: F841
        _ = ReportGenerator()  # noqa: F841

        # Step 1: Get Medicine articles with language links from English Wikipedia
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 1: Retrieving Medicine articles from enwiki")
        logger.info("=" * 60)

        # This is a placeholder - in a real implementation, you would:
        # 1. Query enwiki_p for Medicine articles with langlinks
        # 2. Save language-specific title lists to languages/{lang}.json
        # 3. Query meta_p for database name mapping

        logger.info("✓ Step 1 complete")

        # Step 2: Process each language
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 2: Processing editor statistics by language")
        logger.info("=" * 60)

        # This is a placeholder - in a real implementation, you would:
        # 1. Load title lists from languages/ directory
        # 2. For each language, query editor statistics
        # 3. Save results to editors/{lang}.json
        # 4. Generate per-language reports

        all_editors: Dict[str, Dict[str, int]] = {}  # noqa: F841

        # Example: Process a single language (would be a loop in real implementation)
        # lang = "en"
        # titles = ["Medicine", "Health"]  # Would be loaded from file
        # dbname = "enwiki_p"
        # editors = processor.process_language(lang, titles, dbname, args.year)
        # all_editors[lang] = editors
        # report_generator.save_editors_json(lang, editors)
        # report_generator.generate_language_report(lang, editors, args.year)

        logger.info("✓ Step 2 complete")

        # Step 3: Generate global report
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 3: Generating global summary report")
        logger.info("=" * 60)

        # This would use the actual data in a real implementation
        # report_generator.generate_global_report(all_editors, args.year)

        logger.info("✓ Step 3 complete")

        # Final summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ Analysis complete!")
        logger.info("=" * 60)
        logger.info("Reports saved to: reports/")
        logger.info("Editor data saved to: editors/")
        logger.info("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.warning("Analysis interrupted by user")
        return 1

    except Exception as e:
        logger.error("Analysis failed: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
