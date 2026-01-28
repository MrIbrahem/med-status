"""
Workflow orchestration for Wikipedia Medicine Editor Analysis.

This module provides the WorkflowOrchestrator class that coordinates
the complete data pipeline from retrieving titles to generating reports.
"""

from typing import Dict, List, Optional

from src.config import BATCH_SIZE, OUTPUT_DIRS
from src.database import Database
from src.logging_config import get_logger
from src.processor import EditorProcessor
from src.queries import QueryBuilder
from src.reports import ReportGenerator
from src.utils import get_available_languages, load_language_titles, save_language_titles

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

    def __init__(self, host: str = "analytics.db.svc.wikimedia.cloud"):
        """
        Initialize the workflow orchestrator.

        Args:
            host: Database host (default: analytics.db.svc.wikimedia.cloud)
        """
        self.host = host
        self.query_builder = QueryBuilder()
        self.processor = EditorProcessor()
        self.report_generator = ReportGenerator()
        logger.debug("WorkflowOrchestrator initialized")

    def retrieve_medicine_titles(self) -> Dict[str, List[str]]:
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

        try:
            query = self.query_builder.get_medicine_titles()

            with Database(self.host, "enwiki_p") as db:
                results = db.execute(query)
                logger.info("Retrieved %d article-language pairs", len(results))

                titles_by_language = self._organize_titles_by_language(results)
                self._save_language_files(titles_by_language)

                logger.info("✓ Found %d languages with %d total articles", len(titles_by_language), len(results))

        except Exception as e:
            logger.error("Failed to retrieve medicine titles: %s", str(e), exc_info=True)
            raise

        return titles_by_language

    def _organize_titles_by_language(self, results: List[Dict]) -> Dict[str, List[str]]:
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

    def _save_language_files(self, titles_by_language: Dict[str, List[str]]) -> None:
        """Save title lists to language files."""
        for lang, titles in titles_by_language.items():
            save_language_titles(lang, titles, OUTPUT_DIRS["languages"])

    def get_database_mapping(self) -> Dict[str, str]:
        """
        Get mapping of language codes to database names from meta_p.

        Returns:
            Dictionary mapping language codes to database names

        Example:
            >>> orchestrator = WorkflowOrchestrator()
            >>> mapping = orchestrator.get_database_mapping()
            >>> # Returns: {"en": "enwiki_p", "fr": "frwiki_p", ...}
        """
        logger.info("Retrieving database name mappings from meta_p")

        mapping: Dict[str, str] = {}

        try:
            query = self.query_builder.get_database_mapping()

            with Database(self.host, "meta_p") as db:
                results = db.execute(query)

                for row in results:
                    lang = row.get("lang", "")
                    dbname = row.get("dbname", "")

                    if lang and dbname:
                        mapping[lang] = dbname

                logger.info("✓ Retrieved mappings for %d languages", len(mapping))

        except Exception as e:
            logger.error("Failed to retrieve database mapping: %s", str(e), exc_info=True)
            raise

        return mapping

    def process_languages(
        self, year: str, languages: Optional[List[str]] = None, batch_size: int = BATCH_SIZE
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

        db_mapping = self.get_database_mapping()
        languages_to_process = self._get_languages_to_process(languages)

        logger.info("Processing %d languages", len(languages_to_process))

        all_editors: Dict[str, Dict[str, int]] = {}

        for i, lang in enumerate(languages_to_process, 1):
            self._process_single_language(lang, i, len(languages_to_process), db_mapping, year, batch_size, all_editors)

        logger.info("")
        logger.info("✓ Step 2 complete: %d languages processed", len(all_editors))

        return all_editors

    def _get_languages_to_process(self, languages: Optional[List[str]]) -> List[str]:
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
        self,
        lang: str,
        index: int,
        total: int,
        db_mapping: Dict[str, str],
        year: str,
        batch_size: int,
        all_editors: Dict[str, Dict[str, int]],
    ) -> None:
        """Process a single language."""
        logger.info("")
        logger.info("-" * 60)
        logger.info("Language %d/%d: %s", index, total, lang)
        logger.info("-" * 60)

        try:
            titles = load_language_titles(lang, OUTPUT_DIRS["languages"])

            if lang not in db_mapping:
                logger.warning("No database mapping for language '%s', skipping", lang)
                return

            dbname = db_mapping[lang]
            editors = self._process_titles_for_language(lang, titles, dbname, year, batch_size)

            all_editors[lang] = editors
            self.report_generator.save_editors_json(lang, editors)
            self.report_generator.generate_language_report(lang, editors, year)

            logger.info("✓ Language '%s' complete: %d editors, %d edits", lang, len(editors), sum(editors.values()))

        except Exception as e:
            logger.error("Failed to process language '%s': %s", lang, str(e), exc_info=True)

    def _process_titles_for_language(
        self, lang: str, titles: List[str], dbname: str, year: str, batch_size: int
    ) -> Dict[str, int]:
        """Process titles for a language, with batching if needed."""
        if len(titles) <= batch_size:
            return self.processor.process_language(lang, titles, dbname, year, self.host)

        logger.info("Processing %d titles in batches of %d", len(titles), batch_size)
        editors: Dict[str, int] = {}

        for batch_num in range(0, len(titles), batch_size):
            batch = titles[batch_num : batch_num + batch_size]
            logger.debug("Processing batch %d-%d", batch_num, batch_num + len(batch))

            batch_editors = self.processor.process_language(lang, batch, dbname, year, self.host)

            # Merge batch results
            for editor, count in batch_editors.items():
                if editor in editors:
                    editors[editor] += count
                else:
                    editors[editor] = count

        return editors

    def generate_reports(self, all_editors: Dict[str, Dict[str, int]], year: str) -> None:
        """
        Generate global summary report.

        Args:
            all_editors: Dictionary mapping language codes to editor statistics
            year: Year of the report

        Example:
            >>> orchestrator.generate_reports(all_editors, "2024")
        """
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 3: Generating global summary report")
        logger.info("=" * 60)

        try:
            self.report_generator.generate_global_report(all_editors, year)
            logger.info("✓ Step 3 complete")

        except Exception as e:
            logger.error("Failed to generate global report: %s", str(e), exc_info=True)
            raise

    def run_complete_workflow(self, year: str, languages: Optional[List[str]] = None) -> int:
        """
        Run the complete workflow from start to finish.

        Args:
            year: Year to analyze (e.g., "2024")
            languages: Optional list of specific languages to process

        Returns:
            Exit code (0 for success, 1 for failure)

        Example:
            >>> orchestrator = WorkflowOrchestrator()
            >>> exit_code = orchestrator.run_complete_workflow("2024")
        """
        try:
            # Step 1: Retrieve titles
            self.retrieve_medicine_titles()

            # Step 2: Process languages
            all_editors = self.process_languages(year, languages)

            # Step 3: Generate global report
            self.generate_reports(all_editors, year)

            # Final summary
            logger.info("")
            logger.info("=" * 60)
            logger.info("✓ Analysis complete!")
            logger.info("=" * 60)
            logger.info("Languages processed: %d", len(all_editors))
            logger.info("Total unique editors: %d", len(self.processor.aggregate_editors(all_editors)))
            logger.info("Reports saved to: %s/", OUTPUT_DIRS["reports"])
            logger.info("Editor data saved to: %s/", OUTPUT_DIRS["editors"])
            logger.info("=" * 60)

            return 0

        except Exception as e:
            logger.error("Workflow failed: %s", str(e), exc_info=True)
            return 1
