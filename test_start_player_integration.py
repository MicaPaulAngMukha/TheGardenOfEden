"""
Integration test to verify the actual Player class in Start.py
has the correct inventory methods.
"""

import pygame
import sys

# Initialize pygame before importing Start
pygame.init()

# Import the actual Player class from Start.py
from Start import Player
from key_system import KeyEntity


def test_start_player_inventory():
    """Test the actual Player class from Start.py"""
    
    # Test 1: Player starts with no key
    player = Player()
    assert player.held_key is None
    assert player.has_key() is False
    print("✓ Test 1 passed: Player starts with no key")
    
    # Test 2: Player can pick up a key
    key1 = KeyEntity("bronze", (100, 100))
    old_key = player.pickup_key(key1)
    assert player.held_key == key1
    assert old_key is None
    assert player.has_key() is True
    print("✓ Test 2 passed: Player can pick up a key")
    
    # Test 3: Player can swap keys
    key2 = KeyEntity("gold", (200, 200))
    returned_key = player.pickup_key(key2)
    assert player.held_key == key2
    assert returned_key == key1
    assert player.has_key() is True
    print("✓ Test 3 passed: Player can swap keys")
    
    # Test 4: Player can drop a key
    dropped = player.drop_key()
    assert dropped == key2
    assert player.held_key is None
    assert player.has_key() is False
    print("✓ Test 4 passed: Player can drop a key")
    
    print("\n✅ All integration tests passed!")


if __name__ == "__main__":
    test_start_player_inventory()
