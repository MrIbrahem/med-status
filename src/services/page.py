"""
MediaWiki page management using mwclient.

This module provides a class-based interface for interacting with MediaWiki
pages on mdwiki.org.
"""
import functools
import logging
from typing import Any, Dict

import mwclient
import mwclient.errors

from src.config import MDWIKI_PASSWORD, MDWIKI_SITE, MDWIKI_USERNAME

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def initialize_site_connection(username: str, password: str) -> mwclient.Site:
    """
    Initialize and cache MediaWiki site connection.

    Uses functools.lru_cache to ensure only one connection is created
    and reused across all page operations.

    Args:
        username: MDWiki username
        password: MDWiki password

    Returns:
        Authenticated mwclient.Site instance

    Raises:
        mwclient.errors.LoginError: If authentication fails

    Example:
        >>> site = initialize_site_connection("user", "pass")
        >>> print(site.host)
        'mdwiki.org'
    """
    logger.info("Initializing connection to %s", MDWIKI_SITE)
    site_mw = mwclient.Site(MDWIKI_SITE)

    try:
        site_mw.login(username, password)
        logger.info("Successfully logged in to %s as %s", MDWIKI_SITE, username)
    except mwclient.errors.LoginError as e:
        logger.error("Failed to login to %s: %s", MDWIKI_SITE, e)
        raise

    return site_mw


class PageMWClient:
    """
    MediaWiki page client for mdwiki.org.

    Provides methods to read, create, and update pages on mdwiki.org
    with proper error handling and logging.

    Attributes:
        title: Full page title including namespace
        username: MDWiki username
        password: MDWiki password
        site_mw: Cached site connection
        page: mwclient.Page instance

    Example:
        >>> page = PageMWClient("WikiProjectMed:Test")
        >>> if not page.exists():
        ...     page.create("Test content", "Creating test page")
        >>> else:
        ...     page.save("Updated content", "Updating test page")
    """

    def __init__(self, title: str):
        """
        Initialize page client.

        Args:
            title: Full page title (e.g., "WikiProjectMed:Page_Title")

        Raises:
            ValueError: If credentials are not configured
        """
        if not MDWIKI_USERNAME or not MDWIKI_PASSWORD:
            raise ValueError(
                "MDWiki credentials not configured. "
                "Set MDWIKI_USERNAME and MDWIKI_PASSWORD in .env file."
            )

        self.title = title
        self.username = MDWIKI_USERNAME
        self.password = MDWIKI_PASSWORD

        logger.debug("Initializing PageMWClient for: %s", title)

        # Get cached site connection
        self.site_mw = initialize_site_connection(self.username, self.password)

        # Get page object
        self.page = self.site_mw.pages[title]

        logger.debug("Page object created for: %s", title)

    def get_text(self) -> str:
        """
        Get current page text content.

        Returns:
            Page content as string (empty string if page doesn't exist)

        Example:
            >>> page = PageMWClient("WikiProjectMed:Test")
            >>> content = page.get_text()
            >>> print(content)
            'Current page content...'
        """
        try:
            text = self.page.text()
            logger.debug("Retrieved text from %s (%d chars)", self.title, len(text))
            return text
        except Exception as e:
            logger.error("Failed to get text from %s: %s", self.title, e)
            return ""

    def exists(self) -> bool:
        """
        Check if page exists.

        Returns:
            True if page exists, False otherwise

        Example:
            >>> page = PageMWClient("WikiProjectMed:Test")
            >>> if page.exists():
            ...     print("Page exists")
        """
        exists = self.page.exists
        logger.debug("Page %s exists: %s", self.title, exists)
        return exists

    def save(self, newtext: str, summary: str) -> Dict[str, Any]:
        """
        Save (update) existing page or create new page.

        Args:
            newtext: New page content (WikiText format)
            summary: Edit summary describing the change

        Returns:
            Result dictionary from MediaWiki API

        Raises:
            mwclient.errors.APIError: If save operation fails

        Example:
            >>> page = PageMWClient("WikiProjectMed:Test")
            >>> result = page.save("New content", "Updated statistics")
            >>> print(result)
            {'result': 'Success', ...}
        """
        try:
            logger.info("Saving page: %s", self.title)
            logger.debug("Content length: %d chars", len(newtext))
            logger.debug("Edit summary: %s", summary)

            result = self.page.save(newtext, summary=summary)

            logger.info("Successfully saved page: %s", self.title)
            logger.debug("Save result: %s", result)

            return result

        except mwclient.errors.APIError as e:
            logger.error("Failed to save page %s: %s", self.title, e)
            raise

    def create(self, newtext: str, summary: str) -> Dict[str, Any]:
        """
        Create new page (alias for save).

        Note: In MediaWiki/mwclient, save() works for both creating
        and updating pages. This method is provided for semantic clarity.

        Args:
            newtext: New page content (WikiText format)
            summary: Edit summary describing the page creation

        Returns:
            Result dictionary from MediaWiki API

        Example:
            >>> page = PageMWClient("WikiProjectMed:NewPage")
            >>> result = page.create("Initial content", "Creating new page")
        """
        logger.info("Creating new page: %s", self.title)
        return self.save(newtext, summary)


def get_page_title(lang: str, year: str, is_global: bool = False) -> str:
    """
    Generate MDWiki page title for a report.

    Args:
        lang: Language code (e.g., "ar", "es")
        year: Year of the report (e.g., "2025")
        is_global: True for global report, False for language-specific

    Returns:
        Full page title with namespace

    Example:
        >>> get_page_title("ar", "2025")
        'WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025/ar'
        >>> get_page_title("", "2025", is_global=True)
        'WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025_(all)'
    """
    from src.config import MDWIKI_BASE_PAGE

    if is_global:
        return f"{MDWIKI_BASE_PAGE}_{year}_(all)"
    else:
        return f"{MDWIKI_BASE_PAGE}_{year}/{lang}"
