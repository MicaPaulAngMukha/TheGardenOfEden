# Raziel Interaction Fix - Bugfix Design

## Overview

The Raziel NPC interaction system currently uses a `spoken_count` variable with mutually exclusive conditional checks (== 0, == 1, == 2) that prevent re-interaction after the first dialog. Once `spoken_count` increments past a threshold, previous dialog conditions can never be true again, blocking the player from interacting with Raziel multiple times.

The fix will replace the `spoken_count` counter with a set-based tracking system that records which specific dialogs have been seen, while still allowing re-interaction. This preserves the dialog progression logic (showing different dialogs based on game state) while enabling multiple interactions throughout the game.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when a player approaches Raziel after the first interaction and the mutually exclusive `spoken_count` conditions prevent re-interaction
- **Property (P)**: The desired behavior - Raziel should be interactable multiple times, displaying appropriate dialog based on current game state
- **Preservation**: Existing dialog selection logic, roaming behavior, cooldown mechanics, and chase interactions that must remain unchanged by the fix
- **spoken_count**: The integer counter in `Start.py` that tracks Raziel interactions (currently blocks re-interaction)
- **mikhail.approach**: The counter that tracks how many times the player has approached Mikhail (determines game state)
- **raziel.roaming**: Boolean flag indicating whether Raziel is in roaming mode (triggered after "raziel_after_mikhail_2" dialog)
- **raziel_cooldown**: Timer that prevents immediate re-interaction (currently 240-300 frames)
- **chase_paused**: Boolean flag that pauses Mikhail's chase during Raziel dialog

## Bug Details

### Bug Condition

The bug manifests when a player approaches Raziel after having already interacted with him once. The interaction logic uses mutually exclusive conditions based on `spoken_count` values (== 0, == 1, == 2), which means once the counter increments, previous conditions can never be true again, permanently blocking re-interaction.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type GameState
  OUTPUT: boolean
  
  RETURN input.player_near_raziel == True
         AND input.raziel_cooldown == 0
         AND input.raziel.spoken_count > 0
         AND NOT any_dialog_triggered(input)
END FUNCTION

FUNCTION any_dialog_triggered(input)
  // Check if any of the existing conditional branches would trigger
  RETURN (input.raziel.spoken_count == 0 AND input.mikhail.approach == 0)
         OR (input.raziel.spoken_count == 0 AND input.mikhail.approach >= 1)
         OR (input.raziel.spoken_count == 1 AND input.mikhail.approach >= 2)
         OR (input.raziel.roaming AND input.raziel.spoken_count == 2)
         OR (input.mikhail.chasing AND input.raziel.spoken_count < 3)
