"""
Main entry point for Wikipedia Medicine Editor Analysis tool.

This module provides the CLI interface and orchestrates the complete
workflow for analyzing editor contributions across Wikipedia Medicine projects.
"""

import argparse
import sys

from .config import LAST_YEAR, LOG_LEVEL
from .logging_config import get_logger, setup_logging
from .workflow import WorkflowOrchestrator

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
            python start.py

            # Run with debug logging
            python start.py --log-level DEBUG

            # Specify year and save logs to file
            python start.py --year 2023 --log-file output.log
        """,
    )

    parser.add_argument("--year", type=str, default=LAST_YEAR, help=f"Year to analyze (default: {LAST_YEAR})")

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
    parser.add_argument(
        "--skip-steps",
        type=int,
        nargs="+",
        default=[],
        help="List of steps numbers to skip (default: none), available steps (1,2,3): 1-download_medicine_titles, 2-process_languages, 3-generate_reports",
    )

    parser.add_argument(
        "--desc",
        action="store_true",
        help="Sort languages by titles DESC in step 2 (default: ASC)",
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

    if args.skip_steps:
        logger.info("Skip Steps: %s", ", ".join(map(str, args.skip_steps)))

    if args.languages:
        logger.info("Languages: %s", ", ".join(args.languages))
    logger.info("=" * 60)

    # Initialize workflow orchestrator
    orchestrator = WorkflowOrchestrator()

    # Run complete workflow
    exit_code = orchestrator.run_complete_workflow(
        year=args.year,
        languages=args.languages,
        skip_steps=args.skip_steps,
        sort_desc=args.desc,
    )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
