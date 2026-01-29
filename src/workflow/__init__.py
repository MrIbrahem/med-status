"""
Workflow module - Multi-step processing system with resume support
"""

from typing import Dict, List, Optional

from ..config import OUTPUT_DIRS
from ..logging_config import get_logger
from ..services import EditorProcessor, QueryBuilder, ReportGenerator
from ..services.db_mapping import get_database_mapping
from .step1_retrieve_titles import download_medicine_titles
from .step2_process_languages import process_languages
from .step3_generate_reports import generate_reports

logger = get_logger(__name__)


class WorkflowOrchestrator:
    """
    Orchestrates the complete workflow for analyzing editor contributions.

    This class coordinates all steps:
    1. Retrieve medicine titles from enwiki
    2. Get database mappings from meta_p
    3. Process editor statistics for each language
    4. Generate reports
    """

    def __init__(self):
        """
        Initialize the workflow orchestrator.
        """
        self.query_builder = QueryBuilder()
        self.processor = EditorProcessor()
        self.report_generator = ReportGenerator()
        logger.debug("WorkflowOrchestrator initialized")

    def get_database_mapping(self) -> dict:
        return get_database_mapping()

    def process_languages(
        self, year: str, languages: Optional[List[str]] = None, sort_descending: bool = False
    ) -> dict:
        """
        Process editor statistics for specified languages.

        Args:
            year: Year to analyze (e.g., "2024")
            languages: Optional list of specific languages to process
            sort_descending: Whether to sort languages by titles in descending order
        Returns:
            Dictionary of all editors processed across languages
        """
        return process_languages(year, languages, sort_descending=sort_descending)

    def generate_reports(
        self,
        all_editors: Dict[str, Dict[str, int]],
        year: str,
    ) -> None:
        """
        Generate global summary report.

        Args:
            all_editors: Dictionary mapping language codes to editor statistics
            year: Year of the report

        Example:
            >>> orchestrator.generate_reports(all_editors, "2024")
        """
        return generate_reports(all_editors, year)

    def download_medicine_titles(self) -> None:
        """
        Retrieve medicine-related article titles from enwiki.
        """
        download_medicine_titles()

    def run_complete_workflow(
        self,
        year: str,
        languages: Optional[List[str]] = None,
        skip_steps: Optional[List[int]] = None,
        sort_desc: bool = True,
    ) -> int:
        """
        Run the complete workflow from start to finish.

        Args:
            year: Year to analyze (e.g., "2024")
            languages: Optional list of specific languages to process
            skip_steps: Optional list of workflow steps to skip

        Returns:
            Exit code (0 for success, 1 for failure)

        Example:
            >>> orchestrator = WorkflowOrchestrator()
            >>> exit_code = orchestrator.run_complete_workflow("2024")
        """
        # Step 1: Retrieve titles
        if not skip_steps or 1 not in skip_steps:
            self.download_medicine_titles()
        else:
            logger.info("✓ Skipping Step 1: Retrieve Medicine article titles")

        if not skip_steps or 2 not in skip_steps:
            # Step 2: Process languages
            all_editors = self.process_languages(year, languages, sort_descending=sort_desc)
        else:
            logger.info("✓ Skipping Step 2: Process editor statistics for languages")
            all_editors = {}

        if not skip_steps or 3 not in skip_steps:
            # Step 3: Generate global report
            self.generate_reports(all_editors, year)
        else:
            logger.info("✓ Skipping Step 3: Generate reports")

        # Final summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ Analysis complete!")
        logger.info("=" * 60)
        logger.info("Languages processed: %d", len(all_editors))
        logger.info("Reports saved to: %s/", OUTPUT_DIRS["reports"])
        logger.info("Editor data saved to: %s/", OUTPUT_DIRS["editors"])
        logger.info("=" * 60)

        return 0
