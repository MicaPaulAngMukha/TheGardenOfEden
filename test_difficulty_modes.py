"""
Test script to verify all difficulty modes apply their modifiers correctly.
Tests Bronze (Easy), Gold (Normal), Rusted (Hard), and Divine (God Mode) keys.
"""

import sys
from difficulty_config import (
    EASY, NORMAL, HARD, GOD_MODE,
    KEY_TO_DIFFICULTY,
    DIFFICULTY_MODIFIERS,
    get_difficulty_from_key,
    get_modifiers,
    validate_modifiers
)
from difficulty_manager import DifficultyManager


class MockKeyEntity:
    """Mock key entity for testing"""
    def __init__(self, key_type):
        self.key_type = key_type


class MockPlayer:
    """Mock player for testing"""
    def __init__(self, held_key=None):
        self.held_key = held_key


def test_key_to_difficulty_mapping():
    """Test that all keys map to correct difficulty modes"""
    print("\n" + "="*70)
    print("TEST 1: Key to Difficulty Mapping")
    print("="*70)
    
    test_cases = [
        ("bronze", EASY, "Bronze Key → Easy Mode"),
        ("gold", NORMAL, "Gold Key → Normal Mode"),
        ("rusted", HARD, "Rusted Key → Hard Mode"),
        ("divine", GOD_MODE, "Divine Key → God Mode"),
        (None, NORMAL, "No Key → Normal Mode (default)"),
    ]
    
    all_passed = True
    for key_type, expected_diff, description in test_cases:
        if key_type is None:
            key_entity = None
        else:
            key_entity = MockKeyEntity(key_type)
        
        result = get_difficulty_from_key(key_entity)
        passed = result == expected_diff
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {description}")
        if not passed:
            print(f"  Expected: {expected_diff}, Got: {result}")
    
    return all_passed


def test_level_modifiers():
    """Test that each level applies correct modifiers for each difficulty"""
    print("\n" + "="*70)
    print("TEST 2: Level-Specific Modifiers")
    print("="*70)
    
    levels = ["TheNaga", "TheTwins", "TheGuardian", "TheStatues", "TheGarden"]
    difficulties = [EASY, NORMAL, HARD, GOD_MODE]
    
    all_passed = True
    
    for level in levels:
        print(f"\n{level}:")
        for diff in difficulties:
            modifiers = get_modifiers(level, diff)
            
            # Check if modifiers exist for this level/difficulty combo
            expected_mods = DIFFICULTY_MODIFIERS.get(level, {}).get(diff, {})
            
            if modifiers == expected_mods:
                print(f"  ✓ {diff.upper()}: {len(modifiers)} modifiers")
                if modifiers:
                    for key, value in modifiers.items():
                        print(f"    - {key}: {value}")
            else:
                print(f"  ✗ {diff.upper()}: Modifier mismatch!")
                all_passed = False
    
    return all_passed


def test_god_spawning():
    """Test that God only spawns in God Mode"""
    print("\n" + "="*70)
    print("TEST 3: God Entity Spawning")
    print("="*70)
    
    test_cases = [
        ("bronze", False, "Bronze Key (Easy) → No God"),
        ("gold", False, "Gold Key (Normal) → No God"),
        ("rusted", False, "Rusted Key (Hard) → No God"),
        ("divine", True, "Divine Key (God Mode) → God Spawns"),
    ]
    
    all_passed = True
    
    for key_type, should_spawn, description in test_cases:
        key_entity = MockKeyEntity(key_type)
        player = MockPlayer(held_key=key_entity)
        
        # Test for non-Garden levels (where God spawns)
        for level in ["TheNaga", "TheTwins", "TheGuardian", "TheStatues"]:
            mgr = DifficultyManager(player, level)
            spawns = mgr.should_spawn_god()
            
            passed = spawns == should_spawn
            all_passed = all_passed and passed
            
            status = "✓ PASS" if passed else "✗ FAIL"
            if not passed or key_type == "divine":  # Always show divine key results
                print(f"{status}: {description} in {level}")
                if not passed:
                    print(f"  Expected: {should_spawn}, Got: {spawns}")
    
    return all_passed


def test_normal_mode_no_modifiers():
    """Test that Normal Mode (Gold Key) has no gameplay modifiers"""
    print("\n" + "="*70)
    print("TEST 4: Normal Mode (Gold Key) - No Modifiers")
    print("="*70)
    
    levels = ["TheNaga", "TheTwins", "TheGuardian", "TheStatues", "TheGarden"]
    all_passed = True
    
    for level in levels:
        modifiers = get_modifiers(level, NORMAL)
        
        if len(modifiers) == 0:
            print(f"✓ PASS: {level} - No modifiers in Normal Mode")
        else:
            print(f"✗ FAIL: {level} - Has {len(modifiers)} modifiers in Normal Mode!")
            print(f"  Modifiers: {modifiers}")
            all_passed = False
    
    return all_passed


