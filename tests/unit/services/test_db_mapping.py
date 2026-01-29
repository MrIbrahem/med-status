"""Unit tests for db_mapping module."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.services.db_mapping import (
    fetch_database_mapping,
    get_database_mapping,
    get_database_name_for_language,
    load_db_mapping,
    save_db_mapping,
)


@pytest.mark.unit
class TestDbMapping:
    """Test database mapping functions."""

    def test_save_and_load_db_mapping(self, tmp_path):
        """Test saving and loading database mapping."""
        with patch("src.services.db_mapping.OUTPUT_DIRS", {"sqlresults": tmp_path}):
            mapping = {"en": "enwiki_p", "fr": "frwiki_p"}
            save_db_mapping(mapping)

            # Verify file was created
            output_file = tmp_path / "db_mapping.json"
            assert output_file.exists()

            # Verify content
            loaded = load_db_mapping()
            assert loaded == mapping

    def test_load_db_mapping_file_not_found(self, tmp_path):
        """Test loading when file doesn't exist."""
        with patch("src.services.db_mapping.OUTPUT_DIRS", {"sqlresults": tmp_path}):
            result = load_db_mapping()
            assert result == {}

    def test_fetch_database_mapping(self):
        """Test fetching database mapping from meta database."""
        # Mock Database context manager
        mock_db = MagicMock()
        mock_db.execute.return_value = [
            {"lang": "en", "dbname": "enwiki_p", "url": "https://en.wikipedia.org/"},
            {"lang": "fr", "dbname": "frwiki_p", "url": "https://fr.wikipedia.org/"},
            {"dbname": "dewiki_p", "url": "https://de.wikipedia.org/", "lang": "de"},  # Missing lang
            {"lang": "es", "dbname": "", "url": "https://es.wikipedia.org/"},  # Missing dbname
        ]

        mock_db_context = Mock()
        mock_db_context.__enter__ = Mock(return_value=mock_db)
        mock_db_context.__exit__ = Mock(return_value=None)

        with patch("src.services.db_mapping.Database", return_value=mock_db_context):
            mapping = fetch_database_mapping()

            # Should include languages and url-based mappings
            assert "en" in mapping
            assert "fr" in mapping
            assert "de" in mapping  # From URL
            assert "es" not in mapping  # Missing dbname
            assert mapping["en"] == "enwiki_p"

    def test_get_database_mapping_cached(self, tmp_path):
        """Test get_database_mapping with cached file."""
        with patch("src.services.db_mapping.OUTPUT_DIRS", {"sqlresults": tmp_path}):
            # Create cached mapping file
            cached_mapping = {"en": "enwiki_p", "fr": "frwiki_p"}
            output_file = tmp_path / "db_mapping.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(cached_mapping, f)

            # Clear the cache first
            get_database_mapping.cache_clear()

            mapping = get_database_mapping()

            # The code overwrites "en" with "enwiki" (without _p)
            assert "en" in mapping
            assert mapping["en"] == "enwiki"
            assert mapping["fr"] == "frwiki_p"

    def test_get_database_mapping_fetch_new(self, tmp_path):
        """Test get_database_mapping fetches new when no cache."""
        # Mock the fetch function
        mock_mapping = {"en": "enwiki_p", "fr": "frwiki_p"}

        with patch("src.services.db_mapping.OUTPUT_DIRS", {"sqlresults": tmp_path}):
            with patch("src.services.db_mapping.fetch_database_mapping", return_value=mock_mapping):
                # Clear cache
                get_database_mapping.cache_clear()

                mapping = get_database_mapping()

                # Should include English default
                assert "en" in mapping
                assert "fr" in mapping

    def test_get_database_mapping_ensures_english(self, tmp_path):
        """Test get_database_mapping ensures English value is set."""
        with patch("src.services.db_mapping.OUTPUT_DIRS", {"sqlresults": tmp_path}):
            # Mock fetch to return mapping without English
            mock_mapping = {"fr": "frwiki_p", "de": "dewiki_p"}

            with patch("src.services.db_mapping.fetch_database_mapping", return_value=mock_mapping):
                # Clear cache
                get_database_mapping.cache_clear()

                mapping = get_database_mapping()

                # Should add English
                assert "en" in mapping
                assert mapping["en"] == "enwiki"

    def test_get_database_name_for_language_predefined(self):
        """Test get_database_name_for_language with predefined mapping."""
        # Clear cache first
        get_database_mapping.cache_clear()

        # Mock the full get_database_mapping to return empty
        with patch("src.services.db_mapping.get_database_mapping", return_value={}):
            # Test predefined mappings
            assert get_database_name_for_language("gsw") == "alswiki"
            assert get_database_name_for_language("bat-smg") == "bat_smgwiki"
            assert get_database_name_for_language("be-tarask") == "be_x_oldwiki"

    def test_get_database_name_for_language_from_mapping(self):
        """Test get_database_name_for_language from mapping."""
        # Clear cache and mock
        get_database_mapping.cache_clear()
        mock_mapping = {"en": "enwiki_p", "fr": "frwiki_p"}

        with patch("src.services.db_mapping.get_database_mapping", return_value=mock_mapping):
            assert get_database_name_for_language("en") == "enwiki_p"
            assert get_database_name_for_language("fr") == "frwiki_p"

    def test_get_database_name_for_language_not_found(self):
        """Test get_database_name_for_language when language not found."""
        # Clear cache and mock
        get_database_mapping.cache_clear()

        with patch("src.services.db_mapping.get_database_mapping", return_value={}):
            result = get_database_name_for_language("nonexistent")
            assert result == ""
