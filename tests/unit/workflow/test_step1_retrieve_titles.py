"""Unit tests for step1_retrieve_titles module."""

from unittest.mock import MagicMock, patch

import pytest

from src.workflow.step1_retrieve_titles import (
    _organize_titles_by_language,
    _save_language_files,
    _save_language_summary_report,
    download_medicine_titles,
    fetch_medicine_titles,
)


@pytest.mark.unit
class TestOrganizeTitlesByLanguage:
    """Test _organize_titles_by_language function."""

    def test_organize_titles_basic(self):
        """Test basic title organization by language."""
        results = [
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
            {"page_title": "Medicine", "ll_lang": "de", "ll_title": "Medizin"},
            {"page_title": "Anatomy", "ll_lang": "fr", "ll_title": "Anatomie"},
        ]

        result = _organize_titles_by_language(results)

        assert "en" in result
        assert "fr" in result
        assert "de" in result
        assert set(result["en"]) == {"Medicine", "Anatomy"}
        assert result["fr"] == ["Médecine", "Anatomie"]
        assert result["de"] == ["Medizin"]

    def test_organize_titles_with_missing_lang(self):
        """Test handling rows with missing language."""
        results = [
            {"page_title": "Medicine", "ll_lang": "", "ll_title": "Médecine"},
            {"page_title": "Anatomy", "ll_title": "Anatomie"},
        ]

        result = _organize_titles_by_language(results)

        # Should only have English titles from page_title
        assert "en" in result
        assert set(result["en"]) == {"Medicine", "Anatomy"}
        # Other languages should not be created for missing lang/title
        assert "fr" not in result

    def test_organize_titles_empty_results(self):
        """Test handling empty results."""
        result = _organize_titles_by_language([])

        assert result == {"en": []}

    def test_organize_titles_duplicates(self):
        """Test handling duplicate language entries."""
        results = [
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
        ]

        result = _organize_titles_by_language(results)

        # Duplicates should be preserved (as the function uses list append)
        assert result["fr"] == ["Médecine", "Médecine", "Médecine"]

    def test_organize_titles_multiple_page_titles(self):
        """Test with multiple different page titles."""
        results = [
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
            {"page_title": "Anatomy", "ll_lang": "fr", "ll_title": "Anatomie"},
            {"page_title": "Physiology", "ll_lang": "fr", "ll_title": "Physiologie"},
        ]

        result = _organize_titles_by_language(results)

        assert set(result["en"]) == {"Medicine", "Anatomy", "Physiology"}


@pytest.mark.unit
class TestSaveLanguageSummaryReport:
    """Test _save_language_summary_report function."""

    def test_save_summary_report(self, tmp_path):
        """Test saving language summary report."""
        titles_by_language = {
            "en": ["Medicine", "Anatomy"],
            "fr": ["Médecine", "Anatomie"],
            "de": ["Medizin"],
        }

        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"reports": tmp_path}):
            _save_language_summary_report(titles_by_language)

            output_file = tmp_path / "language_titles_summary.wiki"
            assert output_file.exists()

            content = output_file.read_text(encoding="utf-8")
            assert "Language Titles Summary:" in content
            assert "| [https://en.wikipedia.org/wiki/ en] || 2" in content
            assert "| [https://fr.wikipedia.org/wiki/ fr] || 2" in content
            assert "| [https://de.wikipedia.org/wiki/ de] || 1" in content

    def test_save_summary_report_sorting(self, tmp_path):
        """Test that report is sorted by count descending."""
        titles_by_language = {
            "en": ["a", "b", "c"],  # 3 titles
            "fr": ["x", "y"],  # 2 titles
            "de": ["z"],  # 1 title
        }

        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"reports": tmp_path}):
            _save_language_summary_report(titles_by_language)

            output_file = tmp_path / "language_titles_summary.wiki"
            content = output_file.read_text(encoding="utf-8")

            # Check order: en (3), fr (2), de (1)
            en_pos = content.index("|| 3")
            fr_pos = content.index("|| 2")
            de_pos = content.index("|| 1")

            assert en_pos < fr_pos < de_pos


