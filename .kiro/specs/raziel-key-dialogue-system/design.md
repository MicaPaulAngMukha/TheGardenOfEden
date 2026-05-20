# Design Document: Raziel Key Dialogue System

## Overview

The Raziel Key Dialogue System introduces a multi-difficulty key mechanic to the Garden of Eden game. This system allows players to choose between four keys (Bronze, Gold, Rusted, Divine) that represent different difficulty modes, each with unique lore delivered through Raziel's dynamic dialogue and narrator text. The design integrates seamlessly with the existing game architecture, extending the current dialogue system, NPC behavior, and inventory mechanics.

### Key Design Principles

1. **Narrative Integration**: Keys are woven into the game's lore through Raziel's backstory and dialogue
2. **Player Agency**: Players can discover, pick up, swap, and drop keys freely
3. **Minimal UI Disruption**: Key interactions use existing dialogue patterns
4. **Extensibility**: The system is designed to support future difficulty implementations

### System Context

The system operates within the Start.py game scene (the Garden of Eden entrance area) and integrates with:
- Existing dialogue system (Typewriter, draw_angel_dialog, draw_narrator_dialog)
- NPC behavior (Raziel's roaming and interaction logic)
- Player inventory (extending the existing has_key boolean)
- Event triggers (Mikhail chase activation)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Game Loop (Start.py)                     │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──> Key Spawning System
             │    └──> Triggered by Mikhail chase event
             │         Spawns 4 keys at designated locations
             │
             ├──> Raziel Dialogue System
             │    ├──> Dynamic dialogue pool
             │    ├──> Dialogue cycling logic
             │    └──> Integration with existing Typewriter
             │
             ├──> Key Discovery System
             │    ├──> Proximity detection
             │    ├──> Narrator dialogue trigger
             │    └──> Pickup prompt display
             │
             ├──> Inventory System
             │    ├──> Single key constraint
             │    ├──> Key swapping logic
             │    └──> Visual key indicator
             │
             └──> Key Persistence System
                  └──> Dropped key tracking and rendering
```

### Component Interaction Flow

```
Player Movement
     │
     ├──> Proximity to Raziel
     │    └──> Trigger dialogue from pool
     │         └──> Display via draw_angel_dialog()
     │
     ├──> Proximity to Key Entity
     │    └──> Display narrator text
     │         └──> Show pickup prompt
     │              ├──> Accept: Add to inventory, remove from world
     │              └──> Decline: Leave in world
     │
     └──> Mikhail Chase Triggered
          └──> Spawn all 4 keys at designated locations
```

## Components and Interfaces

### 1. Key Entity Data Structure

```python
class KeyEntity:
    """
    Represents a physical key in the game world.
    """
    def __init__(self, key_type: str, position: tuple[int, int]):
        self.key_type = key_type  # "bronze", "gold", "rusted", "divine"
        self.rect = pygame.Rect(position[0], position[1], 16, 16)
        self.sprite = self._load_sprite()
        self.discovered = False  # Track if player has seen this key
    
    def _load_sprite(self) -> pygame.Surface:
        """Load the appropriate sprite based on key_type"""
        sprite_map = {
            "bronze": "bronze_key.png",
            "gold": "Key.png",
            "rusted": "rusted_key.png",
            "divine": "divine_key.png"
        }
        return pygame.image.load(sprite_map[self.key_type])
    
    def near_player(self, player_rect: pygame.Rect, radius: int = 30) -> bool:
        """Check if player is within interaction range"""
        return self.rect.inflate(radius * 2, radius * 2).colliderect(player_rect)
```

### 2. Key Spawning System

```python
# Key spawn locations (tile coordinates)
KEY_SPAWN_LOCATIONS = {
    "bronze": (15 * T, 25 * T),  # Left side of map
    "gold": (45 * T, 25 * T),    # Right side of map
    "rusted": (20 * T, 35 * T),  # Lower left
    "divine": (40 * T, 35 * T)   # Lower right
}

def spawn_keys() -> list[KeyEntity]:
    """
    Spawn all four keys at designated locations.
    Called when Mikhail chase is triggered.
    """
    keys = []
    for key_type, position in KEY_SPAWN_LOCATIONS.items():
        keys.append(KeyEntity(key_type, position))
    return keys
```

### 3. Raziel Dialogue Pool System

```python
# Extended DIALOGS dictionary in Start.py
DIALOGS = {
    # ... existing dialogues ...
    
    "raziel_key_intro": [
        ("Raziel", "Eden has many keys."),
        ("Raziel", "Some open doors, others... well, they open different kinds of doors."),
    ],
    
    "raziel_key_gold": [
        ("Raziel", "That golden key? Yeah, that's mine."),
        ("Raziel", "I dropped it somewhere around here."),
        ("Raziel", "Nothing special about it, really. Just... shiny."),
    ],
    
    "raziel_key_bronze": [
        ("Raziel", "The bronze key has a story."),
        ("Raziel", "A young cherub once dropped it while guarding the tree of knowledge."),
        ("Raziel", "Got trapped in Eden for centuries because of it."),
        ("Raziel", "That cherub? You might meet them. They're still here, guarding."),
    ],
    
    "raziel_key_rusted": [
        ("Raziel", "That rusted key belonged to a seraph."),
        ("Raziel", "The one who banished your parents from Eden."),
        ("Raziel", "Dropped it in the chaos. Never bothered to pick it up."),
        ("Raziel", "Guess they figured humanity wouldn't be back."),
    ],
    
    "raziel_key_divine": [
        ("Raziel", "The divine key... that one's different."),
        ("Raziel", "Belonged to the watchers. You know, the ones who..."),
        ("Raziel", "...had relations with human women."),
        ("Raziel", "They were banished. Left their keys behind."),
        ("Raziel", "I wouldn't touch it if I were you. But you're not me."),
    ],
}

class RazielDialoguePool:
    """
    Manages Raziel's dynamic dialogue cycling.
    """
    def __init__(self):
        self.dialogue_keys = [
            "raziel_key_intro",
            "raziel_key_gold",
            "raziel_key_bronze",
            "raziel_key_rusted",
            "raziel_key_divine"
        ]
        self.current_index = 0
        self.seen_dialogues = set()
    
    def get_next_dialogue(self) -> list[tuple[str, str]]:
        """
        Return the next dialogue in the pool, cycling through all options.
        """
        dialogue_key = self.dialogue_keys[self.current_index]
        self.seen_dialogues.add(dialogue_key)
        self.current_index = (self.current_index + 1) % len(self.dialogue_keys)
        return DIALOGS[dialogue_key]
```

### 4. Key Discovery and Narrator System

```python
# Narrator text for each key type
KEY_NARRATOR_TEXT = {
    "bronze": "You find a bronze key. It feels light as a feather in your hand.",
    "gold": "A golden key.. It looks brand new. It could be Raziel's.",
    "rusted": "You find an old key. It's rusted and you're not even sure if it will work anymore.",
    "divine": "The key blinks at you. You feel an overwhelming presence..."
}

def check_key_discovery(player: Player, keys: list[KeyEntity]) -> KeyEntity | None:
    """
    Check if player is near an undiscovered key.
    Returns the key if discovered, None otherwise.
    """
    for key in keys:
        if not key.discovered and key.near_player(player.rect):
            key.discovered = True
            return key
    return None
```

### 5. Player Inventory Extension

```python
class Player:
    # ... existing Player class ...
    
    def __init__(self):
        # ... existing initialization ...
        self.held_key: KeyEntity | None = None  # Replace has_key boolean
    
    def pickup_key(self, key: KeyEntity) -> KeyEntity | None:
        """
        Pick up a key. If already holding a key, return the old key.
        Returns: The previously held key (for swapping), or None
        """
        old_key = self.held_key
        self.held_key = key
        return old_key
    
    def drop_key(self) -> KeyEntity | None:
        """
        Drop the currently held key.
        Returns: The dropped key, or None if not holding a key
        """
        dropped = self.held_key
        self.held_key = None
        return dropped
    
    def has_key(self) -> bool:
        """Check if player is holding any key"""
        return self.held_key is not None
```

### 6. Key Swapping System

```python
def handle_key_swap(player: Player, new_key: KeyEntity, 
                    keys_in_world: list[KeyEntity]) -> None:
    """
    Handle key swapping logic when player picks up a new key.
    
    Args:
        player: The player object
        new_key: The key being picked up
        keys_in_world: List of all keys currently in the world
    """
    # Remove new key from world
    keys_in_world.remove(new_key)
    
    # Get old key (if any)
    old_key = player.pickup_key(new_key)
    
    # If there was an old key, drop it at player's location
    if old_key is not None:
        old_key.rect.center = player.rect.center
        old_key.discovered = False  # Reset discovery state
        keys_in_world.append(old_key)
```

### 7. Game State Integration

```python
# New game states
STATE_KEY_DISCOVERY = "key_discovery"
STATE_KEY_PICKUP_PROMPT = "key_pickup_prompt"

# Game loop integration
def main():
    # ... existing initialization ...
    
    keys_in_world = []  # List of KeyEntity objects
    keys_spawned = False
    discovered_key = None  # Currently discovered key awaiting pickup decision
    raziel_dialogue_pool = RazielDialoguePool()
    
    while True:
        # ... existing event handling ...
        
        if state == STATE_EXPLORE:
            # ... existing explore logic ...
            
            # Spawn keys when Mikhail chase starts
            if mikhail.chasing and not keys_spawned:
                keys_in_world = spawn_keys()
                keys_spawned = True
            
            # Check for key discovery
            if keys_spawned:
                discovered_key = check_key_discovery(player, keys_in_world)
                if discovered_key is not None:
                    state = STATE_KEY_DISCOVERY
                    typewriter.set_text(KEY_NARRATOR_TEXT[discovered_key.key_type])
            
            # Raziel interaction with dialogue pool
            if raziel.roaming and raziel.near_player(player.rect) and raziel_cooldown == 0:
                angel_dialog = raziel_dialogue_pool.get_next_dialogue()
                dialog_index = 0
                typewriter.set_text(angel_dialog[0][1])
                raziel_cooldown = 300
                state = STATE_ANGEL_DIALOG
        
        elif state == STATE_KEY_DISCOVERY:
            # Display narrator text, then show pickup prompt
            if typewriter.done:
                state = STATE_KEY_PICKUP_PROMPT
        
        elif state == STATE_KEY_PICKUP_PROMPT:
            # Handle Y/N input for key pickup
            # (handled in event loop)
            pass
        
        # ... existing drawing logic ...
        
        # Draw keys in world
        for key in keys_in_world:
            game_surface.blit(key.sprite, key.rect)
```

## Data Models

### Key Type Enumeration

```python
from enum import Enum

class KeyType(Enum):
    BRONZE = "bronze"
    GOLD = "gold"
    RUSTED = "rusted"
    DIVINE = "divine"
    
    @property
    def sprite_path(self) -> str:
        """Return the sprite file path for this key type"""
        sprite_map = {
            KeyType.BRONZE: "bronze_key.png",
            KeyType.GOLD: "Key.png",
            KeyType.RUSTED: "rusted_key.png",
            KeyType.DIVINE: "divine_key.png"
        }
        return sprite_map[self]
    
    @property
    def narrator_text(self) -> str:
        """Return the narrator discovery text for this key type"""
        text_map = {
            KeyType.BRONZE: "You find a bronze key. It feels light as a feather in your hand.",
            KeyType.GOLD: "A golden key.. It looks brand new. It could be Raziel's.",
            KeyType.RUSTED: "You find an old key. It's rusted and you're not even sure if it will work anymore.",
            KeyType.DIVINE: "The key blinks at you. You feel an overwhelming presence..."
        }
        return text_map[self]
```

### Game State Data

```python
@dataclass
class KeySystemState:
    """
    Encapsulates all state for the key system.
    """
    keys_in_world: list[KeyEntity]
    keys_spawned: bool
    discovered_key: KeyEntity | None
    raziel_dialogue_pool: RazielDialoguePool
```

### Character Lore Update

```python
# Update to CharactersPage.py CHARACTERS list
CHARACTERS = [
    # ... existing characters ...
    {
        "name": "The Guardian",
        "image": "Sprites/Guardian/GuardianFull.png",
        "description": "A young cherubim sent down to guard the tree of knowledge. Once dropped a bronze key and got trapped in Eden for centuries. Much more strict than Mikhail, works under him. Still has mercy to humans, gives them a chance to walk away from the path of sin."
    },
    # ... rest of characters ...
]
```

## Error Handling

### Key Spawning Errors

```python
def spawn_keys() -> list[KeyEntity]:
    """
    Spawn all four keys at designated locations.
    Handles missing sprite files gracefully.
    """
    keys = []
    for key_type, position in KEY_SPAWN_LOCATIONS.items():
        try:
            key = KeyEntity(key_type, position)
            keys.append(key)
        except FileNotFoundError as e:
            print(f"Warning: Could not load sprite for {key_type} key: {e}")
            # Create a placeholder key with a colored rectangle
            key = KeyEntity(key_type, position)
            key.sprite = create_placeholder_sprite(key_type)
            keys.append(key)
    return keys

def create_placeholder_sprite(key_type: str) -> pygame.Surface:
    """Create a colored rectangle as a placeholder sprite"""
    color_map = {
        "bronze": (205, 127, 50),
        "gold": (255, 215, 0),
        "rusted": (183, 65, 14),
        "divine": (255, 255, 255)
    }
    surface = pygame.Surface((16, 16))
    surface.fill(color_map.get(key_type, (128, 128, 128)))
    return surface
```

### Dialogue Pool Errors

```python
class RazielDialoguePool:
    def get_next_dialogue(self) -> list[tuple[str, str]]:
        """
        Return the next dialogue in the pool.
        Falls back to a default dialogue if key is missing.
        """
        dialogue_key = self.dialogue_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.dialogue_keys)
        
        # Fallback if dialogue key doesn't exist
        if dialogue_key not in DIALOGS:
            print(f"Warning: Dialogue key '{dialogue_key}' not found")
            return [("Raziel", "...")]
        
        return DIALOGS[dialogue_key]
