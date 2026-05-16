# MainMenu→Prologue→Start Transition Bugfix Design

## Overview

This design addresses a critical scene transition bug where the game exits immediately after the prologue completes, instead of transitioning to the Start scene. The bug is caused by incorrect exit logic in MainMenuPage.py that calls `pygame.quit()` and `sys.exit()` after the prologue finishes, rather than calling `Start.main()` to continue the game flow.

The fix is minimal and surgical: replace two lines of exit code with a single function call to `Start.main()`. This ensures the game continues to the next scene while preserving all other exit points (Exit button, ESC key in menu).

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when the prologue completes (either by playing through or skipping with ESC) and control returns to MainMenuPage.py
- **Property (P)**: The desired behavior when the prologue completes - the game should call `Start.main()` to transition to the Start scene
- **Preservation**: Existing exit behaviors (Exit button, ESC in menu) that must remain unchanged by the fix
- **MainMenuPage.py**: The main menu module located at the project root that handles menu interactions and scene transitions
- **Prologue.run()**: The blocking method in Prologue.py that plays the story sequence and returns control when complete
- **Start.main()**: The entry point function in Start.py that initializes and runs the Start scene (the first playable level with angels and the gate)
- **Scene Transition**: The handoff from one game scene to another by calling the next scene's main() function

## Bug Details

### Bug Condition

The bug manifests when the prologue completes (either by the player watching it through or pressing ESC to skip) and control returns to MainMenuPage.py. The code at lines 127-129 immediately calls `pygame.quit()` and `sys.exit()`, terminating the entire game process instead of transitioning to the Start scene.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type GameTransition
  OUTPUT: boolean
  
  RETURN input.current_scene = "MainMenu"
         AND input.button_clicked = "start"
         AND input.prologue_completed = true
         AND input.next_scene = "Start"
END FUNCTION
```

### Examples

**Example 1: Player watches prologue through**
- User clicks "Start" button in MainMenu
- Prologue plays all 15 slides with typewriter text and music
- Prologue completes naturally, `p.run()` returns
- **Expected**: Game calls `Start.main()` and player enters the Start scene
- **Actual**: Game calls `pygame.quit()` and `sys.exit()`, terminating the process

**Example 2: Player skips prologue with ESC**
- User clicks "Start" button in MainMenu
- Prologue begins playing
- User presses ESC to skip the prologue
- Prologue's `run()` method returns early
- **Expected**: Game calls `Start.main()` and player enters the Start scene
- **Actual**: Game calls `pygame.quit()` and `sys.exit()`, terminating the process

**Example 3: Player clicks Exit button (should still exit)**
- User clicks "Exit" button in MainMenu
- **Expected**: Game calls `pygame.quit()` and `sys.exit()`, terminating properly
- **Actual**: Same (this behavior must be preserved)

**Example 4: Player presses ESC in MainMenu (should still exit)**
- User is viewing the MainMenu (not in prologue)
- User presses ESC key
- **Expected**: Game calls `pygame.quit()` and `sys.exit()`, terminating properly
- **Actual**: Same (this behavior must be preserved)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Exit button functionality must continue to call `pygame.quit()` and `sys.exit()` to properly close the game
- ESC key during MainMenu (not during prologue) must continue to call `pygame.quit()` and `sys.exit()` to properly close the game
- Prologue's internal ESC handling (skipping the prologue) must continue to work as before
- Music fadeout before scene transitions must continue to work
- All other MainMenu interactions (hovering, disabled buttons) must remain unchanged

**Scope:**
All inputs that do NOT involve the "Start" button followed by prologue completion should be completely unaffected by this fix. This includes:
- Exit button clicks
- ESC key presses in the MainMenu
- Mouse hover effects on buttons
- Disabled "Characters" button behavior
- Window close (X button) behavior

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is clear:

1. **Copy-Paste Error**: The code at lines 127-129 in MainMenuPage.py appears to be copied from the Exit button handler (lines 123-124). The developer likely copied the exit logic and forgot to replace it with the correct scene transition call.

2. **Missing Scene Transition Call**: After `p.run()` completes at line 126, the code should call `Start.main()` to continue the game flow, but instead it calls the exit sequence.

3. **No Conditional Logic**: There is no conditional check to distinguish between "prologue completed successfully" and "user wants to exit". The code unconditionally exits after the prologue, regardless of how it completed.

The fix is straightforward: replace lines 128-129 (`pygame.quit()` and `sys.exit()`) with a single call to `Start.main()`.

## Correctness Properties

Property 1: Bug Condition - Prologue Completion Transitions to Start Scene

_For any_ game transition where the "Start" button is clicked and the prologue completes (either by playing through or skipping with ESC), the fixed MainMenuPage code SHALL call `Start.main()` to transition to the Start scene, allowing the game to continue.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Other Exit Points Unchanged

_For any_ menu interaction that is NOT the "Start" button followed by prologue completion (Exit button clicks, ESC in menu, window close), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing exit functionality.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

**File**: `MainMenuPage.py`

**Function**: `main()` (lines 109-131)

**Specific Changes**:

1. **Replace Exit Logic with Scene Transition**: In the "start" button handler (lines 122-129), replace the exit sequence with a call to `Start.main()`

   **Current Code (lines 122-129)**:
   ```python
   elif btn["id"] == "start":
        pygame.mixer.music.fadeout(500)
        p = Prologue(screen, clock)
        p.run()
        pygame.quit()  # ← REMOVE
        sys.exit()     # ← REMOVE
   ```

   **Fixed Code**:
   ```python
   elif btn["id"] == "start":
        pygame.mixer.music.fadeout(500)
        p = Prologue(screen, clock)
        p.run()
        Start.main()   # ← ADD: Continue to Start scene
   ```

2. **No Other Changes Required**: The Exit button handler (lines 118-120) and ESC key handler (lines 113-115) should remain unchanged, as they correctly exit the game.

3. **Import Already Present**: The `import Start` statement is already present at line 3, so no additional imports are needed.

### Implementation Notes

- The fix is a simple 2-line replacement: remove `pygame.quit()` and `sys.exit()`, add `Start.main()`
- The music fadeout at line 123 is correct and should remain
- The prologue's internal ESC handling (in Prologue.py) is correct and unaffected by this fix
- Start.main() will initialize its own music, screen state, and game loop
- The fix does not require any changes to Prologue.py or Start.py

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm that the game exits instead of transitioning to Start.main().

**Test Plan**: Write tests that simulate the "Start" button click, run the prologue, and observe what happens after the prologue completes. Run these tests on the UNFIXED code to observe the exit behavior and confirm the root cause.

**Test Cases**:
1. **Prologue Completion Test**: Simulate clicking "Start", let prologue complete naturally, verify game exits instead of calling Start.main() (will fail on unfixed code)
2. **Prologue Skip Test**: Simulate clicking "Start", skip prologue with ESC, verify game exits instead of calling Start.main() (will fail on unfixed code)
3. **Exit Button Test**: Simulate clicking "Exit", verify game exits properly (should pass on unfixed code)
4. **ESC in Menu Test**: Simulate pressing ESC in MainMenu, verify game exits properly (should pass on unfixed code)

**Expected Counterexamples**:
- After prologue completes, `pygame.quit()` and `sys.exit()` are called instead of `Start.main()`
- The game process terminates, preventing any further gameplay
- Root cause confirmed: lines 128-129 in MainMenuPage.py contain incorrect exit logic

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := handleStartButton_fixed(input)
  ASSERT result.called_function = "Start.main()"
  ASSERT result.game_continues = true
  ASSERT NOT result.game_exited
END FOR
```

