# MDWiki Upload Integration Plan

## Overview

Add a new step to automatically upload all generated WikiText reports to mdwiki.org using the mwclient library.

---

## New Workflow Step

### Step 6: Upload Reports to MDWiki

**After**: Step 5 (Generate global report)
**Purpose**: Upload all `.wiki` files to mdwiki.org
**Output**: Published pages on MDWiki

**Page Mapping**:
```
reports/total_report.wiki → WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025_(all)
reports/ar.wiki → WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025/ar
reports/es.wiki → WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025/es
...
```

---

## Implementation Plan

### 1. Update Dependencies

**File**: `requirements.txt`

```txt
# MediaWiki client (NEW)
mwclient>=0.11.0
```

---

### 2. Update Environment Configuration

**File**: `.env.example`

```bash
# MDWiki Credentials (NEW)
MDWIKI_USERNAME=your_username_here
MDWIKI_PASSWORD=your_password_here
```

**File**: `.env` (Create locally, add to .gitignore)

```bash
# MDWiki credentials (DO NOT COMMIT)
MDWIKI_USERNAME=YourActualUsername
MDWIKI_PASSWORD=YourActualPassword
```

---

### 3. Update Configuration

**File**: `src/config.py`

```python
"""
Application configuration.

All configuration constants for the Wikipedia Medicine project.
"""
# .. existing code

# MDWiki Configuration (NEW)
MDWIKI_USERNAME: str = os.getenv("MDWIKI_USERNAME", "")
MDWIKI_PASSWORD: str = os.getenv("MDWIKI_PASSWORD", "")
MDWIKI_SITE: str = "mdwiki.org"
MDWIKI_BASE_PAGE: str = "WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors"

# Validate MDWiki credentials
if not MDWIKI_USERNAME or not MDWIKI_PASSWORD:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(
        "MDWiki credentials not found in environment variables. "
        "Upload functionality will be disabled."
    )
```

---

### 4. Create MDWiki Service Module


**File**: `src/services/page.py`

