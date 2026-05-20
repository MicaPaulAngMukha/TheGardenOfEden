# Requirements Document

## Introduction

The Dynamic Key System with Raziel Dialogue introduces a multi-difficulty key system for the Garden of Eden game. Players can choose between four different keys (Bronze, Gold, Rusted, Divine) that represent different difficulty modes. Each key has unique lore delivered through Raziel's dialogue and narrator text. The system includes key spawning mechanics, dynamic NPC dialogue, pickup interactions, and a key swapping system that allows players to change their difficulty choice.

## Glossary

- **Key_System**: The game subsystem responsible for managing key spawning, pickup, swapping, and inventory
- **Raziel**: The laid-back angel NPC who wanders the Garden of Eden and provides dialogue about the keys
- **Narrator**: The game system that displays descriptive text to the player during key discovery
- **Mikhail_Chase**: The game event that triggers when the player encounters Mikhail, serving as the spawn trigger for all keys
- **Player_Inventory**: The data structure that stores the currently held key (maximum one key at a time)
- **Key_Entity**: A game object representing a physical key in the world that can be picked up or dropped
- **Dialogue_System**: The game subsystem responsible for displaying NPC conversations
- **Pickup_Prompt**: The UI element that asks the player whether to pick up a discovered key

## Requirements

### Requirement 1: Key Spawning

**User Story:** As a player, I want all four keys to spawn after the Mikhail chase is triggered, so that I can choose my preferred difficulty mode.

#### Acceptance Criteria

1. WHEN the Mikhail_Chase event is triggered, THE Key_System SHALL spawn exactly four Key_Entity objects in the game world
2. THE Key_System SHALL spawn one Bronze Key_Entity at a designated bronze key location
3. THE Key_System SHALL spawn one Gold Key_Entity at a designated gold key location
4. THE Key_System SHALL spawn one Rusted Key_Entity at a designated rusted key location
5. THE Key_System SHALL spawn one Divine Key_Entity at a designated divine key location
6. WHEN all four Key_Entity objects are spawned, THE Key_System SHALL make each Key_Entity visible and interactable

### Requirement 2: Raziel Dynamic Dialogue

**User Story:** As a player, I want Raziel to provide changing dialogue about the keys when I talk to him, so that I can learn the lore behind each difficulty option.

#### Acceptance Criteria

1. WHEN the player interacts with Raziel while he is wandering, THE Dialogue_System SHALL display one dialogue entry from Raziel's key dialogue pool
2. THE Dialogue_System SHALL include a general introduction dialogue explaining that Eden has many keys
3. THE Dialogue_System SHALL include a Gold Key dialogue where Raziel admits he dropped it and states nothing is unique about it
4. THE Dialogue_System SHALL include a Bronze Key dialogue telling the story of a young cherub who dropped it and got trapped, connecting to Guardian lore
5. THE Dialogue_System SHALL include a Rusted Key dialogue telling the story of a seraph who dropped it after banishing the player's parents
6. THE Dialogue_System SHALL include a Divine Key dialogue telling the story of watchers who had relations with human women and were banished
7. WHEN the player interacts with Raziel multiple times, THE Dialogue_System SHALL cycle through different dialogue entries from the key dialogue pool

### Requirement 3: Narrator Dialogue for Key Discovery

**User Story:** As a player, I want to see unique narrator text when I discover each key, so that I understand the nature and significance of each key.

#### Acceptance Criteria

1. WHEN the player discovers the Bronze Key_Entity, THE Narrator SHALL display the text "You find a bronze key. It feels light as a feather in your hand."
2. WHEN the player discovers the Gold Key_Entity, THE Narrator SHALL display the text "A golden key.. It looks brand new. It could be Raziel's."
3. WHEN the player discovers the Rusted Key_Entity, THE Narrator SHALL display the text "You find an old key. It's rusted and you're not even sure if it will work anymore."
4. WHEN the player discovers the Divine Key_Entity, THE Narrator SHALL display the text "The key blinks at you. You feel an overwhelming presence..."
5. WHEN the Narrator displays key discovery text, THE Narrator SHALL display a Pickup_Prompt asking "Pick it up?"