**Testing Approach**: Property-based testing is recommended for fix checking because:
- It can generate various prologue completion scenarios (different skip timings, different user interactions)
- It provides strong guarantees that the transition works correctly across all valid inputs
- It catches edge cases like rapid button presses or unusual timing

**Test Plan**: After implementing the fix, write property-based tests that simulate the "Start" button click and prologue completion, then verify that `Start.main()` is called and the game continues.

**Test Cases**:
1. **Prologue Completion Transition**: Verify that after prologue completes naturally, `Start.main()` is called
2. **Prologue Skip Transition**: Verify that after prologue is skipped with ESC, `Start.main()` is called
3. **Start Scene Initialization**: Verify that Start.main() initializes the Start scene correctly (player, angels, map, music)
4. **No Premature Exit**: Verify that `pygame.quit()` and `sys.exit()` are NOT called after prologue completion

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT handleMenuAction_original(input) = handleMenuAction_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain (different button clicks, key presses, mouse positions)
- It catches edge cases that manual unit tests might miss (e.g., clicking disabled buttons, rapid clicks, unusual mouse positions)
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for Exit button, ESC key, and other interactions, then write property-based tests capturing that behavior. Verify the FIXED code produces identical results.

**Test Cases**:
1. **Exit Button Preservation**: Observe that Exit button calls `pygame.quit()` and `sys.exit()` on unfixed code, verify same behavior on fixed code
2. **ESC Key Preservation**: Observe that ESC in MainMenu calls `pygame.quit()` and `sys.exit()` on unfixed code, verify same behavior on fixed code
3. **Window Close Preservation**: Observe that window close (X button) calls `pygame.quit()` and `sys.exit()` on unfixed code, verify same behavior on fixed code
4. **Button Hover Preservation**: Observe that button hover effects work correctly on unfixed code, verify same behavior on fixed code
5. **Disabled Button Preservation**: Observe that "Characters" button is unclickable on unfixed code, verify same behavior on fixed code

### Unit Tests

- Test that clicking "Start" button triggers prologue playback
- Test that after prologue completes, `Start.main()` is called (not `pygame.quit()`)
- Test that clicking "Exit" button calls `pygame.quit()` and `sys.exit()`
- Test that pressing ESC in MainMenu calls `pygame.quit()` and `sys.exit()`
- Test that pressing ESC during prologue skips the prologue but still transitions to Start.main()
- Test that music fadeout occurs before prologue starts
- Test that Start.main() initializes the Start scene correctly

### Property-Based Tests

- Generate random menu interaction sequences and verify correct scene transitions
- Generate random prologue completion scenarios (different timings, skip vs. watch through) and verify Start.main() is always called
- Generate random exit scenarios (Exit button, ESC, window close) and verify game always exits properly
- Test that all non-Start button interactions continue to work across many scenarios

### Integration Tests

- Test full game flow: MainMenu → Start button → Prologue → Start scene
- Test prologue skip flow: MainMenu → Start button → Prologue (ESC) → Start scene
- Test exit flow: MainMenu → Exit button → game exits
- Test ESC exit flow: MainMenu → ESC key → game exits
- Test that Start scene loads correctly with all components (player, angels, map, music, HUD)
- Test that after entering Start scene, the game is fully playable (player can move, interact with angels, etc.)