def test_easy_mode_easier():
    """Test that Easy Mode makes the game easier"""
    print("\n" + "="*70)
    print("TEST 5: Easy Mode (Bronze Key) - Easier Gameplay")
    print("="*70)
    
    checks = [
        ("TheNaga", "item_spawn_multiplier", 1.5, "More items spawn"),
        ("TheNaga", "cain_throw_cooldown_multiplier", 1.5, "Cain throws slower"),
        ("TheTwins", "abel_speed", 2.5, "Abel moves slower"),
        ("TheTwins", "cain_throw_cooldown_multiplier", 1.5, "Cain throws slower"),
        ("TheGuardian", "disable_enrage", True, "Guardian doesn't enrage"),
        ("TheStatues", "light_phase_duration", 240, "Longer light phases"),
        ("TheStatues", "statue_speed_multiplier", 0.8, "Statues move slower"),
        ("TheGarden", "tree_shakes_required", 3, "Fewer tree shakes needed"),
    ]
    
    all_passed = True
    
    for level, modifier_key, expected_value, description in checks:
        modifiers = get_modifiers(level, EASY)
        actual_value = modifiers.get(modifier_key)
        
        passed = actual_value == expected_value
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {level}.{modifier_key} = {actual_value} ({description})")
        if not passed:
            print(f"  Expected: {expected_value}")
    
    return all_passed


def test_hard_mode_harder():
    """Test that Hard Mode makes the game harder"""
    print("\n" + "="*70)
    print("TEST 6: Hard Mode (Rusted Key) - Harder Gameplay")
    print("="*70)
    
    checks = [
        ("TheNaga", "naga_speed", 6, "Naga moves faster"),
        ("TheNaga", "item_spawn_multiplier", 0.5, "Fewer items spawn"),
        ("TheNaga", "abel_instant_kill", True, "Abel instant-kills"),
        ("TheTwins", "cain_throw_cooldown_multiplier", 0.5, "Cain throws faster"),
        ("TheTwins", "abel_instant_kill", True, "Abel instant-kills"),
        ("TheGuardian", "light_phase_duration", 120, "Shorter light phases"),
        ("TheGuardian", "dark_phase_duration", 420, "Longer dark phases"),
        ("TheStatues", "statue_speed_multiplier", 1.2, "Statues move faster"),
        ("TheGarden", "tree_shakes_required", 7, "More tree shakes needed"),
    ]
    
    all_passed = True
    
    for level, modifier_key, expected_value, description in checks:
        modifiers = get_modifiers(level, HARD)
        actual_value = modifiers.get(modifier_key)
        
        passed = actual_value == expected_value
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {level}.{modifier_key} = {actual_value} ({description})")
        if not passed:
            print(f"  Expected: {expected_value}")
    
    return all_passed


def test_god_mode_extreme():
    """Test that God Mode has extreme difficulty"""
    print("\n" + "="*70)
    print("TEST 7: God Mode (Divine Key) - Extreme Difficulty")
    print("="*70)
    
    checks = [
        ("TheNaga", "spawn_god", True, "God entity spawns"),
        ("TheTwins", "spawn_god", True, "God entity spawns"),
        ("TheGuardian", "spawn_god", True, "God entity spawns"),
        ("TheStatues", "spawn_god", True, "God entity spawns"),
        ("TheGarden", "lightning_count", 9, "More lightning bolts"),
        ("TheGarden", "god_speed_multiplier", 1.5, "God moves faster"),
    ]
    
    all_passed = True
    
    for level, modifier_key, expected_value, description in checks:
        modifiers = get_modifiers(level, GOD_MODE)
        actual_value = modifiers.get(modifier_key)
        
        passed = actual_value == expected_value
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {level}.{modifier_key} = {actual_value} ({description})")
        if not passed:
            print(f"  Expected: {expected_value}")
    
    return all_passed


def test_modifier_validation():
    """Test that all modifiers pass validation"""
    print("\n" + "="*70)
    print("TEST 8: Modifier Validation")
    print("="*70)
    
    errors = validate_modifiers()
    
    if not errors:
        print("✓ PASS: All modifiers are valid")
        return True
    else:
        print(f"✗ FAIL: Found {len(errors)} validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("DIFFICULTY MODES VERIFICATION TEST SUITE")
    print("="*70)
    print("\nTesting all 4 difficulty modes:")
    print("  • Bronze Key → Easy Mode")
    print("  • Gold Key → Normal Mode (no modifiers)")
    print("  • Rusted Key → Hard Mode")
    print("  • Divine Key → God Mode (with God entity)")
    
    tests = [
        ("Key to Difficulty Mapping", test_key_to_difficulty_mapping),
        ("Level-Specific Modifiers", test_level_modifiers),
        ("God Entity Spawning", test_god_spawning),
        ("Normal Mode No Modifiers", test_normal_mode_no_modifiers),
        ("Easy Mode Easier", test_easy_mode_easier),
        ("Hard Mode Harder", test_hard_mode_harder),
        ("God Mode Extreme", test_god_mode_extreme),
        ("Modifier Validation", test_modifier_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! All difficulty modes work correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
