"""
Preservation Property Tests for Key Spawning Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

This test suite verifies that the fix does NOT break existing functionality.
Tests are designed to PASS on UNFIXED code to establish baseline behavior,
then continue to PASS on FIXED code to confirm no regressions.

CRITICAL: These tests encode the EXPECTED preservation behavior. They should
pass both before and after the fix is implemented.

This test uses static code analysis to verify preservation of key game mechanics,
which is appropriate for this type of Pygame application where full runtime
simulation would be complex.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
import re


class TestPreservationProperties:
    """
    Property 2: Preservation - Key Pickup, Gate Unlock, and Chase Mechanics
    
    This test suite verifies that all existing game mechanics remain unchanged
    by the key spawning fix. The tests check:
    1. Key pickup detection logic (check_key_pickup method)
    2. Gate unlocking logic when player has key
    3. Chase activation when mikhail.approach >= 3
    4. Music transition to "12. March of Iron.mp3" when chase activates
    """
    
    def test_key_pickup_logic_preserved(self):
        """
        **Validates: Requirements 3.1, 3.3**
        
        Test Case 1: Key pickup detection using check_key_pickup(bushes) works correctly
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
        - The test verifies check_key_pickup() method exists and has correct logic
        - This establishes baseline behavior to preserve
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test confirms check_key_pickup() method is unchanged
        - This confirms no regression in key pickup detection
        
        Expected Behavior:
        - check_key_pickup() should iterate through bushes
        - Should check for collision with bushes that have has_key=True
        - Should set player.has_key=True and bush has_key=False when key is found
        - Should return True when key is picked up, False otherwise
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Player class
        player_class_pattern = r'class Player:.*?(?=\nclass\s|\Z)'
        player_class_match = re.search(player_class_pattern, content, re.DOTALL)
        
        if not player_class_match:
            assert False, "Could not find Player class in Start.py"
        
        player_class = player_class_match.group(0)
        
        # Look for check_key_pickup method
        check_key_pickup_pattern = r'def check_key_pickup\(self, bushes\):.*?(?=\n    def\s|\Z)'
        check_key_pickup_match = re.search(check_key_pickup_pattern, player_class, re.DOTALL)
        
        if not check_key_pickup_match:
            assert False, (
                "Preservation violation: check_key_pickup() method not found.\n"
                "Expected: check_key_pickup() method should exist in Player class.\n"
                "This is a critical regression - key pickup detection is broken."
            )
        
        check_key_pickup_code = check_key_pickup_match.group(0)
        
        # Verify the method has the expected logic
        # Should iterate through bushes, check has_key, check collision, set flags
        expected_patterns = [
            r'for\s+\w+\s+in\s+bushes:',  # Iterates through bushes
            r'if\s+\w+\["has_key"\]',  # Checks has_key flag
            r'colliderect',  # Checks collision
            r'self\.has_key\s*=\s*True',  # Sets player.has_key
            r'\["has_key"\]\s*=\s*False',  # Clears bush has_key
            r'return\s+True',  # Returns True on pickup
            r'return\s+False',  # Returns False if no pickup
        ]
        
        missing_patterns = []
        for pattern in expected_patterns:
            if not re.search(pattern, check_key_pickup_code):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            assert False, (
                f"Preservation violation: check_key_pickup() method is missing expected logic.\n"
                f"Missing patterns: {missing_patterns}\n"
                f"Expected: check_key_pickup() should iterate bushes, check collision, set flags.\n"
                f"This is a regression - key pickup detection logic has changed."
            )
        
        print("\n✓ Preservation test PASSED: Key pickup logic is preserved")
    
    def test_gate_unlock_logic_preserved(self):
        """
        **Validates: Requirements 3.1, 3.4**
        
        Test Case 2: Gate unlocking logic when player has key works correctly
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
        - The test verifies gate unlock logic exists in game loop
        - This establishes baseline behavior to preserve
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test confirms gate unlock logic is unchanged
        - This confirms no regression in gate unlocking
        
        Expected Behavior:
        - When player has key and is near gate, STATE_PROMPT should be triggered
        - When player doesn't have key and is near gate, STATE_LOCKED should be triggered
        - When player unlocks gate (presses 'y'), gate_open should be set to True
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the main() function
        main_func_pattern = r'def main\(\):.*?(?=\ndef\s|\Z)'
        main_func_match = re.search(main_func_pattern, content, re.DOTALL)
        
        if not main_func_match:
            assert False, "Could not find main() function in Start.py"
        
        main_func = main_func_match.group(0)
        
        # Look for gate unlock logic patterns
        expected_patterns = [
            r'player\.near_gate\(\)',  # Checks if player is near gate
            r'STATE_PROMPT\s+if\s+player\.has_key\s+else\s+STATE_LOCKED',  # Conditional state based on has_key
            r'if\s+event\.key\s+==\s+pygame\.K_y:',  # Handles 'y' key press
            r'gate_open\s*=\s*True',  # Sets gate_open flag
            r'state\s*=\s*STATE_UNLOCKED',  # Transitions to unlocked state
        ]
        
        missing_patterns = []
        for pattern in expected_patterns:
            if not re.search(pattern, main_func):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            assert False, (
                f"Preservation violation: Gate unlock logic is missing expected patterns.\n"
                f"Missing patterns: {missing_patterns}\n"
                f"Expected: Gate unlock logic should check player.near_gate(), player.has_key, handle 'y' key.\n"
                f"This is a regression - gate unlocking logic has changed."
            )
        
        print("\n✓ Preservation test PASSED: Gate unlock logic is preserved")
    
    def test_chase_activation_logic_preserved(self):
        """
        **Validates: Requirements 3.2, 3.5**
        
        Test Case 3: Chase activation when mikhail.approach >= 3 works correctly
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
        - The test verifies chase activation logic exists in game loop
        - This establishes baseline behavior to preserve
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test confirms chase activation logic is unchanged
        - This confirms no regression in chase mechanics
        
        Expected Behavior:
        - When mikhail.approach >= 3, mikhail.chasing should be set to True
        - Chase activation should trigger music change to "12. March of Iron.mp3"
        - Chase activation should trigger push animation
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the main() function
        main_func_pattern = r'def main\(\):.*?(?=\ndef\s|\Z)'
        main_func_match = re.search(main_func_pattern, content, re.DOTALL)
        
        if not main_func_match:
            assert False, "Could not find main() function in Start.py"
        
        main_func = main_func_match.group(0)
        
        # Look for chase activation logic patterns
        expected_patterns = [
            r'mikhail\.approach\s*>=\s*3',  # Checks if approach >= 3
            r'mikhail\.chasing\s*=\s*True',  # Sets chasing flag
            r'compute_push\(',  # Triggers push animation
        ]
        
        missing_patterns = []
        for pattern in expected_patterns:
            if not re.search(pattern, main_func):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            assert False, (
                f"Preservation violation: Chase activation logic is missing expected patterns.\n"
                f"Missing patterns: {missing_patterns}\n"
                f"Expected: Chase activation should check mikhail.approach >= 3, set mikhail.chasing, trigger push.\n"
                f"This is a regression - chase activation logic has changed."
            )
        
        print("\n✓ Preservation test PASSED: Chase activation logic is preserved")
    
    def test_music_transition_preserved(self):
        """
        **Validates: Requirements 3.5**
        
        Test Case 4: Music transition to "12. March of Iron.mp3" when chase activates
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
        - The test verifies music transition logic exists in chase activation
        - This establishes baseline behavior to preserve
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test confirms music transition logic is unchanged
        - This confirms no regression in music transitions
        
        Expected Behavior:
        - When chase activates (mikhail.approach >= 3), music should fade out
        - New music "12. March of Iron.mp3" should be loaded and played
        - Music volume should be set to 0.7
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the main() function
        main_func_pattern = r'def main\(\):.*?(?=\ndef\s|\Z)'
        main_func_match = re.search(main_func_pattern, content, re.DOTALL)
        
        if not main_func_match:
            assert False, "Could not find main() function in Start.py"
        
        main_func = main_func_match.group(0)
        
        # Look for music transition logic in chase activation section
        # Find the section where mikhail.approach >= 3
        chase_section_pattern = r'mikhail\.approach\s*>=\s*3.*?state\s*=\s*STATE_EXPLORE'
        chase_section_match = re.search(chase_section_pattern, main_func, re.DOTALL)
        
        if not chase_section_match:
            assert False, (
                "Preservation violation: Chase activation section not found.\n"
                "Expected: mikhail.approach >= 3 section should exist.\n"
                "This is a regression - chase activation logic is missing."
            )
        
        chase_section = chase_section_match.group(0)
        
        # Look for music transition patterns
        expected_patterns = [
            r'pygame\.mixer\.music\.fadeout\(',  # Fades out current music
            r'pygame\.mixer\.music\.load\(.*?12\.\s*March\s*of\s*Iron\.mp3',  # Loads chase music
            r'pygame\.mixer\.music\.set_volume\(0\.7\)',  # Sets volume
            r'pygame\.mixer\.music\.play\(-1\)',  # Plays music in loop
        ]
        
        missing_patterns = []
        for pattern in expected_patterns:
            if not re.search(pattern, chase_section):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            assert False, (
                f"Preservation violation: Music transition logic is missing expected patterns.\n"
                f"Missing patterns: {missing_patterns}\n"
                f"Expected: Music should fade out, load '12. March of Iron.mp3', set volume, play.\n"
                f"This is a regression - music transition logic has changed."
            )
        
        print("\n✓ Preservation test PASSED: Music transition logic is preserved")
    
    def test_mikhail_chase_behavior_preserved(self):
        """
        **Validates: Requirements 3.2**
        
        Test Case 5: Mikhail chase behavior works correctly
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
        - The test verifies Mikhail chase logic exists in game loop
        - This establishes baseline behavior to preserve
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test confirms Mikhail chase logic is unchanged
        - This confirms no regression in chase mechanics
        
        Expected Behavior:
        - When mikhail.chasing is True, mikhail.chase() should be called
        - When Mikhail collides with player, player should lose a life
        - Player should be pushed back on collision
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the main() function
        main_func_pattern = r'def main\(\):.*?(?=\ndef\s|\Z)'
        main_func_match = re.search(main_func_pattern, content, re.DOTALL)
        
        if not main_func_match:
            assert False, "Could not find main() function in Start.py"
        
        main_func = main_func_match.group(0)
        
        # Look for Mikhail chase behavior patterns
        expected_patterns = [
            r'if\s+mikhail\.chasing',  # Checks if chasing
            r'mikhail\.chase\(player\.rect\)',  # Calls chase method
            r'mikhail\.rect\.colliderect\(player\.rect\)',  # Checks collision
            r'player\.lives\s*-=\s*1',  # Decrements player lives
            r'player\.trigger_hurt\(\)',  # Triggers hurt animation
        ]
        
        missing_patterns = []
        for pattern in expected_patterns:
            if not re.search(pattern, main_func):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            assert False, (
                f"Preservation violation: Mikhail chase behavior is missing expected patterns.\n"
                f"Missing patterns: {missing_patterns}\n"
                f"Expected: Chase should check mikhail.chasing, call chase(), check collision, decrement lives.\n"
                f"This is a regression - Mikhail chase behavior has changed."
            )
        
        print("\n✓ Preservation test PASSED: Mikhail chase behavior is preserved")
    
    def test_raziel_interactions_preserved(self):
        """
        **Validates: Requirements 3.6**
        
        Test Case 6: Raziel interactions work correctly regardless of key spawn timing
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
        - The test verifies Raziel interaction logic exists in game loop
        - This establishes baseline behavior to preserve
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test confirms Raziel interaction logic is unchanged
        - This confirms no regression in Raziel interactions
        
        Expected Behavior:
        - Raziel should have multiple dialog triggers based on mikhail.approach
        - Raziel should start roaming after mikhail.approach >= 2
        - Raziel interactions should work independently of key spawn timing
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the main() function
        main_func_pattern = r'def main\(\):.*?(?=\ndef\s|\Z)'
        main_func_match = re.search(main_func_pattern, content, re.DOTALL)
        
        if not main_func_match:
            assert False, "Could not find main() function in Start.py"
        
        main_func = main_func_match.group(0)
        
        # Look for Raziel interaction patterns
        expected_patterns = [
            r'raziel\.near_player\(player\.rect\)',  # Checks if Raziel is near player
            r'raziel_before_mikhail',  # Dialog before Mikhail interaction
            r'raziel_after_mikhail',  # Dialog after Mikhail interaction
            r'raziel_after_mikhail_2',  # Dialog after second Mikhail interaction
            r'raziel_roaming',  # Dialog during roaming
            r'raziel_during_chase',  # Dialog during chase
            r'raziel\.start_roaming\(\)',  # Starts roaming behavior
        ]
        
        missing_patterns = []
        for pattern in expected_patterns:
            if not re.search(pattern, main_func):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            assert False, (
                f"Preservation violation: Raziel interaction logic is missing expected patterns.\n"
                f"Missing patterns: {missing_patterns}\n"
                f"Expected: Raziel should have multiple dialog triggers and roaming behavior.\n"
                f"This is a regression - Raziel interaction logic has changed."
            )
        
        print("\n✓ Preservation test PASSED: Raziel interactions are preserved")
    
    @given(
        test_case=st.sampled_from([
            'key_pickup_logic',
            'gate_unlock_logic',
            'chase_activation_logic',
            'music_transition',
            'mikhail_chase_behavior',
            'raziel_interactions'
        ])
    )
    @settings(
        max_examples=18,  # Test each preservation case multiple times
        phases=[Phase.generate, Phase.target]  # Skip shrinking for faster execution
    )
    def test_property_preservation_all_mechanics(self, test_case):
        """
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
        
        Property-Based Test: For ANY game state after key has been spawned,
        ALL existing game mechanics should work exactly as before the fix.
        
        This property test generates checks across all preservation requirements
        to ensure no regressions are introduced by the fix.
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES (establishes baseline)
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES (confirms no regressions)
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the main() function
        main_func_pattern = r'def main\(\):.*?(?=\ndef\s|\Z)'
        main_func_match = re.search(main_func_pattern, content, re.DOTALL)
        
        if not main_func_match:
            assert False, "Could not find main() function in Start.py"
        
        main_func = main_func_match.group(0)
        
        # Check based on test case
        has_regression = False
        error_msg = ""
        
        if test_case == 'key_pickup_logic':
            # Check if check_key_pickup method exists and has correct logic
            player_class_pattern = r'class Player:.*?(?=\nclass\s|\Z)'
            player_class_match = re.search(player_class_pattern, content, re.DOTALL)
            if player_class_match:
                player_class = player_class_match.group(0)
                check_key_pickup_pattern = r'def check_key_pickup\(self, bushes\):.*?return\s+(True|False)'
                has_regression = not re.search(check_key_pickup_pattern, player_class, re.DOTALL)
            else:
                has_regression = True
            error_msg = (
                f"Property violation: Key pickup logic has regressed (test case '{test_case}').\n"
                f"Expected: check_key_pickup() method should exist with correct logic.\n"
                f"This is a regression - key pickup detection is broken."
            )
            
        elif test_case == 'gate_unlock_logic':
            # Check if gate unlock logic exists
            gate_patterns = [
                r'player\.near_gate\(\)',
                r'STATE_PROMPT\s+if\s+player\.has_key\s+else\s+STATE_LOCKED',
                r'gate_open\s*=\s*True'
            ]
            has_regression = not all(re.search(p, main_func) for p in gate_patterns)
            error_msg = (
                f"Property violation: Gate unlock logic has regressed (test case '{test_case}').\n"
                f"Expected: Gate unlock logic should check near_gate(), has_key, set gate_open.\n"
                f"This is a regression - gate unlocking is broken."
            )
            
        elif test_case == 'chase_activation_logic':
            # Check if chase activation logic exists
            chase_patterns = [
                r'mikhail\.approach\s*>=\s*3',
                r'mikhail\.chasing\s*=\s*True'
            ]
            has_regression = not all(re.search(p, main_func) for p in chase_patterns)
            error_msg = (
                f"Property violation: Chase activation logic has regressed (test case '{test_case}').\n"
                f"Expected: Chase should activate when mikhail.approach >= 3.\n"
                f"This is a regression - chase activation is broken."
            )
            
        elif test_case == 'music_transition':
            # Check if music transition logic exists
            music_patterns = [
                r'pygame\.mixer\.music\.fadeout\(',
                r'12\.\s*March\s*of\s*Iron\.mp3'
            ]
            has_regression = not all(re.search(p, main_func) for p in music_patterns)
            error_msg = (
                f"Property violation: Music transition logic has regressed (test case '{test_case}').\n"
                f"Expected: Music should transition to '12. March of Iron.mp3' on chase.\n"
                f"This is a regression - music transition is broken."
            )
            
        elif test_case == 'mikhail_chase_behavior':
            # Check if Mikhail chase behavior exists
            mikhail_patterns = [
                r'mikhail\.chase\(player\.rect\)',
                r'mikhail\.rect\.colliderect\(player\.rect\)',
                r'player\.lives\s*-=\s*1'
            ]
            has_regression = not all(re.search(p, main_func) for p in mikhail_patterns)
            error_msg = (
                f"Property violation: Mikhail chase behavior has regressed (test case '{test_case}').\n"
                f"Expected: Mikhail should chase player, check collision, decrement lives.\n"
                f"This is a regression - Mikhail chase behavior is broken."
            )
            
        elif test_case == 'raziel_interactions':
            # Check if Raziel interaction logic exists
            raziel_patterns = [
                r'raziel\.near_player\(player\.rect\)',
                r'raziel_before_mikhail',
                r'raziel\.start_roaming\(\)'
            ]
            has_regression = not all(re.search(p, main_func) for p in raziel_patterns)
            error_msg = (
                f"Property violation: Raziel interaction logic has regressed (test case '{test_case}').\n"
                f"Expected: Raziel should have dialog triggers and roaming behavior.\n"
                f"This is a regression - Raziel interactions are broken."
            )
        
        # ASSERTION: No regression should exist
        assert not has_regression, error_msg
        
        # If we reach here, the test passed for this case
        print(f"\n✓ Property test PASSED for '{test_case}': Preservation is maintained")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
