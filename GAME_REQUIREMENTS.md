# Garden of Eden - Game Requirements Document

## 1. Executive Summary

**Game Title:** Garden of Eden  
**Genre:** Action-Adventure, Roguelike, Top-Down  
**Platform:** PC (Windows)  
**Engine:** Pygame  
**Target Audience:** Players who enjoy challenging action games with biblical themes  
**Core Concept:** Navigate through the Garden of Eden, defeat angelic guardians, and reach the Tree of Knowledge while managing difficulty through a key-based system.

---

## 2. Game Overview

### 2.1 Premise
The player is a human descendant of Adam and Eve attempting to infiltrate the Garden of Eden to obtain the Fruit of Knowledge (to pass their midterms). The garden is guarded by angels and supernatural entities who will stop at nothing to prevent humanity from returning.

### 2.2 Core Gameplay Loop
1. Navigate through the prologue area (Start level)
2. Discover and select a difficulty key (Bronze/Gold/Rusted/Divine)
3. Progress through 5 increasingly difficult levels
4. Defeat or evade boss enemies in each level
5. Reach the Tree of Knowledge in the final level

---

## 3. Functional Requirements

### 3.1 Player Character

#### 3.1.1 Movement System
- **FR-PC-001**: Player SHALL move in 4 directions (up, down, left, right) using WASD or arrow keys
- **FR-PC-002**: Player movement speed SHALL be 3-6 pixels per frame depending on level
- **FR-PC-003**: Player SHALL be blocked by walls, obstacles, and closed gates
- **FR-PC-004**: Player collision box SHALL be 14-24 pixels depending on level

#### 3.1.2 Health System
- **FR-PC-005**: Player SHALL start with 3 lives (hearts)
- **FR-PC-006**: Player SHALL lose 1 life when hit by enemies or hazards
- **FR-PC-007**: Player SHALL have invincibility frames (90 frames / 1.5 seconds) after taking damage
- **FR-PC-008**: Player SHALL respawn at level entrance when hit (except instant-kill scenarios)
- **FR-PC-009**: Game SHALL end when player reaches 0 lives

#### 3.1.3 Visual Feedback
- **FR-PC-010**: Player sprite SHALL animate with idle and running states
- **FR-PC-011**: Player SHALL display hurt animation when taking damage
- **FR-PC-012**: Player SHALL flash during invincibility frames
- **FR-PC-013**: Player direction SHALL match movement input (4 directional sprites)

### 3.2 Difficulty System

#### 3.2.1 Key Discovery
- **FR-DIFF-001**: Four keys SHALL spawn after triggering Mikhail's chase in the prologue
- **FR-DIFF-002**: Keys SHALL be hidden until player searches nearby bushes
- **FR-DIFF-003**: Key types SHALL be: Bronze (Easy), Gold (Normal), Rusted (Hard), Divine (God Mode)
- **FR-DIFF-004**: Each key SHALL have a unique sprite and visual appearance

#### 3.2.2 Key Selection
- **FR-DIFF-005**: Player SHALL be prompted to pick up or refuse discovered keys
- **FR-DIFF-006**: Player SHALL be able to hold only one key at a time
- **FR-DIFF-007**: Player SHALL be able to swap keys by picking up a different key
- **FR-DIFF-008**: Dropped keys SHALL remain visible on the ground
- **FR-DIFF-009**: Dropped keys SHALL have a 3-second cooldown before re-pickup

#### 3.2.3 Difficulty Modifiers
- **FR-DIFF-010**: Bronze Key (Easy Mode) SHALL apply the following modifiers:
  - Naga speed: 3.5 (reduced from 5)
  - Item spawn rate: 1.5x
  - Abel speed: 2.5 (reduced from 3.6)
  - Cain throw cooldown: 1.5x longer
  - Guardian enrage: disabled
  - Light phase: 240 frames (increased from 180)
  - Dark phase: 240 frames (reduced from 300)

- **FR-DIFF-011**: Gold Key (Normal Mode) SHALL apply no modifiers (baseline difficulty)

- **FR-DIFF-012**: Rusted Key (Hard Mode) SHALL apply the following modifiers:
  - Naga speed: 7 (increased from 5)
  - Item spawn rate: 0.5x
  - Abel speed: 5.0 (increased from 3.6)
  - Cain throw cooldown: 0.5x shorter
  - Cain throw range: 16 tiles (doubled)
  - Guardian chase speed: 1.5x
  - Light phase: 120 frames (reduced from 180)
  - Dark phase: 420 frames (increased from 300)

