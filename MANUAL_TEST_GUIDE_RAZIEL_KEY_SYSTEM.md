# Manual Test Guide - Raziel Key Dialogue System

This guide provides step-by-step instructions for manually testing the complete Raziel Key Dialogue System integration.

## Prerequisites

- Game must be running from Start.py
- All key sprite files must be present (bronze_key.png, Key.png, rusted_key.png, divine_key.png)

## Test 1: Key Spawning After Mikhail Chase

**Objective:** Verify that all 4 keys spawn correctly when Mikhail chase is triggered.

**Steps:**
1. Start the game (run `python Start.py`)
2. Wait for opening cutscene to complete
3. Approach Mikhail (the angel on the left) three times
   - First approach: He warns you
   - Second approach: He warns you again
   - Third approach: He starts chasing you
4. Once chase starts, look around the map for keys

**Expected Results:**
- ✓ Exactly 4 keys spawn in the world
- ✓ Bronze key spawns at left side of map (coordinates: 15*13, 25*13)
- ✓ Gold key spawns at right side of map (coordinates: 45*13, 25*13)
- ✓ Rusted key spawns at lower left (coordinates: 20*13, 35*13)
- ✓ Divine key spawns at lower right (coordinates: 40*13, 35*13)
- ✓ All keys are visible and have correct sprites

---

## Test 2: Key Discovery Flow

**Objective:** Test the complete key discovery flow (proximity → narrator text → pickup prompt).

**Steps:**
1. Continue from Test 1 (keys should be spawned)
2. Walk near any key (within ~30 pixels)
3. Observe the narrator text that appears
4. Read the "Pick it up?" prompt

**Expected Results:**
- ✓ Narrator text appears when player gets close to key
- ✓ Narrator text is specific to the key type:
  - Bronze: "You find a bronze key. It feels light as a feather in your hand."
  - Gold: "A golden key.. It looks brand new. It could be Raziel's."
  - Rusted: "You find an old key. It's rusted and you're not even sure if it will work anymore."
  - Divine: "The key blinks at you. You feel an overwhelming presence..."
- ✓ After narrator text, "Pick it up?" prompt appears with Y/N options

---

## Test 3: Key Pickup Choice

**Objective:** Test accepting and declining key pickup.

**Steps:**
1. Discover a key (follow Test 2)
2. When prompted "Pick it up?", press **N** (decline)
3. Observe that key remains in world
4. Walk away and return to the same key
5. Discover it again and press **Y** (accept)

**Expected Results:**
- ✓ Pressing N leaves key in the world
- ✓ Key can be discovered again after declining
- ✓ Pressing Y adds key to inventory
- ✓ Key disappears from world after accepting
- ✓ Small key icon appears above player's head

---

## Test 4: Key Swapping Flow

**Objective:** Test the complete key swapping flow (hold key → discover new key → swap → old key drops).

**Steps:**
1. Pick up first key (e.g., Bronze key)
2. Verify key icon appears above player
3. Walk to a different key (e.g., Gold key)
4. Discover the second key
5. Accept pickup (press Y)
6. Observe what happens

**Expected Results:**
- ✓ First key is held (icon above player)
- ✓ Second key can be discovered while holding first key
- ✓ Accepting second key triggers swap
- ✓ First key drops at player's current location
- ✓ Player now holds second key (icon updates if sprites differ)
- ✓ Dropped key can be picked up again

---

## Test 5: Key Persistence

**Objective:** Verify that dropped keys remain in the world.

**Steps:**
1. Pick up a key
2. Swap it for another key (follow Test 4)
3. Note the location where first key dropped
4. Walk away from the dropped key
5. Return to the location

**Expected Results:**
- ✓ Dropped key remains at the location where it was dropped
- ✓ Dropped key is visible and interactable
- ✓ Dropped key can be discovered and picked up again

---

## Test 6: Raziel Dialogue Cycling

**Objective:** Verify that Raziel cycles through all 5 key-related dialogues.

**Steps:**
1. After Mikhail starts chasing, Raziel will start roaming
2. Approach Raziel when he's roaming (wait for cooldown between interactions)
3. Interact with him 5 times, noting each dialogue
4. Interact a 6th time to verify cycling

**Expected Dialogues (in order):**

**Dialogue 1 - Introduction:**
- "Eden has many keys."
- "Some open doors, others... well, they open different kinds of doors."

**Dialogue 2 - Gold Key:**
- "That golden key? Yeah, that's mine."
- "I dropped it somewhere around here."
- "Nothing special about it, really. Just... shiny."

**Dialogue 3 - Bronze Key:**
- "The bronze key has a story."
- "A young cherub once dropped it while guarding the tree of knowledge."
- "Got trapped in Eden for centuries because of it."
- "That cherub? You might meet them. They're still here, guarding."

**Dialogue 4 - Rusted Key:**
- "That rusted key belonged to a seraph."
- "The one who banished your parents from Eden."
- "Dropped it in the chaos. Never bothered to pick it up."
- "Guess they figured humanity wouldn't be back."

