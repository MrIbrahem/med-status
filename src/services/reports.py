"""
Report generation.

This module provides the ReportGenerator class for creating WikiText
reports from editor statistics.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict

from ..config import OUTPUT_DIRS
from ..logging_config import get_logger
from ..utils import is_ip_address, load_language_titles

logger = get_logger(__name__)


def work_all_editors(editors, last_year) -> str:

    text = "{{:WPM:WikiProject Medicine/Top medical editors navigation}}\n"
    text += f"{{{{Top medical editors by lang|{last_year}}}}}\n"

    text += f"Numbers of {last_year}.\n"

    txt_table = """{| class="sortable wikitable"\n!#\n"""
    txt_table += """!User\n!Count at wiki\n!Wiki\n!Count global\n"""

    targets = ""

    for i, (user, ta) in enumerate(editors.items(), start=1):
        count_global = ta["count_global"]
        count = ta["count"]
        wiki = ta["site"]
        user = user.replace("_", " ")
        # #{{#target:User:{User}|{wiki}.wikipedia.org}}
        targets += f"#{{{{#target:User:{user}|{wiki}.wikipedia.org}}}}\n"
        txt_table += (
            f"|-\n" f"!{i}\n" f"|[[:w:{wiki}:user:{user}|{user}]]\n" f"|{count:,}\n" f"|{wiki}\n" f"|{count_global:,}\n"
        )
        if count < 10:
            break

    txt_table += "\n|}"

    text += '{| class="sortable wikitable floatright"\n|\n'
    text += '<div style="max-height:250px; overflow: auto;vertical-align:top;font-size:90%;max-width:400px">\n'
    text += "<pre>\n"

    text += targets

    text += "\n</pre>"
    text += "\n</div>"
    text += "\n|-\n|}"
    text += f"\n==users==\n{txt_table}"

    return text


class ReportGenerator:
    """
    Generates WikiText reports from editor statistics.

    Creates both per-language reports and global summary reports
    in WikiText format for uploading to Wikipedia.
    """

    def __init__(self):
        """Initialize the report generator."""
        logger.debug("ReportGenerator initialized")

    def load_editors_json(self, lang: str) -> Dict[str, int]:
        """
        Load editor statistics from JSON file.
        Args:
            lang: Language code
        """
        input_file = Path(OUTPUT_DIRS["editors"]) / f"{lang}.json"
        if not input_file.exists():
            logger.debug("Editor data file not found: %s", input_file)
            return {}
        with open(input_file, "r", encoding="utf-8") as f:
            editors: Dict[str, int] = json.load(f)
            logger.info("✓ Loaded editor data from %s", input_file)
        return editors

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

            ...
        """
        logger.info("Generating report for language: %s", lang)

        output_file = Path(OUTPUT_DIRS["reports"]) / f"{lang}.wiki"

        # Sort editors by edit count (descending)
        sorted_editors = dict(sorted(editors.items(), key=lambda x: x[1], reverse=True))

        text = "{{:WPM:WikiProject Medicine/Top medical editors navigation}}\n"
        text += f"{{{{Top medical editors by lang|{year}}}}}\n"
        # ---
        links = len(load_language_titles(lang, OUTPUT_DIRS["languages"]))
        # ---
        if lang != "ar":
            text += f"Numbers of {year}. There are {links:,} articles in {lang}\n"
        # ---
        text += """{| class="sortable wikitable"\n!#\n!User\n!Count\n|-"""
        # ---
        for i, (user, count) in enumerate(sorted_editors.items(), start=1):
            # ---
            user = user.replace("_", " ")
            # ---
            text += f"\n|-\n!{i}\n|[[:w:{lang}:user:{user}|{user}]]\n|{count:,}"
            # ---
            if i == 100:
                break
        # ---
        text += "\n|}"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        logger.info("✓ Generated report: %s", output_file)

    def generate_global_report(self, all_editors: Dict[str, Dict[str, int]], year: str) -> None:
        """
        Generate global summary report across all languages.

        Args:
            all_editors: Dictionary mapping language codes to editor dictionaries
            year: Year of the report
        """
        logger.info("Generating global report")

        output_file = Path(OUTPUT_DIRS["reports"]) / "total_report.wiki"

        # Aggregate all editors
        global_editors: Dict[str, int] = defaultdict(int)
        editors_by_wiki: Dict[str, int] = defaultdict(lambda: defaultdict(int))

        for lang, editors in all_editors.items():
            for editor, count in editors.items():
                if ">" in editor:
                    # en>Jako96 -> Jako96
                    editor = editor.split(">", 1)[1]

                if is_ip_address(editor):
                    continue  # Skip IP addresses

                global_editors[editor] += count
                editors_by_wiki[editor][lang] += count

        # Sort by total edit count
        sorted_global = sorted(global_editors.items(), key=lambda x: x[1], reverse=True)
        all_editors_status: Dict[str, Dict[str, int]] = {}

        for rank, (editor, count) in enumerate(sorted_global[:1000], 1):
            editor_most_wiki = max(editors_by_wiki[editor].items(), key=lambda x: x[1])
            all_editors_status[editor] = {
                "count": editor_most_wiki[1],
                "site": editor_most_wiki[0],
                "count_global": count,
            }

        all_editors_status = dict(sorted(all_editors_status.items(), key=lambda x: x[1]["count"], reverse=True))

        text = work_all_editors(all_editors_status, year)
        with open(output_file, "w", encoding="utf-8") as f:
            # Header
            f.write(text)

        logger.info("✓ Generated global report: %s", output_file)