```

### Inventory State Errors

```python
def handle_key_swap(player: Player, new_key: KeyEntity, 
                    keys_in_world: list[KeyEntity]) -> None:
    """
    Handle key swapping with validation.
    """
    # Validate new_key is in world
    if new_key not in keys_in_world:
        print(f"Warning: Attempted to pick up key not in world")
        return
    
    # Remove new key from world
    keys_in_world.remove(new_key)
    
    # Get old key (if any)
    old_key = player.pickup_key(new_key)
    
    # If there was an old key, drop it at player's location
    if old_key is not None:
        old_key.rect.center = player.rect.center
        old_key.discovered = False
        keys_in_world.append(old_key)
```

## Testing Strategy

### Unit Testing Approach

The system will use **example-based unit tests** to verify specific behaviors and integration points. Property-based testing is not applicable here because:

1. **UI Interaction Testing**: Key discovery and pickup involve UI state transitions and player input, which are better tested with specific scenarios
2. **NPC Dialogue Cycling**: Raziel's dialogue pool cycles through a fixed set of dialogues in order, making example-based tests more appropriate
3. **Game State Integration**: The system integrates with existing game states and events, requiring specific test scenarios
4. **Visual Asset Dependencies**: Keys depend on sprite files and rendering, which are not suitable for property-based testing

### Test Categories

#### 1. Key Spawning Tests

```python
def test_spawn_keys_creates_four_keys():
    """Verify that spawn_keys creates exactly 4 KeyEntity objects"""
    keys = spawn_keys()
    assert len(keys) == 4

