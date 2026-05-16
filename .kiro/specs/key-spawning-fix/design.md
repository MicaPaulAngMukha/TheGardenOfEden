# Key Spawning Fix Bugfix Design

## Overview

The key spawning bug allows players to find and pick up the key before Mikhail begins chasing them, breaking the intended gameplay flow. The key is currently assigned to a random bush at game initialization (line 714), but should only spawn when `mikhail.chasing` becomes `True` for the first time. This fix will delay key spawning until chase activation, add a flag to ensure the key spawns only once, and preserve all existing key pickup, gate unlocking, and chase mechanics.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when the game initializes and assigns the key immediately, allowing premature pickup before chase activation
- **Property (P)**: The desired behavior - key should spawn only when `mikhail.chasing` becomes `True` for the first time
- **Preservation**: Existing key pickup detection, gate unlocking, chase mechanics, and music transitions that must remain unchanged by the fix
- **mikhail.chasing**: Boolean attribute on the Mikhail instance that indicates whether Mikhail is actively chasing the player
- **bushes**: List of dictionaries containing bush rectangles and `has_key` boolean flags
- **key_spawned**: New flag to track whether the key has been spawned (to ensure it only spawns once)

## Bug Details

### Bug Condition

The bug manifests when the game initializes and immediately assigns the key to a random bush (line 714: `random.choice(bushes)["has_key"] = True`). This allows the player to walk near bushes and pick up the key before triggering Mikhail's chase sequence (which activates when `mikhail.approach >= 3`). The key pickup logic in `player.check_key_pickup(bushes)` works correctly, but it operates on bushes that already have the key assigned prematurely.

**Formal Specification:**
```
FUNCTION isBugCondition(gameState)
  INPUT: gameState containing bushes list, mikhail.chasing, player.has_key
  OUTPUT: boolean
  
  RETURN (ANY bush IN bushes WHERE bush["has_key"] == True)
         AND mikhail.chasing == False
         AND player.has_key == False
END FUNCTION
```

### Examples

- **Example 1**: Player starts game, walks to bushes near spawn point, finds key before ever approaching Mikhail → Key should not be available yet
- **Example 2**: Player approaches Mikhail once (approach=1), walks away to bushes, finds key → Key should not be available yet
- **Example 3**: Player approaches Mikhail twice (approach=2), walks away to bushes, finds key → Key should not be available yet
- **Example 4**: Player approaches Mikhail three times (approach=3), chase activates, player walks to bushes and finds key → Key should be available (correct behavior)
- **Edge Case**: Player triggers chase (approach=3), key spawns in random bush, player picks up key, then dies and respawns → Key should remain picked up (not respawn)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Key pickup detection using `player.check_key_pickup(bushes)` must continue to work exactly as before
- Gate unlocking logic when player has key and presses 'y' at gate must remain unchanged
- Chase activation when `mikhail.approach >= 3` must remain unchanged
- Music transition to "12. March of Iron.mp3" when chase activates must remain unchanged
- Player respawn after being hit by Mikhail must continue to work
- All Raziel interactions and dialog triggers must remain unaffected

**Scope:**
All game mechanics that do NOT involve the initial key assignment should be completely unaffected by this fix. This includes:
- Player movement and collision with bushes
- Mikhail's chase behavior and collision detection
- Raziel's roaming and dialog interactions
- Gate proximity detection and dialog triggers
- Player lives and game over logic

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is clear:

1. **Premature Key Assignment**: Line 714 in `main()` executes `random.choice(bushes)["has_key"] = True` immediately after `bushes = get_bush_rects()`, before the game loop begins. This assigns the key to a random bush at initialization time.

2. **No Spawn Trigger**: There is no code that checks when `mikhail.chasing` becomes `True` and spawns the key at that moment. The key assignment is a one-time operation at startup.

3. **Missing Spawn Flag**: There is no flag to track whether the key has already been spawned, which could lead to the key spawning multiple times if the chase condition is checked repeatedly.

4. **Correct Pickup Logic**: The `player.check_key_pickup(bushes)` method works correctly - it checks for collision with bushes that have `has_key == True`. The issue is not with pickup detection, but with when the key is assigned to a bush.

