"""Unit tests for step2_process_languages module."""

from unittest.mock import patch

import pytest

from src.workflow.step2_process_languages import (
    _get_languages_to_process,
    _process_single_language,
    _process_titles_for_language,
    gather_language_titles,
    process_languages,
)


@pytest.mark.unit
class TestGetLanguagesToProcess:
    """Test _get_languages_to_process function."""

    def test_get_all_available_languages(self, mocker):
        """Test getting all available languages when none specified."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en", "fr", "de"])

        result = _get_languages_to_process(None)

        assert result == ["en", "fr", "de"]

    def test_get_specific_languages(self, mocker):
        """Test getting specific requested languages."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en", "fr", "de"])

        result = _get_languages_to_process(["en", "fr"])

        assert result == ["en", "fr"]

    def test_get_specific_languages_with_missing(self, mocker):
        """Test handling when some requested languages are missing."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en", "fr"])

        result = _get_languages_to_process(["en", "fr", "de"])

        assert result == ["en", "fr"]
        # "de" should be filtered out as it's not available

    def test_get_specific_languages_all_missing(self, mocker):
        """Test handling when all requested languages are missing."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en"])

        result = _get_languages_to_process(["fr", "de"])

        assert result == []


@pytest.mark.unit
class TestProcessTitlesForLanguage:
    """Test _process_titles_for_language function."""

    def test_process_titles_arabic(self, mocker):
        """Test processing Arabic (uses ar_en method)."""
        mocker.patch("src.services.processor.EditorProcessor.process_language_ar_en", return_value={"Editor1": 100})

        result = _process_titles_for_language("ar", [], "2024", 100)

        assert result == {"Editor1": 100}

    def test_process_titles_english(self, mocker):
        """Test processing English (uses ar_en method)."""
        mocker.patch("src.services.processor.EditorProcessor.process_language_ar_en", return_value={"Editor1": 200})

        result = _process_titles_for_language("en", [], "2024", 100)

        assert result == {"Editor1": 200}

    def test_process_titles_other_language(self, mocker):
        """Test processing other language (uses patch method)."""
        mocker.patch("src.services.processor.EditorProcessor.process_language_patch", return_value={"Editor2": 50})

        result = _process_titles_for_language("fr", ["Medicine"], "2024", 100)

        assert result == {"Editor2": 50}


@pytest.mark.unit
class TestProcessSingleLanguage:
    """Test _process_single_language function."""

    def test_process_single_language_with_editors(self, mocker):
        """Test processing a language with editors found."""
        mocker.patch("src.workflow.step2_process_languages._process_titles_for_language", return_value={"Editor1": 100})

        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        result = _process_single_language("en", "2024", 100, ["Medicine"])

        assert result == {"Editor1": 100}
        mock_report_gen.save_editors_json.assert_called_once_with("en", {"Editor1": 100})
        mock_report_gen.generate_language_report.assert_called_once_with("en", {"Editor1": 100}, "2024")

    def test_process_single_language_no_editors(self, mocker):
        """Test processing a language with no editors."""
        mocker.patch("src.workflow.step2_process_languages._process_titles_for_language", return_value={})

        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        result = _process_single_language("en", "2024", 100, ["Medicine"])

        assert result == {}
        # Report generator methods should not be called for empty results
        mock_report_gen.save_editors_json.assert_not_called()
        mock_report_gen.generate_language_report.assert_not_called()


@pytest.mark.unit
class TestGatherLanguageTitles:
    """Test gather_language_titles function."""

    def test_gather_language_titles(self, mocker, tmp_path):
        """Test gathering titles for multiple languages."""
        mocker.patch(
            "src.workflow.step2_process_languages.load_language_titles_safe",
            side_effect=lambda lang, _: {"en": ["Medicine", "Anatomy"], "fr": ["Médecine"]}.get(lang, []),
        )

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path}):
            result = gather_language_titles(["en", "fr"])

            assert result == {"en": ["Medicine", "Anatomy"], "fr": ["Médecine"]}

    def test_gather_language_titles_sort_descending(self, mocker, tmp_path):
        """Test gathering titles with descending sort."""
        mocker.patch(
            "src.workflow.step2_process_languages.load_language_titles_safe",
            side_effect=lambda lang, _: {"en": ["a", "b", "c"], "fr": ["x"], "de": ["y", "z"]}.get(lang, []),
        )

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path}):
            result = gather_language_titles(["en", "fr", "de"], sort_descending=True)

            # Should be sorted by count descending: en (3), de (2), fr (1)
            keys = list(result.keys())
            assert keys == ["en", "de", "fr"]

    def test_gather_language_titles_sort_ascending(self, mocker, tmp_path):
        """Test gathering titles with ascending sort."""
        mocker.patch(
            "src.workflow.step2_process_languages.load_language_titles_safe",
            side_effect=lambda lang, _: {"en": ["a"], "fr": ["x", "y"], "de": ["z"]}.get(lang, []),
        )

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path}):
            result = gather_language_titles(["en", "fr", "de"], sort_descending=False)

            # Should be sorted by count ascending: en (1), de (1), fr (2)
            keys = list(result.keys())
            assert keys == ["en", "de", "fr"]

    def test_gather_language_titles_empty(self, mocker, tmp_path):
        """Test gathering titles with empty language list."""
        mocker.patch("src.workflow.step2_process_languages.load_language_titles_safe", return_value=[])

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path}):
            result = gather_language_titles([])

            assert result == {}


