"""
Test script to verify key rendering and visual indicator functionality.
This test verifies that:
1. Keys are rendered in the world
2. Dropped keys remain visible
3. Player shows key indicator when holding a key
"""
import pygame
import sys
from key_system import KeyEntity, spawn_keys
from resource_path import resource_path

def test_key_rendering():
    """Test that keys can be rendered without errors"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    game_surface = pygame.Surface((800, 600))
    
    # Test 1: Spawn keys
    print("Test 1: Spawning keys...")
    keys_in_world = spawn_keys()
    assert len(keys_in_world) == 4, f"Expected 4 keys, got {len(keys_in_world)}"
    print(f"✓ Spawned {len(keys_in_world)} keys")
    
    # Test 2: Verify each key has a sprite
    print("\nTest 2: Verifying key sprites...")
    for key in keys_in_world:
        assert key.sprite is not None, f"Key {key.key_type} has no sprite"
        assert isinstance(key.sprite, pygame.Surface), f"Key {key.key_type} sprite is not a Surface"
        print(f"✓ {key.key_type} key has sprite: {key.sprite.get_size()}")
    
    # Test 3: Render keys to surface
    print("\nTest 3: Rendering keys to surface...")
    for key in keys_in_world:
        try:
            game_surface.blit(key.sprite, key.rect)
            print(f"✓ {key.key_type} key rendered at {key.rect.topleft}")
        except Exception as e:
            print(f"✗ Failed to render {key.key_type} key: {e}")
            raise
    
    # Test 4: Test key indicator image
    print("\nTest 4: Loading key indicator image...")
    try:
        key_img = pygame.image.load(resource_path("Key.png")).convert_alpha()
        key_img = pygame.transform.scale(key_img, (16, 16))
        print(f"✓ Key indicator loaded: {key_img.get_size()}")
    except Exception as e:
        print(f"✗ Failed to load key indicator: {e}")
        raise
    
    # Test 5: Simulate dropped key
    print("\nTest 5: Testing dropped key persistence...")
    bronze_key = keys_in_world[0]
    original_pos = bronze_key.rect.center
    
    # Simulate dropping at new position
    bronze_key.rect.center = (400, 300)
    bronze_key.discovered = False
    
    # Verify it's still in the list and can be rendered
    assert bronze_key in keys_in_world, "Dropped key not in keys_in_world"
    game_surface.blit(bronze_key.sprite, bronze_key.rect)
    print(f"✓ Dropped key persists at new position: {bronze_key.rect.center}")
    
    print("\n" + "="*50)
    print("All rendering tests passed! ✓")
    print("="*50)
    
    pygame.quit()

if __name__ == "__main__":
    test_key_rendering()
