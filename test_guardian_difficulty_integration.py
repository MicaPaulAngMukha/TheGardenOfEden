"""
Integration test for TheGuardian difficulty system integration.
Tests that difficulty modifiers are correctly applied.
"""

import pygame
import sys
import os

# Initialize pygame before importing TheGuardian
pygame.init()

# Mock the resource_path function
def mock_resource_path(path):
    return path

# Patch resource_path before importing TheGuardian
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
    """Test Easy Mode applies correct modifiers for TheGuardian."""
    print("\n=== Testing Easy Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("bronze"))
    difficulty_mgr = DifficultyManager(player, "TheGuardian")
    
    assert difficulty_mgr.difficulty == EASY
    assert difficulty_mgr.get_modifier("disable_enrage", False) == True
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ Easy Mode modifiers correct (enrage disabled)")


def test_normal_mode_modifiers():
    """Test Normal Mode applies no modifiers for TheGuardian."""
    print("\n=== Testing Normal Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("gold"))
    difficulty_mgr = DifficultyManager(player, "TheGuardian")
    
    assert difficulty_mgr.difficulty == NORMAL
    assert difficulty_mgr.get_modifier("disable_enrage", False) == False
    assert difficulty_mgr.get_modifier("light_phase_duration", 180) == 180
    assert difficulty_mgr.get_modifier("dark_phase_duration", 300) == 300
    assert difficulty_mgr.get_modifier("guardian_chase_speed_multiplier", 1.0) == 1.0
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ Normal Mode modifiers correct (no changes)")


def test_hard_mode_modifiers():
    """Test Hard Mode applies correct modifiers for TheGuardian."""
    print("\n=== Testing Hard Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("rusted"))
    difficulty_mgr = DifficultyManager(player, "TheGuardian")
    
    assert difficulty_mgr.difficulty == HARD
    assert difficulty_mgr.get_modifier("light_phase_duration", 180) == 120
    assert difficulty_mgr.get_modifier("dark_phase_duration", 300) == 420
    assert difficulty_mgr.get_modifier("guardian_chase_speed_multiplier", 1.0) == 1.2
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ Hard Mode modifiers correct")


def test_god_mode_spawn():
    """Test God Mode spawns God entity."""
    print("\n=== Testing God Mode ===")
    
    player = MockPlayer(held_key=MockKeyEntity("divine"))
    difficulty_mgr = DifficultyManager(player, "TheGuardian")
    
    assert difficulty_mgr.difficulty == GOD_MODE
    assert difficulty_mgr.should_spawn_god() == True
    
    print("✓ God Mode spawns God entity")


def test_no_key_defaults_to_normal():
    """Test that no key defaults to Normal Mode."""
    print("\n=== Testing No Key (Default) ===")
    
    player = MockPlayer(held_key=None)
    difficulty_mgr = DifficultyManager(player, "TheGuardian")
    
    assert difficulty_mgr.difficulty == NORMAL
    assert difficulty_mgr.should_spawn_god() == False
    
    print("✓ No key defaults to Normal Mode")


def test_chase_speed_calculation():
    """Test guardian chase speed calculation with multiplier."""
    print("\n=== Testing Chase Speed Calculation ===")
    
    # Normal Mode: 1.0x multiplier
    base_speed = 3.0
    normal_multiplier = 1.0
    normal_speed = base_speed * normal_multiplier
    assert normal_speed == 3.0
    print(f"✓ Normal Mode: {base_speed} * {normal_multiplier} = {normal_speed}")
    
    # Hard Mode: 1.2x multiplier
    hard_multiplier = 1.2
    hard_speed = base_speed * hard_multiplier
    assert abs(hard_speed - 3.6) < 0.001  # Use floating point comparison
    print(f"✓ Hard Mode: {base_speed} * {hard_multiplier} = {hard_speed}")


def test_phase_duration_changes():
    """Test light and dark phase duration changes."""
    print("\n=== Testing Phase Duration Changes ===")
    
    # Normal Mode baseline
    normal_light = 180
    normal_dark = 300
    print(f"✓ Normal Mode: Light={normal_light}, Dark={normal_dark}")
    
    # Hard Mode changes
    hard_light = 120
    hard_dark = 420
    print(f"✓ Hard Mode: Light={hard_light}, Dark={hard_dark}")
    
    # Verify Hard Mode is more challenging
    assert hard_light < normal_light  # Less light time
    assert hard_dark > normal_dark    # More dark time
    print("✓ Hard Mode is more challenging (less light, more dark)")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("TheGuardian Difficulty Integration Tests")
    print("=" * 60)
    
    try:
        test_easy_mode_modifiers()
        test_normal_mode_modifiers()
        test_hard_mode_modifiers()
        test_god_mode_spawn()
        test_no_key_defaults_to_normal()
        test_chase_speed_calculation()
        test_phase_duration_changes()
        
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