def test_spawn_keys_correct_types():
    """Verify that all four key types are spawned"""
    keys = spawn_keys()
    key_types = {key.key_type for key in keys}
    assert key_types == {"bronze", "gold", "rusted", "divine"}

def test_spawn_keys_correct_positions():
    """Verify that keys spawn at designated locations"""
    keys = spawn_keys()
    for key in keys:
        expected_pos = KEY_SPAWN_LOCATIONS[key.key_type]
        assert key.rect.topleft == expected_pos

def test_spawn_keys_handles_missing_sprites():
    """Verify graceful handling of missing sprite files"""
    # Mock missing file
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        keys = spawn_keys()
        assert len(keys) == 4  # Should still create keys with placeholders
```

#### 2. Raziel Dialogue Pool Tests

```python
def test_dialogue_pool_cycles_through_all_dialogues():
    """Verify that dialogue pool cycles through all 5 dialogues"""
    pool = RazielDialoguePool()
    seen_keys = set()
    
    for _ in range(5):
        dialogue = pool.get_next_dialogue()
        # Extract dialogue key from DIALOGS
        for key, value in DIALOGS.items():
            if value == dialogue:
                seen_keys.add(key)
    
    assert len(seen_keys) == 5

def test_dialogue_pool_repeats_after_cycle():
    """Verify that dialogue pool repeats after going through all dialogues"""
    pool = RazielDialoguePool()
    
    # Get first dialogue
    first_dialogue = pool.get_next_dialogue()
    
    # Cycle through remaining 4
    for _ in range(4):
        pool.get_next_dialogue()
    
    # Next should be first again
    repeated_dialogue = pool.get_next_dialogue()
    assert repeated_dialogue == first_dialogue

