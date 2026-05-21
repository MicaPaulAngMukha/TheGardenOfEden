# Implementation Plan: Difficulty Mechanics Implementation

## Overview

This implementation plan breaks down the difficulty mechanics system into discrete coding tasks. The system reads the player's held key at level initialization and applies appropriate difficulty modifiers to enemy behavior, spawn rates, timing mechanics, and the final Garden sequence. The implementation follows a modular approach with centralized configuration, a difficulty manager for state management, and a portable God entity that can spawn in any level.

## Tasks

- [x] 1. Create DifficultyConfig module with centralized configuration
  - Create `difficulty_config.py` file in the project root
  - Define difficulty mode constants (EASY, NORMAL, HARD, GOD_MODE)
  - Define KEY_TO_DIFFICULTY mapping dictionary
  - Define DIFFICULTY_MODIFIERS nested dictionary with all level-specific modifiers
  - Implement `get_difficulty_from_key(key_entity)` function
  - Implement `get_modifiers(level_name, difficulty)` function
  - Implement `validate_modifiers()` function with validation rules
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 16.1, 16.2, 16.3, 16.4, 16.5, 20.1, 20.2, 20.3, 20.4, 20.5_

- [ ]* 1.1 Write unit tests for DifficultyConfig module
  - Test key-to-difficulty mapping for all key types
  - Test get_modifiers returns correct values for each level/difficulty combination
  - Test validate_modifiers catches invalid speed values
  - Test validate_modifiers catches invalid frequency values
  - Test validate_modifiers catches invalid duration values
  - Test validate_modifiers catches invalid range values
  - Test fallback to Normal Mode on invalid key_type
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [x] 2. Create DifficultyManager class for state management
  - Create `difficulty_manager.py` file in the project root
  - Import necessary modules (pygame, difficulty_config)
  - Define DIFFICULTY_COLORS dictionary with color values for each mode
  - Define DIFFICULTY_NAMES dictionary with display names
  - Implement `__init__(player, level_name)` method
  - Implement `update()` method for indicator timer
  - Implement `draw_indicator(surface, font)` method with God Mode glow effect
  - Implement `get_modifier(key, default)` method
  - Implement `should_spawn_god()` method
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6_

- [ ]* 2.1 Write unit tests for DifficultyManager class
  - Test initialization reads player.held_key correctly
  - Test difficulty mode is determined correctly from key_type
  - Test get_modifier returns correct values
  - Test get_modifier returns default when key not present
  - Test should_spawn_god returns True for God Mode
  - Test should_spawn_god returns False for other modes
  - Test indicator timer counts down correctly
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 3. Create portable GodEntity class
  - Create `god_entity.py` file in the project root
  - Import necessary modules (pygame, math, random)
  - Define GodEntity class with SIZE constant
  - Implement `__init__` method with configurable parameters (spawn_x, spawn_y, speed, smite_range, lightning_count, lightning_cooldown)
  - Implement `_load_frames()` method to load God sprite frames
  - Implement `update(player_rect)` method for wall-ignoring chase behavior
  - Implement `in_smite_range(player_rect)` method for instant-kill range check
  - Implement `try_spawn_bolts(player_rect)` method for lightning volley spawning
  - Implement `draw(surface)` method with visual effects (aura, radiant lines, halo)
  - Define Lightning class with warning and strike phases
  - Implement Lightning `update()`, `is_done()`, `get_damage_rect()`, and `draw()` methods
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 17.1, 17.2, 17.3, 17.4, 17.5_

- [ ]* 3.1 Write unit tests for GodEntity class
  - Test God spawns with correct default position
  - Test God spawns with custom position parameters
  - Test God movement ignores walls (no collision detection)
  - Test in_smite_range calculates distance correctly
  - Test try_spawn_bolts respects cooldown timer
  - Test try_spawn_bolts spawns correct number of bolts
  - Test Lightning warning phase duration
  - Test Lightning strike phase duration
  - Test Lightning damage rect is only active during strike
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Integrate difficulty system with TheNaga.py
  - Import DifficultyManager and GodEntity at top of TheNaga.py
  - After player initialization, create DifficultyManager instance with level name "TheNaga"
  - Apply NAGA_SPEED modifier using get_modifier("naga_speed", 5)
  - Apply item_spawn_multiplier to item spawn logic
  - Apply abel_speed modifier to Abel's movement speed
  - Apply cain_throw_cooldown_multiplier to Cain's throw cooldown
  - Check abel_instant_kill modifier and implement instant-kill on contact if True
  - Check should_spawn_god() and spawn GodEntity if True
  - In game loop, call difficulty_mgr.update()
  - In game loop, update God entity if spawned (god.update(player.rect))
  - In game loop, check God smite range and trigger instant-kill if in range
  - In game loop, spawn lightning bolts from God (bolts.extend(god.try_spawn_bolts(player.rect)))
  - In draw function, call difficulty_mgr.draw_indicator(game_surface, font)
  - In draw function, draw God entity if spawned (god.draw(game_surface))
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 12.1, 12.5, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 18.1, 18.2, 18.6_

