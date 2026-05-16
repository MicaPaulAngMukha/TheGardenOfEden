# Bugfix Requirements Document

## Introduction

In the Start scene, a key hidden in a random bush is required to unlock the gate to Eden. The key is intended to spawn only after Mikhail begins chasing the player, creating tension and urgency in the gameplay. However, the key currently spawns immediately at game initialization (line 714), allowing players to pick it up before triggering the chase sequence. This breaks the intended game flow and removes the challenge of finding the key while being pursued.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the game initializes THEN the system assigns the key to a random bush immediately (line 714: `random.choice(bushes)["has_key"] = True`)

1.2 WHEN the player walks near the bush containing the key before triggering Mikhail's chase THEN the system allows the player to pick up the key prematurely

1.3 WHEN the player picks up the key before the chase is activated THEN the system bypasses the intended gameplay sequence (find key while being chased)

### Expected Behavior (Correct)

2.1 WHEN the game initializes THEN the system SHALL NOT assign the key to any bush

2.2 WHEN Mikhail's chase is activated for the first time (mikhail.chasing becomes True) THEN the system SHALL assign the key to a random bush at that moment

2.3 WHEN the player walks near the bush containing the key after the chase is activated THEN the system SHALL allow the player to pick up the key

2.4 WHEN the key spawns during chase activation THEN the system SHALL ensure it spawns in a bush that is accessible and follows the same random selection logic

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the player has picked up the key THEN the system SHALL CONTINUE TO allow the player to unlock the gate using the key

3.2 WHEN the player interacts with Mikhail multiple times (mikhail.approach >= 3) THEN the system SHALL CONTINUE TO activate the chase sequence

3.3 WHEN the player walks near a bush after the key has spawned THEN the system SHALL CONTINUE TO detect key pickup using `player.check_key_pickup(bushes)`

3.4 WHEN the player has not yet picked up the key THEN the system SHALL CONTINUE TO prevent gate unlocking

3.5 WHEN the chase is activated THEN the system SHALL CONTINUE TO change the music to "12. March of Iron.mp3"

3.6 WHEN the player interacts with Raziel or other game elements THEN the system SHALL CONTINUE TO function normally regardless of key spawn timing