END FUNCTION
```

### Examples

**Example 1: Second approach before Mikhail interaction**
- Player interacts with Raziel (spoken_count: 0 → 1, shows "raziel_before_mikhail")
- Player walks away and returns (spoken_count: 1, mikhail.approach: 0)
- Condition `raziel.spoken_count == 0 and mikhail.approach == 0` is FALSE
- **Expected**: Show "raziel_before_mikhail" again or allow interaction
- **Actual**: No interaction occurs (bug)

**Example 2: Third approach after first Mikhail interaction**
- Player talks to Mikhail once (mikhail.approach: 1)
- Player talks to Raziel (spoken_count: 0 → 1, shows "raziel_after_mikhail")
- Player returns to Raziel (spoken_count: 1, mikhail.approach: 1)
- Condition `raziel.spoken_count == 0 and mikhail.approach >= 1` is FALSE
- **Expected**: Show "raziel_after_mikhail" again or allow interaction
- **Actual**: No interaction occurs (bug)

**Example 3: Roaming re-interaction**
- Player triggers "raziel_after_mikhail_2" (spoken_count: 1 → 2, roaming starts)
- Player talks to roaming Raziel (spoken_count: 2 → 3, shows "raziel_roaming")
- Player returns after cooldown (spoken_count: 3, roaming: True, cooldown: 0)
- Condition `raziel.roaming and raziel.spoken_count == 2` is FALSE
- **Expected**: Show "raziel_roaming" again
- **Actual**: No interaction occurs (bug)

**Example 4: Chase interaction re-trigger**
- Mikhail is chasing, player talks to Raziel (spoken_count: 2 → 3, shows "raziel_during_chase")
- Player escapes, gets caught again, approaches Raziel during second chase
- Condition `mikhail.chasing and raziel.spoken_count < 3` is FALSE
- **Expected**: Show "raziel_during_chase" again
- **Actual**: No interaction occurs (bug)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Dialog selection logic must continue to display the correct dialog based on current game state (mikhail.approach count and chase status)
- Raziel must continue to start roaming after "raziel_after_mikhail_2" dialog
- The raziel_cooldown timer must continue to prevent immediate re-interaction (240-300 frames)
- Chase pausing during Raziel dialog must continue to work (`chase_paused = True`)
- Push mechanics after Raziel interactions must continue to apply correctly
- Dialog sequences must continue to return to STATE_EXPLORE correctly
- Roaming behavior (movement, target selection, looking animation) must remain unchanged

**Scope:**
All inputs that do NOT involve approaching Raziel for interaction should be completely unaffected by this fix. This includes:
- Mikhail interaction logic and chase mechanics
- Gate unlock and key pickup mechanics
- Player movement and collision detection
- All other game state transitions

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is:

1. **Mutually Exclusive Conditions**: The interaction logic uses exact equality checks on `spoken_count`:
   - `raziel.spoken_count == 0` (lines 920, 926)
   - `raziel.spoken_count == 1` (line 932)
   - `raziel.spoken_count == 2` (line 909)
   - `raziel.spoken_count < 3` (line 886)
   
   Once `spoken_count` increments past a value, conditions checking for that exact value can never be true again.

2. **Incremental Counter Design**: The variable is designed as a simple counter that only increases, never resets, and is used for both:
   - Tracking which dialog to show (state-based selection)
   - Preventing re-interaction (gate-keeping)
   
   This dual purpose creates the conflict.

3. **No Re-interaction Path**: There is no code path that allows re-interaction once a dialog has been seen. The conditions are designed to trigger exactly once per `spoken_count` value.

## Correctness Properties

Property 1: Bug Condition - Multiple Raziel Interactions

_For any_ game state where the player approaches Raziel after having already interacted with him at least once (spoken_count > 0), and the cooldown has expired (raziel_cooldown == 0), the fixed interaction system SHALL allow re-interaction and display the appropriate dialog for the current game state (based on mikhail.approach and chase status), rather than blocking interaction entirely.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

Property 2: Preservation - Dialog Selection Logic

_For any_ interaction with Raziel, the fixed code SHALL produce the same dialog selection behavior as the original code for the FIRST interaction in each game state, preserving the correct dialog display based on mikhail.approach count and chase status.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `Start.py`

**Class**: `Raziel` (lines 569-621)

**Specific Changes**:

1. **Replace spoken_count with dialog tracking set**:
   - Change `self.spoken_count = 0` to `self.seen_dialogs = set()`
   - This tracks which specific dialogs have been seen, not just a count

2. **Update Raziel stationary interaction logic** (lines 918-937):
   - Replace `raziel.spoken_count == 0 and mikhail.approach == 0` with:
     ```python
     mikhail.approach == 0
     ```
   - Replace `raziel.spoken_count == 0 and mikhail.approach >= 1` with:
     ```python
     mikhail.approach == 1
     ```
   - Replace `raziel.spoken_count == 1 and mikhail.approach >= 2` with:
     ```python
     mikhail.approach >= 2 and not raziel.roaming
     ```
   - Add dialog tracking: `raziel.seen_dialogs.add("raziel_before_mikhail")` etc.

3. **Update Raziel roaming interaction logic** (lines 907-915):
   - Replace `raziel.spoken_count == 2` with:
     ```python
     True  # Always allow interaction during roaming (cooldown already enforces delay)
     ```
   - Add dialog tracking: `raziel.seen_dialogs.add("raziel_roaming")`

4. **Update Raziel chase interaction logic** (lines 884-891):
   - Replace `raziel.spoken_count < 3` with:
     ```python
     True  # Always allow interaction during chase
     ```
   - Add dialog tracking: `raziel.seen_dialogs.add("raziel_during_chase")`

5. **Remove spoken_count increments**:
   - Remove all lines that increment `raziel.spoken_count`
   - Replace with `raziel.seen_dialogs.add(dialog_key)` where appropriate

### Implementation Strategy

The fix will use game state (mikhail.approach, raziel.roaming, mikhail.chasing) as the primary determinant for which dialog to show, rather than relying on spoken_count. The seen_dialogs set will be used for optional tracking/analytics but will not gate interactions.

**Dialog Selection Logic (Fixed):**
```
IF mikhail.chasing AND player_near_raziel:
    SHOW "raziel_during_chase"
ELSE IF raziel.roaming AND player_near_raziel AND cooldown == 0:
    SHOW "raziel_roaming"
ELSE IF NOT raziel.roaming AND player_near_raziel AND cooldown == 0:
    IF mikhail.approach >= 2:
        SHOW "raziel_after_mikhail_2"
        START roaming
    ELSE IF mikhail.approach >= 1:
        SHOW "raziel_after_mikhail"
    ELSE:
        SHOW "raziel_before_mikhail"
