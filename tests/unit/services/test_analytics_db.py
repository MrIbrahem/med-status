"""Unit tests for DatabaseAnalytics module."""

from unittest.mock import MagicMock, patch

import pytest

from src.services.analytics_db import DatabaseAnalytics


@pytest.mark.unit
class TestDatabaseAnalyticsGetDatabaseInfo:
    """Tests for get_database_info method."""

    def test_get_database_info_predefined_meta(self):
        """Test get_database_info with predefined 'meta' site code."""
        db_analytics = DatabaseAnalytics("meta")
        database, host = db_analytics.get_database_info("meta")

        assert database == "meta_p"
        assert host == "s7.analytics.db.svc.wikimedia.cloud"

    def test_get_database_info_standard_language(self):
        """Test get_database_info with standard language code."""
        with patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db:
            mock_get_db.return_value = "enwiki"
            db_analytics = DatabaseAnalytics("en")
            database, host = db_analytics.get_database_info("en")

            assert database == "enwiki"
            assert host == "enwiki.analytics.db.svc.wikimedia.cloud"

    def test_get_database_info_with_hyphen_replacement(self):
        """Test get_database_info replaces hyphens with underscores."""
        with patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db:
            mock_get_db.return_value = "roa_rupwiki"
            db_analytics = DatabaseAnalytics("roa-rup")
            database, host = db_analytics.get_database_info("roa-rup")

            assert database == "roa_rupwiki"
            assert host == "roa_rupwiki.analytics.db.svc.wikimedia.cloud"

    def test_get_database_info_removes_wiki_suffix(self):
        """Test get_database_info removes 'wiki' suffix from site code."""
        with patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db:
            mock_get_db.return_value = "dewiki"
            db_analytics = DatabaseAnalytics("dewiki")
            database, host = db_analytics.get_database_info("dewiki")

            assert database == "dewiki"
            assert host == "dewiki.analytics.db.svc.wikimedia.cloud"
            # Verify that 'wiki' suffix was removed when calling get_database_name_for_language
            mock_get_db.assert_called_with("de")

    def test_get_database_info_case_normalization(self):
        """Test get_database_info converts site code to lowercase."""
        with patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db:
            mock_get_db.return_value = "frwiki"
            db_analytics = DatabaseAnalytics("FR")
            database, host = db_analytics.get_database_info("FR")

            assert database == "frwiki"
            assert host == "frwiki.analytics.db.svc.wikimedia.cloud"
            mock_get_db.assert_called_with("fr")

    def test_get_database_info_complex_case(self):
        """Test get_database_info with complex site code (hyphens, wiki suffix, uppercase)."""
        with patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db:
            mock_get_db.return_value = "zh_min_nanwiki"
            db_analytics = DatabaseAnalytics("ZH-MIN-NANwiki")
            database, host = db_analytics.get_database_info("ZH-MIN-NANwiki")

            assert database == "zh_min_nanwiki"
            assert host == "zh_min_nanwiki.analytics.db.svc.wikimedia.cloud"
            mock_get_db.assert_called_with("zh_min_nan")

    def test_get_database_info_no_mapping_found(self):
        """Test get_database_info when no mapping is found (falls back to pattern)."""
        with patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db:
            mock_get_db.return_value = ""
            db_analytics = DatabaseAnalytics("test")
            database, host = db_analytics.get_database_info("test")

            assert database == "testwiki_p"
            assert host == "testwiki.analytics.db.svc.wikimedia.cloud"


