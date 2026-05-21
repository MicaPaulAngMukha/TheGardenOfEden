#!/usr/bin/env python3
"""
Verification script for difficulty mechanics integration.
This script checks that all difficulty system components are properly integrated.
"""

import sys
import os

def check_file_exists(filepath):
    """Check if a file exists."""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {filepath}")
    return exists

def check_import_in_file(filepath, import_statement):
    """Check if an import statement exists in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            exists = import_statement in content
            status = "✓" if exists else "✗"
            print(f"  {status} Import: {import_statement}")
            return exists
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return False

def check_function_call_in_file(filepath, function_call):
    """Check if a function call exists in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            exists = function_call in content
            status = "✓" if exists else "✗"
            print(f"  {status} Function call: {function_call}")
            return exists
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("DIFFICULTY MECHANICS INTEGRATION VERIFICATION")
    print("=" * 70)
    
    all_checks_passed = True
    
    # Check core files exist
    print("\n1. Core Files:")
    all_checks_passed &= check_file_exists("difficulty_config.py")
    all_checks_passed &= check_file_exists("difficulty_manager.py")
    all_checks_passed &= check_file_exists("god_entity.py")
    
    # Check level files exist
    print("\n2. Level Files:")
    level_files = ["TheNaga.py", "TheTwins.py", "TheGuardian.py", "TheStatues.py", "TheGarden.py"]
    for level_file in level_files:
        all_checks_passed &= check_file_exists(level_file)
    
    # Check imports in level files
    print("\n3. DifficultyManager Imports:")
    for level_file in level_files:
        if os.path.exists(level_file):
            all_checks_passed &= check_import_in_file(
                level_file, 
                "from difficulty_manager import DifficultyManager"
            )
    
    # Check GodEntity imports in non-Garden levels
    print("\n4. GodEntity Imports (non-Garden levels):")
    non_garden_levels = ["TheNaga.py", "TheTwins.py", "TheGuardian.py", "TheStatues.py"]
    for level_file in non_garden_levels:
        if os.path.exists(level_file):
            all_checks_passed &= check_import_in_file(
                level_file, 
                "from god_entity import GodEntity"
            )
    
    # Check DifficultyManager initialization
    print("\n5. DifficultyManager Initialization:")
    level_names = {
        "TheNaga.py": "TheNaga",
        "TheTwins.py": "TheTwins",
        "TheGuardian.py": "TheGuardian",
        "TheStatues.py": "TheStatues",
        "TheGarden.py": "TheGarden"
    }
    for level_file, level_name in level_names.items():
        if os.path.exists(level_file):
            all_checks_passed &= check_function_call_in_file(
                level_file,
                f'DifficultyManager(player, "{level_name}")'
            )
    
    # Check difficulty indicator drawing
    print("\n6. Difficulty Indicator Drawing:")
    for level_file in level_files:
        if os.path.exists(level_file):
            all_checks_passed &= check_function_call_in_file(
                level_file,
                "difficulty_mgr.draw_indicator"
            )
    
    # Check God spawning logic
    print("\n7. God Spawning Logic (non-Garden levels):")
    for level_file in non_garden_levels:
        if os.path.exists(level_file):
            all_checks_passed &= check_function_call_in_file(
                level_file,
                "should_spawn_god()"
            )
    
    # Check modifier application
    print("\n8. Difficulty Modifier Application:")
    modifier_checks = {
        "TheNaga.py": ["naga_speed", "item_spawn_multiplier", "abel_speed"],
        "TheTwins.py": ["abel_speed", "cain_throw_cooldown_multiplier", "cain_throw_range"],
        "TheGuardian.py": ["light_phase_duration", "dark_phase_duration"],
        "TheStatues.py": ["light_phase_duration", "statue_speed_multiplier"],
        "TheGarden.py": ["tree_shakes_required", "lightning_count", "god_speed_multiplier"]
    }
    
    for level_file, modifiers in modifier_checks.items():
        if os.path.exists(level_file):
            print(f"\n  {level_file}:")
            for modifier in modifiers:
                all_checks_passed &= check_function_call_in_file(
                    level_file,
                    f'get_modifier("{modifier}"'
                )
    
    # Summary
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✓ ALL CHECKS PASSED - Difficulty system is fully integrated!")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Review the output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
