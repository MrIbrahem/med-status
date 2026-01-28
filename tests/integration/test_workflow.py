"""Integration tests for complete workflow."""

import pytest
from unittest.mock import Mock, MagicMock

from src.workflow import WorkflowOrchestrator


@pytest.mark.integration
class TestWorkflow:
    """Test complete workflow."""

    @pytest.mark.slow
    def test_full_pipeline(self, mocker):
        """Test complete data pipeline with mocked database."""

        # Mock database execute method to return different results based on query
        def mock_execute(query):
            if "langlinks" in query:
                # Medicine titles query
                return [
                    {"page_title": "Medicine", "ll_lang": "fr", "ll_title": "Médecine"},
                    {"page_title": "Medicine", "ll_lang": "en", "ll_title": "Medicine"},
                ]
            elif "meta_p" in str(query) or "dbname" in query or "wiki" in query:
                # Database mapping query
                return [
                    {"lang": "en", "dbname": "enwiki_p"},
                    {"lang": "fr", "dbname": "frwiki_p"},
                ]
            else:
                # Editor statistics query
                return [
                    {"actor_name": "Editor1", "count": 100},
                    {"actor_name": "Editor2", "count": 50},
                ]

        mock_db = MagicMock()
        mock_db.execute = Mock(side_effect=mock_execute)

        mock_db_context = mocker.Mock()
        mock_db_context.__enter__ = mocker.Mock(return_value=mock_db)
        mock_db_context.__exit__ = mocker.Mock(return_value=None)

        mocker.patch("src.workflow.Database", return_value=mock_db_context)

        # Mock file operations
        mocker.patch("src.utils.save_language_titles")
        mocker.patch("src.utils.load_language_titles", return_value=["Medicine"])
        mocker.patch("src.utils.get_available_languages", return_value=["en"])

        # Create actual instances but mock their file I/O
        mocker.patch("src.reports.ReportGenerator.save_editors_json")
        mocker.patch("src.reports.ReportGenerator.generate_language_report")
        mocker.patch("src.reports.ReportGenerator.generate_global_report")

        # Run workflow
        orchestrator = WorkflowOrchestrator()
        exit_code = orchestrator.run_complete_workflow("2024", languages=["en"])

        # Verify success
        assert exit_code == 0
