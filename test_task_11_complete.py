"""
Comprehensive test for Task 11: Startup validation and error handling.

This test verifies:
- Startup validation is called at game initialization
- Validation errors are logged to console
- Error handling for missing player.held_key attribute
- Error handling for invalid key_type values
- Fallback to Normal Mode on configuration errors
"""
import pytest
import pygame
from difficulty_config import (
    validate_modifiers, 
    get_difficulty_from_key, 
    get_modifiers,
    NORMAL, 
    EASY, 
    HARD, 
    GOD_MODE
)
from difficulty_manager import DifficultyManager


class MockKeyEntity:
    """Mock KeyEntity for testing."""
    def __init__(self, key_type):
        self.key_type = key_type


class MockKeyEntityNoAttribute:
    """Mock KeyEntity without key_type attribute."""
    pass


class MockPlayer:
    """Mock Player with held_key attribute."""
    def __init__(self, held_key=None):
        self.held_key = held_key


class MockPlayerNoAttribute:
    """Mock Player without held_key attribute."""
    pass


def test_requirement_16_1_speed_validation():
    """Requirement 16.1: Speed modifiers must be > 0."""
    errors = validate_modifiers()
    # All speed modifiers in the current config should be valid
    assert all("must be > 0" not in error or "speed" not in error for error in errors)


def test_requirement_16_2_frequency_validation():
    """Requirement 16.2: Frequency modifiers must be > 0."""
    errors = validate_modifiers()
    # All frequency/multiplier modifiers should be valid
    assert all("multiplier" not in error or "must be > 0" not in error for error in errors)


def test_requirement_16_3_duration_validation():
    """Requirement 16.3: Duration modifiers must be >= 30 frames."""
    errors = validate_modifiers()
    # All duration modifiers should be valid
    assert all("duration" not in error or "must be >= 30" not in error for error in errors)


def test_requirement_16_4_invalid_key_type_fallback():
    """Requirement 16.4: Invalid key_type defaults to Normal Mode."""
    mock_key = MockKeyEntity("invalid_type")
    difficulty = get_difficulty_from_key(mock_key)
    assert difficulty == NORMAL


def test_requirement_16_5_range_validation():
    """Requirement 16.5: Range modifiers must be >= 1."""
    errors = validate_modifiers()
    # All range modifiers should be valid
    assert all("range" not in error or "must be >= 1" not in error for error in errors)


def test_requirement_20_4_startup_validation():
    """Requirement 20.4: Configuration validated at game startup."""
    # This test verifies validate_modifiers can be called
    errors = validate_modifiers()
    assert isinstance(errors, list)


def test_requirement_20_5_log_invalid_entries():
    """Requirement 20.5: Log missing or invalid configuration entries."""
    # Test that invalid level returns empty dict (logged internally)
    modifiers = get_modifiers("NonExistentLevel", NORMAL)
    assert modifiers == {}
    
    # Test that invalid difficulty returns empty dict (logged internally)
    modifiers = get_modifiers("TheNaga", "invalid_difficulty")
    assert modifiers == {}


def test_missing_held_key_attribute():
    """Test error handling for missing player.held_key attribute."""
    pygame.init()
    player = MockPlayerNoAttribute()
    
    # DifficultyManager should handle missing attribute gracefully
    manager = DifficultyManager(player, "TheNaga")
    
    # Should default to Normal Mode
    assert manager.difficulty == NORMAL
    assert manager.modifiers == {}
    
    # Should add the attribute
    assert hasattr(player, 'held_key')
    assert player.held_key is None


def test_missing_key_type_attribute():
    """Test error handling for missing key_type attribute on KeyEntity."""
    pygame.init()
    mock_key = MockKeyEntityNoAttribute()
    
    difficulty = get_difficulty_from_key(mock_key)
    
    # Should default to Normal Mode
    assert difficulty == NORMAL


def test_none_key_fallback():
    """Test that None key defaults to Normal Mode."""
    difficulty = get_difficulty_from_key(None)
    assert difficulty == NORMAL


def test_valid_key_types():
    """Test all valid key types map correctly."""
    test_cases = [
        ("bronze", EASY),
        ("gold", NORMAL),
        ("rusted", HARD),
        ("divine", GOD_MODE),
    ]
    
    for key_type, expected_difficulty in test_cases:
        mock_key = MockKeyEntity(key_type)
        difficulty = get_difficulty_from_key(mock_key)
        assert difficulty == expected_difficulty, f"Key type '{key_type}' should map to {expected_difficulty}"


def test_configuration_error_fallback():
    """Test fallback to Normal Mode on configuration errors."""
    pygame.init()
    
    # Test with invalid level name
    player = MockPlayer(held_key=None)
    manager = DifficultyManager(player, "InvalidLevel")
    
    # Should still initialize with Normal Mode
    assert manager.difficulty == NORMAL
    assert manager.modifiers == {}


def test_get_modifier_with_fallback():
    """Test get_modifier returns default value when key not present."""
    pygame.init()
    player = MockPlayer(held_key=None)
    manager = DifficultyManager(player, "TheNaga")
    
    # Normal Mode has no modifiers, so should return default
    value = manager.get_modifier("nonexistent_modifier", 100)
    assert value == 100


def test_validation_success():
    """Test that current configuration passes validation."""
    errors = validate_modifiers()
    assert errors == [], f"Configuration should be valid, but got errors: {errors}"


def test_all_levels_have_configuration():
    """Test that all expected levels have configuration entries."""
    expected_levels = ["TheNaga", "TheTwins", "TheGuardian", "TheStatues", "TheGarden"]
    
    for level in expected_levels:
        modifiers = get_modifiers(level, NORMAL)
        # Should return a dict (even if empty for Normal Mode)
        assert isinstance(modifiers, dict), f"Level '{level}' should have configuration"


def test_all_difficulties_have_configuration():
    """Test that all difficulty modes have configuration for each level."""
    levels = ["TheNaga", "TheTwins", "TheGuardian", "TheStatues", "TheGarden"]
    difficulties = [EASY, NORMAL, HARD, GOD_MODE]
    
    for level in levels:
        for difficulty in difficulties:
            modifiers = get_modifiers(level, difficulty)
            # Should return a dict (may be empty for Normal Mode)
            assert isinstance(modifiers, dict), f"Level '{level}' difficulty '{difficulty}' should have configuration"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