@pytest.mark.unit
class TestSaveLanguageFiles:
    """Test _save_language_files function."""

    def test_save_language_files(self, mocker, tmp_path):
        """Test saving language files."""
        titles_by_language = {
            "en": ["Medicine", "Anatomy"],
            "fr": ["Médecine"],
        }

        mock_save = mocker.patch("src.workflow.step1_retrieve_titles.save_language_titles")
        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"languages": tmp_path}):
            _save_language_files(titles_by_language)

            # Verify save_language_titles was called for each language
            assert mock_save.call_count == 2
            mock_save.assert_any_call("en", ["Medicine", "Anatomy"], tmp_path)
            mock_save.assert_any_call("fr", ["Médecine"], tmp_path)

    def test_save_language_files_empty(self, mocker, tmp_path):
        """Test saving empty language list."""
        titles_by_language = {}

        mock_save = mocker.patch("src.workflow.step1_retrieve_titles.save_language_titles")
        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"languages": tmp_path}):
            _save_language_files(titles_by_language)

            # Should not be called for empty dict
            mock_save.assert_not_called()


@pytest.mark.unit
class TestFetchMedicineTitles:
    """Test fetch_medicine_titles function."""

    def test_fetch_medicine_titles_success(self, mocker, tmp_path):
        """Test successful fetch of medicine titles."""
        mock_results = [
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
            {"page_title": "Anatomy", "ll_lang": "de", "ll_title": "Anatomie"},
        ]

        # Mock DatabaseAnalytics context manager
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_results

        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(return_value=mock_db)
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.workflow.step1_retrieve_titles.DatabaseAnalytics", return_value=mock_db_context)
        mocker.patch("src.workflow.step1_retrieve_titles.save_titles_sql_results")
        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"sqlresults": tmp_path}):
            result = fetch_medicine_titles()

            assert len(result) == 2
            assert result == mock_results

    def test_fetch_medicine_titles_database_error(self, mocker):
        """Test fetch with database error."""
        # Mock DatabaseAnalytics to raise exception
        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(side_effect=Exception("Connection failed"))
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.workflow.step1_retrieve_titles.DatabaseAnalytics", return_value=mock_db_context)

        result = fetch_medicine_titles()

        # Should return empty list on error
        assert result == []

    def test_fetch_medicine_titles_empty_results(self, mocker, tmp_path):
        """Test fetch with no results."""
        # Mock DatabaseAnalytics with empty results
        mock_db = MagicMock()
        mock_db.execute.return_value = []

        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(return_value=mock_db)
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.workflow.step1_retrieve_titles.DatabaseAnalytics", return_value=mock_db_context)

        # save_titles_sql_results should not be called for empty results
        mock_save = mocker.patch("src.workflow.step1_retrieve_titles.save_titles_sql_results")
        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"sqlresults": tmp_path}):
            result = fetch_medicine_titles()

            assert result == []
            mock_save.assert_not_called()


@pytest.mark.unit
class TestDownloadMedicineTitles:
    """Test download_medicine_titles function."""

    def test_download_medicine_titles_full_flow(self, mocker, tmp_path):
        """Test complete download workflow."""
        mock_results = [
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
            {"page_title": "Medicine", "ll_lang": "de", "ll_title": "Medizin"},
            {"page_title": "Anatomy", "ll_lang": "fr", "ll_title": "Anatomie"},
        ]

        # Mock fetch_medicine_titles
        mocker.patch("src.workflow.step1_retrieve_titles.fetch_medicine_titles", return_value=mock_results)

        # Mock save functions
        mock_save_files = mocker.patch("src.workflow.step1_retrieve_titles._save_language_files")
        mock_save_report = mocker.patch("src.workflow.step1_retrieve_titles._save_language_summary_report")

        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"reports": tmp_path, "languages": tmp_path}):
            download_medicine_titles()

            # Verify _save_language_files was called
            mock_save_files.assert_called_once()
            titles_arg = mock_save_files.call_args[0][0]
            assert "en" in titles_arg
            assert "fr" in titles_arg
            assert "de" in titles_arg

            # Verify _save_language_summary_report was called
            mock_save_report.assert_called_once()

    def test_download_medicine_titles_empty_results(self, mocker, tmp_path):
        """Test download with empty results."""
        # Mock fetch_medicine_titles to return empty list
        mocker.patch("src.workflow.step1_retrieve_titles.fetch_medicine_titles", return_value=[])

        mock_save_files = mocker.patch("src.workflow.step1_retrieve_titles._save_language_files")
        mock_save_report = mocker.patch("src.workflow.step1_retrieve_titles._save_language_summary_report")

        with patch("src.workflow.step1_retrieve_titles.OUTPUT_DIRS", {"reports": tmp_path, "languages": tmp_path}):
            download_medicine_titles()

            # Should still call save functions with empty dict
            mock_save_files.assert_called_once_with({"en": []})
            mock_save_report.assert_called_once_with({"en": []})
