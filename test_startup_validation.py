"""
Test startup validation and error handling for difficulty system.
"""
import pytest
from difficulty_config import get_difficulty_from_key, get_modifiers, validate_modifiers, NORMAL, EASY, HARD, GOD_MODE


class MockKeyEntity:
    """Mock KeyEntity for testing."""
    def __init__(self, key_type):
        self.key_type = key_type


class MockKeyEntityNoAttribute:
    """Mock KeyEntity without key_type attribute."""
    pass


def test_validate_modifiers_success():
    """Test that validate_modifiers returns empty list for valid configuration."""
    errors = validate_modifiers()
    assert errors == [], f"Expected no validation errors, got: {errors}"


def test_get_difficulty_from_key_none():
    """Test that None key defaults to Normal Mode."""
    difficulty = get_difficulty_from_key(None)
    assert difficulty == NORMAL


def test_get_difficulty_from_key_missing_attribute():
    """Test that missing key_type attribute defaults to Normal Mode."""
    mock_key = MockKeyEntityNoAttribute()
    difficulty = get_difficulty_from_key(mock_key)
    assert difficulty == NORMAL


def test_get_difficulty_from_key_invalid_type():
    """Test that invalid key_type defaults to Normal Mode."""
    mock_key = MockKeyEntity("invalid_key_type")
    difficulty = get_difficulty_from_key(mock_key)
    assert difficulty == NORMAL


def test_get_difficulty_from_key_valid_bronze():
    """Test that bronze key returns Easy Mode."""
    mock_key = MockKeyEntity("bronze")
    difficulty = get_difficulty_from_key(mock_key)
    assert difficulty == EASY


def test_get_difficulty_from_key_valid_gold():
    """Test that gold key returns Normal Mode."""
    mock_key = MockKeyEntity("gold")
    difficulty = get_difficulty_from_key(mock_key)
    assert difficulty == NORMAL


def test_get_difficulty_from_key_valid_rusted():
    """Test that rusted key returns Hard Mode."""
    mock_key = MockKeyEntity("rusted")
    difficulty = get_difficulty_from_key(mock_key)
    assert difficulty == HARD


def test_get_difficulty_from_key_valid_divine():
    """Test that divine key returns God Mode."""
    mock_key = MockKeyEntity("divine")
    difficulty = get_difficulty_from_key(mock_key)
    assert difficulty == GOD_MODE


def test_get_modifiers_invalid_level():
    """Test that invalid level name returns empty dict."""
    modifiers = get_modifiers("InvalidLevel", NORMAL)
    assert modifiers == {}


def test_get_modifiers_invalid_difficulty():
    """Test that invalid difficulty mode defaults to Normal Mode."""
    modifiers = get_modifiers("TheNaga", "invalid_difficulty")
    assert modifiers == {}


def test_get_modifiers_valid_naga_easy():
    """Test that valid level and difficulty returns correct modifiers."""
    modifiers = get_modifiers("TheNaga", EASY)
    assert "naga_speed" in modifiers or "item_spawn_multiplier" in modifiers


def test_get_modifiers_valid_naga_normal():
    """Test that Normal Mode returns empty modifiers."""
    modifiers = get_modifiers("TheNaga", NORMAL)
    assert modifiers == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
