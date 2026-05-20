# Implementation Plan: Raziel Key Dialogue System

## Overview

This implementation plan breaks down the Raziel Key Dialogue System into discrete coding tasks. The system introduces a multi-difficulty key mechanic with dynamic NPC dialogue, key discovery, pickup/swap mechanics, and inventory management. The implementation extends the existing Start.py game scene and integrates with the current dialogue system, NPC behavior, and player inventory.

## Tasks

- [x] 1. Create KeyEntity class and key spawning system
  - Create KeyEntity class with key_type, position, sprite, and discovered attributes
  - Implement _load_sprite() method with sprite_map for all four key types
  - Implement near_player() method for proximity detection
  - Define KEY_SPAWN_LOCATIONS constant with tile coordinates for all four keys
  - Implement spawn_keys() function that creates and returns list of KeyEntity objects
  - Add error handling for missing sprite files with create_placeholder_sprite() fallback
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 1.1 Write unit tests for KeyEntity and key spawning
  - Test spawn_keys creates exactly 4 keys
  - Test all four key types are spawned
  - Test keys spawn at correct positions
  - Test graceful handling of missing sprites
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 2. Implement Raziel dialogue pool system
  - Add five new dialogue entries to DIALOGS dictionary (raziel_key_intro, raziel_key_gold, raziel_key_bronze, raziel_key_rusted, raziel_key_divine)
  - Create RazielDialoguePool class with dialogue_keys list, current_index, and seen_dialogues set
  - Implement get_next_dialogue() method that cycles through dialogue pool
  - Add error handling for missing dialogue keys with fallback
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [ ]* 2.1 Write unit tests for Raziel dialogue pool
  - Test dialogue pool cycles through all 5 dialogues
  - Test dialogue pool repeats after completing cycle
  - Test seen_dialogues set is updated correctly
  - Test fallback for missing dialogue keys
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [x] 3. Implement key discovery and narrator system
  - Define KEY_NARRATOR_TEXT dictionary with narrator text for all four key types
  - Implement check_key_discovery() function that detects player proximity to undiscovered keys
  - Add STATE_KEY_DISCOVERY and STATE_KEY_PICKUP_PROMPT game states
  - Integrate key discovery check into main game loop during STATE_EXPLORE
  - Display narrator text via typewriter when key is discovered
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 3.1 Write unit tests for key discovery
  - Test key discovery detects nearby keys
  - Test key discovery ignores distant keys
  - Test key discovery ignores already discovered keys
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4. Extend Player class with key inventory
  - Replace Player.has_key boolean with Player.held_key (KeyEntity | None)
  - Implement Player.pickup_key() method that handles key swapping
  - Implement Player.drop_key() method that returns dropped key
  - Implement Player.has_key() method that checks if held_key is not None
  - _Requirements: 5.1, 5.2, 5.3_

- [ ]* 4.1 Write unit tests for player inventory
  - Test player can pick up key when empty
  - Test player swaps keys when already holding one
  - Test drop_key returns the dropped key
  - Test has_key returns correct boolean
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 5. Implement key pickup and swapping logic
  - Implement handle_key_swap() function with validation
  - Add pickup prompt display in STATE_KEY_PICKUP_PROMPT
  - Handle Y/N input for key pickup in event loop
  - On accept: call handle_key_swap() to add key to inventory and drop old key if present
  - On decline: return to STATE_EXPLORE without picking up key
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 5.1 Write unit tests for key swapping
  - Test handle_key_swap drops old key at player location
  - Test handle_key_swap removes new key from world
  - Test handle_key_swap adds new key to inventory
  - Test dropped key has discovered flag reset
  - Test validation for key not in world
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Integrate key spawning with Mikhail chase event
  - Add keys_in_world list to main game loop state
  - Add keys_spawned boolean flag to track spawn state
  - Add logic to spawn keys when mikhail.chasing is True and keys_spawned is False
  - Set keys_spawned flag after spawning keys
  - _Requirements: 1.1_

- [x] 8. Integrate Raziel dialogue pool with NPC interaction
  - Create raziel_dialogue_pool instance in main game loop
  - Replace Raziel's fixed dialogue with raziel_dialogue_pool.get_next_dialogue()
  - Ensure dialogue pool is used during STATE_ANGEL_DIALOG
  - _Requirements: 2.7_

- [x] 9. Implement key rendering and persistence
  - Add key rendering loop that draws all keys in keys_in_world
  - Ensure dropped keys remain in keys_in_world list
  - Ensure dropped keys are rendered at their current positions
  - Add visual key indicator above player when holding a key
  - _Requirements: 7.1, 7.2, 7.3, 8.5_

- [x] 10. Update Guardian character lore
  - Modify CharactersPage.py CHARACTERS list
  - Update Guardian description to reference bronze key backstory
  - Ensure description mentions being trapped in Eden for centuries after dropping the key
  - _Requirements: 9.1, 9.2_

- [x] 11. Final integration and testing
  - Test complete key discovery flow (proximity → narrator text → pickup prompt)
  - Test key swapping flow (hold key → discover new key → swap → old key drops)
  - Test Raziel dialogue cycling through all 5 dialogues
  - Test keys spawn after Mikhail chase
  - Test all four key sprites render correctly
  - Verify Guardian lore update appears in Characters screen
  - _Requirements: All_

- [x] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Unit tests validate specific examples and edge cases
- Property-based testing is NOT used for this feature (see design document for rationale)
- All code examples and implementation should use Python with Pygame
- The system integrates with existing game architecture (Start.py, Typewriter, draw_angel_dialog, draw_narrator_dialog)
- Key sprites already exist in the project root directory