## Correctness Properties

Property 1: Bug Condition - Key Spawns Only After Chase Activation

_For any_ game state where `mikhail.chasing` transitions from `False` to `True` for the first time, the fixed code SHALL assign the key to a random bush at that exact moment, ensuring the key is not available before chase activation and is available after.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: Preservation - Key Pickup and Gate Mechanics

_For any_ game state where the key has been spawned (after chase activation), the fixed code SHALL produce exactly the same key pickup behavior, gate unlocking behavior, and chase mechanics as the original code, preserving all existing gameplay functionality.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `Start.py`

**Function**: `main()`

**Specific Changes**:

1. **Remove Premature Key Assignment**: Delete or comment out line 714:
   ```python
   # BEFORE (line 714):
   random.choice(bushes)["has_key"] = True  # hide key in random bush
   
   # AFTER:
   # Key will spawn when chase is activated (see below)
   ```

2. **Add Key Spawn Flag**: Add a new variable `key_spawned` after initializing `bushes`:
   ```python
   bushes = get_bush_rects()
   key_spawned = False  # Track whether key has been spawned
   ```

3. **Add Key Spawn Logic in Game Loop**: In the `STATE_EXPLORE` section, after the chase activation logic (around line 810-820), add code to spawn the key when chase first activates:
   ```python
   # After the code that sets mikhail.chasing = True (around line 810-820)
   # Add this immediately after the music change:
   
   if mikhail.chasing and not key_spawned:
       random.choice(bushes)["has_key"] = True
       key_spawned = True
   ```

4. **Placement in Game Loop**: The key spawn logic should be placed in the `STATE_EXPLORE` state, specifically in the section that handles `mikhail.approach >= 3` and sets `mikhail.chasing = True`. This ensures the key spawns at the exact moment the chase is activated.

5. **Ensure Single Spawn**: The `key_spawned` flag ensures that even if the chase logic is evaluated multiple times, the key only spawns once. This prevents duplicate key spawns or reassignment to different bushes.

### Implementation Location

The key spawn logic should be inserted in the `STATE_EXPLORE` block, specifically after this section (around lines 810-820):

```python
elif mikhail.approach >= 3:
    push_vx, push_vy, push_timer = compute_push(
        player.rect, mikhail.rect, ANGEL_PUSH_TILES_3)
    mikhail.chasing = True
    pygame.mixer.music.fadeout(1000)
    pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "12. March of Iron.mp3"))
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1)
    state = STATE_EXPLORE
    
    # ADD KEY SPAWN LOGIC HERE:
    if not key_spawned:
        random.choice(bushes)["has_key"] = True
        key_spawned = True
```

However, since this code is inside a dialog completion block, we need to place the spawn check in the main `STATE_EXPLORE` loop to catch the chase activation regardless of where it happens.

**Better Placement**: Add the spawn check in the main `STATE_EXPLORE` section, after all dialog and interaction logic:

```python
if state == STATE_EXPLORE:
    # ... existing movement and interaction logic ...
    
    # Spawn key when chase first activates
    if mikhail.chasing and not key_spawned:
        random.choice(bushes)["has_key"] = True
        key_spawned = True
    
    # ... existing key pickup logic ...
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code (key available before chase), then verify the fix works correctly (key spawns only after chase) and preserves existing behavior (key pickup, gate unlocking, chase mechanics all work the same).

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm that the key is assigned to a bush at game initialization, allowing premature pickup.

**Test Plan**: Write tests that initialize the game state and check whether any bush has `has_key == True` before `mikhail.chasing` is activated. Run these tests on the UNFIXED code to observe the bug and confirm the root cause.

**Test Cases**:
1. **Premature Key Assignment Test**: Initialize game, check bushes immediately → Expect to find one bush with `has_key == True` (will pass on unfixed code, demonstrating the bug)
2. **Premature Pickup Test**: Initialize game, move player near bushes, call `check_key_pickup()` → Expect key pickup to succeed before chase (will pass on unfixed code, demonstrating the bug)
3. **Chase Not Activated Test**: Initialize game with `mikhail.approach = 0`, check bushes → Expect no key available (will fail on unfixed code)
4. **Chase Not Activated Test 2**: Initialize game with `mikhail.approach = 2`, check bushes → Expect no key available (will fail on unfixed code)

**Expected Counterexamples**:
- On unfixed code, one bush will have `has_key == True` immediately after initialization
- On unfixed code, player can pick up key before `mikhail.chasing == True`
- Root cause confirmed: Line 714 assigns key at initialization, not at chase activation

### Fix Checking

**Goal**: Verify that for all game states where the chase is activated for the first time, the fixed function spawns the key at that moment.

**Pseudocode:**
```
FOR ALL gameState WHERE mikhail.chasing transitions from False to True DO
  BEFORE transition: ASSERT NO bush IN bushes WHERE bush["has_key"] == True
  AFTER transition: ASSERT EXISTS bush IN bushes WHERE bush["has_key"] == True
  ASSERT key_spawned == True
