# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Multiple Raziel Interactions Blocked
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: For deterministic bugs, scope the property to the concrete failing case(s) to ensure reproducibility
  - Test implementation details from Bug Condition in design:
    - Simulate game state where player approaches Raziel after first interaction (spoken_count > 0)
    - Verify cooldown has expired (raziel_cooldown == 0)
    - Attempt second interaction
    - Assert that dialog triggers (expected behavior)
  - Test cases to cover:
    1. Second interaction before Mikhail (mikhail.approach == 0, spoken_count == 1)
    2. Second interaction after first Mikhail (mikhail.approach == 1, spoken_count == 1)
    3. Second interaction after second Mikhail (mikhail.approach >= 2, spoken_count == 2)
    4. Roaming re-interaction (roaming == True, spoken_count == 3, cooldown == 0)
    5. Chase re-interaction (chasing == True, spoken_count == 3)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found:
    - Which game states fail to trigger dialog on second interaction
    - Specific spoken_count values that block re-interaction
    - Mutually exclusive conditions that prevent dialog triggers
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - First Interaction Dialog Selection
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (first interactions)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements:
    1. **Dialog Selection**: First interaction in each game state shows correct dialog
       - mikhail.approach == 0 → "raziel_before_mikhail"
       - mikhail.approach == 1 → "raziel_after_mikhail"
       - mikhail.approach >= 2 and not roaming → "raziel_after_mikhail_2"
       - roaming == True → "raziel_roaming"
       - chasing == True → "raziel_during_chase"
    2. **Roaming Trigger**: "raziel_after_mikhail_2" dialog starts Raziel roaming
    3. **Cooldown Enforcement**: raziel_cooldown > 0 prevents interaction
    4. **Chase Pausing**: chase_paused == True during Raziel dialog when chasing
    5. **Push Mechanics**: Push effect applies after Raziel dialog (push_timer > 0)
    6. **State Transitions**: Dialog sequences return to STATE_EXPLORE correctly
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 3. Fix for Raziel re-interaction blocking

  - [x] 3.1 Replace spoken_count with seen_dialogs set in Raziel class
    - In `Start.py`, class `Raziel.__init__` (around line 576)
    - Replace `self.spoken_count = 0` with `self.seen_dialogs = set()`
    - This tracks which specific dialogs have been seen, not just a count
    - _Bug_Condition: isBugCondition(input) where input.raziel.spoken_count > 0 AND input.player_near_raziel == True AND input.raziel_cooldown == 0_
    - _Expected_Behavior: Allow re-interaction and display appropriate dialog based on game state (mikhail.approach, raziel.roaming, mikhail.chasing)_
    - _Preservation: Dialog selection logic, roaming behavior, cooldown mechanics, chase interactions_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 3.2 Update Raziel chase interaction logic
    - In `Start.py`, around lines 884-891
    - Replace condition `raziel.spoken_count < 3` with `True` (always allow interaction during chase)
    - Replace `raziel.spoken_count = 3` with `raziel.seen_dialogs.add("raziel_during_chase")`
    - This allows multiple interactions during chase sequences
    - _Bug_Condition: Chase re-interaction blocked when spoken_count >= 3_
    - _Expected_Behavior: Allow interaction during chase regardless of previous interactions_
    - _Preservation: Chase pausing, dialog display, state transitions_
    - _Requirements: 2.5, 2.6, 3.4_

  - [x] 3.3 Update Raziel roaming interaction logic
    - In `Start.py`, around lines 907-915
    - Replace condition `raziel.spoken_count == 2` with `True` (cooldown already enforces delay)
    - Replace `raziel.spoken_count = 3` with `raziel.seen_dialogs.add("raziel_roaming")`
    - This allows multiple interactions during roaming (cooldown still prevents spam)
    - _Bug_Condition: Roaming re-interaction blocked when spoken_count != 2_
    - _Expected_Behavior: Allow interaction during roaming with cooldown enforcement_
    - _Preservation: Cooldown enforcement, roaming behavior, push mechanics_
    - _Requirements: 2.4, 2.6, 3.3, 3.5_

  - [x] 3.4 Update Raziel stationary interaction logic (before Mikhail)
    - In `Start.py`, around lines 918-924
    - Replace condition `raziel.spoken_count == 0 and mikhail.approach == 0` with `mikhail.approach == 0`
    - Replace `raziel.spoken_count = 1` with `raziel.seen_dialogs.add("raziel_before_mikhail")`
    - This allows multiple interactions before talking to Mikhail
    - _Bug_Condition: Re-interaction blocked when spoken_count > 0_
    - _Expected_Behavior: Allow interaction before Mikhail regardless of previous interactions_
    - _Preservation: Dialog selection, cooldown enforcement_
    - _Requirements: 2.1, 2.6, 3.1_

  - [x] 3.5 Update Raziel stationary interaction logic (after first Mikhail)
    - In `Start.py`, around lines 925-930
    - Replace condition `raziel.spoken_count == 0 and mikhail.approach >= 1` with `mikhail.approach == 1`
    - Replace `raziel.spoken_count = 1` with `raziel.seen_dialogs.add("raziel_after_mikhail")`
    - This allows multiple interactions after first Mikhail approach
    - _Bug_Condition: Re-interaction blocked when spoken_count > 0_
    - _Expected_Behavior: Allow interaction after first Mikhail regardless of previous interactions_
    - _Preservation: Dialog selection, cooldown enforcement_
    - _Requirements: 2.2, 2.6, 3.1_

  - [x] 3.6 Update Raziel stationary interaction logic (after second Mikhail)
    - In `Start.py`, around lines 931-937
    - Replace condition `raziel.spoken_count == 1 and mikhail.approach >= 2` with `mikhail.approach >= 2 and not raziel.roaming`
    - Replace `raziel.spoken_count = 2` with `raziel.seen_dialogs.add("raziel_after_mikhail_2")`
    - This allows multiple interactions after second Mikhail approach (before roaming starts)
    - _Bug_Condition: Re-interaction blocked when spoken_count != 1_
    - _Expected_Behavior: Allow interaction after second Mikhail until roaming starts_
    - _Preservation: Dialog selection, roaming trigger, cooldown enforcement_
    - _Requirements: 2.3, 2.6, 3.1, 3.2_

  - [x] 3.7 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Multiple Raziel Interactions Allowed
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - Verify all test cases now allow re-interaction:
      1. Second interaction before Mikhail works
      2. Second interaction after first Mikhail works
      3. Second interaction after second Mikhail works
      4. Roaming re-interaction works
      5. Chase re-interaction works
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 3.8 Verify preservation tests still pass
    - **Property 2: Preservation** - First Interaction Behavior Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all preservation requirements still hold:
      1. Dialog selection logic unchanged for first interactions
      2. Roaming trigger still works after "raziel_after_mikhail_2"
      3. Cooldown enforcement still prevents spam
      4. Chase pausing still works during dialog
      5. Push mechanics still apply after dialog
      6. State transitions still work correctly

- [x] 4. Checkpoint - Ensure all tests pass
  - Run all tests (bug condition + preservation)
  - Verify no regressions in other game systems (Mikhail interactions, gate mechanics, player movement)
  - Test full game flow manually if possible:
    1. Start game, interact with Raziel multiple times before Mikhail
    2. Talk to Mikhail, interact with Raziel multiple times
    3. Talk to Mikhail again, interact with Raziel multiple times
    4. Wait for roaming to start, interact with Raziel multiple times during roaming
    5. Trigger chase, interact with Raziel during chase
  - Ensure all tests pass, ask the user if questions arise