- **FR-DIFF-013**: Divine Key (God Mode) SHALL apply the following modifiers:
  - All Hard Mode modifiers
  - Abel instant-kill on catch
  - God entity spawns in all non-Garden levels
  - God can instant-kill player in smite range
  - God spawns lightning bolts

#### 3.2.4 Difficulty Indicator
- **FR-DIFF-014**: Difficulty indicator SHALL NOT be displayed to keep difficulty a surprise
- **FR-DIFF-015**: Player SHALL only know difficulty by observing enemy behavior

### 3.3 Level Progression

#### 3.3.1 Level Structure
- **FR-LEVEL-001**: Game SHALL consist of 6 levels in sequence:
  1. Start (Prologue)
  2. TheNaga
  3. TheTwins
  4. TheGuardian
  5. TheStatues
  6. TheGarden (Final)

- **FR-LEVEL-002**: Player's held key SHALL persist across all level transitions
- **FR-LEVEL-003**: Player's remaining lives SHALL persist across level transitions
- **FR-LEVEL-004**: Each level SHALL have entrance and exit zones
- **FR-LEVEL-005**: Exit SHALL be locked until level objective is completed

#### 3.3.2 Level Objectives
- **FR-LEVEL-006**: Start - Obtain a key and unlock the gate
- **FR-LEVEL-007**: TheNaga - Pull red lever to open exit while evading the Naga
- **FR-LEVEL-008**: TheTwins - Collect 3 prayer fragments per twin and banish both
- **FR-LEVEL-009**: TheGuardian - Find key in bushes while evading Guardian in darkness
- **FR-LEVEL-010**: TheStatues - Solve statue puzzle to open exit
- **FR-LEVEL-011**: TheGarden - Reach the Tree of Knowledge

### 3.4 Enemy Systems

#### 3.4.1 Mikhail (Prologue Angel)
- **FR-ENEMY-001**: Mikhail SHALL guard the gate in the prologue
- **FR-ENEMY-002**: Mikhail SHALL have 3 approach dialogues before chasing
- **FR-ENEMY-003**: Mikhail SHALL chase player after 3rd approach
- **FR-ENEMY-004**: Mikhail chase speed SHALL be 3 pixels per frame
- **FR-ENEMY-005**: Mikhail SHALL push player back on contact
- **FR-ENEMY-006**: Mikhail SHALL deal 1 damage on contact during chase

#### 3.4.2 Raziel (Prologue Angel)
- **FR-ENEMY-007**: Raziel SHALL provide hints about keys through dialogue
- **FR-ENEMY-008**: Raziel SHALL have 5 different key-related dialogues
- **FR-ENEMY-009**: Raziel SHALL cycle through dialogues when approached
- **FR-ENEMY-010**: Raziel SHALL start roaming after 2nd Mikhail approach
- **FR-ENEMY-011**: Raziel SHALL have a 300-frame cooldown between dialogues

#### 3.4.3 The Naga
- **FR-ENEMY-012**: Naga SHALL be a serpent boss with head and tail segments
- **FR-ENEMY-013**: Naga SHALL pathfind toward player using BFS algorithm
- **FR-ENEMY-014**: Naga speed SHALL be modified by difficulty key (3.5-7 pixels/frame)
- **FR-ENEMY-015**: Naga SHALL deal 1 damage on head collision
- **FR-ENEMY-016**: Naga SHALL be frozen temporarily by freeze items
- **FR-ENEMY-017**: Naga SHALL navigate around walls and lever-controlled barriers

#### 3.4.4 Cain (Twin Boss)
- **FR-ENEMY-018**: Cain SHALL throw spears at player from range
- **FR-ENEMY-019**: Cain throw range SHALL be 8-32 tiles depending on difficulty
- **FR-ENEMY-020**: Cain throw cooldown SHALL be 180-60 frames depending on difficulty
- **FR-ENEMY-021**: Cain SHALL enrage when Abel is banished (increased speed)
- **FR-ENEMY-022**: Cain spears SHALL deal 1 damage on hit
- **FR-ENEMY-023**: Cain SHALL pathfind toward player using BFS algorithm

#### 3.4.5 Abel (Twin Boss)
- **FR-ENEMY-024**: Abel SHALL chase player directly (no ranged attacks)
- **FR-ENEMY-025**: Abel speed SHALL be 3.6-5.5 pixels/frame depending on difficulty
- **FR-ENEMY-026**: Abel SHALL stun and push player on first catch
- **FR-ENEMY-027**: Abel SHALL deal 1 damage on subsequent catches
- **FR-ENEMY-028**: Abel SHALL instant-kill on catch in God Mode
- **FR-ENEMY-029**: Abel SHALL enrage when Cain is banished (increased speed)

