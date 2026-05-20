"""
Integration test to verify key system works with actual sprite files.
"""

import pygame
from key_system import KeyEntity, spawn_keys

# Initialize pygame with a display
pygame.init()
screen = pygame.display.set_mode((800, 600))

def test_keys_load_actual_sprites():
    """Verify that all keys load their actual sprite files"""
    keys = spawn_keys()
    
    assert len(keys) == 4
    
    # All keys should have loaded sprites
    for key in keys:
        assert key.sprite is not None
        assert key.sprite.get_width() == 16
        assert key.sprite.get_height() == 16
        print(f"✓ {key.key_type} key loaded successfully")
    
    print("\n✓ All 4 keys loaded with actual sprites!")

def test_key_proximity_detection():
    """Verify proximity detection works correctly"""
    key = KeyEntity("bronze", (100, 100))
    
    # Test within range
    player_rect = pygame.Rect(110, 110, 20, 20)
    assert key.near_player(player_rect, radius=30) == True
    print("✓ Proximity detection: within range works")
    
    # Test out of range
    player_rect = pygame.Rect(200, 200, 20, 20)
    assert key.near_player(player_rect, radius=30) == False
    print("✓ Proximity detection: out of range works")

if __name__ == "__main__":
    test_keys_load_actual_sprites()
    test_key_proximity_detection()
    print("\n✅ All integration tests passed!")
    pygame.quit()
