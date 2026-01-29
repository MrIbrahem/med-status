"""Test processor module."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.services.processor import EditorProcessor


@pytest.mark.unit
class TestEditorProcessor:
    """Test EditorProcessor class."""

    def test_processor_init(self):
        """Test processor initialization."""
        processor = EditorProcessor()
        assert processor is not None
        assert processor.query_builder is not None

    @patch("src.services.processor.DatabaseAnalytics")
    def test_process_language_filters_ips(self, mock_db_class):
        """Test that IP addresses are filtered out."""
        # Setup mock
        mock_db = MagicMock()
        mock_db.__enter__ = Mock(return_value=mock_db)
        mock_db.__exit__ = Mock(return_value=False)
        mock_db.execute.return_value = [
            {"actor_name": "192.168.1.1", "count": 100},
            {"actor_name": "ValidUser", "count": 50},
        ]
        mock_db_class.return_value = mock_db

        processor = EditorProcessor()
        editors = processor.process_language("test", ["Title1"], "2024")

        # IP should be filtered out
        assert "192.168.1.1" not in editors
        assert "ValidUser" in editors
        assert editors["ValidUser"] == 50

    @patch("src.services.processor.DatabaseAnalytics")
    def test_process_language_filters_bots(self, mock_db_class):
        """Test that bot accounts are filtered out."""
        # Setup mock
        mock_db = MagicMock()
        mock_db.__enter__ = Mock(return_value=mock_db)
        mock_db.__exit__ = Mock(return_value=False)
        mock_db.execute.return_value = [
            {"actor_name": "SomeBot", "count": 100},
            {"actor_name": "ValidUser", "count": 50},
        ]
        mock_db_class.return_value = mock_db

        processor = EditorProcessor()
        editors = processor.process_language("test", ["Title1"], "2024")

        # Bot should be filtered out
        assert "SomeBot" not in editors
        assert "ValidUser" in editors

    def test_aggregate_editors(self):
        """Test editor aggregation across languages."""
        processor = EditorProcessor()

        all_editors = {"en": {"Editor1": 100, "Editor2": 50}, "fr": {"Editor1": 25, "Editor3": 75}}

        aggregated = processor.aggregate_editors(all_editors)

        assert aggregated["Editor1"] == 125  # 100 + 25
        assert aggregated["Editor2"] == 50
        assert aggregated["Editor3"] == 75
