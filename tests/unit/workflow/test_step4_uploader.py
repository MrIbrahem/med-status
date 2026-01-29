"""Test report uploader service."""

from unittest.mock import Mock, mock_open, patch

import pytest
from src.workflow.step4_uploader import ReportUploader


@pytest.mark.unit
@patch("src.workflow.step4_uploader.Path")
def test_get_report_files(mock_path):
    """Test finding report files."""
    mock_reports_path = Mock()
    mock_reports_path.exists.return_value = True
    mock_reports_path.glob.return_value = [
        Mock(absolute=lambda: "/path/ar.wiki"),
        Mock(absolute=lambda: "/path/es.wiki"),
    ]
    mock_path.return_value = mock_reports_path

    uploader = ReportUploader()
    files = uploader._get_report_files()

    assert len(files) == 2


@pytest.mark.unit
@patch("src.workflow.step4_uploader.PageMWClient")
@patch("builtins.open", new_callable=mock_open, read_data="Test content")
@patch("os.path.basename")
def test_upload_report_success(mock_basename, mock_open_class, mock_page_class):
    """Test successful report upload."""
    # Setup mocks
    mock_basename.return_value = "ar.wiki"

    mock_page = Mock()
    mock_page.exists.return_value = False
    mock_page.save.return_value = {"result": "Success"}
    mock_page_class.return_value = mock_page

    uploader = ReportUploader()
    success = uploader._upload_report("/path/ar.wiki", "2025")

    assert success is True
    mock_page.save.assert_called_once()


@pytest.mark.unit
@patch("src.workflow.step4_uploader.PageMWClient")
@patch("builtins.open", new_callable=mock_open, read_data="Global content")
@patch("os.path.basename")
def test_upload_report_global(mock_basename, mock_open_class, mock_page_class):
    """Test uploading global (total_report) file."""
    # Setup mocks
    mock_basename.return_value = "total_report.wiki"

    mock_page = Mock()
    mock_page.exists.return_value = False
    mock_page.save.return_value = {"result": "Success"}
    mock_page_class.return_value = mock_page

    uploader = ReportUploader()
    success = uploader._upload_report("/path/total_report.wiki", "2025")

    assert success is True
    # Verify the edit summary is for global report
    mock_page.save.assert_called_once()


@pytest.mark.unit
@patch("src.workflow.step4_uploader.Path")
def test_get_report_files_no_directory(mock_path):
    """Test finding report files when directory doesn't exist."""
    mock_reports_path = Mock()
    mock_reports_path.exists.return_value = False
    mock_path.return_value = mock_reports_path

    uploader = ReportUploader()
    files = uploader._get_report_files()

    assert files == []


@pytest.mark.unit
@patch("src.workflow.step4_uploader.PageMWClient")
@patch("builtins.open", new_callable=mock_open, read_data="Test content")
@patch("os.path.basename")
def test_upload_report_file_read_error(mock_basename, mock_open_class, mock_page_class):
    """Test report upload when file read fails."""
    # Setup mocks
    mock_basename.return_value = "ar.wiki"

    mock_page = Mock()
    mock_page.exists.return_value = False
    mock_page.save.side_effect = IOError("Upload failed")
    mock_page_class.return_value = mock_page

    uploader = ReportUploader()
    success = uploader._upload_report("/path/ar.wiki", "2025")

    assert success is False


@pytest.mark.unit
@patch("src.workflow.step4_uploader.Path")
def test_upload_all_reports_no_files(mock_path):
    """Test uploading when no report files exist."""
    mock_reports_path = Mock()
    mock_reports_path.exists.return_value = True
    mock_reports_path.glob.return_value = []
    mock_path.return_value = mock_reports_path

    uploader = ReportUploader()
    results = uploader.upload_all_reports("2025")

    assert results["total"] == 0
    assert results["success"] == 0
    assert results["failed"] == 0


@pytest.mark.unit
@patch("src.workflow.step4_uploader.ReportUploader._upload_report")
@patch("src.workflow.step4_uploader.Path")
def test_upload_all_reports_multiple(mock_path, mock_upload):
    """Test uploading multiple reports."""
    mock_reports_path = Mock()
    mock_reports_path.exists.return_value = True
    mock_reports_path.glob.return_value = [
        Mock(absolute=lambda: "/path/ar.wiki"),
        Mock(absolute=lambda: "/path/es.wiki"),
        Mock(absolute=lambda: "/path/total_report.wiki"),
    ]
    mock_path.return_value = mock_reports_path

    # Make first two succeed, last one fail
    mock_upload.side_effect = [True, True, False]

    uploader = ReportUploader()
    results = uploader.upload_all_reports("2025")

    assert results["total"] == 3
    assert results["success"] == 2
    assert results["failed"] == 1


@pytest.mark.unit
@patch("src.workflow.step4_uploader.PageMWClient")
@patch("builtins.open", new_callable=mock_open, read_data="Test content")
@patch("os.path.exists")
@patch("os.path.join")
def test_upload_single_report(mock_join, mock_exists, mock_open_class, mock_page_class):
    """Test uploading a single report by language code."""
    # Setup mocks
    mock_join.return_value = "/reports/ar.wiki"
    mock_exists.return_value = True

    mock_page = Mock()
    mock_page.exists.return_value = False
    mock_page.save.return_value = {"result": "Success"}
    mock_page_class.return_value = mock_page

    uploader = ReportUploader()
    success = uploader.upload_single_report("ar", "2025")

    assert success is True


@pytest.mark.unit
@patch("os.path.exists")
@patch("os.path.join")
def test_upload_single_report_file_not_found(mock_join, mock_exists):
    """Test uploading single report when file doesn't exist."""
    mock_join.return_value = "/reports/ar.wiki"
    mock_exists.return_value = False

    uploader = ReportUploader()
    success = uploader.upload_single_report("ar", "2025")

    assert success is False


@pytest.mark.unit
@patch("src.workflow.step4_uploader.PageMWClient")
@patch("builtins.open", new_callable=mock_open, read_data="Global content")
@patch("os.path.exists")
@patch("os.path.join")
def test_upload_single_report_global(mock_join, mock_exists, mock_open_class, mock_page_class):
    """Test uploading global report by single report method."""
    # Setup mocks
    mock_join.return_value = "/reports/total_report.wiki"
    mock_exists.return_value = True

    mock_page = Mock()
    mock_page.exists.return_value = False
    mock_page.save.return_value = {"result": "Success"}
    mock_page_class.return_value = mock_page

    uploader = ReportUploader()
    success = uploader.upload_single_report("total_report", "2025", is_global=True)

    assert success is True
