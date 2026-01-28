"""
Utility functions for the Wikipedia Medicine project.

This module provides helper functions used across the application.
"""

import json
import os
import re
from typing import List

import pymysql.converters

from src.logging_config import get_logger

logger = get_logger(__name__)


def is_ip_address(text: str) -> bool:
    """
    Check if text is an IP address (IPv4 or IPv6).

    Args:
        text: String to check

    Returns:
        True if text matches IP pattern, False otherwise

    Example:
        >>> is_ip_address("192.168.1.1")
        True
        >>> is_ip_address("Username")
        False
    """
    # IPv4 pattern
    ipv4_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

    # IPv6 pattern (simplified)
    ipv6_pattern = r"^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$"

    return bool(re.match(ipv4_pattern, text) or re.match(ipv6_pattern, text))


def escape_title(title: str) -> str:
    """
    Escape article title for SQL queries.

    Args:
        title: Article title to escape

    Returns:
        SQL-escaped title

    Example:
        >>> escape_title("O'Reilly")
        "O\\'Reilly"
    """
    return pymysql.converters.escape_string(title)


def format_number(num: int) -> str:
    """
    Format number with thousands separator.

    Args:
        num: Number to format

    Returns:
        Formatted number string

    Example:
        >>> format_number(12345)
        "12,345"
    """
    return f"{num:,}"


def ensure_directory(path: str) -> None:
    """
    Ensure directory exists, create if not.

    Args:
        path: Directory path to ensure

    Raises:
        OSError: If directory cannot be created

    Example:
        >>> ensure_directory("output/reports")
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info("Created directory: %s", path)


def save_language_titles(lang: str, titles: List[str], output_dir: str = "languages") -> None:
    """
    Save article titles for a language to JSON file.

    Args:
        lang: Language code (e.g., "en", "fr", "ar")
        titles: List of article titles
        output_dir: Output directory (default: "languages")

    Example:
        >>> save_language_titles("en", ["Medicine", "Health"], "languages")
    """
    ensure_directory(output_dir)
    output_file = os.path.join(output_dir, f"{lang}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)

    logger.debug("Saved %d titles for language '%s' to %s", len(titles), lang, output_file)


def load_language_titles(lang: str, input_dir: str = "languages") -> List[str]:
    """
    Load article titles for a language from JSON file.

    Args:
        lang: Language code (e.g., "en", "fr", "ar")
        input_dir: Input directory (default: "languages")

    Returns:
        List of article titles

    Raises:
        FileNotFoundError: If language file doesn't exist

    Example:
        >>> titles = load_language_titles("en", "languages")
    """
    input_file = os.path.join(input_dir, f"{lang}.json")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Language file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        titles = json.load(f)

    logger.debug("Loaded %d titles for language '%s' from %s", len(titles), lang, input_file)
    return titles


def get_available_languages(input_dir: str = "languages") -> List[str]:
    """
    Get list of available language codes from the languages directory.

    Args:
        input_dir: Input directory (default: "languages")

    Returns:
        List of language codes

    Example:
        >>> langs = get_available_languages("languages")
        >>> # Returns: ["en", "fr", "ar", ...]
    """
    if not os.path.exists(input_dir):
        return []

    languages = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            lang = filename[:-5]  # Remove .json extension
            languages.append(lang)

    logger.debug("Found %d available languages", len(languages))
    return sorted(languages)
