"""
Upload service for publishing reports to MDWiki.

This module handles uploading all generated WikiText reports to mdwiki.org.
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from src.config import OUTPUT_DIRS
from src.logging_config import get_logger
from src.services.page import PageMWClient, get_page_title

logger = get_logger(__name__)


class ReportUploader:
    """
    Upload WikiText reports to MDWiki.

    Handles uploading both language-specific and global reports
    to the appropriate pages on mdwiki.org.

    Example:
        >>> uploader = ReportUploader()
        >>> results = uploader.upload_all_reports("2025")
        >>> print(f"Uploaded {results['success']} reports")
    """

    def __init__(self):
        """Initialize report uploader."""
        self.reports_dir = OUTPUT_DIRS["reports"]
        logger.debug("ReportUploader initialized with reports_dir: %s", self.reports_dir)

    def upload_all_reports(self, year: str) -> Dict[str, int]:
        """
        Upload all reports in the reports directory.

        Args:
            year: Year for the report pages

        Returns:
            Dictionary with upload statistics:
            - 'success': Number of successful uploads
            - 'failed': Number of failed uploads
            - 'total': Total number of reports

        Example:
            >>> uploader = ReportUploader()
            >>> stats = uploader.upload_all_reports("2025")
            >>> print(f"{stats['success']}/{stats['total']} uploaded")
        """
        logger.info("=" * 60)
        logger.info("Starting upload of all reports to MDWiki")
        logger.info("=" * 60)

        # Find all .wiki files
        report_files = self._get_report_files()

        if not report_files:
            logger.warning("No report files found in %s", self.reports_dir)
            return {"success": 0, "failed": 0, "total": 0}

        logger.info("Found %d report files to upload", len(report_files))

        # Upload each report
        results = {"success": 0, "failed": 0, "total": len(report_files)}

        for filepath in report_files:
            filename = os.path.basename(filepath)

            try:
                success = self._upload_report(filepath, year)
                if success:
                    results["success"] += 1
                    logger.info("Uploaded: %s", filename)
                else:
                    results["failed"] += 1
                    logger.error("Failed: %s", filename)

            except Exception as e:
                results["failed"] += 1
                logger.error("Error uploading %s: %s", filename, e, exc_info=True)

        # Log summary
        logger.info("=" * 60)
        logger.info("Upload Summary:")
        logger.info("  Successful: %d", results["success"])
        logger.info("  Failed: %d", results["failed"])
        logger.info("  Total: %d", results["total"])
        logger.info("=" * 60)

        return results

    def _get_report_files(self) -> List[str]:
        """
        Get list of all .wiki files in reports directory.

        Returns:
            List of absolute file paths
        """
        reports_path = Path(self.reports_dir)

        if not reports_path.exists():
            logger.warning("Reports directory does not exist: %s", self.reports_dir)
            return []

        wiki_files = list(reports_path.glob("*.wiki"))
        filepaths = [str(f.absolute()) for f in wiki_files]

        logger.debug("Found %d .wiki files", len(filepaths))
        return filepaths

    def _upload_report(self, filepath: str, year: str) -> bool:
        """
        Upload a single report file to MDWiki.

        Args:
            filepath: Path to .wiki file
            year: Year for the page title

        Returns:
            True if upload successful, False otherwise
        """
        filename = os.path.basename(filepath)
        lang_code = filename.replace(".wiki", "")

        logger.info("-" * 60)
        logger.info("Uploading: %s", filename)

        # Determine if this is the global report
        is_global = lang_code == "total_report"

        # Generate page title
        page_title = get_page_title(lang_code, year, is_global)
        logger.info("Target page: %s", page_title)

        # Read report content
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            logger.debug("Read %d characters from %s", len(content), filename)

        except Exception as e:
            logger.error("Failed to read file %s: %s", filepath, e)
            return False

        # Upload to MDWiki
        try:
            page = PageMWClient(page_title)

            # Generate edit summary
            if is_global:
                summary = f"Update global medical editors statistics for {year}"
            else:
                summary = f"Update {lang_code} medical editors statistics for {year}"

            # Check if page exists
            if page.exists():
                logger.info("Page exists, updating...")
            else:
                logger.info("Page does not exist, creating...")

            # Save page
            result = page.save(content, summary)

            logger.info("Upload successful")
            return True

        except Exception as e:
            logger.error("Failed to upload to %s: %s", page_title, e)
            return False

    def upload_single_report(
        self, lang: str, year: str, is_global: bool = False
    ) -> bool:
        """
        Upload a single report by language code.

        Args:
            lang: Language code (e.g., "ar", "es") or "total_report"
            year: Year for the page title
            is_global: True for global report

        Returns:
            True if upload successful, False otherwise

        Example:
            >>> uploader = ReportUploader()
            >>> uploader.upload_single_report("ar", "2025")
            True
        """
        if is_global:
            filename = "total_report.wiki"
        else:
            filename = f"{lang}.wiki"

        filepath = os.path.join(self.reports_dir, filename)

        if not os.path.exists(filepath):
            logger.error("Report file not found: %s", filepath)
            return False

        return self._upload_report(filepath, year)