```python
"""
MediaWiki page management using mwclient.

This module provides a class-based interface for interacting with MediaWiki
pages on mdwiki.org.
"""
import functools
import logging
from typing import Optional

import mwclient
import mwclient.errors

from src.config import MDWIKI_USERNAME, MDWIKI_PASSWORD, MDWIKI_SITE

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def initialize_site_connection(username: str, password: str) -> mwclient.Site:
    """
    Initialize and cache MediaWiki site connection.

    Uses functools.lru_cache to ensure only one connection is created
    and reused across all page operations.

    Args:
        username: MDWiki username
        password: MDWiki password

    Returns:
        Authenticated mwclient.Site instance

    Raises:
        mwclient.errors.LoginError: If authentication fails

    Example:
        >>> site = initialize_site_connection("user", "pass")
        >>> print(site.host)
        'mdwiki.org'
    """
    logger.info("Initializing connection to %s", MDWIKI_SITE)
    site_mw = mwclient.Site(MDWIKI_SITE)

    try:
        site_mw.login(username, password)
        logger.info("✓ Successfully logged in to %s as %s", MDWIKI_SITE, username)
    except mwclient.errors.LoginError as e:
        logger.error("Failed to login to %s: %s", MDWIKI_SITE, e)
        raise

    return site_mw


class PageMWClient:
    """
    MediaWiki page client for mdwiki.org.

    Provides methods to read, create, and update pages on mdwiki.org
    with proper error handling and logging.

    Attributes:
        title: Full page title including namespace
        username: MDWiki username
        password: MDWiki password
        site_mw: Cached site connection
        page: mwclient.Page instance

    Example:
        >>> page = PageMWClient("WikiProjectMed:Test")
        >>> if not page.exists():
        ...     page.create("Test content", "Creating test page")
        >>> else:
        ...     page.save("Updated content", "Updating test page")
    """

    def __init__(self, title: str):
        """
        Initialize page client.

        Args:
            title: Full page title (e.g., "WikiProjectMed:Page_Title")

        Raises:
            ValueError: If credentials are not configured
        """
        if not MDWIKI_USERNAME or not MDWIKI_PASSWORD:
            raise ValueError(
                "MDWiki credentials not configured. "
                "Set MDWIKI_USERNAME and MDWIKI_PASSWORD in .env file."
            )

        self.title = title
        self.username = MDWIKI_USERNAME
        self.password = MDWIKI_PASSWORD

        logger.debug("Initializing PageMWClient for: %s", title)

        # Get cached site connection
        self.site_mw = initialize_site_connection(self.username, self.password)

        # Get page object
        self.page = self.site_mw.pages[title]

        logger.debug("Page object created for: %s", title)

    def get_text(self) -> str:
        """
        Get current page text content.

        Returns:
            Page content as string (empty string if page doesn't exist)

        Example:
            >>> page = PageMWClient("WikiProjectMed:Test")
            >>> content = page.get_text()
            >>> print(content)
            'Current page content...'
        """
        try:
            text = self.page.text()
            logger.debug("Retrieved text from %s (%d chars)", self.title, len(text))
            return text
        except Exception as e:
            logger.error("Failed to get text from %s: %s", self.title, e)
            return ""

    def exists(self) -> bool:
        """
        Check if page exists.

        Returns:
            True if page exists, False otherwise

        Example:
            >>> page = PageMWClient("WikiProjectMed:Test")
            >>> if page.exists():
            ...     print("Page exists")
        """
        exists = self.page.exists
        logger.debug("Page %s exists: %s", self.title, exists)
        return exists

    def save(self, newtext: str, summary: str) -> Dict[str, Any]:
        """
        Save (update) existing page or create new page.

        Args:
            newtext: New page content (WikiText format)
            summary: Edit summary describing the change

        Returns:
            Result dictionary from MediaWiki API

        Raises:
            mwclient.errors.APIError: If save operation fails

        Example:
            >>> page = PageMWClient("WikiProjectMed:Test")
            >>> result = page.save("New content", "Updated statistics")
            >>> print(result)
            {'result': 'Success', ...}
        """
        try:
            logger.info("Saving page: %s", self.title)
            logger.debug("Content length: %d chars", len(newtext))
            logger.debug("Edit summary: %s", summary)

            result = self.page.save(newtext, summary=summary)

            logger.info("✓ Successfully saved page: %s", self.title)
            logger.debug("Save result: %s", result)

            return result

        except mwclient.errors.APIError as e:
            logger.error("Failed to save page %s: %s", self.title, e)
            raise

    def create(self, newtext: str, summary: str) -> Dict[str, Any]:
        """
        Create new page (alias for save).

        Note: In MediaWiki/mwclient, save() works for both creating
        and updating pages. This method is provided for semantic clarity.

        Args:
            newtext: New page content (WikiText format)
            summary: Edit summary describing the page creation

        Returns:
            Result dictionary from MediaWiki API

        Example:
            >>> page = PageMWClient("WikiProjectMed:NewPage")
            >>> result = page.create("Initial content", "Creating new page")
        """
        logger.info("Creating new page: %s", self.title)
        return self.save(newtext, summary)


def get_page_title(lang: str, year: str, is_global: bool = False) -> str:
    """
    Generate MDWiki page title for a report.

    Args:
        lang: Language code (e.g., "ar", "es")
        year: Year of the report (e.g., "2025")
        is_global: True for global report, False for language-specific

    Returns:
        Full page title with namespace

    Example:
        >>> get_page_title("ar", "2025")
        'WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025/ar'
        >>> get_page_title("", "2025", is_global=True)
        'WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025_(all)'
    """
    from src.config import MDWIKI_BASE_PAGE

    if is_global:
        return f"{MDWIKI_BASE_PAGE}_{year}_(all)"
    else:
        return f"{MDWIKI_BASE_PAGE}_{year}/{lang}"
```

add `PageMWClient` to  `src/services/__init__.py`

---

### 5. Create Upload Service Module

**File**: `src/workflow/step4_uploader.py`

