# Requirements Document

## Introduction

The Difficulty Mechanics Implementation introduces gameplay difficulty scaling based on the four keys (Bronze, Gold, Rusted, Divine) that players can pick up in the Garden of Eden game. Each key represents a different difficulty mode that modifies enemy behavior, spawn rates, timing windows, and challenge intensity across all game levels. The system reads the player's currently held key and applies appropriate difficulty modifiers to enemy AI, item spawning, timing mechanics, and the final Garden sequence.

## Glossary

- **Difficulty_System**: The game subsystem responsible for reading the player's held key and applying difficulty modifiers to game mechanics
- **Player_Inventory**: The data structure that stores the currently held key (player.held_key attribute containing a KeyEntity object)
- **KeyEntity**: A game object representing a physical key with a key_type attribute ("bronze", "gold", "rusted", "divine")
- **Naga_Level**: The first enemy encounter level (TheNaga.py) featuring a snake-like enemy and item spawning mechanics
- **Twins_Level**: The second enemy encounter level (TheTwins.py) featuring Cain (spear thrower) and Abel (chaser)
- **Guardian_Level**: The third enemy encounter level (TheGuardian.py) featuring a guardian angel with light/dark mechanics
- **Statues_Level**: The fourth enemy encounter level (TheStatues.py) featuring moving statue enemies with light pulse mechanics
- **Garden_Sequence**: The final level (TheGarden.py) featuring God as the boss enemy and lightning bolt mechanics
- **Easy_Mode**: Difficulty mode activated when player holds the Bronze Key
- **Normal_Mode**: Difficulty mode activated when player holds the Gold Key (baseline game behavior)
- **Hard_Mode**: Difficulty mode activated when player holds the Rusted Key
- **God_Mode**: Difficulty mode activated when player holds the Divine Key

## Requirements

### Requirement 1: Difficulty System Initialization

**User Story:** As a developer, I want the difficulty system to read the player's held key at level start, so that the appropriate difficulty modifiers are applied throughout the level.

#### Acceptance Criteria

1. WHEN a game level initializes, THE Difficulty_System SHALL read the player.held_key attribute from Player_Inventory
2. WHEN player.held_key is None, THE Difficulty_System SHALL default to Normal_Mode difficulty
3. WHEN player.held_key contains a KeyEntity, THE Difficulty_System SHALL extract the key_type attribute
4. WHEN key_type is "bronze", THE Difficulty_System SHALL activate Easy_Mode modifiers
5. WHEN key_type is "gold", THE Difficulty_System SHALL activate Normal_Mode modifiers
6. WHEN key_type is "rusted", THE Difficulty_System SHALL activate Hard_Mode modifiers
7. WHEN key_type is "divine", THE Difficulty_System SHALL activate God_Mode modifiers

### Requirement 2: Naga Level Easy Mode Modifications

**User Story:** As a player holding the Bronze Key, I want the Naga level to be easier, so that I can progress through the game with reduced challenge.

#### Acceptance Criteria

1. WHEN Easy_Mode is active in Naga_Level, THE Difficulty_System SHALL increase item spawn frequency by 50 percent
2. WHEN Easy_Mode is active in Naga_Level, THE Difficulty_System SHALL reduce Abel's movement speed from 3.6 to 2.5 pixels per frame
3. WHEN Easy_Mode is active in Naga_Level, THE Difficulty_System SHALL reduce Cain's spear throw frequency by 50 percent

### Requirement 3: Naga Level Hard Mode Modifications

**User Story:** As a player holding the Rusted Key, I want the Naga level to be more challenging, so that I experience increased difficulty.

#### Acceptance Criteria

1. WHEN Hard_Mode is active in Naga_Level, THE Difficulty_System SHALL increase Naga movement speed from 5 to 6 pixels per frame
2. WHEN Hard_Mode is active in Naga_Level, THE Difficulty_System SHALL decrease item spawn frequency by 50 percent
3. WHEN Hard_Mode is active in Naga_Level, THE Difficulty_System SHALL increase Cain's spear throw frequency by 100 percent
4. WHEN Hard_Mode is active in Naga_Level, THE Difficulty_System SHALL enable Abel instant-kill on contact

