"""
Unit tests for handle_key_swap function (Task 5)

Tests the key swapping logic when player picks up a new key.
"""

import pytest
import pygame
from key_system import KeyEntity
from Start import handle_key_swap


# Mock Player class for testing
class Player:
    SIZE = 20
    SPEED = 3

    def __init__(self):
        self.lives = 3
        self.rect = pygame.Rect(150, 150, self.SIZE, self.SIZE)
        self.held_key = None

    def pickup_key(self, key):
        """Pick up a key. If already holding a key, return the old key."""
        old_key = self.held_key
        self.held_key = key
        return old_key
    
    def drop_key(self):
        """Drop the currently held key."""
        dropped = self.held_key
        self.held_key = None
        return dropped
    
    def has_key(self):
        """Check if player is holding any key."""
        return self.held_key is not None


class TestHandleKeySwap:
    """Test suite for handle_key_swap function"""
    
    def test_handle_key_swap_pickup_when_empty(self):
        """Verify player can pick up key when not holding one"""
        pygame.init()
        player = Player()
        new_key = KeyEntity("gold", (200, 200))
        keys_in_world = [new_key]
        
        handle_key_swap(player, new_key, keys_in_world)
        
        assert player.held_key == new_key
        assert new_key not in keys_in_world
        assert len(keys_in_world) == 0
    
    def test_handle_key_swap_drops_old_key(self):
        """Verify that key swapping drops old key at player location"""
        pygame.init()
        player = Player()
        player.rect.center = (150, 150)
        
        old_key = KeyEntity("bronze", (100, 100))
        new_key = KeyEntity("gold", (200, 200))
        
        player.pickup_key(old_key)
        keys_in_world = [new_key]
        
        handle_key_swap(player, new_key, keys_in_world)
        
        assert player.held_key == new_key
        assert old_key in keys_in_world
        assert old_key.rect.center == (150, 150)
        assert old_key.discovered == False
    
    def test_handle_key_swap_removes_new_key_from_world(self):
        """Verify that picked up key is removed from world"""
        pygame.init()
        player = Player()
        new_key = KeyEntity("gold", (200, 200))
        keys_in_world = [new_key]
        
        handle_key_swap(player, new_key, keys_in_world)
        
        assert new_key not in keys_in_world
        assert player.held_key == new_key
    
    def test_handle_key_swap_with_multiple_keys_in_world(self):
        """Verify swapping works correctly with multiple keys in world"""
        pygame.init()
        player = Player()
        player.rect.center = (150, 150)
        
        old_key = KeyEntity("bronze", (100, 100))
        new_key = KeyEntity("gold", (200, 200))
        other_key = KeyEntity("rusted", (300, 300))
        
        player.pickup_key(old_key)
        keys_in_world = [new_key, other_key]
        
        handle_key_swap(player, new_key, keys_in_world)
        
        assert player.held_key == new_key
        assert old_key in keys_in_world
        assert other_key in keys_in_world
        assert new_key not in keys_in_world
        assert len(keys_in_world) == 2
    
    def test_handle_key_swap_resets_discovered_flag(self):
        """Verify that dropped key has discovered flag reset"""
        pygame.init()
        player = Player()
        
        old_key = KeyEntity("bronze", (100, 100))
        old_key.discovered = True
        new_key = KeyEntity("gold", (200, 200))
        
        player.pickup_key(old_key)
        keys_in_world = [new_key]
        
        handle_key_swap(player, new_key, keys_in_world)
        
        assert old_key.discovered == False
    
    def test_handle_key_swap_invalid_key_not_in_world(self, capsys):
        """Verify graceful handling when key is not in world"""
        pygame.init()
        player = Player()
        new_key = KeyEntity("gold", (200, 200))
        keys_in_world = []  # Empty list - key not in world
        
        handle_key_swap(player, new_key, keys_in_world)
        
        # Should print warning and not crash
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert player.held_key is None  # Should not pick up invalid key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
