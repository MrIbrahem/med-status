"""Unit tests for step3_generate_reports module."""

import pytest

from src.workflow.step3_generate_reports import generate_reports


@pytest.mark.unit
class TestGenerateReports:
    """Test generate_reports function."""

    def test_generate_reports(self, mocker):
        """Test generating global report."""
        all_editors = {
            "en": {"Editor1": 100, "Editor2": 50},
            "fr": {"Editor3": 75},
        }

        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.step3_generate_reports.ReportGenerator", return_value=mock_report_gen)

        generate_reports(all_editors, "2024")

        # Verify generate_global_report was called with correct args
        mock_report_gen.generate_global_report.assert_called_once_with(all_editors, "2024")

    def test_generate_reports_empty_editors(self, mocker):
        """Test generating report with empty editors."""
        all_editors = {}

        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.step3_generate_reports.ReportGenerator", return_value=mock_report_gen)

        generate_reports(all_editors, "2024")

        # Should still call generate_global_report even with empty dict
        mock_report_gen.generate_global_report.assert_called_once_with({}, "2024")

    def test_generate_reports_single_language(self, mocker):
        """Test generating report with single language."""
        all_editors = {"en": {"Editor1": 100}}

        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.step3_generate_reports.ReportGenerator", return_value=mock_report_gen)

        generate_reports(all_editors, "2023")

        mock_report_gen.generate_global_report.assert_called_once_with({"en": {"Editor1": 100}}, "2023")

    def test_generate_reports_multiple_languages(self, mocker):
        """Test generating report with multiple languages."""
        all_editors = {
            "en": {"Editor1": 100},
            "fr": {"Editor2": 50},
            "de": {"Editor3": 75},
            "ar": {"Editor4": 25},
        }

        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.step3_generate_reports.ReportGenerator", return_value=mock_report_gen)

        generate_reports(all_editors, "2024")

        # Verify all editors are passed
        call_args = mock_report_gen.generate_global_report.call_args[0]
        assert call_args[0] == all_editors
        assert call_args[1] == "2024"

    def test_generate_reports_year_parameter(self, mocker):
        """Test that year parameter is correctly passed."""
        all_editors = {"en": {"Editor1": 100}}

        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.step3_generate_reports.ReportGenerator", return_value=mock_report_gen)

        # Test with different years
        for year in ["2020", "2021", "2022", "2023", "2024"]:
            generate_reports(all_editors, year)

            # Check the last call (most recent)
            assert mock_report_gen.generate_global_report.call_args[0][1] == year
