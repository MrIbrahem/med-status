"""
Report generation.

This module provides the ReportGenerator class for creating WikiText
reports from editor statistics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from ..config import OUTPUT_DIRS
from ..logging_config import get_logger
from ..utils import format_number

logger = get_logger(__name__)


class ReportGenerator:
    """
    Generates WikiText reports from editor statistics.

    Creates both per-language reports and global summary reports
    in WikiText format for uploading to Wikipedia.
    """

    def __init__(self):
        """Initialize the report generator."""
        logger.debug("ReportGenerator initialized")

    def save_editors_json(self, lang: str, editors: Dict[str, int]) -> None:
        """
        Save editor statistics to JSON file.

        Args:
            lang: Language code
            editors: Dictionary of editor names to edit counts
        """
        output_file = Path(OUTPUT_DIRS["editors"]) / f"{lang}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(editors, f, ensure_ascii=False, indent=2)

        logger.info("✓ Saved editor data to %s", output_file)

    def generate_language_report(self, lang: str, editors: Dict[str, int], year: str) -> None:
        """
        Generate WikiText report for a specific language.

        Args:
            lang: Language code (e.g., "en", "ar", "fr")
            editors: Dictionary mapping editor names to edit counts
            year: Year of the report

        Example output:
            == Editors Statistics for 2024 ==
            Total editors: 150

            {| class="wikitable sortable"
            ! Rank !! Editor !! Edits
            |-
            | 1 || Editor1 || 1,234
            ...
        """
        logger.info("Generating report for language: %s", lang)

        output_file = Path(OUTPUT_DIRS["reports"]) / f"{lang}.wiki"

        # Sort editors by edit count (descending)
        sorted_editors = sorted(editors.items(), key=lambda x: x[1], reverse=True)

        with open(output_file, "w", encoding="utf-8") as f:
            # Header
            f.write(f"== Editors Statistics for {year} ==\n")
            f.write(f"Total editors: {format_number(len(editors))}\n\n")

            # Table
            f.write('{| class="wikitable sortable"\n')
            f.write("! Rank !! Editor !! Edits\n")

            for rank, (editor, count) in enumerate(sorted_editors, 1):
                f.write("|-\n")
                f.write(f"| {rank} || {editor} || {format_number(count)}\n")

            f.write("|}\n")

            # Footer
            f.write(f"\n''Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC''\n")

        logger.info("✓ Generated report: %s", output_file)

    def generate_global_report(self, all_editors: Dict[str, Dict[str, int]], year: str) -> None:
        """
        Generate global summary report across all languages.

        Args:
            all_editors: Dictionary mapping language codes to editor dictionaries
            year: Year of the report

        Example output:
            == Global Medicine Editor Statistics for 2024 ==

            === Summary ===
            * Total languages: 50
            * Total unique editors: 5,432
            * Total edits: 123,456

            === Top 100 Editors Globally ===
            ...
        """
        logger.info("Generating global report")

        output_file = Path(OUTPUT_DIRS["reports"]) / "total_report.wiki"

        # Aggregate all editors
        global_editors: Dict[str, int] = {}
        total_edits = 0

        for lang, editors in all_editors.items():
            for editor, count in editors.items():
                if editor in global_editors:
                    global_editors[editor] += count
                else:
                    global_editors[editor] = count
                total_edits += count

        # Sort by total edit count
        sorted_global = sorted(global_editors.items(), key=lambda x: x[1], reverse=True)

        with open(output_file, "w", encoding="utf-8") as f:
            # Header
            f.write(f"== Global Medicine Editor Statistics for {year} ==\n\n")

            # Summary
            f.write("=== Summary ===\n")
            f.write(f"* Total languages: {format_number(len(all_editors))}\n")
            f.write(f"* Total unique editors: {format_number(len(global_editors))}\n")
            f.write(f"* Total edits: {format_number(total_edits)}\n\n")

            # Top 100 editors
            f.write("=== Top 100 Editors Globally ===\n")
            f.write('{| class="wikitable sortable"\n')
            f.write("! Rank !! Editor !! Total Edits\n")

            for rank, (editor, count) in enumerate(sorted_global[:100], 1):
                f.write("|-\n")
                f.write(f"| {rank} || {editor} || {format_number(count)}\n")

            f.write("|}\n")

            # Language breakdown
            f.write("\n=== Per-Language Statistics ===\n")
            f.write('{| class="wikitable sortable"\n')
            f.write("! Language !! Editors !! Total Edits\n")

            # Sort languages by total edits
            lang_stats = []
            for lang, editors in all_editors.items():
                lang_total = sum(editors.values())
                lang_stats.append((lang, len(editors), lang_total))

            lang_stats.sort(key=lambda x: x[2], reverse=True)

            for lang, editor_count, edit_count in lang_stats:
                f.write("|-\n")
                f.write(f"| {lang} || {format_number(editor_count)} || {format_number(edit_count)}\n")

            f.write("|}\n")

            # Footer
            f.write(f"\n''Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC''\n")

        logger.info("✓ Generated global report: %s", output_file)
