# Design Document: Difficulty Mechanics Implementation

## Overview

The Difficulty Mechanics Implementation introduces a comprehensive difficulty scaling system that modifies gameplay based on the player's held key (Bronze, Gold, Rusted, or Divine). The system reads the `player.held_key` attribute at level initialization and applies appropriate modifiers to enemy behavior, spawn rates, timing mechanics, and the final Garden sequence.

### Key Design Principles

1. **Centralized Configuration**: All difficulty modifiers are defined in a single configuration module for easy balancing
2. **Level-Agnostic Design**: The difficulty system integrates with existing level code without requiring major refactoring
3. **Persistence**: Difficulty settings persist across level transitions based on the player's held key
4. **God Mode Special Case**: Divine Key spawns God entity in all levels, creating the ultimate challenge

### Difficulty Modes

- **Easy Mode (Bronze Key)**: Reduced enemy aggression, increased item spawns, longer timing windows
- **Normal Mode (Gold Key)**: Baseline game behavior (no modifiers)
- **Hard Mode (Rusted Key)**: Increased enemy aggression, reduced item spawns, shorter timing windows, instant-kill mechanics
- **God Mode (Divine Key)**: God spawns immediately in all levels, extreme Garden sequence difficulty

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Difficulty System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  DifficultyConfig│         │ DifficultyManager│          │
│  │                  │────────▶│                  │          │
│  │  - Modifiers     │         │  - Read Key      │          │
│  │  - Validation    │         │  - Apply Mods    │          │
│  └──────────────────┘         └──────────────────┘          │
│                                        │                      │
└────────────────────────────────────────┼──────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
            ┌───────▼────────┐  ┌────────▼───────┐  ┌────────▼───────┐
            │  Level Modules │  │  Enemy Classes │  │  God Entity    │
            │                │  │                │  │                │
            │  - TheNaga     │  │  - Naga        │  │  - Spawnable   │
            │  - TheTwins    │  │  - Cain/Abel   │  │  - Wall-ignore │
            │  - TheGuardian │  │  - Guardian    │  │  - Lightning   │
            │  - TheStatues  │  │  - Statues     │  │                │
            │  - TheGarden   │  │                │  │                │
            └────────────────┘  └────────────────┘  └────────────────┘
```

### Data Flow

```
Level Start
    │
    ▼
Read player.held_key
    │
    ▼
Extract key_type ("bronze", "gold", "rusted", "divine")
    │
    ▼
DifficultyManager.get_modifiers(level_name, key_type)
    │
    ▼
Apply modifiers to:
  - Enemy speeds
  - Attack frequencies
  - Spawn rates
  - Timing durations
    │
    ▼
Special Case: If key_type == "divine"
    │
    ▼
Spawn God entity
    │
    ▼
Level runs with modified parameters
```

## Components and Interfaces

### 1. DifficultyConfig Module

**File**: `difficulty_config.py`

**Purpose**: Centralized configuration for all difficulty modifiers

**Interface**:

```python
# Difficulty mode constants
EASY = "easy"
NORMAL = "normal"
HARD = "hard"
GOD_MODE = "god"

# Key type to difficulty mode mapping
KEY_TO_DIFFICULTY = {
    "bronze": EASY,
    "gold": NORMAL,
    "rusted": HARD,
    "divine": GOD_MODE,
    None: NORMAL  # Default when no key held
}

