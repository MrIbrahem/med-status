"""Unit tests for workflow orchestration."""

from unittest.mock import MagicMock

import pytest

from src.workflow import WorkflowOrchestrator


@pytest.mark.unit
class TestWorkflowOrchestrator:
    """Test workflow orchestrator."""

    def test_orchestrator_init(self):
        """Test orchestrator initialization."""
        orchestrator = WorkflowOrchestrator()
        assert orchestrator.query_builder is not None
        assert orchestrator.processor is not None
        assert orchestrator.report_generator is not None

    def test_get_database_mapping(self, mocker):
        """Test getting database mappings."""
        # Mock database
        mock_db = MagicMock()
        mock_db.execute.return_value = [
            {"lang": "ar", "dbname": "arwiki"},
            {"lang": "fr", "dbname": "frwiki"},
        ]

        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(return_value=mock_db)
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.services.db_mapping.save_db_mapping", return_value={})
        mocker.patch("src.services.db_mapping.load_db_mapping", return_value={})
        mocker.patch("src.services.db_mapping.Database", return_value=mock_db_context)
        # mocker.patch("src.workflow.get_database_mapping", return_value=mock_db_context)

        orchestrator = WorkflowOrchestrator()
        mapping = orchestrator.get_database_mapping()

        assert mapping["ar"] == "arwiki"
        assert mapping["fr"] == "frwiki"

        # get_database_mapping added 'en' by default
        assert mapping["en"] == "enwiki"

    @pytest.mark.skip(reason="Global report has changed, needs update")
    def test_generate_reports(self, mocker):
        """Test generating reports."""
        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.ReportGenerator", return_value=mock_report_gen)

        orchestrator = WorkflowOrchestrator()
        all_editors = {"en": {"Editor1": 100}}

        orchestrator.generate_reports(all_editors, "2024")

        mock_report_gen.generate_global_report.assert_not_called()

    def test_process_languages(self, mocker):
        """Test processing languages."""
        # Mock database
        mock_db = MagicMock()
        mock_db.execute.return_value = [
            {"lang": "en", "dbname": "enwiki_p"},
        ]

        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(return_value=mock_db)
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.workflow.step1_retrieve_titles.DatabaseAnalytics", return_value=mock_db_context)
        mocker.patch("src.services.processor.DatabaseAnalytics", return_value=mock_db_context)
        mocker.patch("src.workflow.step2_process_languages.get_available_languages", return_value=["en"])
        mocker.patch("src.workflow.step2_process_languages.load_language_titles_safe", return_value=["Medicine"])

        # Mock processor methods - patch at the class level
        mocker.patch("src.services.processor.EditorProcessor.process_language_ar_en", return_value={"Editor1": 100})
        mocker.patch("src.services.processor.EditorProcessor.process_language_patch", return_value={"Editor1": 100})

        # Mock report generator methods
        mock_report_gen = mocker.Mock()
        mock_report_gen.load_editors_json.return_value = None
        mocker.patch("src.workflow.step2_process_languages.ReportGenerator", return_value=mock_report_gen)

        orchestrator = WorkflowOrchestrator()
        all_editors = orchestrator.process_languages("2024", languages=["en"])

        assert "en" in all_editors
        assert all_editors == {"en": {"Editor1": 100}}
        assert all_editors["en"]["Editor1"] == 100