### Requirement 4: Twins Level Easy Mode Modifications

**User Story:** As a player holding the Bronze Key, I want the Twins level to be easier, so that I can manage the dual enemy encounter more comfortably.

#### Acceptance Criteria

1. WHEN Easy_Mode is active in Twins_Level, THE Difficulty_System SHALL reduce Abel's movement speed from 3.6 to 2.5 pixels per frame
2. WHEN Easy_Mode is active in Twins_Level, THE Difficulty_System SHALL reduce Cain's spear throw frequency by 50 percent
3. WHEN Easy_Mode is active in Twins_Level, THE Difficulty_System SHALL reduce Cain's spear throw range from 8 tiles to 6 tiles

### Requirement 5: Twins Level Hard Mode Modifications

**User Story:** As a player holding the Rusted Key, I want the Twins level to be more challenging, so that the dual enemy encounter tests my skills.

#### Acceptance Criteria

1. WHEN Hard_Mode is active in Twins_Level, THE Difficulty_System SHALL increase Cain's spear throw frequency by 100 percent
2. WHEN Hard_Mode is active in Twins_Level, THE Difficulty_System SHALL increase Cain's spear throw range from 8 tiles to 12 tiles
3. WHEN Hard_Mode is active in Twins_Level, THE Difficulty_System SHALL enable Abel instant-kill on contact

### Requirement 6: Guardian Level Easy Mode Modifications

**User Story:** As a player holding the Bronze Key, I want the Guardian level to be easier, so that the stealth mechanics are more forgiving.

#### Acceptance Criteria

1. WHEN Easy_Mode is active in Guardian_Level, THE Difficulty_System SHALL disable Guardian enrage behavior when player makes noise
2. WHEN Easy_Mode is active in Guardian_Level, THE Difficulty_System SHALL maintain Guardian normal speed regardless of player actions

### Requirement 7: Guardian Level Hard Mode Modifications

**User Story:** As a player holding the Rusted Key, I want the Guardian level to be more challenging, so that stealth mechanics require greater precision.

#### Acceptance Criteria

1. WHEN Hard_Mode is active in Guardian_Level, THE Difficulty_System SHALL reduce light phase duration from 180 frames to 120 frames
2. WHEN Hard_Mode is active in Guardian_Level, THE Difficulty_System SHALL increase dark phase duration from 300 frames to 420 frames
3. WHEN Hard_Mode is active in Guardian_Level, THE Difficulty_System SHALL increase Guardian chase speed by 20 percent

### Requirement 8: Statues Level Easy Mode Modifications

**User Story:** As a player holding the Bronze Key, I want the Statues level to be easier, so that I have more time to navigate during light phases.

#### Acceptance Criteria

1. WHEN Easy_Mode is active in Statues_Level, THE Difficulty_System SHALL increase light phase duration from 180 frames to 240 frames
2. WHEN Easy_Mode is active in Statues_Level, THE Difficulty_System SHALL reduce statue movement speed by 20 percent

### Requirement 9: Statues Level Hard Mode Modifications

**User Story:** As a player holding the Rusted Key, I want the Statues level to be more challenging, so that light phases are shorter and more intense.

#### Acceptance Criteria

1. WHEN Hard_Mode is active in Statues_Level, THE Difficulty_System SHALL reduce light phase duration from 180 frames to 120 frames
2. WHEN Hard_Mode is active in Statues_Level, THE Difficulty_System SHALL increase dark phase duration from 300 frames to 420 frames
3. WHEN Hard_Mode is active in Statues_Level, THE Difficulty_System SHALL increase statue movement speed by 20 percent

### Requirement 10: Garden Sequence Easy Mode Modifications

**User Story:** As a player holding the Bronze Key, I want the Garden sequence to be easier, so that the final challenge is more manageable.

#### Acceptance Criteria