- [ ]* 5.1 Write integration tests for TheNaga difficulty integration
  - Test Easy Mode increases item spawn rate by 50%
  - Test Easy Mode reduces Abel speed to 2.5
  - Test Easy Mode reduces Cain throw frequency by 50%
  - Test Hard Mode increases Naga speed to 6
  - Test Hard Mode decreases item spawn rate by 50%
  - Test Hard Mode increases Cain throw frequency by 100%
  - Test Hard Mode enables Abel instant-kill
  - Test God Mode spawns God entity
  - Test Normal Mode applies no modifiers
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 6. Integrate difficulty system with TheTwins.py
  - Import DifficultyManager and GodEntity at top of TheTwins.py
  - After player initialization, create DifficultyManager instance with level name "TheTwins"
  - Apply abel_speed modifier to Abel's movement speed
  - Apply cain_throw_cooldown_multiplier to Cain's throw cooldown
  - Apply cain_throw_range modifier to Cain's throw range
  - Check abel_instant_kill modifier and implement instant-kill on contact if True
  - Check should_spawn_god() and spawn GodEntity if True
  - In game loop, call difficulty_mgr.update()
  - In game loop, update God entity if spawned
  - In game loop, check God smite range and trigger instant-kill if in range
  - In game loop, spawn lightning bolts from God
  - In draw function, call difficulty_mgr.draw_indicator(game_surface, font)
  - In draw function, draw God entity if spawned
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 12.2, 12.5, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 18.1, 18.3, 18.6_

- [ ]* 6.1 Write integration tests for TheTwins difficulty integration
  - Test Easy Mode reduces Abel speed to 2.5
  - Test Easy Mode reduces Cain throw frequency by 50%
  - Test Easy Mode reduces Cain throw range to 6 tiles
  - Test Hard Mode increases Cain throw frequency by 100%
  - Test Hard Mode increases Cain throw range to 12 tiles
  - Test Hard Mode enables Abel instant-kill
  - Test God Mode spawns God entity
  - Test Normal Mode applies no modifiers
  - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 7. Integrate difficulty system with TheGuardian.py
  - Import DifficultyManager and GodEntity at top of TheGuardian.py
  - After player initialization, create DifficultyManager instance with level name "TheGuardian"
  - Apply disable_enrage modifier to Guardian enrage behavior
  - Apply light_phase_duration modifier to light phase timing
  - Apply dark_phase_duration modifier to dark phase timing
  - Apply guardian_chase_speed_multiplier to Guardian chase speed
  - Check should_spawn_god() and spawn GodEntity if True
  - In game loop, call difficulty_mgr.update()
  - In game loop, update God entity if spawned
  - In game loop, check God smite range and trigger instant-kill if in range
  - In game loop, spawn lightning bolts from God
  - In draw function, call difficulty_mgr.draw_indicator(game_surface, font)
  - In draw function, draw God entity if spawned
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 6.1, 6.2, 7.1, 7.2, 7.3, 12.3, 12.5, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 18.1, 18.4, 18.6_

- [ ]* 7.1 Write integration tests for TheGuardian difficulty integration
  - Test Easy Mode disables Guardian enrage behavior
  - Test Hard Mode reduces light phase duration to 120 frames
  - Test Hard Mode increases dark phase duration to 420 frames
  - Test Hard Mode increases Guardian chase speed by 20%
  - Test God Mode spawns God entity
  - Test Normal Mode applies no modifiers
  - _Requirements: 6.1, 6.2, 7.1, 7.2, 7.3, 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 8. Integrate difficulty system with TheStatues.py
  - Import DifficultyManager and GodEntity at top of TheStatues.py
  - After player initialization, create DifficultyManager instance with level name "TheStatues"
  - Apply light_phase_duration modifier to light phase timing
  - Apply dark_phase_duration modifier to dark phase timing
  - Apply statue_speed_multiplier to statue movement speed
  - Check should_spawn_god() and spawn GodEntity if True
  - In game loop, call difficulty_mgr.update()
  - In game loop, update God entity if spawned
  - In game loop, check God smite range and trigger instant-kill if in range
  - In game loop, spawn lightning bolts from God
  - In draw function, call difficulty_mgr.draw_indicator(game_surface, font)
  - In draw function, draw God entity if spawned
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 8.1, 8.2, 9.1, 9.2, 9.3, 12.4, 12.5, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 18.1, 18.4, 18.6_