### Requirement 4: Key Pickup Choice

**User Story:** As a player, I want to choose whether to pick up or leave a key, so that I can decide if I want to commit to that difficulty mode.

#### Acceptance Criteria

1. WHEN the Pickup_Prompt is displayed, THE Key_System SHALL wait for player input before proceeding
2. WHEN the player confirms the pickup action, THE Key_System SHALL add the Key_Entity to the Player_Inventory
3. WHEN the player confirms the pickup action, THE Key_System SHALL remove the Key_Entity from the game world
4. WHEN the player declines the pickup action, THE Key_System SHALL leave the Key_Entity at its current location in the game world
5. WHEN the player declines the pickup action, THE Key_System SHALL close the Pickup_Prompt

### Requirement 5: Single Key Inventory Constraint

**User Story:** As a player, I want to hold only one key at a time, so that I must commit to a single difficulty choice.

#### Acceptance Criteria

1. THE Player_Inventory SHALL store a maximum of one Key_Entity at any time
2. WHEN the Player_Inventory contains a Key_Entity, THE Key_System SHALL prevent adding additional Key_Entity objects without first removing the existing one
3. WHEN the player attempts to view their inventory, THE Key_System SHALL display the currently held Key_Entity if one exists

### Requirement 6: Key Swapping System

**User Story:** As a player, I want to swap my current key for a different one, so that I can change my difficulty choice if I find another key.

#### Acceptance Criteria

1. WHEN the player holds a Key_Entity in Player_Inventory and discovers a different Key_Entity, THE Key_System SHALL display the Pickup_Prompt for the new Key_Entity
2. WHEN the player confirms pickup of a new Key_Entity while holding an existing Key_Entity, THE Key_System SHALL remove the existing Key_Entity from Player_Inventory
3. WHEN the player confirms pickup of a new Key_Entity while holding an existing Key_Entity, THE Key_System SHALL spawn the previously held Key_Entity at the player's current location
4. WHEN the player confirms pickup of a new Key_Entity while holding an existing Key_Entity, THE Key_System SHALL add the new Key_Entity to Player_Inventory
5. WHEN a Key_Entity is dropped during a swap, THE Key_Entity SHALL remain interactable at the drop location

### Requirement 7: Key Persistence

**User Story:** As a player, I want dropped keys to remain in the world where I left them, so that I can return to pick them up later if I change my mind.

#### Acceptance Criteria

1. WHEN a Key_Entity is dropped at a location, THE Key_System SHALL maintain the Key_Entity at that location until it is picked up again
2. WHEN the player returns to a location containing a dropped Key_Entity, THE Key_Entity SHALL be visible and interactable
3. WHEN the player picks up a previously dropped Key_Entity, THE Key_System SHALL follow the same pickup mechanics as initial key discovery

### Requirement 8: Key Visual Assets

**User Story:** As a developer, I want each key type to have a unique visual representation, so that players can distinguish between difficulty modes.

#### Acceptance Criteria

1. THE Key_System SHALL use bronze_key.png as the sprite for Bronze Key_Entity objects
2. THE Key_System SHALL use Key.png as the sprite for Gold Key_Entity objects
3. THE Key_System SHALL use rusted_key.png as the sprite for Rusted Key_Entity objects
4. THE Key_System SHALL use divine_key.png as the sprite for Divine Key_Entity objects
5. WHEN a Key_Entity is rendered in the game world, THE Key_System SHALL display the appropriate sprite for that key type

### Requirement 9: Character Lore Integration

**User Story:** As a player, I want the Guardian character lore to reflect the bronze key backstory, so that the game narrative is consistent.

#### Acceptance Criteria

1. THE Dialogue_System SHALL update the Guardian character description to reference being the young cherub who dropped the bronze key
2. WHEN the player views the Guardian character information, THE Dialogue_System SHALL display lore consistent with Raziel's bronze key dialogue
