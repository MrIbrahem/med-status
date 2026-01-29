"""Test query builder module."""

import pytest

from src.services.queries import QueryBuilder


@pytest.mark.unit
class TestQueryBuilder:
    """Test QueryBuilder class."""

    def test_get_medicine_titles(self):
        """Test Medicine titles query."""
        query = QueryBuilder.get_medicine_titles()
        assert "page_title" in query
        assert "langlinks" in query
        assert "Medicine" in query

    def test_get_database_mapping(self):
        """Test database mapping query."""
        query = QueryBuilder.get_database_mapping()
        assert "dbname" in query
        assert "lang" in query
        assert "wikipedia" in query

    def test_get_editors_standard(self):
        """Test standard editors query."""
        titles = ["Medicine", "Health"]
        year = "2024"
        query, params = QueryBuilder.get_editors_standard(titles, year)
        assert "actor_name" in query
        assert "2024" in params
        assert "Medicine" in params or "Health" in params

    def test_get_editors_arabic(self):
        """Test Arabic editors query."""
        year = "2024"
        query, params = QueryBuilder.get_editors_arabic(year)
        assert "actor_name" in query
        assert year in params
        assert "طب" in query

    def test_get_editors_english(self):
        """Test English editors query."""
        year = "2024"
        query, params = QueryBuilder.get_editors_english(year)
        assert "actor_name" in query
        assert "WikiProject_Medicine" in query
        assert year in params

    def test_get_editors_standard_empty_titles(self):
        """Test get_editors_standard with empty titles list."""
        with pytest.raises(ValueError, match="Titles list cannot be empty"):
            QueryBuilder.get_editors_standard([], "2024")
