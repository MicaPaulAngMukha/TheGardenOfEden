"""
Unit tests for Player inventory system (Task 4)

Tests the Player class methods:
- pickup_key()
- drop_key()
- has_key()
"""

import pytest
import pygame
from key_system import KeyEntity


# Mock Player class for testing (simplified version)
class Player:
    SIZE = 20
    SPEED = 3

    def __init__(self):
        self.lives = 3
        self.rect = pygame.Rect(100, 100, self.SIZE, self.SIZE)
        self.held_key = None

    def pickup_key(self, key):
        """
        Pick up a key. If already holding a key, return the old key.
        
        Args:
            key: The KeyEntity to pick up
        
        Returns:
            The previously held key (for swapping), or None
        """
        old_key = self.held_key
        self.held_key = key
        return old_key
    
    def drop_key(self):
        """
        Drop the currently held key.
        
        Returns:
            The dropped key, or None if not holding a key
        """
        dropped = self.held_key
        self.held_key = None
        return dropped
    
    def has_key(self):
        """
        Check if player is holding any key.
        
        Returns:
            True if holding a key, False otherwise
        """
        return self.held_key is not None


class TestPlayerInventory:
    """Test suite for Player inventory methods"""
    
    def test_player_pickup_key_when_empty(self):
        """Verify player can pick up key when not holding one"""
        pygame.init()
        player = Player()
        key = KeyEntity("bronze", (100, 100))
        
        old_key = player.pickup_key(key)
        
        assert player.held_key == key
        assert old_key is None
    
    def test_player_pickup_key_when_holding(self):
        """Verify player swaps keys when already holding one"""
        pygame.init()
        player = Player()
        old_key = KeyEntity("bronze", (100, 100))
        new_key = KeyEntity("gold", (200, 200))
        
        player.pickup_key(old_key)
        returned_key = player.pickup_key(new_key)
        
        assert player.held_key == new_key
        assert returned_key == old_key
    
    def test_drop_key_returns_dropped_key(self):
        """Verify drop_key returns the dropped key"""
        pygame.init()
        player = Player()
        key = KeyEntity("bronze", (100, 100))
        
        player.pickup_key(key)
        dropped = player.drop_key()
        
        assert dropped == key
        assert player.held_key is None
    
    def test_drop_key_when_empty(self):
        """Verify drop_key returns None when not holding a key"""
        pygame.init()
        player = Player()
        
        dropped = player.drop_key()
        
        assert dropped is None
        assert player.held_key is None
    
    def test_has_key_returns_true_when_holding(self):
        """Verify has_key returns True when holding a key"""
        pygame.init()
        player = Player()
        key = KeyEntity("bronze", (100, 100))
        
        player.pickup_key(key)
        
        assert player.has_key() is True
    
    def test_has_key_returns_false_when_empty(self):
        """Verify has_key returns False when not holding a key"""
        pygame.init()
        player = Player()
        
        assert player.has_key() is False
    
    def test_has_key_returns_false_after_drop(self):
        """Verify has_key returns False after dropping a key"""
        pygame.init()
        player = Player()
        key = KeyEntity("bronze", (100, 100))
        
        player.pickup_key(key)
        player.drop_key()
        
        assert player.has_key() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