#### 3.4.6 The Guardian
- **FR-ENEMY-030**: Guardian SHALL patrol in darkness with light/dark cycles
- **FR-ENEMY-031**: Guardian SHALL chase player during light phases
- **FR-ENEMY-032**: Guardian SHALL investigate last known position when hearing bushes
- **FR-ENEMY-033**: Guardian chase speed SHALL be 3.0-4.5 pixels/frame depending on difficulty
- **FR-ENEMY-034**: Guardian SHALL deal 1 damage on contact
- **FR-ENEMY-035**: Dense bushes SHALL alert Guardian with loud sound (5 pixels/frame chase)
- **FR-ENEMY-036**: Light bushes SHALL alert Guardian with quiet sound (3.4 pixels/frame chase)

#### 3.4.7 God Entity (God Mode Only)
- **FR-ENEMY-037**: God SHALL spawn in TheNaga, TheTwins, and TheGuardian levels when player has Divine key
- **FR-ENEMY-038**: God SHALL descend from top of screen after intro dialogue
- **FR-ENEMY-039**: God SHALL follow player at 2 pixels per frame
- **FR-ENEMY-040**: God SHALL instant-kill player within smite range (100 pixels)
- **FR-ENEMY-041**: God SHALL spawn lightning bolts every 90-120 frames
- **FR-ENEMY-042**: Lightning bolts SHALL have 45-frame warning before striking
- **FR-ENEMY-043**: Lightning bolts SHALL deal 1 damage on hit
- **FR-ENEMY-044**: God SHALL have special spawn dialogue in each level

### 3.5 Dialogue System

#### 3.5.1 Dialogue Display
- **FR-DIALOG-001**: Dialogue SHALL display in portrait boxes at bottom of screen
- **FR-DIALOG-002**: Dialogue SHALL use typewriter effect (2 frames per character)
- **FR-DIALOG-003**: Player SHALL be able to skip typewriter effect with Enter/Space
- **FR-DIALOG-004**: Dialogue SHALL pause gameplay during display
- **FR-DIALOG-005**: Each character SHALL have unique portrait and border color

#### 3.5.2 Narrator Dialogue
- **FR-DIALOG-006**: Narrator dialogue SHALL display in centered box without portrait
- **FR-DIALOG-007**: Narrator SHALL provide story context and hints
- **FR-DIALOG-008**: Narrator dialogue SHALL appear in prologue cutscene

#### 3.5.3 God Spawn Dialogue
- **FR-DIALOG-009**: God spawn dialogue SHALL trigger after normal intro dialogue
- **FR-DIALOG-010**: God spawn dialogue SHALL only appear when player has Divine key
- **FR-DIALOG-011**: TheNaga god spawn SHALL have 2 narrator lines: ".... ?" and "!!!!"
- **FR-DIALOG-012**: TheTwins god spawn SHALL have 4 lines alternating between Cain and Abel
- **FR-DIALOG-013**: TheGuardian god spawn SHALL have 2 Guardian lines about capturing player
- **FR-DIALOG-014**: God SHALL descend after god spawn dialogue completes

### 3.6 Interactive Elements

#### 3.6.1 Levers
- **FR-INTERACT-001**: Levers SHALL be activated by pressing 'E' when nearby
- **FR-INTERACT-002**: Levers SHALL toggle colored walls (green/red)
- **FR-INTERACT-003**: Lever state SHALL be visually indicated (on/off)
- **FR-INTERACT-004**: Levers SHALL be used in TheNaga level for progression

#### 3.6.2 Bushes
- **FR-INTERACT-005**: Bushes SHALL hide keys until player searches nearby
- **FR-INTERACT-006**: Bushes SHALL make rustling sound when triggered
- **FR-INTERACT-007**: Dense bushes SHALL alert Guardian with loud sound
- **FR-INTERACT-008**: Light bushes SHALL alert Guardian with quiet sound
- **FR-INTERACT-009**: Each bush SHALL only trigger once per level

#### 3.6.3 Gates and Doors
- **FR-INTERACT-010**: Gates SHALL require keys to unlock
- **FR-INTERACT-011**: Player SHALL be prompted to unlock when near gate with key
- **FR-INTERACT-012**: Locked gates SHALL display "Gate is locked" message
- **FR-INTERACT-013**: Unlocked gates SHALL open permanently
- **FR-INTERACT-014**: Some doors SHALL require multiple kicks to break open (God Mode backtrack)

