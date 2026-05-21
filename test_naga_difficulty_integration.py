"""
Integration test for TheNaga difficulty system integration.
Tests that difficulty modifiers are correctly applied.
"""

import pygame
import sys
import os

# Initialize pygame before importing TheNaga
pygame.init()

# Mock the resource_path function
def mock_resource_path(path):
    return path

# Patch resource_path before importing TheNaga
sys.modules['resource_path'] = type(sys)('resource_path')
sys.modules['resource_path'].resource_path = mock_resource_path

from difficulty_manager import DifficultyManager
from difficulty_config import EASY, NORMAL, HARD, GOD_MODE


class MockKeyEntity:
    """Mock KeyEntity for testing."""
    def __init__(self, key_type):
        self.key_type = key_type


class MockPlayer:
    """Mock Player for testing."""
    def __init__(self, held_key=None):
        self.held_key = held_key
        self.rect = pygame.Rect(100, 100, 14, 14)


def test_easy_mode_modifiers():
    """Test Easy Mode applies correct modifiers for TheNaga."""
    print("\n=== Testing Easy Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("bronze"))
    difficulty_mgr = DifficultyManager(player, "TheNaga")
    
    assert difficulty_mgr.difficulty == EASY
    assert difficulty_mgr.get_modifier("naga_speed", 5) == 5  # No change
    assert difficulty_mgr.get_modifier("item_spawn_multiplier", 1.0) == 1.5
    assert difficulty_mgr.get_modifier("abel_speed", 3.6) == 2.5
    assert difficulty_mgr.get_modifier("cain_throw_cooldown_multiplier", 1.0) == 1.5
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ Easy Mode modifiers correct")


def test_normal_mode_modifiers():
    """Test Normal Mode applies no modifiers for TheNaga."""
    print("\n=== Testing Normal Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("gold"))
    difficulty_mgr = DifficultyManager(player, "TheNaga")
    
    assert difficulty_mgr.difficulty == NORMAL
    assert difficulty_mgr.get_modifier("naga_speed", 5) == 5
    assert difficulty_mgr.get_modifier("item_spawn_multiplier", 1.0) == 1.0
    assert difficulty_mgr.get_modifier("abel_speed", 3.6) == 3.6
    assert difficulty_mgr.get_modifier("cain_throw_cooldown_multiplier", 1.0) == 1.0
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ Normal Mode modifiers correct (no changes)")


def test_hard_mode_modifiers():
    """Test Hard Mode applies correct modifiers for TheNaga."""
    print("\n=== Testing Hard Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("rusted"))
    difficulty_mgr = DifficultyManager(player, "TheNaga")
    
    assert difficulty_mgr.difficulty == HARD
    assert difficulty_mgr.get_modifier("naga_speed", 5) == 6
    assert difficulty_mgr.get_modifier("item_spawn_multiplier", 1.0) == 0.5
    assert difficulty_mgr.get_modifier("cain_throw_cooldown_multiplier", 1.0) == 0.5
    assert difficulty_mgr.get_modifier("abel_instant_kill", False) == True
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ Hard Mode modifiers correct")


def test_god_mode_spawn():
    """Test God Mode spawns God entity."""
    print("\n=== Testing God Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("divine"))
    difficulty_mgr = DifficultyManager(player, "TheNaga")
    
    assert difficulty_mgr.difficulty == GOD_MODE
    assert difficulty_mgr.should_spawn_god() == True
    
    print("✓ God Mode spawns God entity")


def test_no_key_defaults_to_normal():
    """Test that no key defaults to Normal Mode."""
    print("\n=== Testing No Key (Default) ===")
    
    player = MockPlayer(held_key=None)
    difficulty_mgr = DifficultyManager(player, "TheNaga")
    
    assert difficulty_mgr.difficulty == NORMAL
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ No key defaults to Normal Mode")


def test_item_spawn_calculation():
    """Test item spawn timer calculation with multiplier."""
    print("\n=== Testing Item Spawn Calculation ===")
    
    # Easy Mode: 1.5x spawn rate (divide timer by 1.5)
    base_time = 600
    easy_multiplier = 1.5
    easy_time = int(base_time / easy_multiplier)
    assert easy_time == 400
    print(f"✓ Easy Mode: {base_time} / {easy_multiplier} = {easy_time} frames")
    
    # Hard Mode: 0.5x spawn rate (divide timer by 0.5 = multiply by 2)
    hard_multiplier = 0.5
    hard_time = int(base_time / hard_multiplier)
    assert hard_time == 1200
    print(f"✓ Hard Mode: {base_time} / {hard_multiplier} = {hard_time} frames")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("TheNaga Difficulty Integration Tests")
    print("=" * 60)
    
    try:
        test_easy_mode_modifiers()
        test_normal_mode_modifiers()
        test_hard_mode_modifiers()
        test_god_mode_spawn()
        test_no_key_defaults_to_normal()
        test_item_spawn_calculation()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    pygame.quit()
    sys.exit(0 if success else 1)
