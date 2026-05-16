# Bugfix Requirements Document

## Introduction

This document addresses a critical bug in the game's scene transition system where the game exits immediately after the prologue completes, instead of transitioning to the Start scene (Start.main()). This breaks the expected game flow and prevents players from progressing beyond the prologue sequence.

The bug occurs in MainMenuPage.py where, after the prologue finishes playing, the code calls `pygame.quit()` and `sys.exit()` instead of calling `Start.main()` to continue the game.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the user presses "Start" in the MainMenu and the prologue completes (either by playing through or skipping with ESC) THEN the system calls `pygame.quit()` and `sys.exit()`, terminating the entire game process

1.2 WHEN the prologue's `run()` method returns control to MainMenuPage.py THEN the system immediately executes the exit sequence instead of transitioning to the next scene

### Expected Behavior (Correct)

2.1 WHEN the user presses "Start" in the MainMenu and the prologue completes (either by playing through or skipping with ESC) THEN the system SHALL call `Start.main()` to transition to the Start scene

2.2 WHEN the prologue's `run()` method returns control to MainMenuPage.py THEN the system SHALL continue the game flow by invoking the Start scene's main function

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the user presses "Exit" in the MainMenu THEN the system SHALL CONTINUE TO call `pygame.quit()` and `sys.exit()` to properly close the game

3.2 WHEN the user presses ESC during the MainMenu (not during prologue) THEN the system SHALL CONTINUE TO call `pygame.quit()` and `sys.exit()` to properly close the game

3.3 WHEN the prologue is playing THEN the system SHALL CONTINUE TO support skipping with ESC and fast-forwarding with S key

3.4 WHEN the prologue completes THEN the system SHALL CONTINUE TO fade out the prologue music before transitioning

3.5 WHEN Start.main() is called THEN the system SHALL CONTINUE TO initialize the Start scene with all its components (player, angels, map, etc.)

## Bug Condition Analysis

### Bug Condition Function

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type GameTransition
  OUTPUT: boolean
  
  // Returns true when transitioning from Prologue to next scene
  RETURN X.current_scene = "Prologue" AND 
         X.prologue_completed = true AND
         X.next_scene = "Start"
END FUNCTION
```

### Property Specification

```pascal
// Property: Fix Checking - Proper Scene Transition
FOR ALL X WHERE isBugCondition(X) DO
  result ← handlePrologueCompletion'(X)
  ASSERT result.called_function = "Start.main()" AND
         result.game_continues = true AND
         NOT result.game_exited
END FOR
```

### Preservation Goal

```pascal
// Property: Preservation Checking - Other Exit Points Unchanged
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT handleMenuAction(X) = handleMenuAction'(X)
END FOR
```

This ensures that:
- **Fix Checking**: When the prologue completes, the game transitions to Start.main() instead of exiting
- **Preservation Checking**: All other exit points (Exit button, ESC in menu) continue to work as before

## Counterexample

**Concrete example demonstrating the bug:**

```python
# Current buggy code in MainMenuPage.py (lines 127-129):
elif btn["id"] == "start":
    pygame.mixer.music.fadeout(500)
    p = Prologue(screen, clock)
    p.run()
    pygame.quit()  # ← BUG: Game exits here
    sys.exit()     # ← BUG: Process terminates
```

**Expected flow:**
1. User clicks "Start" button
2. Prologue plays (with music, story slides, typewriter effect)
3. Prologue completes (user watches through or presses ESC)
4. **Should call**: `Start.main()` to continue the game
5. **Actually does**: Exits the entire game

**Result**: Player cannot progress beyond the prologue, breaking the entire game flow.