END FOR
```

**Test Cases**:
1. **Key Spawns on Chase Activation**: Simulate game state where `mikhail.approach = 3`, trigger dialog completion that sets `mikhail.chasing = True`, verify one bush has `has_key == True` after
2. **Key Not Available Before Chase**: Simulate game state where `mikhail.approach < 3`, verify no bush has `has_key == True`
3. **Key Spawns Only Once**: Simulate chase activation, verify key spawns, then simulate multiple game loop iterations with `mikhail.chasing == True`, verify key does not respawn or move to different bush
4. **Key Pickup After Spawn**: Simulate chase activation, key spawn, player movement to key bush, verify `check_key_pickup()` returns `True` and `player.has_key` becomes `True`

### Preservation Checking

**Goal**: Verify that for all game mechanics that do NOT involve the initial key assignment, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL gameState WHERE key has been spawned (mikhail.chasing == True) DO
  ASSERT check_key_pickup_original(gameState) == check_key_pickup_fixed(gameState)
  ASSERT gate_unlock_original(gameState) == gate_unlock_fixed(gameState)
  ASSERT chase_behavior_original(gameState) == chase_behavior_fixed(gameState)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain (different player positions, bush configurations, game states)
- It catches edge cases that manual unit tests might miss (e.g., key in corner bush, player at exact collision boundary)
- It provides strong guarantees that behavior is unchanged for all post-spawn gameplay

**Test Plan**: Observe behavior on UNFIXED code first for key pickup, gate unlocking, and chase mechanics after the key has been assigned, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Key Pickup Preservation**: Generate random player positions and bush configurations where key has spawned, verify `check_key_pickup()` works identically on fixed and unfixed code
2. **Gate Unlock Preservation**: Generate random game states where player has key and is near gate, verify gate unlock prompt and logic work identically
3. **Chase Behavior Preservation**: Generate random game states where `mikhail.chasing == True`, verify Mikhail's movement, collision, and player damage work identically
4. **Music Transition Preservation**: Verify that music changes to "12. March of Iron.mp3" when chase activates, same as unfixed code
5. **Raziel Interaction Preservation**: Generate random game states with various `mikhail.approach` values and Raziel positions, verify all dialog triggers work identically

### Unit Tests

- Test that no bush has `has_key == True` at game initialization (after fix)
- Test that exactly one bush has `has_key == True` after chase activation (after fix)
- Test that `key_spawned` flag is `False` at initialization and `True` after chase activation
- Test that key does not respawn if chase is triggered multiple times
- Test that `check_key_pickup()` works correctly after key spawns
- Test that gate unlock logic works correctly after key is picked up
- Test edge case: player dies after picking up key, respawns, still has key

### Property-Based Tests

- Generate random bush configurations and verify key spawns in exactly one bush after chase activation
- Generate random player positions after key spawn and verify pickup detection works correctly
- Generate random game states with `mikhail.chasing == True` and verify chase behavior is preserved
- Generate random sequences of player actions (movement, interactions) and verify game state consistency

### Integration Tests

- Test full game flow: start game, approach Mikhail three times, verify chase activates and key spawns, find key, unlock gate
- Test that key is not available before chase across multiple playthroughs with different player paths
- Test that all Raziel interactions work correctly regardless of key spawn timing
- Test that player can complete the level (pick up key, unlock gate, proceed to next scene) after the fix
