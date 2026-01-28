"""
Utility functions for the Wikipedia Medicine project.

This module provides helper functions used across the application.
"""

import os
import re

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
