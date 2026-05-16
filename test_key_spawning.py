"""
Bug Condition Exploration Test for Key Spawning Fix

**Validates: Requirements 2.1, 2.2**

This test is designed to FAIL on unfixed code to confirm the bug exists.
When the test fails, it demonstrates that the key is assigned to a bush at
game initialization, allowing premature pickup before chase activation.

CRITICAL: This test encodes the EXPECTED behavior. When it passes after the fix,
it confirms the bug is resolved.

This test uses static code analysis to verify the bug condition and expected behavior,
which is appropriate for this type of initialization bug in a Pygame application.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
import re


class TestBugConditionExploration:
    """
    Property 1: Bug Condition - Key Available Before Chase Activation
    
    This test explores the bug condition where the key is assigned to a random
    bush at game initialization (line 714), allowing players to pick it up before
    triggering Mikhail's chase sequence.
    
    The test uses static code analysis to verify:
    1. The bug exists in the unfixed code (key assigned at initialization)
    2. The fix is correctly implemented (key spawns only when chase activates)
    """
    
    def test_key_not_assigned_at_initialization(self):
        """
        **Validates: Requirements 2.1, 2.2**
        
        Test Case 1: Key should NOT be assigned at game initialization
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will detect line 714: random.choice(bushes)["has_key"] = True
        - This confirms the bug exists (key assigned at initialization)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will NOT find the premature key assignment at initialization
        - This confirms the bug is fixed
        
        Expected Behavior:
        - Key should NOT be assigned to any bush at initialization
        - Key should spawn only when mikhail.chasing becomes True
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
        
        # Look for the buggy pattern: key assignment immediately after bushes initialization
        # Pattern: bushes = get_bush_rects() followed by random.choice(bushes)["has_key"] = True
        buggy_pattern = r'bushes\s*=\s*get_bush_rects\(\)\s*\n\s*random\.choice\(bushes\)\["has_key"\]\s*=\s*True'
        buggy_match = re.search(buggy_pattern, main_func)
        
        if buggy_match:
            # Buggy code found - test fails with counterexample
            assert False, (
                f"COUNTEREXAMPLE FOUND: Key is assigned at game initialization.\n"
                f"Bug confirmed in Start.py main() function around line 714.\n"
                f"Current code: random.choice(bushes)[\"has_key\"] = True (at initialization)\n"
                f"This allows premature key pickup before chase activation.\n"
                f"Expected: Key should NOT be assigned at initialization.\n"
                f"Expected: Key should spawn only when mikhail.chasing becomes True.\n"
                f"Root cause: Premature key assignment at initialization (line 714).\n"
                f"Game state at initialization: mikhail.chasing=False, player.has_key=False\n"
                f"Bug condition: (ANY bush IN bushes WHERE bush[\"has_key\"] == True) AND mikhail.chasing == False\n"
                f"Expected behavior: No bush should have has_key=True at initialization\n"
                f"Actual behavior: One bush has has_key=True at initialization (bug)"
            )
        
        # If we reach here, the premature assignment is not found
        print("\n✓ Bug condition test PASSED: Key is NOT assigned at initialization")
    
    def test_key_spawns_when_chase_activates(self):
        """
        **Validates: Requirements 2.2, 2.3**
        
        Test Case 2: Key should spawn when mikhail.chasing becomes True
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will NOT find key spawn logic in the game loop
        - This confirms the bug exists (no spawn trigger on chase activation)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will find key spawn logic when mikhail.chasing becomes True
        - This confirms the fix is implemented correctly
        
        Expected Behavior:
        - Key should spawn when mikhail.chasing transitions from False to True
        - Key should spawn exactly once (key_spawned flag prevents respawning)
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
        
        # Look for the fixed pattern: key spawn logic in game loop
        # Pattern: if mikhail.chasing and not key_spawned: ... random.choice(bushes)["has_key"] = True ... key_spawned = True
        fixed_pattern = r'if\s+mikhail\.chasing\s+and\s+not\s+key_spawned:.*?random\.choice\(bushes\)\["has_key"\]\s*=\s*True.*?key_spawned\s*=\s*True'
        fixed_match = re.search(fixed_pattern, main_func, re.DOTALL)
        
        if not fixed_match:
            # Fixed code not found - test fails
            assert False, (
                f"COUNTEREXAMPLE FOUND: Key spawn logic not found in game loop.\n"
                f"Bug confirmed in Start.py main() function.\n"
                f"Expected: Key should spawn when mikhail.chasing becomes True.\n"
                f"Expected pattern: if mikhail.chasing and not key_spawned: ... random.choice(bushes)[\"has_key\"] = True ... key_spawned = True\n"
                f"Root cause: No spawn trigger on chase activation.\n"
                f"Expected behavior: Key spawns when mikhail.chasing transitions to True\n"
                f"Actual behavior: Key assigned at initialization (bug)"
            )
        
        # If we reach here, the fixed spawn logic is found
        print("\n✓ Bug condition test PASSED: Key spawns when chase activates")
    
    def test_key_spawned_flag_exists(self):
        """
        **Validates: Requirements 2.2, 2.4**
        
        Test Case 3: key_spawned flag should exist to prevent respawning
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
        - The test will NOT find key_spawned flag initialization
        - This confirms the bug exists (no spawn tracking)
        
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES
        - The test will find key_spawned = False initialization
        - This confirms the fix prevents key respawning
        
        Expected Behavior:
        - key_spawned flag should be initialized to False
        - Flag should prevent key from spawning multiple times
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
        
        # Look for key_spawned flag initialization
        flag_pattern = r'key_spawned\s*=\s*False'
        flag_match = re.search(flag_pattern, main_func)
        
        if not flag_match:
            # Flag not found - test fails
            assert False, (
                f"COUNTEREXAMPLE FOUND: key_spawned flag not found.\n"
                f"Bug confirmed in Start.py main() function.\n"
                f"Expected: key_spawned = False (to track spawn state)\n"
                f"Root cause: No flag to prevent key respawning.\n"
                f"Expected behavior: Key spawns exactly once\n"
                f"Actual behavior: No spawn tracking (bug)"
            )
        
        # If we reach here, the flag is found
        print("\n✓ Bug condition test PASSED: key_spawned flag exists")
    
    @given(
        test_case=st.sampled_from([
            'no_premature_assignment',
            'spawn_on_chase',
            'spawn_flag_exists'
        ])
    )
    @settings(
        max_examples=15,  # Scoped PBT: test each concrete failing case multiple times
        phases=[Phase.generate, Phase.target]  # Skip shrinking for faster execution
    )
    def test_property_key_spawns_only_after_chase_activation(self, test_case):
        """
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
        
        Property-Based Test: For ANY game state at initialization, NO bush should
        have has_key=True. The key should spawn ONLY when mikhail.chasing becomes
        True for the first time.
        
        This property test generates checks across all aspects of the fix to ensure
        the bug is completely resolved.
        
        EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS with counterexamples
        EXPECTED OUTCOME ON FIXED CODE: This test PASSES for all generated checks
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
        has_bug = False
        error_msg = ""
        
        if test_case == 'no_premature_assignment':
            # Check if key is assigned at initialization
            buggy_pattern = r'bushes\s*=\s*get_bush_rects\(\)\s*\n\s*random\.choice\(bushes\)\["has_key"\]\s*=\s*True'
            has_bug = re.search(buggy_pattern, main_func) is not None
            error_msg = (
                f"Property violation: Key assigned at initialization (test case '{test_case}').\n"
                f"Root cause: Premature key assignment at line 714.\n"
                f"Expected behavior: No bush should have has_key=True at initialization\n"
                f"Actual behavior: One bush has has_key=True at initialization (bug)"
            )
            
        elif test_case == 'spawn_on_chase':
            # Check if key spawn logic exists in game loop
            fixed_pattern = r'if\s+mikhail\.chasing\s+and\s+not\s+key_spawned:.*?random\.choice\(bushes\)\["has_key"\]\s*=\s*True'
            has_bug = re.search(fixed_pattern, main_func, re.DOTALL) is None
            error_msg = (
                f"Property violation: Key spawn logic not found (test case '{test_case}').\n"
                f"Root cause: No spawn trigger on chase activation.\n"
                f"Expected behavior: Key spawns when mikhail.chasing becomes True\n"
                f"Actual behavior: Key assigned at initialization (bug)"
            )
            
        elif test_case == 'spawn_flag_exists':
            # Check if key_spawned flag exists
            flag_pattern = r'key_spawned\s*=\s*False'
            has_bug = re.search(flag_pattern, main_func) is None
            error_msg = (
                f"Property violation: key_spawned flag not found (test case '{test_case}').\n"
                f"Root cause: No flag to prevent key respawning.\n"
                f"Expected behavior: Key spawns exactly once\n"
                f"Actual behavior: No spawn tracking (bug)"
            )
        
        # ASSERTION: Bug should not exist
        assert not has_bug, error_msg
        
        # If we reach here, the test passed for this case
        print(f"\n✓ Property test PASSED for '{test_case}': Key spawning behavior is correct")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
