"""
Unit tests for ValidationSkill implementation.

Tests input validation per data-model.md validation rules.
"""

import pytest
from src.services.validation import validate_title, validate_id, validate_description
from src.exceptions import EmptyTitleError, InvalidIdError


class TestValidateTitle:
    """Tests for title validation (VR-001, VR-002)."""

    def test_valid_title_passes(self) -> None:
        """Valid non-empty title passes validation."""
        result = validate_title("Buy groceries")
        assert result == "Buy groceries"

    def test_valid_title_is_stripped(self) -> None:
        """Valid title is stripped of leading/trailing whitespace."""
        result = validate_title("  Buy groceries  ")
        assert result == "Buy groceries"

    def test_empty_title_raises_error(self) -> None:
        """Empty string title raises EmptyTitleError."""
        with pytest.raises(EmptyTitleError):
            validate_title("")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Whitespace-only title raises EmptyTitleError."""
        with pytest.raises(EmptyTitleError):
            validate_title("   ")

    def test_tab_only_title_raises_error(self) -> None:
        """Tab-only title raises EmptyTitleError."""
        with pytest.raises(EmptyTitleError):
            validate_title("\t\t")

    def test_newline_only_title_raises_error(self) -> None:
        """Newline-only title raises EmptyTitleError."""
        with pytest.raises(EmptyTitleError):
            validate_title("\n\n")

    def test_title_with_special_characters(self) -> None:
        """Title with special characters is valid."""
        result = validate_title("Task with $pecial ch@racters!")
        assert result == "Task with $pecial ch@racters!"

    def test_title_with_unicode(self) -> None:
        """Title with unicode characters is valid."""
        result = validate_title("Tarea en español")
        assert result == "Tarea en español"


class TestValidateId:
    """Tests for ID validation (VR-003, VR-004)."""

    def test_valid_integer_id_passes(self) -> None:
        """Valid positive integer ID passes."""
        result = validate_id("1")
        assert result == 1

    def test_valid_large_id_passes(self) -> None:
        """Large positive integer ID passes."""
        result = validate_id("12345")
        assert result == 12345

    def test_non_numeric_id_raises_error(self) -> None:
        """Non-numeric ID raises InvalidIdError."""
        with pytest.raises(InvalidIdError) as exc_info:
            validate_id("abc")
        assert exc_info.value.invalid_id == "abc"

    def test_float_id_raises_error(self) -> None:
        """Float ID raises InvalidIdError."""
        with pytest.raises(InvalidIdError) as exc_info:
            validate_id("1.5")
        assert exc_info.value.invalid_id == "1.5"

    def test_negative_id_raises_error(self) -> None:
        """Negative ID raises InvalidIdError."""
        with pytest.raises(InvalidIdError) as exc_info:
            validate_id("-1")
        assert exc_info.value.invalid_id == "-1"

    def test_zero_id_raises_error(self) -> None:
        """Zero ID raises InvalidIdError."""
        with pytest.raises(InvalidIdError) as exc_info:
            validate_id("0")
        assert exc_info.value.invalid_id == "0"

    def test_empty_id_raises_error(self) -> None:
        """Empty string ID raises InvalidIdError."""
        with pytest.raises(InvalidIdError) as exc_info:
            validate_id("")
        assert exc_info.value.invalid_id == ""

    def test_whitespace_id_raises_error(self) -> None:
        """Whitespace ID raises InvalidIdError."""
        with pytest.raises(InvalidIdError) as exc_info:
            validate_id("   ")
        assert exc_info.value.invalid_id == "   "


class TestValidateDescription:
    """Tests for description validation (always passes in Phase I)."""

    def test_valid_description_passes(self) -> None:
        """Valid description passes."""
        result = validate_description("Some description")
        assert result == "Some description"

    def test_empty_description_passes(self) -> None:
        """Empty description is valid."""
        result = validate_description("")
        assert result == ""

    def test_description_is_stripped(self) -> None:
        """Description is stripped of leading/trailing whitespace."""
        result = validate_description("  Some description  ")
        assert result == "Some description"

    def test_whitespace_description_becomes_empty(self) -> None:
        """Whitespace-only description becomes empty string."""
        result = validate_description("   ")
        assert result == ""

    def test_description_with_special_characters(self) -> None:
        """Description with special characters is valid."""
        result = validate_description("Special: $100 @ 50%!")
        assert result == "Special: $100 @ 50%!"

    def test_description_with_newlines(self) -> None:
        """Description with newlines is preserved."""
        result = validate_description("Line 1\nLine 2")
        assert result == "Line 1\nLine 2"

    def test_none_description_handled(self) -> None:
        """None description returns empty string."""
        result = validate_description(None)
        assert result == ""