1. WHEN Easy_Mode is active in Garden_Sequence, THE Difficulty_System SHALL reduce required tree shakes from 5 to 3
2. WHEN Easy_Mode is active in Garden_Sequence, THE Difficulty_System SHALL increase time gap between lightning bolt volleys by 50 percent
3. WHEN Easy_Mode is active in Garden_Sequence, THE Difficulty_System SHALL reduce God movement speed by 20 percent

### Requirement 11: Garden Sequence Hard Mode Modifications

**User Story:** As a player holding the Rusted Key, I want the Garden sequence to be more challenging, so that the final encounter tests my mastery.

#### Acceptance Criteria

1. WHEN Hard_Mode is active in Garden_Sequence, THE Difficulty_System SHALL increase required tree shakes from 5 to 7
2. WHEN Hard_Mode is active in Garden_Sequence, THE Difficulty_System SHALL reduce time gap between lightning bolt volleys by 30 percent
3. WHEN Hard_Mode is active in Garden_Sequence, THE Difficulty_System SHALL increase God movement speed by 30 percent
4. WHEN Hard_Mode is active in Garden_Sequence, THE Difficulty_System SHALL increase lightning bolt count per volley from 5 to 7

### Requirement 12: God Mode Immediate Spawn

**User Story:** As a player holding the Divine Key, I want God to spawn immediately at level start, so that I face the ultimate challenge from the beginning.

#### Acceptance Criteria

1. WHEN God_Mode is active in Naga_Level, THE Difficulty_System SHALL spawn God at level initialization
2. WHEN God_Mode is active in Twins_Level, THE Difficulty_System SHALL spawn God at level initialization
3. WHEN God_Mode is active in Guardian_Level, THE Difficulty_System SHALL spawn God at level initialization
4. WHEN God_Mode is active in Statues_Level, THE Difficulty_System SHALL spawn God at level initialization
5. WHEN God spawns in a pre-Garden level, THE Difficulty_System SHALL maintain all existing level enemies as active

### Requirement 13: God Mode Garden Sequence Modifications

**User Story:** As a player holding the Divine Key, I want the Garden sequence to be extremely challenging, so that I face the hardest possible final encounter.

#### Acceptance Criteria

1. WHEN God_Mode is active in Garden_Sequence, THE Difficulty_System SHALL increase lightning bolt count per volley from 5 to 9
2. WHEN God_Mode is active in Garden_Sequence, THE Difficulty_System SHALL reduce time gap between lightning bolt volleys by 50 percent
3. WHEN God_Mode is active in Garden_Sequence, THE Difficulty_System SHALL increase God movement speed by 50 percent
4. WHEN God_Mode is active in Garden_Sequence, THE Difficulty_System SHALL increase God aggression by reducing smite range cooldown by 40 percent
5. WHEN God_Mode is active in Garden_Sequence, THE Difficulty_System SHALL disable all prior level enemies

### Requirement 14: Difficulty Persistence Across Levels

**User Story:** As a player, I want my chosen difficulty to persist across all game levels, so that my key choice affects the entire playthrough.

#### Acceptance Criteria

1. WHEN a player completes a level, THE Difficulty_System SHALL preserve the player.held_key attribute
2. WHEN a player transitions to the next level, THE Difficulty_System SHALL read the preserved player.held_key attribute
3. WHEN a player swaps keys during a level, THE Difficulty_System SHALL apply new difficulty modifiers on the next level transition
4. THE Difficulty_System SHALL NOT change difficulty modifiers mid-level when player swaps keys

### Requirement 15: Normal Mode Baseline Behavior

**User Story:** As a player holding the Gold Key, I want to experience the game as originally designed, so that I have the intended baseline difficulty.

#### Acceptance Criteria

1. WHEN Normal_Mode is active in any level, THE Difficulty_System SHALL apply no modifications to enemy behavior
2. WHEN Normal_Mode is active in any level, THE Difficulty_System SHALL apply no modifications to spawn rates
3. WHEN Normal_Mode is active in any level, THE Difficulty_System SHALL apply no modifications to timing mechanics
4. WHEN Normal_Mode is active in any level, THE Difficulty_System SHALL apply no modifications to the Garden_Sequence
5. THE Difficulty_System SHALL treat Normal_Mode as the reference implementation for all difficulty calculations

