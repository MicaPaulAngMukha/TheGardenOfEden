# Bugfix Requirements Document

## Introduction

Raziel is an NPC in the Start scene who should be interactable multiple times throughout different game states. Currently, the player can only interact with Raziel once, after which he becomes permanently non-interactable despite continuing to move around the map. This prevents players from accessing different dialog options that should be available at different stages (before Mikhail interaction, after Mikhail interaction, during roaming, and during chase).

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the player interacts with Raziel for the first time THEN the system increments `raziel.spoken_count` and prevents all subsequent interactions

1.2 WHEN `raziel.spoken_count` reaches value 1 or higher THEN the system blocks the "raziel_before_mikhail" dialog from triggering again

1.3 WHEN `raziel.spoken_count` reaches value 2 or higher THEN the system blocks the "raziel_after_mikhail" and "raziel_after_mikhail_2" dialogs from triggering

1.4 WHEN `raziel.spoken_count` reaches value 3 THEN the system blocks the "raziel_roaming" dialog from triggering again

1.5 WHEN the player approaches Raziel after any interaction THEN the system's conditional logic prevents re-interaction due to mutually exclusive `spoken_count` conditions

### Expected Behavior (Correct)

2.1 WHEN the player approaches Raziel before talking to Mikhail THEN the system SHALL display "raziel_before_mikhail" dialog and allow future interactions

2.2 WHEN the player approaches Raziel after talking to Mikhail (approach >= 1) but before the second Mikhail interaction THEN the system SHALL display "raziel_after_mikhail" dialog and allow future interactions

2.3 WHEN the player approaches Raziel after the second Mikhail interaction (approach >= 2) THEN the system SHALL display "raziel_after_mikhail_2" dialog, start Raziel roaming, and allow future interactions

2.4 WHEN the player approaches Raziel while he is roaming THEN the system SHALL display "raziel_roaming" dialog and allow future interactions with appropriate cooldown

2.5 WHEN the player approaches Raziel during the Mikhail chase sequence THEN the system SHALL display "raziel_during_chase" dialog

2.6 WHEN the player has already seen a specific dialog for the current game state THEN the system SHALL allow re-interaction but display the appropriate dialog for the current game state (not necessarily the same dialog)

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the player interacts with Raziel THEN the system SHALL CONTINUE TO display the correct dialog based on the current game state (Mikhail approach count and chase status)

3.2 WHEN Raziel starts roaming after "raziel_after_mikhail_2" dialog THEN the system SHALL CONTINUE TO make Raziel move around the map with the roaming behavior

3.3 WHEN the raziel_cooldown timer is active (> 0) THEN the system SHALL CONTINUE TO prevent immediate re-interaction until the cooldown expires

3.4 WHEN the player interacts with Raziel during the chase THEN the system SHALL CONTINUE TO pause the chase (`chase_paused = True`) during the dialog

3.5 WHEN Raziel interactions trigger push mechanics THEN the system SHALL CONTINUE TO apply the push effect to the player

3.6 WHEN dialog sequences complete THEN the system SHALL CONTINUE TO return to the STATE_EXPLORE state correctly