@pytest.mark.unit
class TestProcessLanguages:
    """Test process_languages function."""

    def test_process_languages_all(self, mocker, tmp_path):
        """Test processing all languages."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en", "fr"])

        mocker.patch(
            "src.workflow.step2_process_languages.load_language_titles_safe",
            side_effect=lambda lang, _: ["Medicine"] if lang == "en" else ["Médecine"],
        )

        mocker.patch(
            "src.workflow.step2_process_languages._process_titles_for_language",
            side_effect=lambda lang, *_, **__: {"Editor1": 100} if lang == "en" else {"Editor2": 50},
        )

        mock_report_gen = mocker.Mock()
        mock_report_gen.load_editors_json.return_value = None
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path, "reports": tmp_path}):
            result = process_languages("2024")

            assert "en" in result
            assert "fr" in result
            assert result["en"] == {"Editor1": 100}
            assert result["fr"] == {"Editor2": 50}

    def test_process_languages_specific_list(self, mocker, tmp_path):
        """Test processing specific languages from list."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en", "fr", "de"])

        mocker.patch("src.workflow.step2_process_languages.load_language_titles_safe", return_value=["Medicine"])

        mocker.patch("src.workflow.step2_process_languages._process_titles_for_language", return_value={"Editor1": 100})

        mock_report_gen = mocker.Mock()
        mock_report_gen.load_editors_json.return_value = None
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path, "reports": tmp_path}):
            result = process_languages("2024", languages=["en", "fr"])

            assert "en" in result
            assert "fr" in result
            assert "de" not in result

    def test_process_languages_skip_existing(self, mocker, tmp_path):
        """Test skipping languages with existing data."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en", "fr"])

        mocker.patch("src.workflow.step2_process_languages.load_language_titles_safe", return_value=["Medicine"])

        # Mock report generator to return existing data for "en" only (non-empty dict = truthy)
        mock_report_gen = mocker.Mock()
        mock_report_gen.load_editors_json.side_effect = lambda lang: {"en": {"Editor1": 100}, "fr": None}.get(lang)
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        mocker.patch("src.workflow.step2_process_languages._process_titles_for_language", return_value={"Editor1": 100})

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path, "reports": tmp_path}):
            result = process_languages("2024", skip_existing=True)

            # "en" should be skipped, "fr" should be processed
            assert "en" not in result
            assert "fr" in result

    def test_process_languages_with_custom_batch_size(self, mocker, tmp_path):
        """Test processing with custom batch size."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en"])

        mocker.patch("src.workflow.step2_process_languages.load_language_titles_safe", return_value=["Medicine"])

        mock_process = mocker.patch(
            "src.workflow.step2_process_languages._process_titles_for_language", return_value={"Editor1": 100}
        )

        mock_report_gen = mocker.Mock()
        mock_report_gen.load_editors_json.return_value = None
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path, "reports": tmp_path}):
            process_languages("2024", batch_size=50)

            # Verify batch_size was passed through
            mock_process.assert_called_once()
            call_args = mock_process.call_args[0]
            assert call_args[3] == 50  # batch_size parameter

    def test_process_languages_empty_results(self, mocker, tmp_path):
        """Test processing when no languages are available."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=[])

        mocker.patch("src.workflow.step2_process_languages.load_language_titles_safe", return_value=[])

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path, "reports": tmp_path}):
            result = process_languages("2024")

            assert result == {}

    def test_process_languages_sort_descending(self, mocker, tmp_path):
        """Test that languages are sorted by title count when requested."""
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en", "fr", "de"])

        def mock_load(lang, _):
            return {"en": ["a"], "fr": ["x", "y", "z"], "de": ["p", "q"]}[lang]

        mocker.patch("src.workflow.step2_process_languages.load_language_titles_safe", side_effect=mock_load)

        mocker.patch(
            "src.workflow.step2_process_languages._process_titles_for_language",
            side_effect=lambda lang, *_, **__: {lang: 100},
        )

        mock_report_gen = mocker.Mock()
        mock_report_gen.load_editors_json.return_value = None
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        with patch("src.workflow.step2_process_languages.OUTPUT_DIRS", {"languages": tmp_path, "reports": tmp_path}):
            result = process_languages("2024", sort_descending=True)

            # Verify ordering by title count: fr (3), de (2), en (1)
            keys = list(result.keys())
            assert keys == ["fr", "de", "en"]