END IF
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that simulate multiple interactions with Raziel in various game states. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Second Interaction Before Mikhail**: Interact with Raziel twice before talking to Mikhail (will fail on unfixed code - second interaction blocked)
2. **Second Interaction After Mikhail**: Talk to Mikhail once, then interact with Raziel twice (will fail on unfixed code - second interaction blocked)
3. **Roaming Re-interaction**: Trigger roaming, interact with Raziel, wait for cooldown, interact again (will fail on unfixed code - second roaming interaction blocked)
4. **Chase Re-interaction**: Trigger chase, interact with Raziel during chase, escape and get chased again, interact again (will fail on unfixed code - second chase interaction blocked)

**Expected Counterexamples**:
- After first interaction, subsequent approaches to Raziel do not trigger any dialog
- Possible causes: mutually exclusive spoken_count conditions, no re-interaction code path

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL game_state WHERE isBugCondition(game_state) DO
  result := raziel_interaction_fixed(game_state)
  ASSERT dialog_triggered(result) == True
  ASSERT correct_dialog_for_state(result, game_state) == True
END FOR
```

**Property-Based Test Strategy:**
Generate random game states with:
- Random mikhail.approach values (0-5)
- Random raziel.roaming states (True/False)
- Random mikhail.chasing states (True/False)
- Random raziel_cooldown values (0, 100, 300)
- Random player positions (near/far from Raziel)

For each state where player is near Raziel and cooldown is 0, verify:
1. Interaction is allowed (dialog triggers)
2. Correct dialog is shown based on game state
3. Multiple interactions in the same state are allowed (after cooldown)

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL game_state WHERE NOT isBugCondition(game_state) DO
  ASSERT raziel_interaction_original(game_state) = raziel_interaction_fixed(game_state)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for the FIRST interaction in each game state, then write property-based tests capturing that behavior.

**Test Cases**:
1. **First Interaction Dialog Selection**: Observe that the first interaction in each game state shows the correct dialog on unfixed code, then verify this continues after fix
2. **Roaming Trigger**: Observe that "raziel_after_mikhail_2" triggers roaming on unfixed code, then verify this continues after fix
3. **Cooldown Enforcement**: Observe that cooldown prevents immediate re-interaction on unfixed code, then verify this continues after fix
4. **Chase Pausing**: Observe that chase pauses during Raziel dialog on unfixed code, then verify this continues after fix
5. **Push Mechanics**: Observe that push effect applies after Raziel dialog on unfixed code, then verify this continues after fix

### Unit Tests

- Test each dialog trigger condition in isolation (before Mikhail, after Mikhail, after second Mikhail, roaming, chase)
- Test cooldown enforcement (interaction blocked when cooldown > 0)
- Test roaming start trigger (after "raziel_after_mikhail_2")
- Test chase pause during dialog
- Test that player can interact multiple times in the same game state (after cooldown)
- Test edge cases (cooldown = 1, mikhail.approach = 0 vs 1 vs 2, roaming = True/False)

### Property-Based Tests

**Test 1: Multiple Interactions Allowed (Fix Checking)**
- Generate random game states with player near Raziel and cooldown = 0
- For each state, simulate interaction, reset cooldown to 0, simulate interaction again
- Verify both interactions trigger dialogs
- Verify dialogs are appropriate for game state

**Test 2: Dialog Selection Correctness (Fix Checking)**
- Generate random combinations of (mikhail.approach, raziel.roaming, mikhail.chasing)
- For each combination, simulate interaction
- Verify correct dialog is shown based on game state priority:
  1. Chase dialog if chasing
  2. Roaming dialog if roaming
  3. "raziel_after_mikhail_2" if approach >= 2 and not roaming
  4. "raziel_after_mikhail" if approach >= 1
  5. "raziel_before_mikhail" if approach == 0

**Test 3: First Interaction Preservation (Preservation Checking)**
- Generate random game states for FIRST interaction in each state
- Compare dialog shown by unfixed vs fixed code
- Verify they are identical

**Test 4: Roaming and Cooldown Preservation (Preservation Checking)**
- Generate random game states
- Simulate interactions and verify:
  - Roaming starts after "raziel_after_mikhail_2" (both versions)
  - Cooldown is set correctly (both versions)
  - Cooldown blocks interaction when > 0 (both versions)

### Integration Tests

- Test full game flow: start game, interact with Raziel multiple times before Mikhail, talk to Mikhail, interact with Raziel multiple times, talk to Mikhail again, interact with Raziel multiple times, trigger roaming, interact multiple times during roaming, trigger chase, interact during chase
- Test cooldown timing: interact, verify cooldown is set, wait for cooldown to expire, interact again
- Test dialog progression: verify correct dialog is shown at each stage of game progression
- Test roaming behavior: verify Raziel moves around after "raziel_after_mikhail_2" and continues to be interactable
- Test chase interaction: verify chase pauses during dialog and resumes after