# Difficulty modifiers organized by level and mode
DIFFICULTY_MODIFIERS = {
    "TheNaga": {
        EASY: {
            "naga_speed": 5,  # No change from baseline
            "item_spawn_multiplier": 1.5,
            "abel_speed": 2.5,
            "cain_throw_cooldown_multiplier": 1.5,  # 50% slower
        },
        NORMAL: {},  # Empty dict = no modifiers
        HARD: {
            "naga_speed": 6,
            "item_spawn_multiplier": 0.5,
            "cain_throw_cooldown_multiplier": 0.5,  # 100% faster
            "abel_instant_kill": True,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheTwins": {
        EASY: {
            "abel_speed": 2.5,
            "cain_throw_cooldown_multiplier": 1.5,
            "cain_throw_range": 6,
        },
        NORMAL: {},
        HARD: {
            "cain_throw_cooldown_multiplier": 0.5,
            "cain_throw_range": 12,
            "abel_instant_kill": True,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheGuardian": {
        EASY: {
            "disable_enrage": True,
        },
        NORMAL: {},
        HARD: {
            "light_phase_duration": 120,
            "dark_phase_duration": 420,
            "guardian_chase_speed_multiplier": 1.2,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheStatues": {
        EASY: {
            "light_phase_duration": 240,
            "statue_speed_multiplier": 0.8,
        },
        NORMAL: {},
        HARD: {
            "light_phase_duration": 120,
            "dark_phase_duration": 420,
            "statue_speed_multiplier": 1.2,
        },
        GOD_MODE: {
            "spawn_god": True,
        }
    },
    "TheGarden": {
        EASY: {
            "tree_shakes_required": 3,
            "lightning_cooldown_multiplier": 1.5,
            "god_speed_multiplier": 0.8,
        },
        NORMAL: {},
        HARD: {
            "tree_shakes_required": 7,
            "lightning_cooldown_multiplier": 0.7,
            "god_speed_multiplier": 1.3,
            "lightning_count": 7,
        },
        GOD_MODE: {
            "lightning_count": 9,
            "lightning_cooldown_multiplier": 0.5,
            "god_speed_multiplier": 1.5,
            "god_smite_cooldown_multiplier": 0.6,
            "disable_prior_enemies": True,
        }
    }
}

def get_difficulty_from_key(key_entity):
    """
    Extract difficulty mode from player's held key.
    
    Args:
        key_entity: KeyEntity object or None
        
    Returns:
        str: Difficulty mode constant (EASY, NORMAL, HARD, GOD_MODE)
    """
    if key_entity is None:
        return NORMAL
    
    key_type = getattr(key_entity, 'key_type', None)
    return KEY_TO_DIFFICULTY.get(key_type, NORMAL)

def get_modifiers(level_name, difficulty):
    """
    Retrieve difficulty modifiers for a specific level and difficulty.
    
    Args:
        level_name: str - Name of the level ("TheNaga", "TheTwins", etc.)
        difficulty: str - Difficulty mode constant
        
    Returns:
        dict: Modifier dictionary for the level/difficulty combination
    """
    if level_name not in DIFFICULTY_MODIFIERS:
        return {}
    
    return DIFFICULTY_MODIFIERS[level_name].get(difficulty, {})

def validate_modifiers():
    """
    Validate all modifier values at startup.
    
    Checks:
    - Speed modifiers > 0
    - Frequency modifiers > 0
    - Duration modifiers >= 30 frames
    - Range modifiers >= 1
    
    Returns:
        list: List of validation error messages (empty if valid)
    """
    errors = []
    
    for level, difficulties in DIFFICULTY_MODIFIERS.items():
        for diff, mods in difficulties.items():
            # Speed validation
            for key in ["naga_speed", "abel_speed", "cain_speed"]:
                if key in mods and mods[key] <= 0:
                    errors.append(f"{level}.{diff}.{key} must be > 0")
            
            # Multiplier validation
            for key in [k for k in mods if "multiplier" in k]:
                if mods[key] <= 0:
                    errors.append(f"{level}.{diff}.{key} must be > 0")
            
            # Duration validation
            for key in [k for k in mods if "duration" in k]:
                if mods[key] < 30:
                    errors.append(f"{level}.{diff}.{key} must be >= 30 frames")
            
            # Range validation
            for key in [k for k in mods if "range" in k]:
                if mods[key] < 1:
                    errors.append(f"{level}.{diff}.{key} must be >= 1")
    
    return errors
```

### 2. DifficultyManager Class

**File**: `difficulty_manager.py`

**Purpose**: Manages difficulty state and provides UI feedback

**Interface**:

```python
import pygame
from difficulty_config import get_difficulty_from_key, get_modifiers, EASY, NORMAL, HARD, GOD_MODE

class DifficultyManager:
    """
    Manages difficulty state and provides visual feedback.
    """
    
    # Display colors for each difficulty
    DIFFICULTY_COLORS = {
        EASY: (205, 127, 50),      # Bronze
        NORMAL: (212, 175, 55),    # Gold
        HARD: (183, 65, 14),       # Rust
        GOD_MODE: (255, 255, 255), # White
    }
    
    # Display names
    DIFFICULTY_NAMES = {
        EASY: "Bronze Key - Easy Mode",
        NORMAL: "Gold Key - Normal Mode",
        HARD: "Rusted Key - Hard Mode",
        GOD_MODE: "Divine Key - God Mode",
    }
    
    def __init__(self, player, level_name):
        """
        Initialize difficulty manager for a level.
        
        Args:
            player: Player object with held_key attribute
            level_name: str - Name of the current level
        """
        self.player = player
        self.level_name = level_name
        self.difficulty = get_difficulty_from_key(player.held_key)
        self.modifiers = get_modifiers(level_name, self.difficulty)
        
        # UI state
        self.show_indicator = True
        self.indicator_timer = 180  # 3 seconds at 60 FPS
    
    def update(self):
        """Update indicator timer."""
        if self.indicator_timer > 0:
            self.indicator_timer -= 1
            if self.indicator_timer == 0:
                self.show_indicator = False
    
    def draw_indicator(self, surface, font):
        """
        Draw difficulty indicator at top-center of screen.
        
        Args:
            surface: pygame.Surface to draw on
            font: pygame.Font for text rendering
        """
        if not self.show_indicator:
            return
        
        name = self.DIFFICULTY_NAMES[self.difficulty]
        color = self.DIFFICULTY_COLORS[self.difficulty]
        
        text = font.render(name, True, color)
        x = surface.get_width() // 2 - text.get_width() // 2
        y = 10
        
        # God Mode gets a glow effect
        if self.difficulty == GOD_MODE:
            glow = pygame.Surface((text.get_width() + 20, text.get_height() + 10), 
                                  pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 60), glow.get_rect(), border_radius=5)
            surface.blit(glow, (x - 10, y - 5))
        
        surface.blit(text, (x, y))
    
    def get_modifier(self, key, default=None):
        """
        Get a specific modifier value.
        
        Args:
            key: str - Modifier key name
            default: Default value if modifier not present
            
        Returns:
            Modifier value or default
        """
        return self.modifiers.get(key, default)
    
    def should_spawn_god(self):
        """Check if God should spawn in this level."""
        return self.modifiers.get("spawn_god", False)
```

### 3. God Entity (Portable)

**File**: `god_entity.py`

**Purpose**: Standalone God class that can be spawned in any level

**Interface**:

```python
import pygame
import math
import random

class GodEntity:
    """
    Portable God entity that can be spawned in any level.
    Ignores walls, chases player, spawns lightning bolts.
    """
    
    SIZE = 20
    
    def __init__(self, spawn_x=None, spawn_y=None, 
                 speed=0.9, smite_range=85, 
                 lightning_count=5, lightning_cooldown=90):
        """
        Initialize God entity.
        
        Args:
            spawn_x: X spawn position (defaults to screen center-top)
            spawn_y: Y spawn position (defaults to -80, off-screen top)
            speed: Movement speed (pixels per frame)
            smite_range: Instant-kill range (pixels)
            lightning_count: Number of bolts per volley
            lightning_cooldown: Frames between volleys
        """
        # Get screen dimensions from pygame display
        screen = pygame.display.get_surface()
        width = screen.get_width() if screen else 793
        
        if spawn_x is None:
            spawn_x = width // 2 - self.SIZE // 2
        if spawn_y is None:
            spawn_y = -80
        
        self.rect = pygame.Rect(spawn_x, spawn_y, self.SIZE, self.SIZE)
        self.speed = speed
        self.smite_range = smite_range
        self.lightning_count = lightning_count
        self.lightning_cooldown = lightning_cooldown
        self.bolt_timer = lightning_cooldown // 2
        
        # Animation state
        self.anim_index = 0
        self.anim_timer = 0
        self.ANIM_SPEED = 8
        
        # Load sprite frames if available
        self.frames = self._load_frames()
    
    def _load_frames(self):
        """Load God sprite frames (same as TheGarden.py)."""
        try:
            import os
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            sheet = pygame.image.load(
                os.path.join(BASE_DIR, "Sprites", "boss", "bossSprite.png")
            ).convert_alpha()
            
            fw = sheet.get_width() // 5
            fh = sheet.get_height()
            dw, dh = 160, 200
            
            return [
                pygame.transform.scale(
                    sheet.subsurface((fw * i, 0, fw, fh)),
                    (dw, dh)
                )
                for i in range(5)
            ]
        except Exception:
            return []
    
    def update(self, player_rect):
        """
        Update God position (chase player, ignore walls).
        
        Args:
            player_rect: pygame.Rect of player position
        """
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        
        self.rect.x += (dx / dist) * self.speed
        self.rect.y += (dy / dist) * self.speed
        # Intentionally no wall collision
    
    def in_smite_range(self, player_rect):
        """
        Check if player is within instant-kill range.
        
        Args:
            player_rect: pygame.Rect of player position
            
        Returns:
            bool: True if player is in smite range
        """
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        return math.sqrt(dx * dx + dy * dy) < self.smite_range
    
    def try_spawn_bolts(self, player_rect):
        """
        Attempt to spawn lightning bolt volley.
        
        Args:
            player_rect: pygame.Rect of player position
            
        Returns:
            list: List of Lightning objects (empty if on cooldown)
        """
        self.bolt_timer -= 1
        if self.bolt_timer > 0:
            return []
        
        self.bolt_timer = self.lightning_cooldown
        bolts = []
        
        # Get screen dimensions
        screen = pygame.display.get_surface()
        width = screen.get_width() if screen else 793
        height = screen.get_height() if screen else 650
        T = 13  # Tile size
        
        for _ in range(self.lightning_count):
            tx = player_rect.centerx + random.randint(-130, 130)
            ty = player_rect.centery + random.randint(-90, 90)
            tx = max(T * 2, min(width - T * 2, tx))
            ty = max(T * 4, min(height - T * 2, ty))
            bolts.append(Lightning(tx, ty))
        
        return bolts
    
    def draw(self, surface):
        """
        Draw God entity with visual effects.
        
        Args:
            surface: pygame.Surface to draw on
        """
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % max(len(self.frames), 1)
        
        cx, cy = int(self.rect.centerx), int(self.rect.centery)
        ticks = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(ticks / 200)
        
        # Outer pulsing aura
        glow_r = int(80 + 20 * pulse)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 255, 200, int(40 + 30 * pulse)), 
                           glow.get_rect())
        surface.blit(glow, (cx - glow_r, cy - glow_r))
        
        # Radiant lines
        for angle in range(0, 360, 45):
            rad = math.radians(angle + ticks / 10)
            x1 = cx + int(math.cos(rad) * 55)
            y1 = cy + int(math.sin(rad) * 55)
            x2 = cx + int(math.cos(rad) * 75)
            y2 = cy + int(math.sin(rad) * 75)
            pygame.draw.line(surface, (255, 240, 120, 180), (x1, y1), (x2, y2), 2)
        
        # Sprite
        if self.frames:
            frame = self.frames[self.anim_index]
            draw_x = cx - frame.get_width() // 2
            draw_y = cy - frame.get_height() // 2
            surface.blit(frame, (draw_x, draw_y))
        
        # Halo ring
        halo_r = int(28 + 4 * pulse)
        halo_y = cy - (self.frames[0].get_height() // 2) + 10 if self.frames else cy - 50
        halo_surf = pygame.Surface((halo_r * 2 + 10, halo_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(halo_surf, (255, 240, 100, int(160 + 60 * pulse)),
                           halo_surf.get_rect(), 4)
        surface.blit(halo_surf, (cx - halo_r - 5, halo_y - halo_r - 5))


class Lightning:
    """Lightning bolt entity (same as TheGarden.py)."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 60  # Warning phase
        self.strike_timer = 15  # Strike phase
        self.struck = False
    
    def update(self):
        if not self.struck:
            self.timer -= 1
            if self.timer <= 0:
                self.struck = True
        else:
            self.strike_timer -= 1
    
    def is_done(self):
        return self.struck and self.strike_timer <= 0
    
    def get_damage_rect(self):
        if self.struck:
            return pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        return None
    
    def draw(self, surface):
        if not self.struck:
            # Warning indicator
            alpha = int(200 * (1 - self.timer / 60))
            circle = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(circle, (255, 255, 100, alpha), (20, 20), 18, 3)
            surface.blit(circle, (self.x - 20, self.y - 20))
        else:
            # Strike effect
            pygame.draw.circle(surface, (255, 255, 200), (self.x, self.y), 15)
            pygame.draw.circle(surface, (255, 255, 100), (self.x, self.y), 12)
            pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), 8)
```

## Data Models

### Difficulty Configuration Structure

```python
{
    "level_name": {
        "difficulty_mode": {
            "modifier_key": value,
            ...
        }
    }
}
```

### Modifier Keys by Level

**TheNaga**:
- `naga_speed`: float (pixels/frame)
- `item_spawn_multiplier`: float (1.0 = normal)
- `abel_speed`: float (pixels/frame)
- `cain_throw_cooldown_multiplier`: float (1.0 = normal)
- `abel_instant_kill`: bool
- `spawn_god`: bool

**TheTwins**:
- `abel_speed`: float
- `cain_throw_cooldown_multiplier`: float
- `cain_throw_range`: int (tiles)
- `abel_instant_kill`: bool
- `spawn_god`: bool

**TheGuardian**:
- `disable_enrage`: bool
- `light_phase_duration`: int (frames)
- `dark_phase_duration`: int (frames)
- `guardian_chase_speed_multiplier`: float
- `spawn_god`: bool

**TheStatues**:
- `light_phase_duration`: int (frames)
- `dark_phase_duration`: int (frames)
- `statue_speed_multiplier`: float
- `spawn_god`: bool

**TheGarden**:
- `tree_shakes_required`: int
- `lightning_cooldown_multiplier`: float
- `god_speed_multiplier`: float
- `lightning_count`: int
- `god_smite_cooldown_multiplier`: float
- `disable_prior_enemies`: bool

## Error Handling

### Validation Strategy

1. **Startup Validation**: Call `validate_modifiers()` at game initialization
2. **Runtime Checks**: Validate modifier values before application
3. **Fallback Behavior**: Default to Normal Mode on invalid configuration
4. **Logging**: Log all validation errors and fallback actions

### Error Cases

| Error Condition | Handling Strategy |
|----------------|-------------------|
| Invalid key_type | Default to Normal Mode, log warning |
| Missing level in config | Return empty modifiers dict |
| Invalid modifier value | Use baseline value, log error |
| Missing player.held_key | Treat as None, use Normal Mode |
| God spawn failure | Log error, continue without God |

## Testing Strategy

### Unit Tests

**Test Coverage**:
1. `test_key_to_difficulty_mapping()`: Verify all key types map correctly
2. `test_get_modifiers()`: Verify correct modifiers returned for each level/difficulty
3. `test_validate_modifiers()`: Verify validation catches invalid values
4. `test_difficulty_manager_initialization()`: Verify manager reads key correctly
5. `test_god_entity_spawn()`: Verify God spawns with correct parameters
6. `test_god_entity_movement()`: Verify God ignores walls
7. `test_god_smite_range()`: Verify instant-kill range calculation
8. `test_lightning_spawn()`: Verify correct number of bolts spawn

### Integration Tests

**Test Scenarios**:
1. **Easy Mode Naga**: Verify item spawn rate increased, Abel slowed
2. **Hard Mode Twins**: Verify Cain throw frequency doubled, Abel instant-kill
3. **God Mode Spawn**: Verify God spawns in non-Garden levels
4. **Garden Sequence Hard**: Verify tree shakes increased, lightning faster
5. **Difficulty Persistence**: Verify difficulty persists across level transitions
6. **Key Swap Mid-Level**: Verify difficulty doesn't change until next level

### Manual Testing

**Test Plan**:
1. Play through each level with each key type
2. Verify visual difficulty indicator displays correctly
3. Verify God spawns and behaves correctly in all levels
4. Verify instant-kill mechanics work in Hard/God modes
5. Verify timing changes are noticeable but fair
6. Balance testing: Ensure each difficulty is appropriately challenging

### Property-Based Testing

This feature is **not suitable for property-based testing** because:
- It involves game balance and feel (subjective qualities)
- It modifies external game state (enemy AI, spawn rates)
- It depends on player interaction and timing
- The "correctness" of difficulty scaling is a design decision, not a universal property

Instead, we rely on:
- **Unit tests** for configuration validation and modifier application
- **Integration tests** for verifying modifiers affect gameplay correctly
- **Manual playtesting** for balance and feel

## Implementation Notes

### Level Integration Pattern

Each level should follow this pattern:

```python
# At top of level file
from difficulty_manager import DifficultyManager
from god_entity import GodEntity, Lightning

# In main() function, after player initialization
difficulty_mgr = DifficultyManager(player, "TheLevelName")

# Apply modifiers to constants
ENEMY_SPEED = difficulty_mgr.get_modifier("enemy_speed", DEFAULT_SPEED)
SPAWN_RATE = difficulty_mgr.get_modifier("spawn_rate_multiplier", 1.0) * BASE_RATE

# Spawn God if needed
god = None
if difficulty_mgr.should_spawn_god():
    god = GodEntity(
        speed=difficulty_mgr.get_modifier("god_speed_multiplier", 1.0) * 0.9,
        lightning_count=difficulty_mgr.get_modifier("lightning_count", 5)
    )

# In game loop
difficulty_mgr.update()
if god:
    god.update(player.rect)
    if god.in_smite_range(player.rect):
        # Instant kill
        player.lives = 0
    bolts.extend(god.try_spawn_bolts(player.rect))

# In draw function
difficulty_mgr.draw_indicator(surface, font)
if god:
    god.draw(surface)
```

### Baseline Values Reference

| Parameter | Baseline Value | Source |
|-----------|---------------|--------|
| NAGA_SPEED | 5 | TheNaga.py:283 |
| CAIN_SPEED_NORMAL | 2.5 | TheTwins.py:130 |
| ABEL_SPEED_NORMAL | 3.6 | TheTwins.py:132 |
| CAIN_THROW_COOLDOWN | 180 | TheTwins.py:138 |
| CAIN_THROW_RANGE_NORMAL | 8 | TheTwins.py:136 |
| GUARD_SPEED_CHASE | 3.0 | TheGuardian.py:88 |
| PULSE_LIGHT_DURATION | 180 | TheGuardian.py:93 |
| PULSE_DARK_DURATION | 300 | TheGuardian.py:92 |
| STATUE_BASE_SPEED | 1.6 | TheStatues.py:96 |
| GOD_SPEED | 0.9 | TheGarden.py:119 |
| LIGHTNING_COUNT | 5 | TheGarden.py:121 |
| LIGHTNING_COOLDOWN | 90 | TheGarden.py:122 |
| TREE_SHAKE_NEEDED | 3 | TheGarden.py:117 |

### Configuration File Location

Create `.kiro/specs/difficulty-mechanics-implementation/.config.kiro`:

```json
{
  "specId": "2c2b60ed-7b18-4b9d-837f-d988d7e67ab9",
  "workflowType": "requirements-first",
  "specType": "feature"
}
```

## Summary

This design provides a comprehensive, centralized difficulty system that:

1. **Reads player key** at level start to determine difficulty
2. **Applies modifiers** from centralized configuration
3. **Spawns God** in all levels for Divine Key holders
4. **Displays visual feedback** to inform players of active difficulty
5. **Validates configuration** to prevent broken gameplay
6. **Integrates cleanly** with existing level code

The system is designed for easy balancing (all values in one config file), maintainability (clear separation of concerns), and extensibility (easy to add new levels or modifiers).

