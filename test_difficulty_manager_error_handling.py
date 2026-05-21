"""
Test error handling in DifficultyManager class.
"""
import pytest
import pygame
from difficulty_manager import DifficultyManager
from difficulty_config import NORMAL, EASY


class MockPlayer:
    """Mock Player with held_key attribute."""
    def __init__(self, held_key=None):
        self.held_key = held_key


class MockPlayerNoAttribute:
    """Mock Player without held_key attribute."""
    pass


class MockKeyEntity:
    """Mock KeyEntity for testing."""
    def __init__(self, key_type):
        self.key_type = key_type


def test_difficulty_manager_with_none_key():
    """Test DifficultyManager handles None key correctly."""
    pygame.init()
    player = MockPlayer(held_key=None)
    manager = DifficultyManager(player, "TheNaga")
    
    assert manager.difficulty == NORMAL
    assert manager.modifiers == {}


def test_difficulty_manager_with_missing_held_key_attribute():
    """Test DifficultyManager handles missing held_key attribute."""
    pygame.init()
    player = MockPlayerNoAttribute()
    manager = DifficultyManager(player, "TheNaga")
    
    # Should default to Normal Mode
    assert manager.difficulty == NORMAL
    assert manager.modifiers == {}
    # Should add held_key attribute
    assert hasattr(player, 'held_key')
    assert player.held_key is None


def test_difficulty_manager_with_valid_key():
    """Test DifficultyManager with valid bronze key."""
    pygame.init()
    key = MockKeyEntity("bronze")
    player = MockPlayer(held_key=key)
    manager = DifficultyManager(player, "TheNaga")
    
    assert manager.difficulty == EASY
    assert len(manager.modifiers) > 0


def test_difficulty_manager_get_modifier_with_default():
    """Test get_modifier returns default when key not present."""
    pygame.init()
    player = MockPlayer(held_key=None)
    manager = DifficultyManager(player, "TheNaga")
    
    value = manager.get_modifier("nonexistent_key", 42)
    assert value == 42


def test_difficulty_manager_get_modifier_existing():
    """Test get_modifier returns correct value for existing modifier."""
    pygame.init()
    key = MockKeyEntity("bronze")
    player = MockPlayer(held_key=key)
    manager = DifficultyManager(player, "TheNaga")
    
    # Bronze key in TheNaga should have item_spawn_multiplier
    value = manager.get_modifier("item_spawn_multiplier", 1.0)
    assert value == 1.5  # Easy mode multiplier


def test_difficulty_manager_should_spawn_god_false():
    """Test should_spawn_god returns False for non-God modes."""
    pygame.init()
    player = MockPlayer(held_key=None)
    manager = DifficultyManager(player, "TheNaga")
    
    assert manager.should_spawn_god() == False


def test_difficulty_manager_should_spawn_god_true():
    """Test should_spawn_god returns True for God Mode."""
    pygame.init()
    key = MockKeyEntity("divine")
    player = MockPlayer(held_key=key)
    manager = DifficultyManager(player, "TheNaga")
    
    assert manager.should_spawn_god() == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
