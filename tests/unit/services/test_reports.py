"""Test reports module."""

import json
import os

import pytest

from src.config import OUTPUT_DIRS
from src.services.reports import ReportGenerator


@pytest.mark.unit
class TestReportGenerator:
    """Test ReportGenerator class."""

    def test_report_generator_init(self):
        """Test report generator initialization."""
        # The init will create actual directories
        generator = ReportGenerator()
        assert generator is not None
        # Verify directories were created
        for dir_path in OUTPUT_DIRS.values():
            assert os.path.exists(dir_path)

    def test_save_editors_json(self):
        """Test saving editors to JSON."""
        generator = ReportGenerator()
        editors = {"Editor1": 100, "Editor2": 50}

        generator.save_editors_json("test", editors)

        # Verify file was created
        output_file = os.path.join(OUTPUT_DIRS["editors"], "test.json")
        assert os.path.exists(output_file)

        # Verify content
        with open(output_file, "r") as f:
            data = json.load(f)
            assert data == editors

        # Cleanup
        os.remove(output_file)

    @pytest.mark.skip(reason="Language report has changed, needs update")
    def test_generate_language_report(self):
        """Test language report generation."""
        generator = ReportGenerator()
        editors = {"Editor1": 100, "Editor2": 50}

        generator.generate_language_report("test", editors, "2024")

        # Verify file was created
        output_file = os.path.join(OUTPUT_DIRS["reports"], "test.wiki")
        assert os.path.exists(output_file)

        # Verify content
        with open(output_file, "r") as f:
            content = f.read()
            assert "2024" in content
            assert "Editor1" in content
            assert "100" in content
            assert "wikitable" in content

        # Cleanup
        os.remove(output_file)

    @pytest.mark.skip(reason="Global report has changed, needs update")
    def test_generate_global_report(self):
        """Test global report generation."""
        generator = ReportGenerator()
        all_editors = {"en": {"Editor1": 100, "Editor2": 50}, "fr": {"Editor1": 25, "Editor3": 75}}

        generator.generate_global_report(all_editors, "2024")

        # Verify file was created
        output_file = os.path.join(OUTPUT_DIRS["reports"], "total_report.wiki")
        assert os.path.exists(output_file)

        # Verify content
        with open(output_file, "r") as f:
            content = f.read()
            assert "2024" in content
            assert "Global" in content
            assert "Total languages" in content
            assert "Total unique editors" in content

        # Cleanup
        os.remove(output_file)

    def test_load_editors_json_file_not_found(self):
        """Test loading editors JSON when file doesn't exist."""
        generator = ReportGenerator()

        result = generator.load_editors_json("nonexistent_lang")

        # Should return empty list when file not found
        assert result == {}