@pytest.mark.unit
class TestDatabaseAnalyticsInit:
    """Tests for DatabaseAnalytics initialization."""

    def test_init_with_standard_language(self):
        """Test initialization with standard language code."""
        with patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db:
            mock_get_db.return_value = "enwiki"

            db_analytics = DatabaseAnalytics("en")

            assert db_analytics.database == "enwiki"
            assert db_analytics.host == "enwiki.analytics.db.svc.wikimedia.cloud"
            assert db_analytics.db is None

    def test_init_with_meta(self):
        """Test initialization with 'meta' site code."""
        # with patch("src.services.analytics_db.Database") as mock_database_class:
        #     mock_db_instance = MagicMock()
        #     mock_database_class.return_value = mock_db_instance

        db_analytics = DatabaseAnalytics("meta")

        assert db_analytics.database == "meta_p"
        assert db_analytics.host == "s7.analytics.db.svc.wikimedia.cloud"
        # mock_database_class.assert_not_called()

    def test_init_with_hyphenated_site_code(self):
        """Test initialization with hyphenated site code."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            # patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = "bat_smgwiki"
            # mock_db_instance = MagicMock()
            # mock_database_class.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("bat-smg")

            assert db_analytics.database == "bat_smgwiki"
            assert db_analytics.host == "bat_smgwiki.analytics.db.svc.wikimedia.cloud"
            # mock_database_class.assert_not_called()


@pytest.mark.unit
class TestDatabaseAnalyticsContextManager:
    """Tests for DatabaseAnalytics context manager behavior."""

    def test_context_manager_enter(self):
        """Test __enter__ delegates to Database.__enter__."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = "enwiki"
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance
            mock_db_instance.__enter__.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("en")

            with db_analytics as db:
                assert db == mock_db_instance
                mock_db_instance.__enter__.assert_called_once()

    def test_context_manager_exit(self):
        """Test __exit__ delegates to Database.__exit__."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = "enwiki"
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("en")

            with db_analytics:
                pass

            mock_db_instance.__exit__.assert_called_once()

    def test_context_manager_with_exception(self):
        """Test context manager properly handles exceptions."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = "enwiki"
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("en")

            with pytest.raises(ValueError):
                with db_analytics:
                    raise ValueError("Test exception")

            # Ensure __exit__ was still called
            mock_db_instance.__exit__.assert_called_once()
            # Check that exception info was passed
            args = mock_db_instance.__exit__.call_args[0]
            assert args[0] is ValueError
            assert isinstance(args[1], ValueError)


@pytest.mark.unit
class TestDatabaseAnalyticsEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_multiple_instances(self):
        """Test creating multiple DatabaseAnalytics instances."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.side_effect = ["enwiki", "frwiki", "dewiki"]
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance

            db_en = DatabaseAnalytics("en")
            db_fr = DatabaseAnalytics("fr")
            db_de = DatabaseAnalytics("de")

            assert db_en.database == "enwiki"
            assert db_fr.database == "frwiki"
            assert db_de.database == "dewiki"

    def test_wiki_suffix_removal_case_insensitive(self):
        """Test that 'wiki' suffix removal is case-insensitive."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = "itwiki"
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("ITWIKI")

            assert db_analytics.database == "itwiki"
            mock_get_db.assert_called_with("it")

    def test_empty_site_code(self):
        """Test behavior with empty site code."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = ""
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("")

            # When site_code is empty and no mapping found, fallback is "wiki_p"
            assert db_analytics.database == "wiki_p"
            assert db_analytics.host == "wiki.analytics.db.svc.wikimedia.cloud"

    def test_site_code_with_only_hyphens(self):
        """Test behavior with site code containing only hyphens."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = ""
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("--")

            assert db_analytics.database == "__wiki_p"
            assert db_analytics.host == "__wiki.analytics.db.svc.wikimedia.cloud"


@pytest.mark.unit
class TestDatabaseAnalytics:
    """Test DatabaseAnalytics class."""

    def test_check_database_name_special_cases_under(self):
        """Test database name handling for special cases with underscores."""
        with (
            patch("src.services.analytics_db.get_database_name_for_language") as mock_get_db,
            patch("src.services.analytics_db.Database") as mock_database_class,
        ):
            mock_get_db.return_value = ""
            mock_db_instance = MagicMock()
            mock_database_class.return_value = mock_db_instance

            db_analytics = DatabaseAnalytics("be-x-old")

            assert db_analytics.database == "be_x_oldwiki_p"
            assert db_analytics.host == "be_x_oldwiki.analytics.db.svc.wikimedia.cloud"