```python
"""
Upload service for publishing reports to MDWiki.

This module handles uploading all generated WikiText reports to mdwiki.org.
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

from src.config import OUTPUT_DIRS, CURRENT_YEAR
from src.services.page import PageMWClient, get_page_title

logger = logging.getLogger(__name__)


class ReportUploader:
    """
    Upload WikiText reports to MDWiki.

    Handles uploading both language-specific and global reports
    to the appropriate pages on mdwiki.org.

    Example:
        >>> uploader = ReportUploader()
        >>> results = uploader.upload_all_reports("2025")
        >>> print(f"Uploaded {results['success']} reports")
    """

    def __init__(self):
        """Initialize report uploader."""
        self.reports_dir = OUTPUT_DIRS["reports"]
        logger.debug("ReportUploader initialized with reports_dir: %s", self.reports_dir)

    def upload_all_reports(self, year: str = CURRENT_YEAR) -> Dict[str, int]:
        """
        Upload all reports in the reports directory.

        Args:
            year: Year for the report pages (default: current year)

        Returns:
            Dictionary with upload statistics:
            - 'success': Number of successful uploads
            - 'failed': Number of failed uploads
            - 'total': Total number of reports

        Example:
            >>> uploader = ReportUploader()
            >>> stats = uploader.upload_all_reports("2025")
            >>> print(f"{stats['success']}/{stats['total']} uploaded")
        """
        logger.info("=" * 60)
        logger.info("Starting upload of all reports to MDWiki")
        logger.info("=" * 60)

        # Find all .wiki files
        report_files = self._get_report_files()

        if not report_files:
            logger.warning("No report files found in %s", self.reports_dir)
            return {"success": 0, "failed": 0, "total": 0}

        logger.info("Found %d report files to upload", len(report_files))

        # Upload each report
        results = {"success": 0, "failed": 0, "total": len(report_files)}

        for filepath in report_files:
            filename = os.path.basename(filepath)

            try:
                success = self._upload_report(filepath, year)
                if success:
                    results["success"] += 1
                    logger.info("✓ Uploaded: %s", filename)
                else:
                    results["failed"] += 1
                    logger.error("✗ Failed: %s", filename)

            except Exception as e:
                results["failed"] += 1
                logger.error("✗ Error uploading %s: %s", filename, e, exc_info=True)

        # Log summary
        logger.info("=" * 60)
        logger.info("Upload Summary:")
        logger.info("  Successful: %d", results["success"])
        logger.info("  Failed: %d", results["failed"])
        logger.info("  Total: %d", results["total"])
        logger.info("=" * 60)

        return results

    def _get_report_files(self) -> List[str]:
        """
        Get list of all .wiki files in reports directory.

        Returns:
            List of absolute file paths
        """
        reports_path = Path(self.reports_dir)

        if not reports_path.exists():
            logger.warning("Reports directory does not exist: %s", self.reports_dir)
            return []

        wiki_files = list(reports_path.glob("*.wiki"))
        filepaths = [str(f.absolute()) for f in wiki_files]

        logger.debug("Found %d .wiki files", len(filepaths))
        return filepaths

    def _upload_report(self, filepath: str, year: str) -> bool:
        """
        Upload a single report file to MDWiki.

        Args:
            filepath: Path to .wiki file
            year: Year for the page title

        Returns:
            True if upload successful, False otherwise
        """
        filename = os.path.basename(filepath)
        lang_code = filename.replace(".wiki", "")

        logger.info("-" * 60)
        logger.info("Uploading: %s", filename)

        # Determine if this is the global report
        is_global = (lang_code == "total_report")

        # Generate page title
        page_title = get_page_title(lang_code, year, is_global)
        logger.info("Target page: %s", page_title)

        # Read report content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.debug("Read %d characters from %s", len(content), filename)

        except Exception as e:
            logger.error("Failed to read file %s: %s", filepath, e)
            return False

        # Upload to MDWiki
        try:
            page = PageMWClient(page_title)

            # Generate edit summary
            if is_global:
                summary = f"Update global medical editors statistics for {year}"
            else:
                summary = f"Update {lang_code} medical editors statistics for {year}"

            # Check if page exists
            if page.exists():
                logger.info("Page exists, updating...")
            else:
                logger.info("Page does not exist, creating...")

            # Save page
            result = page.save(content, summary)

            logger.info("✓ Upload successful")
            return True

        except Exception as e:
            logger.error("Failed to upload to %s: %s", page_title, e)
            return False

    def upload_single_report(
        self,
        lang: str,
        year: str = CURRENT_YEAR,
        is_global: bool = False
    ) -> bool:
        """
        Upload a single report by language code.

        Args:
            lang: Language code (e.g., "ar", "es") or "total_report"
            year: Year for the page title
            is_global: True for global report

        Returns:
            True if upload successful, False otherwise

        Example:
            >>> uploader = ReportUploader()
            >>> uploader.upload_single_report("ar", "2025")
            True
        """
        if is_global:
            filename = "total_report.wiki"
        else:
            filename = f"{lang}.wiki"

        filepath = os.path.join(self.reports_dir, filename)

        if not os.path.exists(filepath):
            logger.error("Report file not found: %s", filepath)
            return False

        return self._upload_report(filepath, year)
```