def test_dialogue_pool_tracks_seen_dialogues():
    """Verify that seen_dialogues set is updated correctly"""
    pool = RazielDialoguePool()
    
    assert len(pool.seen_dialogues) == 0
    
    pool.get_next_dialogue()
    assert len(pool.seen_dialogues) == 1
    
    for _ in range(4):
        pool.get_next_dialogue()
    
    assert len(pool.seen_dialogues) == 5
```

#### 3. Key Discovery Tests

```python
def test_key_discovery_detects_nearby_key():
    """Verify that check_key_discovery detects keys within range"""
    player = Player()
    player.rect.center = (100, 100)
    
    key = KeyEntity("bronze", (110, 110))  # Within range
    keys = [key]
    
    discovered = check_key_discovery(player, keys)
    assert discovered == key
    assert key.discovered == True

def test_key_discovery_ignores_distant_key():
    """Verify that check_key_discovery ignores keys out of range"""
    player = Player()
    player.rect.center = (100, 100)
    
    key = KeyEntity("bronze", (200, 200))  # Out of range
    keys = [key]
    
    discovered = check_key_discovery(player, keys)
    assert discovered is None
    assert key.discovered == False

def test_key_discovery_ignores_already_discovered():
    """Verify that already discovered keys are not re-discovered"""
    player = Player()
    player.rect.center = (100, 100)
    
    key = KeyEntity("bronze", (110, 110))
    key.discovered = True
    keys = [key]
    
    discovered = check_key_discovery(player, keys)
    assert discovered is None