### Requirement 16: Difficulty Modifier Validation

**User Story:** As a developer, I want the difficulty system to validate all modifier values, so that invalid configurations do not break gameplay.

#### Acceptance Criteria

1. WHEN the Difficulty_System applies a speed modifier, THE Difficulty_System SHALL ensure the resulting speed is greater than zero
2. WHEN the Difficulty_System applies a frequency modifier, THE Difficulty_System SHALL ensure the resulting frequency is greater than zero
3. WHEN the Difficulty_System applies a duration modifier, THE Difficulty_System SHALL ensure the resulting duration is at least 30 frames
4. WHEN the Difficulty_System encounters an invalid key_type, THE Difficulty_System SHALL default to Normal_Mode and log a warning
5. WHEN the Difficulty_System applies a range modifier, THE Difficulty_System SHALL ensure the resulting range is at least 1 tile

### Requirement 17: God Entity Integration

**User Story:** As a developer, I want God to be spawnable in any level, so that God Mode can function across all game stages.

#### Acceptance Criteria

1. THE Difficulty_System SHALL provide a God class that can be instantiated in any game level
2. WHEN God is spawned in a non-Garden level, THE God entity SHALL use the same movement and attack patterns as in Garden_Sequence
3. WHEN God is spawned in a non-Garden level, THE God entity SHALL ignore all wall collision detection
4. WHEN God is spawned in a non-Garden level, THE God entity SHALL spawn lightning bolts at the same frequency as in Garden_Sequence
5. WHEN God is spawned in a non-Garden level, THE God entity SHALL trigger instant-kill on contact with player within smite range

### Requirement 18: Difficulty Indicator Display

**User Story:** As a player, I want to see which difficulty mode is active, so that I understand the current challenge level.

#### Acceptance Criteria

1. WHEN a level starts, THE Difficulty_System SHALL display the active difficulty mode name for 3 seconds
2. WHEN Easy_Mode is active, THE Difficulty_System SHALL display "Bronze Key - Easy Mode" in bronze color
3. WHEN Normal_Mode is active, THE Difficulty_System SHALL display "Gold Key - Normal Mode" in gold color
4. WHEN Hard_Mode is active, THE Difficulty_System SHALL display "Rusted Key - Hard Mode" in rust color
5. WHEN God_Mode is active, THE Difficulty_System SHALL display "Divine Key - God Mode" in white color with glow effect
6. THE Difficulty_System SHALL display the difficulty indicator in the top-center of the screen

### Requirement 19: Difficulty Testing Support

**User Story:** As a developer, I want to test each difficulty mode independently, so that I can verify all modifiers work correctly.

#### Acceptance Criteria

1. THE Difficulty_System SHALL provide a test mode that allows setting difficulty without requiring a key
2. WHEN test mode is enabled, THE Difficulty_System SHALL accept a difficulty parameter ("easy", "normal", "hard", "god")
3. WHEN test mode is enabled, THE Difficulty_System SHALL log all applied modifiers to the console
4. THE Difficulty_System SHALL disable test mode in production builds
5. THE Difficulty_System SHALL provide a command-line flag to enable test mode during development

### Requirement 20: Difficulty Configuration Centralization

**User Story:** As a developer, I want all difficulty modifiers defined in a central configuration, so that balancing changes are easy to implement.

#### Acceptance Criteria

1. THE Difficulty_System SHALL define all difficulty modifiers in a single configuration dictionary
2. THE Difficulty_System SHALL organize modifiers by level and difficulty mode
3. THE Difficulty_System SHALL provide a function to retrieve modifiers for a given level and difficulty
4. THE Difficulty_System SHALL validate the configuration dictionary at game startup
5. THE Difficulty_System SHALL log any missing or invalid configuration entries