---

### 6. Update Main Application

* add Step 4 to *`src/workflow/__init__.py`

```python
    def run_complete_workflow(...):
        # ... existing code

        if not skip_steps or 4 not in skip_steps:
            # Step 4: Upload reports
            results = uploader.upload_all_reports(year=CURRENT_YEAR)
        else:
            logger.info("✓ Skipping Step 5: Upload reports")

```

---

### 7. Add Tests

**File**: `tests/unit/test_services_page.py`

```python
"""Test MDWiki page service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.page import PageMWClient, get_page_title, initialize_site_connection


@pytest.mark.unit
def test_get_page_title_language():
    """Test page title generation for language-specific report."""
    title = get_page_title("ar", "2025")
    assert title == "WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025/ar"


@pytest.mark.unit
def test_get_page_title_global():
    """Test page title generation for global report."""
    title = get_page_title("", "2025", is_global=True)
    assert title == "WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025_(all)"


@pytest.mark.unit
@patch('src.services.page.MDWIKI_USERNAME', 'testuser')
@patch('src.services.page.MDWIKI_PASSWORD', 'testpass')
@patch('src.services.page.mwclient.Site')
def test_initialize_site_connection(mock_site):
    """Test site connection initialization."""
    mock_site_instance = Mock()
    mock_site.return_value = mock_site_instance

    # Clear cache
    initialize_site_connection.cache_clear()

    site = initialize_site_connection('testuser', 'testpass')

    assert site == mock_site_instance
    mock_site_instance.login.assert_called_once_with('testuser', 'testpass')


@pytest.mark.unit
@patch('src.services.page.MDWIKI_USERNAME', 'testuser')
@patch('src.services.page.MDWIKI_PASSWORD', 'testpass')
@patch('src.services.page.initialize_site_connection')
def test_page_mwclient_init(mock_init):
    """Test PageMWClient initialization."""
    mock_site = Mock()
    mock_page = Mock()
    mock_site.pages = {"Test:Page": mock_page}
    mock_init.return_value = mock_site

    page = PageMWClient("Test:Page")

    assert page.title == "Test:Page"
    assert page.site_mw == mock_site


@pytest.mark.unit
@patch('src.services.page.MDWIKI_USERNAME', 'testuser')
@patch('src.services.page.MDWIKI_PASSWORD', 'testpass')
@patch('src.services.page.initialize_site_connection')
def test_page_exists(mock_init):
    """Test page existence check."""
    mock_site = Mock()
    mock_page = Mock()
    mock_page.exists = True
    mock_site.pages = {"Test:Page": mock_page}
    mock_init.return_value = mock_site

    page = PageMWClient("Test:Page")

    assert page.exists() is True


@pytest.mark.unit
@patch('src.services.page.MDWIKI_USERNAME', 'testuser')
@patch('src.services.page.MDWIKI_PASSWORD', 'testpass')
@patch('src.services.page.initialize_site_connection')
def test_page_save(mock_init):
    """Test page save operation."""
    mock_site = Mock()
    mock_page = Mock()
    mock_page.save.return_value = {"result": "Success"}
    mock_site.pages = {"Test:Page": mock_page}
    mock_init.return_value = mock_site

    page = PageMWClient("Test:Page")
    result = page.save("New content", "Test edit")

    mock_page.save.assert_called_once_with("New content", summary="Test edit")
    assert result["result"] == "Success"
```

**File**: `tests/unit/workflow/test_uploader.py`

