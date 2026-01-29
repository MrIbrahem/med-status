"""
Data processing logic.

This module provides the EditorProcessor class for processing and
aggregating editor statistics from Wikipedia databases.
"""

from typing import Dict, List

from ..logging_config import get_logger
from ..utils import is_ip_address
from .analytics_db import DatabaseAnalytics
from .queries import QueryBuilder

logger = get_logger(__name__)


class EditorProcessor:
    """
    Processes editor statistics from Wikipedia databases.

    Handles querying, filtering, and aggregating editor contribution data
    across multiple languages and projects.
    """

    def __init__(self):
        """Initialize the editor processor."""
        self.query_builder = QueryBuilder()
        logger.debug("EditorProcessor initialized")

    def process_language_ar_en(self, lang: str, year: str) -> Dict[str, int]:
        """
        Process editor statistics for a specific language.

        Args:
            lang: Language code (e.g., "en", "ar", "fr")
            year: Year to filter (e.g., "2024")

        Returns:
            Dictionary mapping editor names to edit counts
        """
        logger.info("Processing language: %s", lang)

        editors: Dict[str, int] = {}
        params = None

        # Special handling for Arabic and English
        if lang == "ar":
            query, params = self.query_builder.get_editors_arabic(year)
        elif lang == "en":
            query, params = self.query_builder.get_editors_english(year)

        results = []
        try:
            with DatabaseAnalytics(lang) as db:
                results = db.execute(query, params=params)

        except Exception as e:
            logger.error("Failed to process language %s: %s", lang, str(e), exc_info=True)
            raise

        for row in results:
            actor_name = row.get("actor_name", "")
            count = row.get("count", 0)

            # Filter out IP addresses
            if is_ip_address(actor_name):
                logger.debug("Skipped IP address: %s", actor_name)
                continue

            # Filter out bot accounts (additional check)
            if "bot" in actor_name.lower():
                logger.debug("Skipped bot account: %s", actor_name)
                continue

            editors[actor_name] = count

        return editors

    def _batch_titles(self, titles: List[str], batch_size: int) -> List[List[str]]:
        """Helper method to batch titles into smaller lists."""
        batches = []
        for i in range(0, len(titles), batch_size):
            batches.append(titles[i : i + batch_size])
        return batches

    def process_language_patch(
        self,
        lang: str,
        titles: List[str],
        year: str,
        batch_size: int = 100,
    ) -> Dict[str, int]:
        """
        Process editor statistics for a specific language.

        Args:
            lang: Language code (e.g., "en", "ar", "fr")
            titles: List of article titles in this language
            year: Year to filter (e.g., "2024")

        Returns:
            Dictionary mapping editor names to edit counts

        Example:
            >>> processor = EditorProcessor()
            >>> editors = processor.process_language_patch("en", ["Medicine"], "2024", 100)
            >>> # Returns: {"Editor1": 150, "Editor2": 75, ...}
        """
        logger.info("Processing language: %s", lang)
        logger.debug("Processing %d titles for year %s", len(titles), year)

        editors: Dict[str, int] = {}

        with DatabaseAnalytics(lang) as db:
            batches = self._batch_titles(titles, batch_size)
            for batch_num, batch in enumerate(batches, 1):
                logger.debug("Processing batch %d/%d", batch_num, len(batches))
                query, params = self.query_builder.get_editors_standard(batch, year)

                try:
                    results = db.execute(query, params=params)
                except Exception as e:
                    logger.error("Failed to process language %s: %s", lang, str(e), exc_info=True)
                    raise

                for row in results:
                    actor_name = row.get("actor_name", "")
                    count = row.get("count", 0)

                    # Filter out IP addresses
                    if is_ip_address(actor_name):
                        logger.debug("Skipped IP address: %s", actor_name)
                        continue

                    # Filter out bot accounts (additional check)
                    if "bot" in actor_name.lower():
                        logger.debug("Skipped bot account: %s", actor_name)
                        continue

                    editors[actor_name] = count

        return editors

    def process_language(self, lang: str, titles: List[str], year: str, batch_size: int = 100) -> Dict[str, int]:
        """
        Process editor statistics for a specific language.

        Args:
            lang: Language code (e.g., "en", "ar", "fr")
            titles: List of article titles in this language
            year: Year to filter (e.g., "2024")

        Returns:
            Dictionary mapping editor names to edit counts

        Example:
            >>> processor = EditorProcessor()
            >>> editors = processor.process_language("en", ["Medicine"], "2024")
            >>> # Returns: {"Editor1": 150, "Editor2": 75, ...}
        """
        logger.info("Processing language: %s", lang)
        logger.debug("Processing %d titles for year %s", len(titles), year)

        if lang in ["ar", "en"]:
            return self.process_language_ar_en(lang, year)

        return self.process_language_patch(lang, titles, year, batch_size)

    def aggregate_editors(self, all_editors: Dict[str, Dict[str, int]]) -> Dict[str, int]:
        """
        Aggregate editor statistics across all languages.

        Args:
            all_editors: Dictionary mapping language codes to editor dictionaries

        Returns:
            Dictionary mapping editor names to total edit counts across all languages

        Example:
            >>> all_editors = {
            ...     "en": {"Editor1": 100, "Editor2": 50},
            ...     "fr": {"Editor1": 25, "Editor3": 75}
            ... }
            >>> aggregated = processor.aggregate_editors(all_editors)
            >>> # Returns: {"Editor1": 125, "Editor2": 50, "Editor3": 75}
        """
        logger.info("Aggregating editors across %d languages", len(all_editors))

        global_editors: Dict[str, int] = {}

        for lang, editors in all_editors.items():
            for editor, count in editors.items():
                if editor in global_editors:
                    global_editors[editor] += count
                else:
                    global_editors[editor] = count

        logger.info("✓ Aggregation complete: %d unique editors found", len(global_editors))
        return global_editors
