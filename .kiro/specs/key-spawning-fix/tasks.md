# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Key Available Before Chase Activation
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists (key assigned to bush at initialization)
  - **Scoped PBT Approach**: Scope the property to the concrete failing case - game initialization with mikhail.chasing=False
  - Test that when game initializes (bushes created, mikhail.chasing=False, player.has_key=False), NO bush should have has_key=True
  - The test assertions should match the Expected Behavior: key should NOT be available before chase activation
  - Bug Condition from design: `(ANY bush IN bushes WHERE bush["has_key"] == True) AND mikhail.chasing == False AND player.has_key == False`
  - Expected Behavior: Key should spawn only when mikhail.chasing becomes True for the first time
  - Run test on UNFIXED code (line 714 still assigns key at initialization)
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists: key is assigned at initialization)
  - Document counterexamples found: "At game initialization, one bush has has_key=True even though mikhail.chasing=False"
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Key Pickup, Gate Unlock, and Chase Mechanics
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (after key has been assigned)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements:
    - Key pickup detection using check_key_pickup(bushes) works correctly
    - Gate unlocking logic when player has key works correctly
    - Chase activation when mikhail.approach >= 3 works correctly
    - Music transition to "12. March of Iron.mp3" when chase activates works correctly
  - Property-based testing generates many test cases for stronger guarantees
  - Test cases to observe and encode:
    - For any player position near a bush with has_key=True, check_key_pickup() returns True
    - For any game state where player.has_key=True and player near gate, gate unlock prompt appears
    - For any game state where mikhail.approach >= 3, chase activates and music changes
  - Run tests on UNFIXED code (after manually setting has_key=True on a bush to simulate post-spawn state)
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 3. Fix key spawning to occur only after chase activation

  - [x] 3.1 Implement the fix in Start.py
    - Remove line 714: `random.choice(bushes)["has_key"] = True` (premature key assignment)
    - Add key_spawned flag after bushes initialization: `key_spawned = False`
    - Add key spawn logic in STATE_EXPLORE section of game loop:
      ```python
      # Spawn key when chase first activates
      if mikhail.chasing and not key_spawned:
          random.choice(bushes)["has_key"] = True
          key_spawned = True
      ```
    - Place spawn check after all dialog and interaction logic in STATE_EXPLORE
    - Ensure spawn logic runs in main game loop to catch chase activation regardless of trigger path
    - _Bug_Condition: isBugCondition(gameState) where (ANY bush IN bushes WHERE bush["has_key"] == True) AND mikhail.chasing == False_
    - _Expected_Behavior: Key spawns only when mikhail.chasing transitions from False to True for the first time_
    - _Preservation: Key pickup detection, gate unlocking, chase mechanics, music transitions remain unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Key Spawns Only After Chase Activation
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior (no key before chase)
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed: key no longer assigned at initialization)
    - Verify that key spawns correctly when mikhail.chasing becomes True
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Key Pickup, Gate Unlock, and Chase Mechanics
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix:
      - Key pickup detection works correctly after key spawns
      - Gate unlocking works correctly after key is picked up
      - Chase activation and music transition work correctly
    - Verify no regressions in Raziel interactions, player movement, or other game mechanics

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
  - Verify complete game flow: start game → approach Mikhail 3 times → chase activates → key spawns → find key → unlock gate
  - Confirm key is not available before chase activation
  - Confirm key spawns exactly once (does not respawn on subsequent game loop iterations)
