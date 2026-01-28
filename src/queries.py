"""
SQL query templates and builders.

This module provides SQL query templates for retrieving data from
Wikimedia databases. All queries are optimized for read replicas.

See .claude/context/database_schema.md for schema details.
"""

from typing import List

from src.utils import escape_title
from src.logging_config import get_logger

logger = get_logger(__name__)


class QueryBuilder:
    """
    SQL query builder for Wikimedia databases.

    Provides static methods for building optimized SQL queries.
    All queries use indexed columns and are designed for read replicas.
    """

    @staticmethod
    def get_medicine_titles() -> str:
        """
        Get Medicine project articles with language links.

        Database: enwiki_p

        Returns:
            SQL query string
        """
        return """
            SELECT page_title, ll_lang, ll_title
            FROM page, langlinks, page_assessments, page_assessments_projects
            WHERE pap_project_title = "Medicine"
              AND pa_project_id = pap_project_id
              AND pa_page_id = page_id
              AND page_id = ll_from
              AND page_is_redirect = 0
              AND page_namespace = 0
        """

    @staticmethod
    def get_database_mapping() -> str:
        """
        Get mapping of language codes to database names.

        Database: meta_p

        Returns:
            SQL query string
        """
        return """
            SELECT dbname, family, lang, url
            FROM wiki
            WHERE is_closed = 0
              AND family = 'wikipedia'
        """

    @staticmethod
    def get_editors_standard(titles: List[str], year: str) -> str:
        """
        Get editor statistics for given titles (standard languages).

        Args:
            titles: List of article titles (will be escaped)
            year: Year to filter (e.g., "2024")

        Returns:
            SQL query string with escaped titles

        Note:
            Titles are automatically escaped to prevent SQL injection.
        """
        # Escape all titles
        escaped_titles = [escape_title(title) for title in titles]
        titles_str = "', '".join(escaped_titles)

        logger.debug("Building query for %d titles in year %s", len(titles), year)

        return f"""
            SELECT actor_name, COUNT(*) as count
            FROM revision
            JOIN actor ON rev_actor = actor_id
            JOIN page ON rev_page = page_id
            WHERE page_title IN ('{titles_str}')
              AND page_namespace = 0
              AND rev_timestamp LIKE '{year}%'
              AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
            GROUP BY actor_id
            ORDER BY count DESC
        """

    @staticmethod
    def get_editors_arabic(year: str) -> str:
        """
        Get editor statistics for Arabic Wikipedia Medicine project.

        Uses project assessment directly (no title filtering needed).

        Args:
            year: Year to filter (e.g., "2024")

        Returns:
            SQL query string
        """
        return f"""
            SELECT actor_name, COUNT(*) as count
            FROM revision
            JOIN actor ON rev_actor = actor_id
            JOIN page ON rev_page = page_id
            WHERE page_id IN (
                SELECT DISTINCT pa_page_id
                FROM page_assessments, page_assessments_projects
                WHERE pa_project_id = pap_project_id
                  AND pap_project_title = "طب"
            )
              AND page_namespace = 0
              AND rev_timestamp LIKE '{year}%'
              AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
            GROUP BY actor_id
            ORDER BY count DESC
            LIMIT 100
        """

    @staticmethod
    def get_editors_english(year: str) -> str:
        """
        Get editor statistics for English Wikipedia Medicine project.

        Uses WikiProject Medicine templatelinks on talk pages.

        Args:
            year: Year to filter (e.g., "2025")

        Returns:
            SQL query string
        """
        return f"""
            SELECT actor_name, COUNT(*) as count
            FROM revision
            JOIN actor ON rev_actor = actor_id
            JOIN page ON rev_page = page_id
            WHERE page_title IN (
                SELECT page_title
                FROM (
                    SELECT tl_from, rd_from
                    FROM templatelinks
                    LEFT JOIN redirect
                      ON rd_from = tl_from
                      AND rd_title = 'WikiProject_Medicine'
                      AND (rd_interwiki = '' OR rd_interwiki IS NULL)
                      AND rd_namespace = 10
                    JOIN page ON tl_from = page_id
                    JOIN linktarget ON tl_target_id = lt_id
                    WHERE lt_namespace = 10
                      AND lt_title = 'WikiProject_Medicine'
                    ORDER BY tl_from
                ) temp
                JOIN page ON tl_from = page_id
                WHERE page_namespace = 1
            )
              AND page_namespace = 0
              AND rev_timestamp LIKE '{year}%'
              AND LOWER(CAST(actor_name AS CHAR)) NOT LIKE '%bot%'
            GROUP BY actor_id
            ORDER BY count DESC
            LIMIT 100
        """