```

#### 4. Inventory and Swapping Tests

```python
def test_player_pickup_key_when_empty():
    """Verify player can pick up key when not holding one"""
    player = Player()
    key = KeyEntity("bronze", (100, 100))
    
    old_key = player.pickup_key(key)
    
    assert player.held_key == key
    assert old_key is None

def test_player_pickup_key_when_holding():
    """Verify player swaps keys when already holding one"""
    player = Player()
    old_key = KeyEntity("bronze", (100, 100))
    new_key = KeyEntity("gold", (200, 200))
    
    player.pickup_key(old_key)
    returned_key = player.pickup_key(new_key)
    
    assert player.held_key == new_key
    assert returned_key == old_key

def test_handle_key_swap_drops_old_key():
    """Verify that key swapping drops old key at player location"""
    player = Player()
    player.rect.center = (150, 150)
    
    old_key = KeyEntity("bronze", (100, 100))
    new_key = KeyEntity("gold", (200, 200))
    
    player.pickup_key(old_key)
    keys_in_world = [new_key]
    
    handle_key_swap(player, new_key, keys_in_world)
    
    assert player.held_key == new_key
    assert old_key in keys_in_world
    assert old_key.rect.center == (150, 150)
    assert old_key.discovered == False

def test_handle_key_swap_removes_new_key_from_world():
    """Verify that picked up key is removed from world"""
    player = Player()
    new_key = KeyEntity("gold", (200, 200))
    keys_in_world = [new_key]
    
    handle_key_swap(player, new_key, keys_in_world)
    
    assert new_key not in keys_in_world
    assert player.held_key == new_key