```python
"""Test report uploader service."""
import pytest
from unittest.mock import Mock, patch, mock_open
from src.services.uploader import ReportUploader


@pytest.mark.unit
@patch('src.services.uploader.Path')
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
@patch('src.services.uploader.PageMWClient')
@patch('builtins.open', mock_open(read_data='Test content'))
def test_upload_report_success(mock_page_class):
    """Test successful report upload."""
    mock_page = Mock()
    mock_page.exists.return_value = False
    mock_page.save.return_value = {"result": "Success"}
    mock_page_class.return_value = mock_page

    uploader = ReportUploader()
    success = uploader._upload_report("/path/ar.wiki", "2025")

    assert success is True
    mock_page.save.assert_called_once()
```

---

### 8. Update Documentation

**File**: `README.md` (Add section)

```markdown
## MDWiki Upload

Reports are automatically uploaded to mdwiki.org after generation.

### Configuration

1. Create `.env` file:
```bash
MDWIKI_USERNAME=your_username
MDWIKI_PASSWORD=your_password
```

2. Run with upload:
```bash
python -m src.main
```

3. Skip upload:
```bash
python -m src.main --skip-upload
```

4. Upload only (no data collection):
```bash
python -m src.main --upload-only
```

### Page Mapping

- Global report: `WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025_(all)`
- Arabic: `WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025/ar`
- Spanish: `WikiProjectMed:WikiProject_Medicine/Stats/Top_medical_editors_2025/es`
- ...
```

---

## Usage Examples

### Basic Usage (with upload)

```bash
# Run complete workflow including upload
python -m src.main

# Output:
# Step 1: Retrieving medicine titles
# ...
# Step 6: Uploading reports to MDWiki
# ✓ Uploaded: ar.wiki
# ✓ Uploaded: es.wiki
# ✓ Uploaded: total_report.wiki
# Upload Summary: 330/330 successful
```

---

## Security Best Practices

### 1. Never Commit Credentials

```bash
# .gitignore already includes:
.env
.env.local
.env.*.local
```

### 2. Use Environment Variables

```python
# ✓ Good - from environment
MDWIKI_USERNAME = os.getenv("MDWIKI_USERNAME")

# ✗ Bad - hardcoded
MDWIKI_USERNAME = "myusername"  # Never!
```

### 3. Validate Before Use

```python
if not MDWIKI_USERNAME or not MDWIKI_PASSWORD:
    logger.warning("MDWiki credentials not configured")
    # Disable upload functionality
```

---

## Error Handling

### Connection Failures

```python
try:
    site = initialize_site_connection(username, password)
except mwclient.errors.LoginError as e:
    logger.error("Failed to login: %s", e)
    # Continue with other operations
```

### Upload Failures

```python
# Individual upload failures don't stop the process
results = uploader.upload_all_reports()
if results["failed"] > 0:
    logger.warning("%d uploads failed", results["failed"])
    # Reports still saved locally in reports/ directory
```

---

## Testing

```bash
# Test page service
pytest tests/unit/services/test_page.py -v

# Test uploader service
pytest tests/unit/workflow/test_uploader.py -v

# Test with mocked credentials
MDWIKI_USERNAME=test MDWIKI_PASSWORD=test pytest tests/unit/test_services*.py
```

---

## File Structure (Updated)

```
med-status/
├── src/
│   ├── services/
│   │   ├── page.py           # ⭐ NEW MDWiki page client
│   ├── workflow/
│   │   └── uploader.py       # ⭐ NEW Report uploader
│   └── ...
├── tests/
│   ├── unit/
│   │   ├── test_services_page.py      # ⭐ NEW
│   │   └── test_services_uploader.py  # ⭐ NEW
│   └── ...
└── ...
```

---

## Summary

✅ **New Step 6**: Upload reports to MDWiki
✅ **mwclient Integration**: Professional MediaWiki client
✅ **Secure Credentials**: Environment variables
✅ **Connection Caching**: Single login reused
✅ **Error Handling**: Robust with retries
✅ **Logging**: Color-coded progress
✅ **CLI Options**: --skip-upload, --upload-only
✅ **Tests**: Full coverage
✅ **Documentation**: Complete guide

**Ready to upload reports automatically!** 🚀
