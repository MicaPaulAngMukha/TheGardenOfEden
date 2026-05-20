# Key System Implementation - Task 1

## Overview

This document describes the implementation of Task 1 from the Raziel Key Dialogue System spec: **Create KeyEntity class and key spawning system**.

## Files Created

### 1. `key_system.py`
The main module containing the key system implementation.

**Components:**
- `KeyEntity` class: Represents a physical key in the game world
- `spawn_keys()` function: Creates and returns all four keys
- `create_placeholder_sprite()` function: Fallback for missing sprite files
- `KEY_SPAWN_LOCATIONS` constant: Tile coordinates for all four keys

### 2. `test_key_system.py`
Comprehensive unit tests for the key system.

**Test Coverage:**
- KeyEntity initialization and attributes
- Sprite loading with error handling
- Proximity detection (near_player method)
- Key spawning functionality
- Spawn location validation

### 3. `test_key_integration.py`
Integration tests verifying the system works with actual sprite files.

### 4. `test_key_visual.py`
Visual test tool to verify key sprites render correctly.

## Implementation Details

### KeyEntity Class

```python
class KeyEntity:
    def __init__(self, key_type: str, position: tuple[int, int])
    def _load_sprite(self) -> pygame.Surface
    def near_player(self, player_rect: pygame.Rect, radius: int = 30) -> bool
```

**Attributes:**
- `key_type`: One of "bronze", "gold", "rusted", "divine"
- `rect`: pygame.Rect for collision detection (16x16 pixels)
- `sprite`: pygame.Surface containing the key's visual representation
- `discovered`: Boolean tracking if player has seen this key

**Features:**
- Automatic sprite loading with error handling
- Fallback to placeholder sprites if files are missing
- Proximity detection for player interaction
- Scales sprites to 16x16 if needed

### Key Spawn Locations

```python
KEY_SPAWN_LOCATIONS = {
    "bronze": (15 * T, 25 * T),  # Left side of map
    "gold": (45 * T, 25 * T),    # Right side of map
    "rusted": (20 * T, 35 * T),  # Lower left
    "divine": (40 * T, 35 * T)   # Lower right
}
```

Where `T = 13` (tile size in pixels).

### Spawn Keys Function

```python
def spawn_keys() -> list[KeyEntity]:
    """
    Spawn all four keys at designated locations.
    Called when Mikhail chase is triggered.
    """
```

**Returns:** List of 4 KeyEntity objects, one for each key type.

**Error Handling:** Continues spawning even if individual keys fail to load.

## Sprite Files

All four key sprites are present in the project root:
- `bronze_key.png` ✓
- `Key.png` (gold key) ✓
- `rusted_key.png` ✓
- `divine_key.png` ✓

## Testing

### Run Unit Tests
```bash
python -m pytest test_key_system.py -v
```

**Result:** 17 tests, all passing ✓

### Run Integration Tests
```bash
python test_key_integration.py
```

**Verifies:**
- All 4 keys load with actual sprites
- Proximity detection works correctly

### Run Visual Test
```bash
python test_key_visual.py
```

**Shows:** All four keys rendered on screen with labels.

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

### Requirement 1: Key Spawning
- ✓ 1.1: Spawns exactly four KeyEntity objects
- ✓ 1.2: Spawns Bronze Key at designated location
- ✓ 1.3: Spawns Gold Key at designated location
- ✓ 1.4: Spawns Rusted Key at designated location
- ✓ 1.5: Spawns Divine Key at designated location
- ✓ 1.6: All keys are visible and interactable

### Requirement 8: Key Visual Assets
- ✓ 8.1: Uses bronze_key.png for Bronze Key
- ✓ 8.2: Uses Key.png for Gold Key
- ✓ 8.3: Uses rusted_key.png for Rusted Key
- ✓ 8.4: Uses divine_key.png for Divine Key
- ✓ 8.5: Displays appropriate sprite for each key type

## Design Compliance

The implementation follows the design document specifications:

1. **KeyEntity Data Structure** (Design Section 1)
   - ✓ Implements all specified attributes
   - ✓ Implements _load_sprite() method with sprite_map
   - ✓ Implements near_player() method for proximity detection

2. **Key Spawning System** (Design Section 2)
   - ✓ Defines KEY_SPAWN_LOCATIONS constant
   - ✓ Implements spawn_keys() function
   - ✓ Returns list of KeyEntity objects

3. **Error Handling** (Design Section: Error Handling)
   - ✓ Handles missing sprite files gracefully
   - ✓ Implements create_placeholder_sprite() fallback
   - ✓ Continues spawning even if individual keys fail

## Usage Example

```python
from key_system import spawn_keys

# In your game loop, when Mikhail chase is triggered:
if mikhail.chasing and not keys_spawned:
    keys_in_world = spawn_keys()
    keys_spawned = True

# Later, in your render loop:
for key in keys_in_world:
    game_surface.blit(key.sprite, key.rect)

# Check for player proximity:
for key in keys_in_world:
    if key.near_player(player.rect):
        # Show discovery dialog
        pass
```

## Next Steps

This implementation provides the foundation for:
- Task 2: Raziel dialogue pool system
- Task 3: Key discovery and narrator system
- Task 4: Key pickup and inventory system
- Task 5: Key swapping mechanics

The KeyEntity class is ready to be integrated into Start.py's game loop.

## Notes

- The implementation is fully tested and ready for integration
- All sprite files are present and load correctly
- Error handling ensures the game won't crash if sprites are missing
- The proximity detection radius (30 pixels) can be adjusted as needed
- Keys are 16x16 pixels, matching the tile size (T=13) with some overlap
