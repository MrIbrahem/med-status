"""Unit tests for workflow orchestration."""

import pytest
from unittest.mock import MagicMock

from src.workflow import WorkflowOrchestrator


@pytest.mark.unit
class TestWorkflowOrchestrator:
    """Test workflow orchestrator."""

    def test_orchestrator_init(self):
        """Test orchestrator initialization."""
        orchestrator = WorkflowOrchestrator()
        assert orchestrator.host == "analytics.db.svc.wikimedia.cloud"
        assert orchestrator.query_builder is not None
        assert orchestrator.processor is not None
        assert orchestrator.report_generator is not None

    def test_retrieve_medicine_titles(self, mocker):
        """Test retrieving medicine titles."""
        # Mock database
        mock_db = MagicMock()
        mock_db.execute.return_value = [
            {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
            {"page_title": "Health", "ll_lang": "es", "ll_title": "Salud"},
        ]

        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(return_value=mock_db)
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.workflow.Database", return_value=mock_db_context)
        mocker.patch("src.workflow.save_language_titles")

        orchestrator = WorkflowOrchestrator()
        titles = orchestrator.retrieve_medicine_titles()

        assert "fr" in titles
        assert "es" in titles
        assert "Médecine" in titles["fr"]
        assert "Salud" in titles["es"]

    def test_get_database_mapping(self, mocker):
        """Test getting database mappings."""
        # Mock database
        mock_db = MagicMock()
        mock_db.execute.return_value = [
            {"lang": "en", "dbname": "enwiki_p"},
            {"lang": "fr", "dbname": "frwiki_p"},
        ]

        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(return_value=mock_db)
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.workflow.Database", return_value=mock_db_context)

        orchestrator = WorkflowOrchestrator()
        mapping = orchestrator.get_database_mapping()

        assert mapping["en"] == "enwiki_p"
        assert mapping["fr"] == "frwiki_p"

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

        mocker.patch("src.workflow.Database", return_value=mock_db_context)
        mocker.patch("src.workflow.get_available_languages", return_value=["en"])
        mocker.patch("src.workflow.load_language_titles", return_value=["Medicine"])

        # Mock processor
        mock_processor = mocker.Mock()
        mock_processor.process_language.return_value = {"Editor1": 100}
        mocker.patch("src.workflow.EditorProcessor", return_value=mock_processor)

        # Mock report generator
        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.ReportGenerator", return_value=mock_report_gen)

        orchestrator = WorkflowOrchestrator()
        all_editors = orchestrator.process_languages("2024", languages=["en"])

        assert "en" in all_editors
        assert all_editors["en"]["Editor1"] == 100

    def test_generate_reports(self, mocker):
        """Test generating reports."""
        mock_report_gen = mocker.Mock()
        mocker.patch("src.workflow.ReportGenerator", return_value=mock_report_gen)

        orchestrator = WorkflowOrchestrator()
        all_editors = {"en": {"Editor1": 100}}

        orchestrator.generate_reports(all_editors, "2024")

        mock_report_gen.generate_global_report.assert_called_once_with(all_editors, "2024")

    def test_run_complete_workflow_success(self, mocker):
        """Test running complete workflow successfully."""
        # Mock all workflow methods
        orchestrator = WorkflowOrchestrator()

        mocker.patch.object(orchestrator, "retrieve_medicine_titles", return_value={"en": ["Medicine"]})
        mocker.patch.object(orchestrator, "process_languages", return_value={"en": {"Editor1": 100}})
        mocker.patch.object(orchestrator, "generate_reports")

        # Mock processor for final summary
        mock_processor = mocker.Mock()
        mock_processor.aggregate_editors.return_value = {"Editor1": 100}
        orchestrator.processor = mock_processor

        exit_code = orchestrator.run_complete_workflow("2024")

        assert exit_code == 0

    def test_run_complete_workflow_failure(self, mocker):
        """Test running complete workflow with failure."""
        orchestrator = WorkflowOrchestrator()

        # Mock method to raise exception
        mocker.patch.object(orchestrator, "retrieve_medicine_titles", side_effect=Exception("Test error"))

        exit_code = orchestrator.run_complete_workflow("2024")

        assert exit_code == 1
