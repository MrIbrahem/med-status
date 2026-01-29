"""Unit tests for main module."""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.main import main, parse_arguments


@pytest.mark.unit
class TestParseArguments:
    """Test argument parsing."""

    def test_parse_arguments_defaults(self):
        """Test parsing with default arguments."""
        with patch.object(sys, "argv", ["start.py"]):
            args = parse_arguments()
            assert args.year  # Has default value
            assert args.log_level == "INFO"
            assert args.log_file is None
            assert args.languages is None
            assert args.skip_steps == []
            assert args.desc is False
            assert args.skip_existing is False

    def test_parse_arguments_with_year(self):
        """Test parsing with year argument."""
        with patch.object(sys, "argv", ["start.py", "--year", "2023"]):
            args = parse_arguments()
            assert args.year == "2023"

    def test_parse_arguments_with_log_level(self):
        """Test parsing with log level argument."""
        with patch.object(sys, "argv", ["start.py", "--log-level", "DEBUG"]):
            args = parse_arguments()
            assert args.log_level == "DEBUG"

    def test_parse_arguments_with_log_file(self):
        """Test parsing with log file argument."""
        with patch.object(sys, "argv", ["start.py", "--log-file", "output.log"]):
            args = parse_arguments()
            assert args.log_file == "output.log"

    def test_parse_arguments_with_languages(self):
        """Test parsing with specific languages."""
        with patch.object(sys, "argv", ["start.py", "--languages", "en", "fr", "de"]):
            args = parse_arguments()
            assert args.languages == ["en", "fr", "de"]

    def test_parse_arguments_with_skip_steps(self):
        """Test parsing with skip steps argument."""
        with patch.object(sys, "argv", ["start.py", "--skip-steps", "1", "3"]):
            args = parse_arguments()
            assert args.skip_steps == [1, 3]

    def test_parse_arguments_with_desc(self):
        """Test parsing with descending sort flag."""
        with patch.object(sys, "argv", ["start.py", "--desc"]):
            args = parse_arguments()
            assert args.desc is True

    def test_parse_arguments_with_skip_existing(self):
        """Test parsing with skip existing flag."""
        with patch.object(sys, "argv", ["start.py", "--skip-existing"]):
            args = parse_arguments()
            assert args.skip_existing is True


@pytest.mark.unit
class TestMain:
    """Test main function."""

    @patch("src.main.WorkflowOrchestrator")
    @patch("src.main.parse_arguments")
    @patch("src.main.setup_logging")
    def test_main_success(self, mock_setup_logging, mock_parse_args, mock_orchestrator_class):
        """Test main function with successful execution."""
        # Setup mocks
        mock_args = Mock()
        mock_args.year = "2024"
        mock_args.log_level = "INFO"
        mock_args.log_file = None
        mock_args.languages = None
        mock_args.skip_steps = []
        mock_args.desc = False
        mock_args.skip_existing = False
        mock_parse_args.return_value = mock_args

        mock_orchestrator = Mock()
        mock_orchestrator.run_complete_workflow.return_value = 0
        mock_orchestrator_class.return_value = mock_orchestrator

        # Run main
        exit_code = main()

        # Verify
        assert exit_code == 0
        mock_setup_logging.assert_called_once_with(level="INFO", log_file=None)
        mock_orchestrator.run_complete_workflow.assert_called_once_with(
            year="2024", languages=None, skip_steps=[], sort_desc=False, skip_existing=False
        )

    @patch("src.main.WorkflowOrchestrator")
    @patch("src.main.parse_arguments")
    @patch("src.main.setup_logging")
    def test_main_with_arguments(self, mock_setup_logging, mock_parse_args, mock_orchestrator_class):
        """Test main function with custom arguments."""
        # Setup mocks
        mock_args = Mock()
        mock_args.year = "2023"
        mock_args.log_level = "DEBUG"
        mock_args.log_file = "debug.log"
        mock_args.languages = ["en", "fr"]
        mock_args.skip_steps = [2]
        mock_args.desc = True
        mock_args.skip_existing = True
        mock_parse_args.return_value = mock_args

        mock_orchestrator = Mock()
        mock_orchestrator.run_complete_workflow.return_value = 1
        mock_orchestrator_class.return_value = mock_orchestrator

        # Run main
        exit_code = main()

        # Verify arguments passed through
        mock_setup_logging.assert_called_once_with(level="DEBUG", log_file="debug.log")
        mock_orchestrator.run_complete_workflow.assert_called_once_with(
            year="2023", languages=["en", "fr"], skip_steps=[2], sort_desc=True, skip_existing=True
        )
        assert exit_code == 1

    @patch("src.main.WorkflowOrchestrator")
    @patch("src.main.parse_arguments")
    @patch("src.main.setup_logging")
    def test_main_with_skip_steps_logging(self, mock_setup_logging, mock_parse_args, mock_orchestrator_class):
        """Test main function logs skip steps correctly."""
        # Setup mocks
        mock_args = Mock()
        mock_args.year = "2024"
        mock_args.log_level = "INFO"
        mock_args.log_file = None
        mock_args.languages = None
        mock_args.skip_steps = [1, 3]
        mock_args.desc = False
        mock_args.skip_existing = False
        mock_parse_args.return_value = mock_args

        mock_orchestrator = Mock()
        mock_orchestrator.run_complete_workflow.return_value = 0
        mock_orchestrator_class.return_value = mock_orchestrator

        # Run main
        exit_code = main()

        # Verify skip steps are passed
        mock_orchestrator.run_complete_workflow.assert_called_once()
        call_args = mock_orchestrator.run_complete_workflow.call_args[1]
        assert call_args["skip_steps"] == [1, 3]

    @patch("src.main.WorkflowOrchestrator")
    @patch("src.main.parse_arguments")
    @patch("src.main.setup_logging")
    def test_main_with_languages_logging(self, mock_setup_logging, mock_parse_args, mock_orchestrator_class):
        """Test main function logs languages correctly."""
        # Setup mocks
        mock_args = Mock()
        mock_args.year = "2024"
        mock_args.log_level = "INFO"
        mock_args.log_file = None
        mock_args.languages = ["en", "fr", "de"]
        mock_args.skip_steps = []
        mock_args.desc = False
        mock_args.skip_existing = False
        mock_parse_args.return_value = mock_args

        mock_orchestrator = Mock()
        mock_orchestrator.run_complete_workflow.return_value = 0
        mock_orchestrator_class.return_value = mock_orchestrator

        # Run main
        exit_code = main()

        # Verify languages are passed
        mock_orchestrator.run_complete_workflow.assert_called_once()
        call_args = mock_orchestrator.run_complete_workflow.call_args[1]
        assert call_args["languages"] == ["en", "fr", "de"]
