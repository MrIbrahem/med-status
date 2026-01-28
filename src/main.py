"""
Main entry point for Wikipedia Medicine Editor Analysis tool.

This module provides the CLI interface and orchestrates the complete
workflow for analyzing editor contributions across Wikipedia Medicine projects.
"""

import argparse
import sys

from src.config import CURRENT_YEAR, LOG_LEVEL
from src.logging_config import setup_logging, get_logger
from src.workflow import WorkflowOrchestrator

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
    if args.languages:
        logger.info("Languages: %s", ", ".join(args.languages))
    logger.info("=" * 60)

    try:
        # Initialize workflow orchestrator
        orchestrator = WorkflowOrchestrator()

        # Run complete workflow
        exit_code = orchestrator.run_complete_workflow(year=args.year, languages=args.languages)

        return exit_code

    except KeyboardInterrupt:
        logger.warning("Analysis interrupted by user")
        return 1

    except Exception as e:
        logger.error("Analysis failed: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
