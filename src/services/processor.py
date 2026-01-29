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

    def process_language(self, lang: str, titles: List[str], year: str) -> Dict[str, int]:
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

        editors: Dict[str, int] = {}
        params = []

        # Special handling for Arabic and English
        if lang == "ar":
            query, params = self.query_builder.get_editors_arabic(year)
        elif lang == "en":
            query, params = self.query_builder.get_editors_english(year)
        else:
            # Standard query for other languages
            query, params = self.query_builder.get_editors_standard(titles, year)

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

            logger.info("✓ Language '%s' complete: %d editors found", lang, len(editors))

        return editors

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