- [ ]* 8.1 Write integration tests for TheStatues difficulty integration
  - Test Easy Mode increases light phase duration to 240 frames
  - Test Easy Mode reduces statue speed by 20%
  - Test Hard Mode reduces light phase duration to 120 frames
  - Test Hard Mode increases dark phase duration to 420 frames
  - Test Hard Mode increases statue speed by 20%
  - Test God Mode spawns God entity
  - Test Normal Mode applies no modifiers
  - _Requirements: 8.1, 8.2, 9.1, 9.2, 9.3, 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Integrate difficulty system with TheGarden.py
  - Import DifficultyManager at top of TheGarden.py (God already exists in this level)
  - After player initialization, create DifficultyManager instance with level name "TheGarden"
  - Apply tree_shakes_required modifier to tree shake counter
  - Apply lightning_cooldown_multiplier to God's lightning cooldown
  - Apply god_speed_multiplier to God's movement speed
  - Apply lightning_count modifier to number of bolts per volley
  - Apply god_smite_cooldown_multiplier to God's smite cooldown
  - Check disable_prior_enemies modifier and disable Naga/Cain/Abel/Guardian/Statues if True
  - In game loop, call difficulty_mgr.update()
  - In draw function, call difficulty_mgr.draw_indicator(game_surface, font)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 10.1, 10.2, 10.3, 11.1, 11.2, 11.3, 11.4, 13.1, 13.2, 13.3, 13.4, 13.5, 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 18.1, 18.5, 18.6_

- [ ]* 10.1 Write integration tests for TheGarden difficulty integration
  - Test Easy Mode reduces tree shakes required to 3
  - Test Easy Mode increases lightning cooldown by 50%
  - Test Easy Mode reduces God speed by 20%
  - Test Hard Mode increases tree shakes required to 7
  - Test Hard Mode reduces lightning cooldown by 30%
  - Test Hard Mode increases God speed by 30%
  - Test Hard Mode increases lightning count to 7
  - Test God Mode increases lightning count to 9
  - Test God Mode reduces lightning cooldown by 50%
  - Test God Mode increases God speed by 50%
  - Test God Mode reduces smite cooldown by 40%
  - Test God Mode disables prior enemies
  - Test Normal Mode applies no modifiers
  - _Requirements: 10.1, 10.2, 10.3, 11.1, 11.2, 11.3, 11.4, 13.1, 13.2, 13.3, 13.4, 13.5, 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 11. Add startup validation and error handling
  - In main game initialization file, import difficulty_config
  - Call validate_modifiers() at game startup
  - Log any validation errors to console
  - Add error handling for missing player.held_key attribute
  - Add error handling for invalid key_type values
  - Add fallback to Normal Mode on any configuration errors
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 20.4, 20.5_

- [ ]* 11.1 Write unit tests for error handling
  - Test validation catches speed values <= 0
  - Test validation catches frequency values <= 0
  - Test validation catches duration values < 30
  - Test validation catches range values < 1
  - Test fallback to Normal Mode on invalid key_type
  - Test fallback to Normal Mode on missing player.held_key
  - Test error logging for invalid configurations
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [x] 12. Final checkpoint - Ensure all tests pass and verify integration
  - Run all unit tests and ensure they pass
  - Run all integration tests and ensure they pass
  - Verify difficulty indicator displays correctly in each level
  - Verify God spawns correctly in non-Garden levels for God Mode
  - Verify all difficulty modifiers are applied correctly
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Unit tests validate configuration and individual components
- Integration tests validate modifiers affect gameplay correctly
- The design explicitly states this feature is not suitable for property-based testing due to subjective game balance considerations
- All difficulty modifiers are centralized in `difficulty_config.py` for easy balancing
- The GodEntity class is portable and can be spawned in any level
- Difficulty persists across level transitions based on player.held_key
- Normal Mode (Gold Key) represents the baseline game behavior with no modifiers