```

#### 5. Integration Tests

```python
def test_keys_spawn_on_mikhail_chase():
    """Integration test: Keys spawn when Mikhail chase is triggered"""
    # This would be a full game loop test
    # Verify that keys_spawned flag is set and keys list is populated
    pass

def test_raziel_dialogue_triggers_on_interaction():
    """Integration test: Raziel dialogue from pool triggers on player proximity"""
    # Verify that dialogue pool is used instead of fixed dialogue
    pass

def test_key_pickup_flow():
    """Integration test: Complete key pickup flow from discovery to inventory"""
    # Verify state transitions: EXPLORE -> KEY_DISCOVERY -> KEY_PICKUP_PROMPT -> EXPLORE
    pass
```

### Test Execution

Tests will be run using pytest:

```bash
# Run all tests
pytest tests/test_key_system.py

# Run specific test category
pytest tests/test_key_system.py::test_spawn_keys_creates_four_keys

# Run with coverage
pytest --cov=. tests/test_key_system.py
```

### Manual Testing Checklist

- [ ] All four keys spawn after Mikhail chase triggers
- [ ] Each key displays correct narrator text on discovery
- [ ] Pickup prompt appears with Y/N options
- [ ] Declining pickup leaves key in world
- [ ] Accepting pickup adds key to inventory
- [ ] Key icon appears above player when holding key
- [ ] Raziel cycles through all 5 dialogue options
- [ ] Raziel dialogue doesn't repeat until all 5 are seen
- [ ] Swapping keys drops old key at player location
- [ ] Dropped keys remain interactable
- [ ] Guardian character description updated in Characters screen
- [ ] All key sprites load correctly
- [ ] Placeholder sprites appear if files missing

## Implementation Notes

### File Modifications Required

1. **Start.py**
   - Add KeyEntity class
   - Add RazielDialoguePool class
   - Extend Player class with held_key attribute
   - Add KEY_SPAWN_LOCATIONS constant
   - Add KEY_NARRATOR_TEXT constant
   - Add new dialogue entries to DIALOGS dictionary
   - Add STATE_KEY_DISCOVERY and STATE_KEY_PICKUP_PROMPT states
   - Modify main() game loop to integrate key system
   - Add key spawning logic on Mikhail chase trigger
   - Add key discovery and pickup logic
   - Modify Raziel interaction to use dialogue pool

2. **CharactersPage.py**
   - Update Guardian character description to reference bronze key backstory

3. **New Test File**
   - Create tests/test_key_system.py with unit tests

### Asset Requirements

- bronze_key.png (already exists)
- Key.png (already exists)
- rusted_key.png (already exists)
- divine_key.png (already exists)

### Performance Considerations

- Key proximity checks run every frame during STATE_EXPLORE
  - Optimization: Only check when keys_spawned is True
  - Optimization: Use spatial partitioning if performance issues arise
- Dialogue pool lookup is O(1) with dictionary access
- Key rendering is minimal (4 small sprites maximum)

### Future Extensibility

The system is designed to support:
- Additional key types (add to KeyType enum and spawn locations)
- Difficulty implementation (keys can store difficulty metadata)
- Key-specific game mechanics (keys can have behavior methods)
- Save/load system (KeySystemState can be serialized)
