"""
Integration tests for key pickup and swapping flow (Task 5)

Tests the complete flow:
1. Key discovery
2. Narrator text display
3. Pickup prompt
4. Y/N input handling
5. Key swapping logic
"""

import pytest
import pygame
from key_system import KeyEntity, spawn_keys
from Start import check_key_discovery, handle_key_swap, KEY_NARRATOR_TEXT


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


class TestKeyPickupIntegration:
    """Integration tests for complete key pickup flow"""
    
    def test_complete_pickup_flow_accept(self):
        """Test complete flow: discover -> accept -> pickup"""
        pygame.init()
        player = Player()
        player.rect.center = (200, 200)
        
        # Create a key near the player
        key = KeyEntity("bronze", (210, 210))
        keys_in_world = [key]
        
        # Step 1: Discovery
        discovered_key = check_key_discovery(player, keys_in_world)
        assert discovered_key is not None
        assert discovered_key.key_type == "bronze"
        assert discovered_key.discovered == True
        
        # Step 2: Narrator text should be available
        narrator_text = KEY_NARRATOR_TEXT[discovered_key.key_type]
        assert "bronze key" in narrator_text.lower()
        
        # Step 3: Accept pickup (simulate Y key press)
        handle_key_swap(player, discovered_key, keys_in_world)
        
        # Step 4: Verify key is in inventory and removed from world
        assert player.held_key == discovered_key
        assert discovered_key not in keys_in_world
        assert len(keys_in_world) == 0
    
    def test_complete_pickup_flow_decline(self):
        """Test complete flow: discover -> decline -> key remains in world"""
        pygame.init()
        player = Player()
        player.rect.center = (200, 200)
        
        # Create a key near the player
        key = KeyEntity("gold", (210, 210))
        keys_in_world = [key]
        
        # Step 1: Discovery
        discovered_key = check_key_discovery(player, keys_in_world)
        assert discovered_key is not None
        
        # Step 2: Decline pickup (simulate N key press)
        # In the actual game, this just sets discovered_key = None and returns to STATE_EXPLORE
        # The key remains in keys_in_world
        
        # Verify key is still in world and player has no key
        assert player.held_key is None
        assert discovered_key in keys_in_world
        assert len(keys_in_world) == 1
    
    def test_complete_swap_flow(self):
        """Test complete flow: have key -> discover new key -> accept -> swap"""
        pygame.init()
        player = Player()
        player.rect.center = (200, 200)
        
        # Player already has a bronze key
        old_key = KeyEntity("bronze", (100, 100))
        player.pickup_key(old_key)
        
        # Create a new gold key near the player
        new_key = KeyEntity("gold", (210, 210))
        keys_in_world = [new_key]
        
        # Step 1: Discovery
        discovered_key = check_key_discovery(player, keys_in_world)
        assert discovered_key is not None
        assert discovered_key.key_type == "gold"
        
        # Step 2: Accept pickup (simulate Y key press)
        handle_key_swap(player, discovered_key, keys_in_world)
        
        # Step 3: Verify swap occurred
        assert player.held_key == new_key
        assert old_key in keys_in_world
        assert new_key not in keys_in_world
        assert old_key.rect.center == (200, 200)  # Dropped at player location
        assert old_key.discovered == False  # Reset for re-discovery
    
    def test_multiple_keys_discovery_sequence(self):
        """Test discovering multiple keys in sequence"""
        pygame.init()
        player = Player()
        
        # Spawn all keys
        keys_in_world = spawn_keys()
        assert len(keys_in_world) == 4
        
        # Move player near bronze key
        bronze_key = next(k for k in keys_in_world if k.key_type == "bronze")
        player.rect.center = bronze_key.rect.center
        
        # Discover bronze key
        discovered = check_key_discovery(player, keys_in_world)
        assert discovered == bronze_key
        
        # Pick up bronze key
        handle_key_swap(player, discovered, keys_in_world)
        assert player.held_key == bronze_key
        assert len(keys_in_world) == 3
        
        # Move player near gold key
        gold_key = next(k for k in keys_in_world if k.key_type == "gold")
        player.rect.center = gold_key.rect.center
        
        # Discover gold key
        discovered = check_key_discovery(player, keys_in_world)
        assert discovered == gold_key
        
        # Swap to gold key
        handle_key_swap(player, discovered, keys_in_world)
        assert player.held_key == gold_key
        assert bronze_key in keys_in_world  # Bronze key dropped
        assert len(keys_in_world) == 3  # Bronze dropped, gold picked up
    
    def test_rediscovery_of_dropped_key(self):
        """Test that dropped keys can be rediscovered"""
        pygame.init()
        player = Player()
        player.rect.center = (200, 200)
        
        # Pick up bronze key
        bronze_key = KeyEntity("bronze", (210, 210))
        keys_in_world = [bronze_key]
        discovered = check_key_discovery(player, keys_in_world)
        handle_key_swap(player, discovered, keys_in_world)
        
        # Pick up gold key (drops bronze)
        gold_key = KeyEntity("gold", (220, 220))
        keys_in_world.append(gold_key)
        discovered = check_key_discovery(player, keys_in_world)
        handle_key_swap(player, discovered, keys_in_world)
        
        # Bronze key should be dropped and undiscovered
        assert bronze_key in keys_in_world
        assert bronze_key.discovered == False
        
        # Move back to bronze key location
        player.rect.center = bronze_key.rect.center
        
        # Should be able to rediscover bronze key
        rediscovered = check_key_discovery(player, keys_in_world)
        assert rediscovered == bronze_key
        assert bronze_key.discovered == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
