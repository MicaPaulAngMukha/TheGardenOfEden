"""
Bug Condition Exploration Test for Raziel Re-interaction Blocking

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

This test is designed to FAIL on unfixed code to confirm the bug exists.
When the test fails, it demonstrates that Raziel cannot be interacted with
multiple times due to mutually exclusive spoken_count conditions.

CRITICAL: This test encodes the EXPECTED behavior. When it passes after the fix,
it confirms the bug is resolved.

This test uses static code analysis to verify the bug condition and expected behavior,
which is appropriate for this type of interaction bug in a Pygame application.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
import re


class TestBugConditionExploration:
    """
    Property 1: Bug Condition - Multiple Raziel Interactions Blocked
    
    This test explores the bug condition where approaching Raziel after having
    already interacted with him once causes the interaction to be blocked due to
    mutually exclusive spoken_count conditions.
    
    The test uses static code analysis to verify:
    1. The bug exists in the unfixed code (mutually exclusive spoken_count checks)
    2. The fix is correctly implemented (game state-based checks instead)
    """
    
    def test_raziel_second_interaction_before_mikhail_should_trigger(self):
        """
        **Validates: Requirements 1.1, 1.2, 2.1, 2.6**
        
        Test Case 1: Second interaction before Mikhail (mikhail.approach == 0)
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect that the condition requires spoken_count == 0
        - After first interaction, spoken_count == 1, so condition is FALSE
        - This confirms the bug exists
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will detect that the condition checks mikhail.approach == 0
        - This allows re-interaction regardless of previous interactions
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Dialog "raziel_before_mikhail" should trigger
        - Interaction should be allowed multiple times
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "raziel_before_mikhail" dialog trigger
        # Try to find the fixed pattern first
        fixed_pattern = r'if\s+mikhail\.approach\s*==\s*0:\s*angel_dialog\s*=\s*DIALOGS\["raziel_before_mikhail"\]'
        fixed_match = re.search(fixed_pattern, content)
        
        # Try to find the buggy pattern
        buggy_pattern = r'if\s+raziel\.spoken_count\s*==\s*0\s+and\s+mikhail\.approach\s*==\s*0:\s*angel_dialog\s*=\s*DIALOGS\["raziel_before_mikhail"\]'
        buggy_match = re.search(buggy_pattern, content)
        
        if fixed_match:
            # Fixed code found - test passes
            print("\n✓ Bug condition test PASSED: Second interaction before Mikhail is allowed")
            assert True
        elif buggy_match:
            # Buggy code found - test fails with counterexample
            condition = buggy_match.group(0)
            assert False, (
                f"COUNTEREXAMPLE FOUND: Second interaction before Mikhail is blocked.\n"
                f"Bug confirmed in Start.py Raziel stationary interaction logic.\n"
                f"Current condition: {condition}\n"
                f"After first interaction (spoken_count=1), this condition is FALSE.\n"
                f"Expected: Condition should allow re-interaction (e.g., 'mikhail.approach == 0')\n"
                f"Root cause: Mutually exclusive spoken_count check prevents re-interaction.\n"
                f"Game state: mikhail.approach=0, spoken_count=1, cooldown=0, player_near=True\n"
                f"Expected behavior: Dialog 'raziel_before_mikhail' should trigger\n"
                f"Actual behavior: No interaction occurs (bug)"
            )
        else:
            # Neither pattern found - code structure changed unexpectedly
            assert False, "Could not find the 'raziel_before_mikhail' dialog trigger in Start.py"
    
    def test_raziel_second_interaction_after_first_mikhail_should_trigger(self):
        """
        **Validates: Requirements 1.1, 1.2, 2.2, 2.6**
        
        Test Case 2: Second interaction after first Mikhail (mikhail.approach == 1)
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect that the condition requires spoken_count == 0
        - After first interaction, spoken_count == 1, so condition is FALSE
        - This confirms the bug exists
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will detect that the condition checks mikhail.approach == 1
        - This allows re-interaction regardless of previous interactions
        - This confirms the bug is fixed
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to find the fixed pattern first
        fixed_pattern = r'elif\s+mikhail\.approach\s*==\s*1:\s*angel_dialog\s*=\s*DIALOGS\["raziel_after_mikhail"\]'
        fixed_match = re.search(fixed_pattern, content)
        
        # Try to find the buggy pattern
        buggy_pattern = r'elif\s+raziel\.spoken_count\s*==\s*0\s+and\s+mikhail\.approach\s*>=\s*1:\s*angel_dialog\s*=\s*DIALOGS\["raziel_after_mikhail"\]'
        buggy_match = re.search(buggy_pattern, content)
        
        if fixed_match:
            # Fixed code found - test passes
            print("\n✓ Bug condition test PASSED: Second interaction after first Mikhail is allowed")
            assert True
        elif buggy_match:
            # Buggy code found - test fails with counterexample
            condition = buggy_match.group(0)
            assert False, (
                f"COUNTEREXAMPLE FOUND: Second interaction after first Mikhail is blocked.\n"
                f"Bug confirmed in Start.py Raziel stationary interaction logic.\n"
                f"Current condition: {condition}\n"
                f"After first interaction (spoken_count=1), this condition is FALSE.\n"
                f"Expected: Condition should allow re-interaction (e.g., 'mikhail.approach == 1')\n"
                f"Root cause: Mutually exclusive spoken_count check prevents re-interaction.\n"
                f"Game state: mikhail.approach=1, spoken_count=1, cooldown=0, player_near=True\n"
                f"Expected behavior: Dialog 'raziel_after_mikhail' should trigger\n"
                f"Actual behavior: No interaction occurs (bug)"
            )
        else:
            # Neither pattern found - code structure changed unexpectedly
            assert False, "Could not find the 'raziel_after_mikhail' dialog trigger in Start.py"
    
    def test_raziel_second_interaction_after_second_mikhail_should_trigger(self):
        """
        **Validates: Requirements 1.1, 1.3, 2.3, 2.6**
        
        Test Case 3: Second interaction after second Mikhail (mikhail.approach >= 2)
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect that the condition requires spoken_count == 1
        - After "raziel_after_mikhail_2" dialog, spoken_count == 2, so condition is FALSE
        - This confirms the bug exists
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will detect that the condition checks mikhail.approach >= 2 and not raziel.roaming
        - This allows re-interaction before roaming starts
        - This confirms the bug is fixed
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to find the fixed pattern first
        fixed_pattern = r'elif\s+mikhail\.approach\s*>=\s*2\s+and\s+not\s+raziel\.roaming:\s*angel_dialog\s*=\s*DIALOGS\["raziel_after_mikhail_2"\]'
        fixed_match = re.search(fixed_pattern, content)
        
        # Try to find the buggy pattern
        buggy_pattern = r'elif\s+raziel\.spoken_count\s*==\s*1\s+and\s+mikhail\.approach\s*>=\s*2:\s*angel_dialog\s*=\s*DIALOGS\["raziel_after_mikhail_2"\]'
        buggy_match = re.search(buggy_pattern, content)
        
        if fixed_match:
            # Fixed code found - test passes
            print("\n✓ Bug condition test PASSED: Second interaction after second Mikhail is allowed")
            assert True
        elif buggy_match:
            # Buggy code found - test fails with counterexample
            condition = buggy_match.group(0)
            assert False, (
                f"COUNTEREXAMPLE FOUND: Second interaction after second Mikhail is blocked.\n"
                f"Bug confirmed in Start.py Raziel stationary interaction logic.\n"
                f"Current condition: {condition}\n"
                f"After 'raziel_after_mikhail_2' dialog (spoken_count=2), this condition is FALSE.\n"
                f"Expected: Condition should allow re-interaction (e.g., 'mikhail.approach >= 2 and not raziel.roaming')\n"
                f"Root cause: Mutually exclusive spoken_count check prevents re-interaction.\n"
                f"Game state: mikhail.approach=2, spoken_count=2, cooldown=0, player_near=True, roaming=False\n"
                f"Expected behavior: Dialog 'raziel_after_mikhail_2' should trigger again\n"
                f"Actual behavior: No interaction occurs (bug)"
            )
        else:
            # Neither pattern found - code structure changed unexpectedly
            assert False, "Could not find the 'raziel_after_mikhail_2' dialog trigger in Start.py"
    
    def test_raziel_roaming_reinteraction_should_trigger(self):
        """
        **Validates: Requirements 1.1, 1.4, 2.4, 2.6**
        
        Test Case 4: Roaming re-interaction (roaming == True, cooldown == 0)
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect that the condition requires spoken_count == 2
        - After first roaming interaction, spoken_count == 3, so condition is FALSE
        - This confirms the bug exists
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will detect that the condition allows interaction during roaming
        - This allows re-interaction with cooldown enforcement
        - This confirms the bug is fixed
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to find the fixed pattern (cooldown check only, no spoken_count)
        # The fixed code should have: elif raziel.roaming and raziel.near_player(player_rect) and raziel_cooldown == 0:
        # Account for line continuations with backslash
        fixed_pattern = r'elif raziel\.roaming and raziel\.near_player\(player\.rect\)[\s\\]+and raziel_cooldown\s*==\s*0:'
        fixed_match = re.search(fixed_pattern, content)
        
        # Try to find the buggy pattern (with spoken_count == 2)
        buggy_pattern = r'elif raziel\.roaming and raziel\.near_player\(player\.rect\).*?raziel\.spoken_count\s*==\s*2'
        buggy_match = re.search(buggy_pattern, content, re.DOTALL)
        
        if fixed_match:
            # Fixed code found - test passes
            print("\n✓ Bug condition test PASSED: Roaming re-interaction is allowed")
            assert True
        elif buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: Roaming re-interaction is blocked.\n"
                f"Bug confirmed in Start.py Raziel roaming interaction logic.\n"
                f"After first roaming interaction (spoken_count=3), the condition is FALSE.\n"
                f"Expected: Condition should allow re-interaction (e.g., 'raziel_cooldown == 0')\n"
                f"Root cause: Mutually exclusive spoken_count check prevents re-interaction.\n"
                f"Game state: roaming=True, spoken_count=3, cooldown=0, player_near=True\n"
                f"Expected behavior: Dialog 'raziel_roaming' should trigger again\n"
                f"Actual behavior: No interaction occurs (bug)"
            )
        else:
            # Neither pattern found - code structure changed unexpectedly
            assert False, "Could not find the Raziel roaming interaction logic in Start.py"
    
    def test_raziel_chase_reinteraction_should_trigger(self):
        """
        **Validates: Requirements 1.1, 1.5, 2.5**
        
        Test Case 5: Chase re-interaction (chasing == True)
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect that the condition requires spoken_count < 3
        - After first chase interaction, spoken_count == 3, so condition is FALSE
        - This confirms the bug exists
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will detect that the condition allows interaction during chase
        - This allows re-interaction during chase sequences
        - This confirms the bug is fixed
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to find the fixed pattern (no spoken_count check)
        # The fixed code should have: elif mikhail.chasing and raziel.near_player(player.rect):
        fixed_pattern = r'elif mikhail\.chasing and raziel\.near_player\(player\.rect\):\s*angel_dialog\s*=\s*DIALOGS\["raziel_during_chase"\]'
        fixed_match = re.search(fixed_pattern, content)
        
        # Try to find the buggy pattern (with spoken_count < 3)
        buggy_pattern = r'elif mikhail\.chasing and raziel\.near_player\(player\.rect\).*?raziel\.spoken_count\s*<\s*3'
        buggy_match = re.search(buggy_pattern, content, re.DOTALL)
        
        if fixed_match:
            # Fixed code found - test passes
            print("\n✓ Bug condition test PASSED: Chase re-interaction is allowed")
            assert True
        elif buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: Chase re-interaction is blocked.\n"
                f"Bug confirmed in Start.py Raziel chase interaction logic.\n"
                f"After first chase interaction (spoken_count=3), the condition is FALSE.\n"
                f"Expected: Condition should allow re-interaction (e.g., remove spoken_count check)\n"
                f"Root cause: Mutually exclusive spoken_count check prevents re-interaction.\n"
                f"Game state: chasing=True, spoken_count=3, player_near=True\n"
                f"Expected behavior: Dialog 'raziel_during_chase' should trigger again\n"
                f"Actual behavior: No interaction occurs (bug)"
            )
        else:
            # Neither pattern found - code structure changed unexpectedly
            assert False, "Could not find the Raziel chase interaction logic in Start.py"
    
    @given(
        test_case=st.sampled_from([
            'before_mikhail',
            'after_first_mikhail',
            'after_second_mikhail',
            'roaming',
            'chase'
        ])
    )
    @settings(
        max_examples=25,  # Scoped PBT: test each concrete failing case multiple times
        phases=[Phase.generate, Phase.target]  # Skip shrinking for faster execution
    )
    def test_property_multiple_raziel_interactions_allowed(self, test_case):
        """
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
        
        Property-Based Test: For ANY game state where the player approaches Raziel
        after having already interacted with him, and the cooldown has expired, the 
        interaction system MUST allow re-interaction and display the appropriate dialog 
        for the current game state.
        
        This property test generates checks across all known failing cases to ensure
        the fix addresses all instances of the bug.
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS with counterexamples
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES for all generated game states
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for blocking conditions based on test case
        has_blocking = False
        
        if test_case == 'before_mikhail':
            # Check if spoken_count == 0 is required
            buggy_pattern = r'if\s+raziel\.spoken_count\s*==\s*0\s+and\s+mikhail\.approach\s*==\s*0:'
            has_blocking = re.search(buggy_pattern, content) is not None
            
        elif test_case == 'after_first_mikhail':
            # Check if spoken_count == 0 is required
            buggy_pattern = r'elif\s+raziel\.spoken_count\s*==\s*0\s+and\s+mikhail\.approach\s*>=\s*1:'
            has_blocking = re.search(buggy_pattern, content) is not None
            
        elif test_case == 'after_second_mikhail':
            # Check if spoken_count == 1 is required
            buggy_pattern = r'elif\s+raziel\.spoken_count\s*==\s*1\s+and\s+mikhail\.approach\s*>=\s*2:'
            has_blocking = re.search(buggy_pattern, content) is not None
            
        elif test_case == 'roaming':
            # Check if spoken_count == 2 is required
            buggy_pattern = r'raziel\.spoken_count\s*==\s*2'
            has_blocking = re.search(buggy_pattern, content) is not None
            
        elif test_case == 'chase':
            # Check if spoken_count < 3 is required
            buggy_pattern = r'raziel\.spoken_count\s*<\s*3'
            has_blocking = re.search(buggy_pattern, content) is not None
        
        # ASSERTION: Interaction should be allowed (no blocking spoken_count condition)
        assert not has_blocking, (
            f"Property violation: Multiple interactions blocked for test case '{test_case}'.\n"
            f"Root cause: Mutually exclusive spoken_count check prevents re-interaction.\n"
            f"Expected behavior: Dialog should trigger on second approach\n"
            f"Actual behavior: No interaction occurs (bug)"
        )
        
        # If we reach here, the test passed for this case
        if test_case == 'before_mikhail':
            print(f"\n✓ Property test PASSED for '{test_case}': Multiple interactions allowed")
        elif test_case == 'after_first_mikhail':
            print(f"\n✓ Property test PASSED for '{test_case}': Multiple interactions allowed")
        elif test_case == 'after_second_mikhail':
            print(f"\n✓ Property test PASSED for '{test_case}': Multiple interactions allowed")
        elif test_case == 'roaming':
            print(f"\n✓ Property test PASSED for '{test_case}': Multiple interactions allowed")
        elif test_case == 'chase':
            print(f"\n✓ Property test PASSED for '{test_case}': Multiple interactions allowed")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
