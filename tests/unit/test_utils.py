"""Unit tests for utility functions."""

import json
import os
import tempfile

import pytest

from src.utils import (
    escape_title,
    format_number,
    get_available_languages,
    is_ip_address,
    load_language_titles,
    load_language_titles_safe,
    save_language_titles,
    save_titles_sql_results,
)


@pytest.mark.unit
class TestUtils:
    """Test utility functions."""

    @pytest.mark.parametrize(
        "ip,expected",
        [
            ("192.168.1.1", True),
            ("255.255.255.255", True),
            ("Username123", False),
            ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", True),
            ("NotAnIP", False),
        ],
    )
    def test_is_ip_address(self, ip, expected):
        """Test IP address detection."""
        assert is_ip_address(ip) == expected

    def test_escape_title(self):
        """Test SQL title escaping."""
        # Test with apostrophe
        assert "\\'" in escape_title("O'Reilly")
        # Test normal title
        assert escape_title("Normal_Title") == "Normal_Title"

    @pytest.mark.parametrize(
        "num,expected",
        [
            (1234, "1,234"),
            (1234567, "1,234,567"),
            (0, "0"),
            (1000, "1,000"),
        ],
    )
    def test_format_number(self, num, expected):
        """Test number formatting."""
        assert format_number(num) == expected

    def test_save_and_load_language_titles(self):
        """Test saving and loading language titles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            titles = ["Medicine", "Health", "Disease"]
            save_language_titles("en", titles, tmpdir)

            # Verify file was created
            output_file = os.path.join(tmpdir, "en.json")
            assert os.path.exists(output_file)

            # Verify content
            loaded_titles = load_language_titles("en", tmpdir)
            assert loaded_titles == titles

    def test_load_language_titles_not_found(self):
        """Test loading titles when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                load_language_titles("nonexistent", tmpdir)

    def test_get_available_languages(self):
        """Test getting available languages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some language files
            for lang in ["en", "fr", "es"]:
                filepath = os.path.join(tmpdir, f"{lang}.json")
                with open(filepath, "w") as f:
                    json.dump([], f)

            # Get available languages
            languages = get_available_languages(tmpdir)
            assert sorted(languages) == ["en", "es", "fr"]

    def test_get_available_languages_empty_dir(self):
        """Test getting languages from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            languages = get_available_languages(tmpdir)
            assert languages == []

    def test_get_available_languages_nonexistent_dir(self):
        """Test getting languages from nonexistent directory."""
        languages = get_available_languages("/nonexistent/path")
        assert languages == []

    def test_save_titles_sql_results(self):
        """Test saving SQL results to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = tmpdir
            titles = ["Medicine", "Health", "Disease"]
            save_titles_sql_results(titles, tmp_path)

            # Verify file was created
            output_file = os.path.join(tmp_path, "medicine_titles.json")
            assert os.path.exists(output_file)

            # Verify content
            with open(output_file, "r") as f:
                data = json.load(f)
                assert data == titles

    def test_save_titles_sql_results_error_fallback(self):
        """Test save_titles_sql_results fallback on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = tmpdir
            # Create a directory that will cause json.dump to fail
            output_file = os.path.join(tmp_path, "medicine_titles.json")
            os.mkdir(output_file)  # Create as directory instead of file

            titles = ["Medicine", "Health"]
            save_titles_sql_results(titles, tmp_path)

            # Should create .text fallback file
            fallback_file = os.path.join(tmp_path, "medicine_titles.text")
            assert os.path.exists(fallback_file)

    def test_load_language_titles_safe(self):
        """Test load_language_titles_safe returns empty list on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_language_titles_safe("nonexistent", tmpdir)
            assert result == []
