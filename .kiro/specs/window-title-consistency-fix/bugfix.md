# Bugfix Requirements Document

## Introduction

The game window title changes inconsistently as players progress through different scenes. Each scene file independently sets its own window title using `pygame.display.set_caption()`, resulting in the window name changing from "Garden of Eden" to scene-specific titles like "Garden of Eden – Prologue", "Garden of Eden – The Naga's Lair", etc. This inconsistency was noticed by a user's classmate during gameplay. The fix will ensure the window title remains "Garden of Eden" consistently throughout the entire game experience.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the Prologue scene is loaded THEN the system changes the window title to "Garden of Eden – Prologue"

1.2 WHEN TheNaga scene is loaded THEN the system changes the window title to "Garden of Eden – The Naga's Lair"

1.3 WHEN TheTwins scene is loaded THEN the system changes the window title to "Garden of Eden – The Twins"

1.4 WHEN TheGuardian scene is loaded THEN the system changes the window title to "Garden of Eden – The Guardian"

1.5 WHEN TheStatues scene is loaded THEN the system changes the window title to "Garden of Eden – The Statues"

1.6 WHEN TheGarden scene is loaded THEN the system changes the window title to "Garden of Eden – The Garden"

### Expected Behavior (Correct)

2.1 WHEN the Prologue scene is loaded THEN the system SHALL maintain the window title as "Garden of Eden"

2.2 WHEN TheNaga scene is loaded THEN the system SHALL maintain the window title as "Garden of Eden"

2.3 WHEN TheTwins scene is loaded THEN the system SHALL maintain the window title as "Garden of Eden"

2.4 WHEN TheGuardian scene is loaded THEN the system SHALL maintain the window title as "Garden of Eden"

2.5 WHEN TheStatues scene is loaded THEN the system SHALL maintain the window title as "Garden of Eden"

2.6 WHEN TheGarden scene is loaded THEN the system SHALL maintain the window title as "Garden of Eden"

### Unchanged Behavior (Regression Prevention)

3.1 WHEN MainMenuPage is loaded THEN the system SHALL CONTINUE TO set the window title to "Garden of Eden"

3.2 WHEN Start scene is loaded THEN the system SHALL CONTINUE TO set the window title to "Garden of Eden"

3.3 WHEN any scene transition occurs THEN the system SHALL CONTINUE TO function normally without crashes or display issues

3.4 WHEN pygame.display.set_mode() is called in any scene THEN the system SHALL CONTINUE TO create the display window correctly with dimensions 793x650