#### 3.6.4 Prayer Fragments
- **FR-INTERACT-015**: Prayer fragments SHALL spawn in 6 locations in TheTwins level
- **FR-INTERACT-016**: Fragments SHALL be collected automatically on contact
- **FR-INTERACT-017**: 3 fragments SHALL be required to banish each twin
- **FR-INTERACT-018**: Fragment count SHALL be displayed in HUD
- **FR-INTERACT-019**: Fragments SHALL glow when player is nearby (4 tile radius)

#### 3.6.5 Banishment Tiles
- **FR-INTERACT-020**: Banishment tiles SHALL be marked with colored borders
- **FR-INTERACT-021**: Player SHALL press 'E' on banishment tile to banish twin
- **FR-INTERACT-022**: Banishment SHALL require 3 collected fragments
- **FR-INTERACT-023**: Banished twin SHALL disappear and remaining twin SHALL enrage

#### 3.6.6 Items
- **FR-INTERACT-024**: Life items SHALL restore 1 heart when collected
- **FR-INTERACT-025**: Freeze items SHALL freeze Naga for 180 frames (3 seconds)
- **FR-INTERACT-026**: Items SHALL spawn randomly based on difficulty modifier
- **FR-INTERACT-027**: Maximum 3 items SHALL exist on map simultaneously

### 3.7 User Interface

#### 3.7.1 HUD Elements
- **FR-UI-001**: Hearts SHALL display in top-left corner (full/empty states)
- **FR-UI-002**: Held key SHALL display above player's head
- **FR-UI-003**: Fragment counter SHALL display in TheTwins level
- **FR-UI-004**: Interaction prompts SHALL display when near interactive objects
- **FR-UI-005**: Hints SHALL display at bottom-center of screen

#### 3.7.2 Menus and Prompts
- **FR-UI-006**: Game over screen SHALL offer "Retry" and "Quit" options
- **FR-UI-007**: Key pickup prompt SHALL offer "Yes" and "No" options
- **FR-UI-008**: Gate unlock prompt SHALL offer "Yes, unlock it" and "Not yet" options
- **FR-UI-009**: All prompts SHALL use gold text for options

#### 3.7.3 Visual Effects
- **FR-UI-010**: Darkness overlay SHALL be used in TheGuardian level
- **FR-UI-011**: Light radius SHALL be 70 pixels around player in darkness
- **FR-UI-012**: Warning ring SHALL appear when Guardian is nearby (200-60 pixels)
- **FR-UI-013**: Enraged enemies SHALL have red glow effect
- **FR-UI-014**: Invincibility SHALL cause player to flash

### 3.8 Audio System

#### 3.8.1 Music
- **FR-AUDIO-001**: Each level SHALL have unique background music
- **FR-AUDIO-002**: Music SHALL loop continuously during gameplay
- **FR-AUDIO-003**: Music SHALL fade out during level transitions
- **FR-AUDIO-004**: Chase music SHALL play when Mikhail starts chasing
- **FR-AUDIO-005**: Music volume SHALL be adjustable (0.4-0.7 range)

#### 3.8.2 Sound Effects
- **FR-AUDIO-006**: Bush rustle sound SHALL play when bushes are triggered
- **FR-AUDIO-007**: Sound effects SHALL have independent volume control
- **FR-AUDIO-008**: Sound effects SHALL not interrupt music playback

### 3.9 Save System

#### 3.9.1 Progress Persistence
- **FR-SAVE-001**: Game SHALL NOT have save/load functionality (roguelike design)
- **FR-SAVE-002**: Player MUST complete game in single session
- **FR-SAVE-003**: Death SHALL restart from beginning of current level
- **FR-SAVE-004**: Held key and lives SHALL persist within single session

### 3.10 Window and Display

#### 3.10.1 Window Properties
- **FR-DISPLAY-001**: Native resolution SHALL be 793x650 pixels
- **FR-DISPLAY-002**: Window SHALL be resizable
- **FR-DISPLAY-003**: Game SHALL use letterboxing/pillarboxing to maintain aspect ratio
- **FR-DISPLAY-004**: Window title SHALL be "Garden of Eden"
- **FR-DISPLAY-005**: Game SHALL run at 60 FPS