**Dialogue 5 - Divine Key:**
- "The divine key... that one's different."
- "Belonged to the watchers. You know, the ones who..."
- "...had relations with human women."
- "They were banished. Left their keys behind."
- "I wouldn't touch it if I were you. But you're not me."

**Expected Results:**
- ✓ Raziel cycles through all 5 dialogues in order
- ✓ After 5th dialogue, next interaction shows 1st dialogue again
- ✓ Dialogue continues cycling indefinitely

---

## Test 7: Key Sprites Visual Verification

**Objective:** Verify that all four key sprites render correctly.

**Steps:**
1. Spawn all keys (trigger Mikhail chase)
2. Locate each key type on the map
3. Observe the sprite for each key

**Expected Results:**
- ✓ Bronze key: Bronze/copper colored key sprite (bronze_key.png)
- ✓ Gold key: Golden/yellow key sprite (Key.png)
- ✓ Rusted key: Rusty/reddish-brown key sprite (rusted_key.png)
- ✓ Divine key: White/glowing key sprite (divine_key.png)
- ✓ All sprites are 16x16 pixels
- ✓ All sprites are clearly visible on the map

---

## Test 8: Guardian Lore Update

**Objective:** Verify that Guardian character lore references the bronze key backstory.

**Steps:**
1. Exit the game (or press ESC to return to main menu)
2. From main menu, select "Characters"
3. Navigate to "The Guardian" character (use arrow keys or click arrows)
4. Read the character description

**Expected Results:**
- ✓ Guardian character exists in the Characters screen
- ✓ Description mentions "bronze key"
- ✓ Description mentions being "trapped in Eden for centuries"
- ✓ Description mentions "young cherubim"
- ✓ Description mentions "dropped" the key
- ✓ Lore is consistent with Raziel's bronze key dialogue

**Full Expected Description:**
"A young cherubim sent down to guard the tree of knowledge. Once dropped a bronze key and got trapped in Eden for centuries. Much more strict than Mikhail, works under him. Still has mercy to humans, gives them a chance to walk away from the path of sin."

---

## Test 9: Complete Integration Test

**Objective:** Test the entire system end-to-end in one playthrough.

**Steps:**
1. Start game
2. Complete opening cutscene
3. Trigger Mikhail chase (approach 3 times)
4. Verify 4 keys spawn
5. Interact with Raziel 5 times to hear all dialogues
6. Discover and pick up Bronze key
7. Discover and swap for Gold key
8. Verify Bronze key dropped at player location
9. Pick up Bronze key again
10. Discover and swap for Rusted key
11. Discover and swap for Divine key
12. Return to main menu and check Guardian lore

**Expected Results:**
- ✓ All keys spawn correctly
- ✓ All Raziel dialogues cycle properly
- ✓ All key discoveries show correct narrator text
- ✓ All key pickups work correctly
- ✓ All key swaps work correctly
- ✓ Dropped keys persist and can be picked up
- ✓ Guardian lore is updated correctly

---

## Known Issues / Edge Cases

### Edge Case 1: Multiple Keys in Same Location
If you drop multiple keys in the same spot by swapping repeatedly, they will stack. This is expected behavior - the last dropped key will be on top.

### Edge Case 2: Key Discovery During Dialogue
If you're in a dialogue with Raziel and walk near a key, the key discovery will not trigger until the dialogue ends. This is expected behavior.

### Edge Case 3: Mikhail Chase and Key Pickup
You can pick up keys while Mikhail is chasing you. Be careful not to get hit while reading narrator text!

---

## Troubleshooting

### Keys Don't Spawn
- **Cause:** Mikhail chase not triggered
- **Solution:** Approach Mikhail 3 times to trigger chase

### Key Sprites Missing
- **Cause:** Sprite files not found
- **Solution:** Verify all key sprite files exist in project root:
  - bronze_key.png
  - Key.png
  - rusted_key.png
  - divine_key.png

### Raziel Doesn't Cycle Dialogues
- **Cause:** Interacting before Mikhail chase
- **Solution:** Trigger Mikhail chase first, then interact with roaming Raziel

### Guardian Lore Not Updated
- **Cause:** Old version of CharactersPage.py
- **Solution:** Verify CharactersPage.py has been updated with new Guardian description

---

## Test Completion Checklist

Use this checklist to track your manual testing progress:

- [ ] Test 1: Key Spawning After Mikhail Chase
- [ ] Test 2: Key Discovery Flow
- [ ] Test 3: Key Pickup Choice
- [ ] Test 4: Key Swapping Flow
- [ ] Test 5: Key Persistence
- [ ] Test 6: Raziel Dialogue Cycling
- [ ] Test 7: Key Sprites Visual Verification
- [ ] Test 8: Guardian Lore Update
- [ ] Test 9: Complete Integration Test

---

## Test Results Summary

**Date:** _______________

**Tester:** _______________

**Overall Result:** [ ] PASS  [ ] FAIL

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Issues Found:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
