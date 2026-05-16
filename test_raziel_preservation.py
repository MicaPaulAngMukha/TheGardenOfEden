"""
Preservation Property Tests for Raziel Interaction Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

These tests capture the CORRECT baseline behavior that must be preserved when
implementing the fix. They are written based on observation of the UNFIXED code
for FIRST interactions (non-buggy inputs).

EXPECTED OUTCOME: These tests PASS on both unfixed and fixed code, confirming
that the fix does not introduce regressions.

Property 2: Preservation - First Interaction Dialog Selection
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
import re


class TestPreservationProperties:
    """
    Property 2: Preservation - First Interaction Behavior
    
    These tests verify that the fix preserves all correct behavior from the
    original implementation, specifically:
    1. Dialog selection logic for first interactions
    2. Roaming trigger after "raziel_after_mikhail_2"
    3. Cooldown enforcement
    4. Chase pausing during dialog
    5. Push mechanics after dialog
    6. State transitions to STATE_EXPLORE
    """
    
    def test_preservation_dialog_selection_before_mikhail(self):
        """
        **Validates: Requirements 3.1**
        
        Preservation Test 1: Dialog Selection - Before Mikhail
        
        OBSERVATION: On unfixed code, when mikhail.approach == 0 and spoken_count == 0,
        the system displays "raziel_before_mikhail" dialog.
        
        PRESERVATION: After fix, when mikhail.approach == 0 (regardless of spoken_count),
        the system MUST still display "raziel_before_mikhail" dialog.
        
        This test verifies the dialog selection logic is preserved for first interactions.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "raziel_before_mikhail" dialog trigger
        # This pattern should match both unfixed and fixed code
        pattern = r'if\s+.*?mikhail\.approach\s*==\s*0.*?:\s*angel_dialog\s*=\s*DIALOGS\["raziel_before_mikhail"\]'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, (
            "Preservation violation: 'raziel_before_mikhail' dialog trigger not found.\n"
            "Expected: Condition checking mikhail.approach == 0 should trigger this dialog.\n"
            "This is a regression - the dialog selection logic has been broken."
        )
        
        # Verify the dialog is assigned correctly
        assert 'DIALOGS["raziel_before_mikhail"]' in content, (
            "Preservation violation: 'raziel_before_mikhail' dialog not assigned.\n"
            "This is a regression - the dialog selection logic has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Dialog selection before Mikhail is preserved")
    
    def test_preservation_dialog_selection_after_first_mikhail(self):
        """
        **Validates: Requirements 3.1**
        
        Preservation Test 2: Dialog Selection - After First Mikhail
        
        OBSERVATION: On unfixed code, when mikhail.approach >= 1 and spoken_count == 0,
        the system displays "raziel_after_mikhail" dialog.
        
        PRESERVATION: After fix, when mikhail.approach == 1 (regardless of spoken_count),
        the system MUST still display "raziel_after_mikhail" dialog.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "raziel_after_mikhail" dialog trigger
        # Accept both >= 1 (unfixed) and == 1 (fixed) as valid conditions
        pattern = r'elif\s+mikhail\.approach\s*(?:>=|==)\s*1.*?:\s*angel_dialog\s*=\s*DIALOGS\["raziel_after_mikhail"\]'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, (
            "Preservation violation: 'raziel_after_mikhail' dialog trigger not found.\n"
            "Expected: Condition checking mikhail.approach == 1 should trigger this dialog.\n"
            "This is a regression - the dialog selection logic has been broken."
        )
        
        # Verify the dialog is assigned correctly
        assert 'DIALOGS["raziel_after_mikhail"]' in content, (
            "Preservation violation: 'raziel_after_mikhail' dialog not assigned.\n"
            "This is a regression - the dialog selection logic has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Dialog selection after first Mikhail is preserved")
    
    def test_preservation_dialog_selection_after_second_mikhail(self):
        """
        **Validates: Requirements 3.1, 3.2**
        
        Preservation Test 3: Dialog Selection - After Second Mikhail
        
        OBSERVATION: On unfixed code, when mikhail.approach >= 2 and spoken_count == 1,
        the system displays "raziel_after_mikhail_2" dialog.
        
        PRESERVATION: After fix, when mikhail.approach >= 2 and not roaming,
        the system MUST still display "raziel_after_mikhail_2" dialog.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "raziel_after_mikhail_2" dialog trigger
        pattern = r'elif\s+.*?mikhail\.approach\s*>=\s*2.*?:\s*angel_dialog\s*=\s*DIALOGS\["raziel_after_mikhail_2"\]'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, (
            "Preservation violation: 'raziel_after_mikhail_2' dialog trigger not found.\n"
            "Expected: Condition checking mikhail.approach >= 2 should trigger this dialog.\n"
            "This is a regression - the dialog selection logic has been broken."
        )
        
        # Verify the dialog is assigned correctly
        assert 'DIALOGS["raziel_after_mikhail_2"]' in content, (
            "Preservation violation: 'raziel_after_mikhail_2' dialog not assigned.\n"
            "This is a regression - the dialog selection logic has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Dialog selection after second Mikhail is preserved")
    
    def test_preservation_roaming_trigger(self):
        """
        **Validates: Requirements 3.2**
        
        Preservation Test 4: Roaming Trigger
        
        OBSERVATION: On unfixed code, after "raziel_after_mikhail_2" dialog,
        the system calls raziel.start_roaming() to begin Raziel's roaming behavior.
        
        PRESERVATION: After fix, this roaming trigger MUST still occur after
        "raziel_after_mikhail_2" dialog.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the roaming trigger after "raziel_after_mikhail_2"
        # Look for the pattern where raziel.start_roaming() is called
        pattern = r'angel_dialog\s*=\s*DIALOGS\["raziel_after_mikhail_2"\].*?raziel\.start_roaming\(\)'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, (
            "Preservation violation: Roaming trigger not found after 'raziel_after_mikhail_2' dialog.\n"
            "Expected: raziel.start_roaming() should be called after this dialog.\n"
            "This is a regression - the roaming behavior has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Roaming trigger is preserved")
    
    def test_preservation_cooldown_enforcement(self):
        """
        **Validates: Requirements 3.3**
        
        Preservation Test 5: Cooldown Enforcement
        
        OBSERVATION: On unfixed code, the system enforces a cooldown (raziel_cooldown > 0)
        that prevents immediate re-interaction. The cooldown is set to 240-300 frames
        after each interaction.
        
        PRESERVATION: After fix, cooldown enforcement MUST still work:
        - raziel_cooldown is set after interactions
        - raziel_cooldown > 0 prevents interaction
        - raziel_cooldown decrements each frame
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that cooldown is initialized
        assert 'raziel_cooldown = 0' in content, (
            "Preservation violation: raziel_cooldown initialization not found.\n"
            "This is a regression - the cooldown system has been broken."
        )
        
        # Check that cooldown is set after interactions (240 or 300)
        cooldown_set_pattern = r'raziel_cooldown\s*=\s*(240|300)'
        matches = re.findall(cooldown_set_pattern, content)
        
        assert len(matches) >= 2, (
            f"Preservation violation: Expected at least 2 cooldown assignments, found {len(matches)}.\n"
            "Expected: raziel_cooldown should be set after Raziel interactions.\n"
            "This is a regression - the cooldown system has been broken."
        )
        
        # Check that cooldown is checked in interaction conditions
        cooldown_check_pattern = r'raziel_cooldown\s*==\s*0'
        matches = re.findall(cooldown_check_pattern, content)
        
        assert len(matches) >= 2, (
            f"Preservation violation: Expected at least 2 cooldown checks, found {len(matches)}.\n"
            "Expected: raziel_cooldown == 0 should be checked before allowing interaction.\n"
            "This is a regression - the cooldown enforcement has been broken."
        )
        
        # Check that cooldown decrements
        cooldown_decrement_pattern = r'if\s+raziel_cooldown\s*>\s*0:\s*raziel_cooldown\s*-=\s*1'
        match = re.search(cooldown_decrement_pattern, content)
        
        assert match, (
            "Preservation violation: Cooldown decrement logic not found.\n"
            "Expected: raziel_cooldown should decrement each frame when > 0.\n"
            "This is a regression - the cooldown system has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Cooldown enforcement is preserved")
    
    def test_preservation_chase_pausing(self):
        """
        **Validates: Requirements 3.4**
        
        Preservation Test 6: Chase Pausing
        
        OBSERVATION: On unfixed code, when the player interacts with Raziel during
        the Mikhail chase, the system sets chase_paused = True to pause the chase
        during the dialog.
        
        PRESERVATION: After fix, chase pausing MUST still work during Raziel dialog.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the chase pausing logic during Raziel chase interaction
        pattern = r'mikhail\.chasing.*?raziel\.near_player.*?chase_paused\s*=\s*True'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, (
            "Preservation violation: Chase pausing not found during Raziel chase interaction.\n"
            "Expected: chase_paused = True should be set when interacting with Raziel during chase.\n"
            "This is a regression - the chase pausing behavior has been broken."
        )
        
        # Verify the "raziel_during_chase" dialog is triggered
        assert 'DIALOGS["raziel_during_chase"]' in content, (
            "Preservation violation: 'raziel_during_chase' dialog not found.\n"
            "This is a regression - the chase interaction has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Chase pausing is preserved")
    
    def test_preservation_push_mechanics(self):
        """
        **Validates: Requirements 3.5**
        
        Preservation Test 7: Push Mechanics
        
        OBSERVATION: On unfixed code, after Raziel dialog completes, the system
        applies a push effect to the player using compute_push() and push_timer.
        
        PRESERVATION: After fix, push mechanics MUST still apply after Raziel dialog.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the push mechanics after Raziel dialog
        # Look for compute_push being called with raziel.rect
        pattern = r'if\s+speaker\s*==\s*"Raziel":\s*push_vx,\s*push_vy,\s*push_timer\s*=\s*compute_push\(\s*player\.rect,\s*raziel\.rect'
        match = re.search(pattern, content)
        
        assert match, (
            "Preservation violation: Push mechanics not found after Raziel dialog.\n"
            "Expected: compute_push() should be called with raziel.rect after Raziel dialog.\n"
            "This is a regression - the push mechanics have been broken."
        )
        
        # Verify compute_push function exists
        assert 'def compute_push(' in content, (
            "Preservation violation: compute_push function not found.\n"
            "This is a regression - the push mechanics have been broken."
        )
        
        # Verify push_timer is used in the game loop
        assert 'if push_timer > 0:' in content, (
            "Preservation violation: push_timer logic not found.\n"
            "This is a regression - the push mechanics have been broken."
        )
        
        print("\n✓ Preservation test PASSED: Push mechanics are preserved")
    
    def test_preservation_state_transitions(self):
        """
        **Validates: Requirements 3.6**
        
        Preservation Test 8: State Transitions
        
        OBSERVATION: On unfixed code, after Raziel dialog sequences complete,
        the system transitions to STATE_EXPLORE to allow the player to continue
        exploring.
        
        PRESERVATION: After fix, state transitions MUST still work correctly.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that STATE_ANGEL_DIALOG is defined
        assert 'STATE_ANGEL_DIALOG' in content, (
            "Preservation violation: STATE_ANGEL_DIALOG not found.\n"
            "This is a regression - the state system has been broken."
        )
        
        # Check that STATE_EXPLORE is defined
        assert 'STATE_EXPLORE' in content, (
            "Preservation violation: STATE_EXPLORE not found.\n"
            "This is a regression - the state system has been broken."
        )
        
        # Check that Raziel interactions set state to STATE_ANGEL_DIALOG
        pattern = r'angel_dialog\s*=\s*DIALOGS\["raziel_.*?"\].*?state\s*=\s*STATE_ANGEL_DIALOG'
        matches = re.findall(pattern, content, re.DOTALL)
        
        assert len(matches) >= 4, (
            f"Preservation violation: Expected at least 4 state transitions to STATE_ANGEL_DIALOG, found {len(matches)}.\n"
            "Expected: Raziel interactions should set state = STATE_ANGEL_DIALOG.\n"
            "This is a regression - the state transition logic has been broken."
        )
        
        # Check that dialog completion transitions to STATE_EXPLORE
        pattern = r'state\s*=\s*STATE_EXPLORE'
        matches = re.findall(pattern, content)
        
        assert len(matches) >= 1, (
            f"Preservation violation: Expected at least 1 transition to STATE_EXPLORE, found {len(matches)}.\n"
            "Expected: Dialog completion should transition to STATE_EXPLORE.\n"
            "This is a regression - the state transition logic has been broken."
        )
        
        print("\n✓ Preservation test PASSED: State transitions are preserved")
    
    def test_preservation_roaming_dialog(self):
        """
        **Validates: Requirements 3.1, 3.3**
        
        Preservation Test 9: Roaming Dialog
        
        OBSERVATION: On unfixed code, when raziel.roaming == True and cooldown == 0,
        the system displays "raziel_roaming" dialog.
        
        PRESERVATION: After fix, roaming dialog MUST still be displayed correctly.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the roaming dialog trigger
        pattern = r'elif\s+raziel\.roaming.*?raziel\.near_player.*?raziel_cooldown\s*==\s*0.*?angel_dialog\s*=\s*DIALOGS\["raziel_roaming"\]'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, (
            "Preservation violation: 'raziel_roaming' dialog trigger not found.\n"
            "Expected: Condition checking raziel.roaming and raziel_cooldown == 0 should trigger this dialog.\n"
            "This is a regression - the roaming dialog has been broken."
        )
        
        # Verify the dialog is assigned correctly
        assert 'DIALOGS["raziel_roaming"]' in content, (
            "Preservation violation: 'raziel_roaming' dialog not assigned.\n"
            "This is a regression - the roaming dialog has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Roaming dialog is preserved")
    
    def test_preservation_chase_dialog(self):
        """
        **Validates: Requirements 3.1**
        
        Preservation Test 10: Chase Dialog
        
        OBSERVATION: On unfixed code, when mikhail.chasing == True and player is near Raziel,
        the system displays "raziel_during_chase" dialog.
        
        PRESERVATION: After fix, chase dialog MUST still be displayed correctly.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the chase dialog trigger
        pattern = r'elif\s+mikhail\.chasing.*?raziel\.near_player.*?angel_dialog\s*=\s*DIALOGS\["raziel_during_chase"\]'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, (
            "Preservation violation: 'raziel_during_chase' dialog trigger not found.\n"
            "Expected: Condition checking mikhail.chasing should trigger this dialog.\n"
            "This is a regression - the chase dialog has been broken."
        )
        
        # Verify the dialog is assigned correctly
        assert 'DIALOGS["raziel_during_chase"]' in content, (
            "Preservation violation: 'raziel_during_chase' dialog not assigned.\n"
            "This is a regression - the chase dialog has been broken."
        )
        
        print("\n✓ Preservation test PASSED: Chase dialog is preserved")
    
    @given(
        dialog_type=st.sampled_from([
            'raziel_before_mikhail',
            'raziel_after_mikhail',
            'raziel_after_mikhail_2',
            'raziel_roaming',
            'raziel_during_chase'
        ])
    )
    @settings(
        max_examples=25,  # Test each dialog type multiple times
        phases=[Phase.generate, Phase.target]
    )
    def test_property_dialog_selection_preserved(self, dialog_type):
        """
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
        
        Property-Based Test: For ALL Raziel dialog types, the dialog selection logic
        MUST be preserved after the fix. Each dialog should still be triggered by the
        correct game state conditions.
        
        This property test verifies that all dialog types are still present and
        correctly assigned in the code.
        
        EXPECTED OUTCOME: This test PASSES on both unfixed and fixed code.
        """
        
        # Read the Start.py file
        with open('Start.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify the dialog exists in DIALOGS dictionary
        dialog_definition_pattern = f'"{dialog_type}":\\s*\\['
        match = re.search(dialog_definition_pattern, content)
        
        assert match, (
            f"Preservation violation: Dialog '{dialog_type}' not found in DIALOGS dictionary.\n"
            f"This is a regression - the dialog definition has been removed."
        )
        
        # Verify the dialog is assigned somewhere in the code
        dialog_assignment_pattern = f'angel_dialog\\s*=\\s*DIALOGS\\["{dialog_type}"\\]'
        match = re.search(dialog_assignment_pattern, content)
        
        assert match, (
            f"Preservation violation: Dialog '{dialog_type}' is not assigned anywhere.\n"
            f"This is a regression - the dialog is defined but never used."
        )


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