#### 3.10.2 Graphics
- **FR-DISPLAY-006**: Tile size SHALL be 13x13 pixels
- **FR-DISPLAY-007**: Sprite animations SHALL use frame-based timing
- **FR-DISPLAY-008**: All sprites SHALL use alpha transparency
- **FR-DISPLAY-009**: TMX tilemap format SHALL be used for level layouts

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-PERF-001**: Game SHALL maintain 60 FPS on minimum spec hardware
- **NFR-PERF-002**: Level transitions SHALL complete within 2 seconds
- **NFR-PERF-003**: Pathfinding SHALL recalculate every 3-10 frames (not every frame)
- **NFR-PERF-004**: Maximum 100 entities SHALL be active simultaneously

### 4.2 Usability
- **NFR-USE-001**: Controls SHALL be intuitive (WASD/Arrows for movement, E for interact)
- **NFR-USE-002**: All interactive elements SHALL have visual indicators
- **NFR-USE-003**: Dialogue SHALL be skippable to avoid repetition
- **NFR-USE-004**: Game SHALL provide hints for unclear objectives

### 4.3 Reliability
- **NFR-REL-001**: Game SHALL handle missing assets gracefully (placeholder graphics)
- **NFR-REL-002**: Game SHALL not crash on invalid input
- **NFR-REL-003**: Collision detection SHALL be consistent and predictable
- **NFR-REL-004**: Enemy pathfinding SHALL not get stuck in infinite loops

### 4.4 Maintainability
- **NFR-MAINT-001**: Code SHALL be modular with separate files per level
- **NFR-MAINT-002**: Difficulty modifiers SHALL be centralized in difficulty_config.py
- **NFR-MAINT-003**: Dialogue SHALL be stored in dictionaries for easy editing
- **NFR-MAINT-004**: Constants SHALL be defined at top of files

### 4.5 Compatibility
- **NFR-COMPAT-001**: Game SHALL run on Windows 10/11
- **NFR-COMPAT-002**: Game SHALL require Python 3.8+ and Pygame 2.0+
- **NFR-COMPAT-003**: Game SHALL support keyboard input only (no controller)

---

## 5. System Requirements

### 5.1 Minimum Requirements
- **OS**: Windows 10 or later
- **Processor**: Intel Core i3 or equivalent
- **Memory**: 2 GB RAM
- **Graphics**: Integrated graphics with OpenGL 2.0 support
- **Storage**: 100 MB available space
- **Additional**: Python 3.8+, Pygame 2.0+

### 5.2 Recommended Requirements
- **OS**: Windows 11
- **Processor**: Intel Core i5 or equivalent
- **Memory**: 4 GB RAM
- **Graphics**: Dedicated GPU
- **Storage**: 200 MB available space

---

## 6. Testing Requirements

### 6.1 Functional Testing
- **TEST-FUNC-001**: All difficulty modes SHALL be tested for balance
- **TEST-FUNC-002**: All enemy behaviors SHALL be tested in each difficulty
- **TEST-FUNC-003**: All dialogue sequences SHALL be tested for correctness
- **TEST-FUNC-004**: All level transitions SHALL be tested for data persistence
- **TEST-FUNC-005**: Key swap system SHALL be tested for cooldown functionality

### 6.2 Integration Testing
- **TEST-INT-001**: Difficulty system SHALL be tested across all levels
- **TEST-INT-002**: God entity SHALL be tested in all applicable levels
- **TEST-INT-003**: Key persistence SHALL be tested through full playthrough

### 6.3 Performance Testing
- **TEST-PERF-001**: Frame rate SHALL be measured during intense gameplay
- **TEST-PERF-002**: Memory usage SHALL be monitored for leaks
- **TEST-PERF-003**: Pathfinding performance SHALL be tested with multiple enemies

---

## 7. Future Enhancements (Out of Scope)

### 7.1 Potential Features
- Controller support
- Additional difficulty modes
- New game+ mode with carried-over progress
- Achievement system
- Speedrun timer
- Multiple endings based on key choice
- Additional boss phases
- Co-op multiplayer

### 7.2 Quality of Life
- Settings menu for audio/video
- Rebindable controls
- Accessibility options (colorblind mode, text size)
- Tutorial level
- Pause menu

---

## 8. Glossary

- **BFS**: Breadth-First Search pathfinding algorithm
- **FPS**: Frames Per Second
- **HUD**: Heads-Up Display
- **TMX**: Tiled Map XML format
- **Invincibility Frames**: Period after taking damage where player cannot be hurt
- **Enrage**: Enemy state with increased speed/aggression
- **Smite Range**: Distance at which God can instant-kill player
- **Cooldown**: Time period before action can be repeated

---

## 9. Approval

**Document Version**: 1.0  
**Last Updated**: 2026-05-26  
**Status**: Complete

This requirements document covers all implemented features in the Garden of Eden game as of the current build.
