# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Prologue Completion Exits Instead of Transitioning
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: For this deterministic bug, scope the property to the concrete failing case: clicking "Start" button, completing prologue, and observing the exit behavior
  - Test implementation details from Bug Condition in design:
    - Simulate clicking "Start" button in MainMenu
    - Run prologue to completion (or skip with ESC)
    - Verify that the game calls `Start.main()` instead of `pygame.quit()` and `sys.exit()`
  - The test assertions should match the Expected Behavior Properties from design:
    - `result.called_function = "Start.main()"`
    - `result.game_continues = true`
    - `NOT result.game_exited`
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found:
    - After prologue completes, `pygame.quit()` and `sys.exit()` are called instead of `Start.main()`
    - The game process terminates, preventing any further gameplay
    - Root cause confirmed: lines 128-129 in MainMenuPage.py contain incorrect exit logic
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Other Exit Points Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs:
    - Exit button clicks → observe `pygame.quit()` and `sys.exit()` are called
    - ESC key in MainMenu (not during prologue) → observe `pygame.quit()` and `sys.exit()` are called
    - Window close (X button) → observe `pygame.quit()` and `sys.exit()` are called
    - Button hover effects → observe visual feedback works correctly
    - Disabled "Characters" button → observe it's unclickable
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements:
    - For all menu interactions that are NOT "Start" button followed by prologue completion
    - Verify the same exit behavior occurs (Exit button, ESC, window close)
    - Verify the same UI behavior occurs (hover effects, disabled buttons)
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3. Fix for MainMenu→Prologue→Start transition bug

  - [x] 3.1 Implement the fix in MainMenuPage.py
    - Open MainMenuPage.py and locate the "start" button handler (lines 122-129)
    - Replace lines 128-129 (`pygame.quit()` and `sys.exit()`) with `Start.main()`
    - Verify the import statement `import Start` is present at line 3 (it already exists)
    - Keep the music fadeout at line 123 unchanged
    - Keep the prologue initialization and run at lines 124-126 unchanged
    - **Before**:
      ```python
      elif btn["id"] == "start":
           pygame.mixer.music.fadeout(500)
           p = Prologue(screen, clock)
           p.run()
           pygame.quit()  # ← REMOVE
           sys.exit()     # ← REMOVE
      ```
    - **After**:
      ```python
      elif btn["id"] == "start":
           pygame.mixer.music.fadeout(500)
           p = Prologue(screen, clock)
           p.run()
           Start.main()   # ← ADD: Continue to Start scene
      ```
    - _Bug_Condition: isBugCondition(input) where input.current_scene = "MainMenu" AND input.button_clicked = "start" AND input.prologue_completed = true AND input.next_scene = "Start"_
    - _Expected_Behavior: result.called_function = "Start.main()" AND result.game_continues = true AND NOT result.game_exited_
    - _Preservation: Exit button (lines 118-120) and ESC key handler (lines 113-115) must remain unchanged_
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Prologue Completion Transitions to Start Scene
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - Verify that:
      - After prologue completes, `Start.main()` is called
      - The game continues to the Start scene
      - `pygame.quit()` and `sys.exit()` are NOT called after prologue
    - _Requirements: 2.1, 2.2_

  - [x] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Other Exit Points Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix:
      - Exit button still calls `pygame.quit()` and `sys.exit()`
      - ESC key in MainMenu still calls `pygame.quit()` and `sys.exit()`
      - Window close still calls `pygame.quit()` and `sys.exit()`
      - Button hover effects still work correctly
      - Disabled "Characters" button is still unclickable
    - Verify no regressions in any non-buggy menu interactions

- [x] 4. Checkpoint - Ensure all tests pass
  - Run all tests (bug condition exploration + preservation tests)
  - Verify all tests pass
  - If any test fails, investigate and fix before proceeding
  - Ask the user if questions arise
