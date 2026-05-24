# Difficulty Modes Summary

## Overview
The game has **4 difficulty modes** determined by which key the player picks up in the first level (Start.py):

| Key | Difficulty | Description |
|-----|-----------|-------------|
| 🥉 **Bronze Key** | **Easy Mode** | Easier gameplay with slower enemies and more resources |
| 🥇 **Gold Key** | **Normal Mode** | Standard gameplay with no modifiers (baseline difficulty) |
| 🔧 **Rusted Key** | **Hard Mode** | Harder gameplay with faster enemies and fewer resources |
| ✨ **Divine Key** | **God Mode** | Extreme difficulty with God entity spawning |

---

## 🥇 Gold Key - Normal Mode (Baseline)

**No modifiers applied** - This is the standard, intended gameplay experience.

All enemy speeds, spawn rates, and timing mechanics use their default values.

---

## 🥉 Bronze Key - Easy Mode

Makes the game **easier** for players who want a more relaxed experience.

### TheNaga Level
- ✓ **50% more items spawn** (health/speed pickups)
- ✓ **Cain throws 50% slower** (1.5x cooldown)
- ✓ **Abel moves slower** (2.5 speed instead of 3.6)

### TheTwins Level
- ✓ **Abel moves slower** (2.5 speed)
- ✓ **Cain throws 50% slower** (1.5x cooldown)
- ✓ **Cain's throw range reduced** (6 tiles instead of 8)

### TheGuardian Level
- ✓ **Guardian doesn't enrage** (stays at normal speed)

### TheStatues Level
- ✓ **Light phases last longer** (240 frames = 4 seconds)
- ✓ **Statues move 20% slower** (0.8x speed multiplier)

### TheGarden Level
- ✓ **Fewer tree shakes needed** (3 instead of 5)
- ✓ **God moves 20% slower** (0.8x speed)
- ✓ **Lightning strikes 50% slower** (1.5x cooldown)

---

## 🔧 Rusted Key - Hard Mode

Makes the game **harder** for experienced players seeking a challenge.

### TheNaga Level
- ⚠️ **Naga moves faster** (6 speed instead of 5)
- ⚠️ **50% fewer items spawn** (0.5x multiplier)
- ⚠️ **Cain throws 100% faster** (0.5x cooldown)
- ⚠️ **Abel instant-kills on contact** (no damage, instant death)

### TheTwins Level
- ⚠️ **Cain throws 100% faster** (0.5x cooldown)
- ⚠️ **Cain's throw range doubled** (12 tiles instead of 8)
- ⚠️ **Abel instant-kills on contact**

### TheGuardian Level
- ⚠️ **Shorter light phases** (120 frames = 2 seconds)
- ⚠️ **Longer dark phases** (420 frames = 7 seconds)
- ⚠️ **Guardian chases 20% faster** (1.2x speed multiplier)

### TheStatues Level
- ⚠️ **Shorter light phases** (120 frames = 2 seconds)
- ⚠️ **Longer dark phases** (420 frames = 7 seconds)
- ⚠️ **Statues move 20% faster** (1.2x speed multiplier)

### TheGarden Level
- ⚠️ **More tree shakes needed** (7 instead of 5)
- ⚠️ **God moves 30% faster** (1.3x speed)
- ⚠️ **Lightning strikes 30% faster** (0.7x cooldown)
- ⚠️ **More lightning bolts** (7 instead of 5)

---

## ✨ Divine Key - God Mode (Impossible)

**Extreme difficulty** with the God entity spawning in all non-Garden levels.

### TheNaga, TheTwins, TheGuardian, TheStatues
- 💀 **God entity spawns** - A powerful boss that:
  - Floats through walls
  - Chases the player relentlessly
  - Spawns lightning bolts around the player
  - Instant-kills on close proximity
  - Cannot be defeated or avoided

### TheGarden Level
- 💀 **9 lightning bolts per volley** (instead of 5)
- 💀 **God moves 50% faster** (1.5x speed)
- 💀 **Lightning strikes 100% faster** (0.5x cooldown)
- 💀 **God's instant-kill range increased** (0.6x multiplier)
- 💀 **Prior enemies disabled** (only God remains)

---

## Technical Implementation

### How It Works

1. **Key Selection** (Start.py):
   - Player discovers and picks up one of 4 keys hidden in bushes
   - Key type is stored in `player.held_key` attribute

2. **Level Transitions**:
   - `held_key` is passed through ALL level transitions:
   - `Start.py` → `TheNaga.py` → `TheTwins.py` → `TheGuardian.py` → `TheStatues.py` → `TheGarden.py`
   - Each level's `main()` function accepts `player_held_key` parameter
   - Key is restored to player object: `player.held_key = player_held_key`

3. **Difficulty Detection** (DifficultyManager):
   - Reads `player.held_key.key_type` attribute
   - Maps key type to difficulty mode:
     - `"bronze"` → `EASY`
     - `"gold"` → `NORMAL`
     - `"rusted"` → `HARD`
     - `"divine"` → `GOD_MODE`

4. **Modifier Application**:
   - Each level calls `difficulty_mgr.get_modifier(key, default)`
   - Returns level-specific modifier value for current difficulty
   - Modifiers are applied to enemy speeds, spawn rates, timings, etc.

### Files Involved

- `difficulty_config.py` - Centralized configuration for all modifiers
- `difficulty_manager.py` - Manages difficulty detection and modifier retrieval
- `key_system.py` - Defines KeyEntity class with key types
- `Start.py` - Key spawning and initial selection
- `TheNaga.py`, `TheTwins.py`, `TheGuardian.py`, `TheStatues.py`, `TheGarden.py` - Apply modifiers

---

## Verification

All difficulty modes have been tested and verified:

✅ **Key to Difficulty Mapping** - All 4 keys map correctly  
✅ **Level-Specific Modifiers** - All 5 levels apply correct modifiers  
✅ **God Entity Spawning** - God spawns only in God Mode  
✅ **Normal Mode No Modifiers** - Gold key has no gameplay changes  
✅ **Easy Mode Easier** - Bronze key makes game easier  
✅ **Hard Mode Harder** - Rusted key makes game harder  
✅ **God Mode Extreme** - Divine key enables extreme difficulty  
✅ **Modifier Validation** - All modifier values are valid  

Run `python test_difficulty_modes.py` to verify all modes work correctly.

---

## Player Experience

### Recommended for New Players
🥉 **Bronze Key (Easy Mode)** - Forgiving gameplay, more time to react

### Recommended for Most Players
🥇 **Gold Key (Normal Mode)** - Balanced, intended experience

### Recommended for Experienced Players
🔧 **Rusted Key (Hard Mode)** - Challenging but fair

### Recommended for Masochists Only
✨ **Divine Key (God Mode)** - Nearly impossible, designed to be unfair

---

## Design Philosophy

- **Normal Mode** is the baseline - all other modes modify this
- **Easy Mode** gives players more time and resources
- **Hard Mode** requires faster reactions and better strategy
- **God Mode** is intentionally unfair - a "secret" extreme challenge
- Difficulty is **permanent** once a key is picked up (no changing mid-game)
- Difficulty is **hidden** from the player (no UI indicator) to maintain surprise
