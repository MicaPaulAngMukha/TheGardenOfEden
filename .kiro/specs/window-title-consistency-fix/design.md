# Window Title Consistency Bugfix Design

## Overview

This bugfix addresses inconsistent window titles across different game scenes. Currently, six scene files (Prologue.py, TheNaga.py, TheTwins.py, TheGuardian.py, TheStatues.py, TheGarden.py) each call `pygame.display.set_caption()` with scene-specific titles, causing the window title to change as players progress through the game. The fix will remove these redundant `set_caption()` calls, allowing the window title to remain "Garden of Eden" consistently throughout gameplay. This is a minimal, surgical fix that only removes the offending lines without altering any other functionality.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when any of the six scene files loads and calls `pygame.display.set_caption()` with a scene-specific title
- **Property (P)**: The desired behavior - the window title should remain "Garden of Eden" regardless of which scene is active
- **Preservation**: Existing scene initialization, display window creation, and scene transitions that must remain unchanged by the fix
- **pygame.display.set_caption()**: The pygame function that sets the window title text
- **Scene file**: A Python module that implements a specific game scene (e.g., TheNaga.py, TheTwins.py)
- **Module-level initialization**: Code that runs when a Python module is imported, typically at the top of the file

## Bug Details

### Bug Condition

The bug manifests when any of the six affected scene files is imported or executed. Each file contains a module-level call to `pygame.display.set_caption()` that overwrites the window title with a scene-specific name. The root cause is redundant title-setting code in scene files that should rely on the initial title set by MainMenuPage.py or Start.py.

**Formal Specification:**
```
FUNCTION isBugCondition(sceneFile)
  INPUT: sceneFile of type PythonModule
  OUTPUT: boolean
  
  RETURN sceneFile.name IN ['Prologue.py', 'TheNaga.py', 'TheTwins.py', 
                             'TheGuardian.py', 'TheStatues.py', 'TheGarden.py']
         AND sceneFile.contains('pygame.display.set_caption')
         AND sceneFile.captionValue != "Garden of Eden"
END FUNCTION
```

### Examples

- **Prologue.py (line 399)**: `pygame.display.set_caption("Garden of Eden – Prologue")` changes title when Prologue scene's main() function is called
- **TheNaga.py (line 15)**: `pygame.display.set_caption("Garden of Eden – The Naga's Lair")` changes title when TheNaga module is imported
- **TheTwins.py (line 16)**: `pygame.display.set_caption("Garden of Eden – The Twins")` changes title when TheTwins module is imported
- **TheGuardian.py (line 16)**: `pygame.display.set_caption("Garden of Eden – The Guardian")` changes title when TheGuardian module is imported
- **TheStatues.py (line 15)**: `pygame.display.set_caption("Garden of Eden – The Statues")` changes title when TheStatues module is imported
- **TheGarden.py (line 13)**: `pygame.display.set_caption("Garden of Eden – The Garden")` changes title when TheGarden module is imported

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- MainMenuPage.py must continue to set the window title to "Garden of Eden" on initial load
- Start.py must continue to set the window title to "Garden of Eden" when the start scene loads
- All scene transitions must continue to function normally without crashes or display issues
- pygame.display.set_mode() calls in all scenes must continue to create the display window correctly with dimensions 793x650
- All scene initialization logic (pygame.init(), screen creation, clock creation, tmx loading, etc.) must remain unchanged
- Scene gameplay, rendering, and event handling must remain completely unaffected

**Scope:**
All functionality that does NOT involve the window title text should be completely unaffected by this fix. This includes:
- Scene rendering and game loop execution
- Player input handling and game mechanics
- Scene transitions and module imports
- Display window creation and management (except title text)
- Audio, sprites, and all other game assets

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is clear:

1. **Redundant Title Setting**: Each scene file independently calls `pygame.display.set_caption()` with a scene-specific title during module initialization or in standalone test entry points. This was likely done during development to identify which scene was running during testing.

2. **Module-Level Execution**: For TheNaga.py, TheTwins.py, TheGuardian.py, TheStatues.py, and TheGarden.py, the `set_caption()` call occurs at module level (lines 13-16), meaning it executes immediately when the module is imported, overwriting the title set by MainMenuPage.py or Start.py.

3. **Test Entry Point**: For Prologue.py, the `set_caption()` call occurs in the `main()` function (line 399), which is a standalone test entry point. This overwrites the title when the prologue is run standalone.

4. **Lack of Centralized Title Management**: The codebase does not have a single source of truth for the window title. MainMenuPage.py and Start.py correctly set "Garden of Eden", but scene files override this without coordination.

## Correctness Properties

Property 1: Bug Condition - Window Title Remains Consistent

_For any_ scene transition where one of the six affected scene files (Prologue, TheNaga, TheTwins, TheGuardian, TheStatues, TheGarden) is loaded, the fixed code SHALL maintain the window title as "Garden of Eden" without changing it to a scene-specific title.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

Property 2: Preservation - Scene Initialization and Transitions

_For any_ scene initialization or transition that does NOT involve window title text, the fixed code SHALL produce exactly the same behavior as the original code, preserving all scene functionality including display window creation, pygame initialization, scene rendering, and gameplay mechanics.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

The fix is surgical and minimal - remove only the `pygame.display.set_caption()` lines from the six affected files.

**File 1**: `Prologue.py`

**Line to Remove**: Line 399

**Current Code**:
```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Garden of Eden – Prologue")
    clock  = pygame.time.Clock()
```

**Fixed Code**:
```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()
```

---

**File 2**: `TheNaga.py`

**Line to Remove**: Line 15

**Current Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Naga's Lair")
clock  = pygame.time.Clock()
```

**Fixed Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()
```

---

**File 3**: `TheTwins.py`

**Line to Remove**: Line 16

**Current Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Twins")
clock  = pygame.time.Clock()
```

**Fixed Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()
```

---

**File 4**: `TheGuardian.py`

**Line to Remove**: Line 16

**Current Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Guardian")
clock = pygame.time.Clock()
```

**Fixed Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
```

---

**File 5**: `TheStatues.py`

**Line to Remove**: Line 15

**Current Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Statues")
clock = pygame.time.Clock()
```

**Fixed Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
```

---

**File 6**: `TheGarden.py`

**Line to Remove**: Line 13

**Current Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Garden")
clock = pygame.time.Clock()
```

**Fixed Code**:
```python
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code (window title changes when scenes load), then verify the fix maintains "Garden of Eden" consistently and preserves all existing scene functionality.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm that scene files change the window title when loaded.

**Test Plan**: Write tests that import or execute each of the six affected scene files and capture the window title using `pygame.display.get_caption()`. Run these tests on the UNFIXED code to observe the title changes and confirm the root cause.

**Test Cases**:
1. **Prologue Title Change Test**: Call Prologue.main() and verify title changes to "Garden of Eden – Prologue" (will fail on unfixed code - title WILL change)
2. **TheNaga Import Test**: Import TheNaga module and verify title changes to "Garden of Eden – The Naga's Lair" (will fail on unfixed code - title WILL change)
3. **TheTwins Import Test**: Import TheTwins module and verify title changes to "Garden of Eden – The Twins" (will fail on unfixed code - title WILL change)
4. **TheGuardian Import Test**: Import TheGuardian module and verify title changes to "Garden of Eden – The Guardian" (will fail on unfixed code - title WILL change)
5. **TheStatues Import Test**: Import TheStatues module and verify title changes to "Garden of Eden – The Statues" (will fail on unfixed code - title WILL change)
6. **TheGarden Import Test**: Import TheGarden module and verify title changes to "Garden of Eden – The Garden" (will fail on unfixed code - title WILL change)

**Expected Counterexamples**:
- Window title changes from "Garden of Eden" to scene-specific titles when scene files are imported or executed
- Root cause confirmed: Each scene file contains `pygame.display.set_caption()` call with scene-specific title

### Fix Checking

**Goal**: Verify that for all scene transitions where the bug condition holds (loading one of the six affected scenes), the fixed code maintains the window title as "Garden of Eden".

**Pseudocode:**
```
FOR ALL sceneFile IN [Prologue, TheNaga, TheTwins, TheGuardian, TheStatues, TheGarden] DO
  initialTitle := "Garden of Eden"
  pygame.display.set_caption(initialTitle)
  
  IF sceneFile == Prologue THEN
    Prologue.main()  # Call main function
  ELSE
    import sceneFile  # Import module
  END IF
  
  currentTitle := pygame.display.get_caption()[0]
  ASSERT currentTitle == "Garden of Eden"
END FOR
```

**Testing Approach**: Property-based testing is ideal for this fix because:
- It can generate test cases for all six scene files systematically
- It verifies the invariant (title == "Garden of Eden") holds across all scene transitions
- It provides strong guarantees that the title never changes regardless of scene load order

### Preservation Checking

**Goal**: Verify that for all scene functionality that does NOT involve window title text, the fixed code produces the same behavior as the original code.

**Pseudocode:**
```
FOR ALL sceneFile IN [Prologue, TheNaga, TheTwins, TheGuardian, TheStatues, TheGarden] DO
  # Verify display window creation still works
  ASSERT pygame.display.get_surface() is not None
  ASSERT pygame.display.get_surface().get_size() == (793, 650)
  
  # Verify pygame initialization still works
  ASSERT pygame.get_init() == True
  
  # Verify scene-specific initialization (tmx loading, etc.) still works
  ASSERT sceneFile.screen is not None
  ASSERT sceneFile.clock is not None
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across different scene load orders
- It catches edge cases that manual unit tests might miss (e.g., loading scenes in different sequences)
- It provides strong guarantees that display window creation and scene initialization are unchanged

**Test Plan**: Observe behavior on UNFIXED code first to capture baseline scene initialization behavior, then write property-based tests verifying this behavior continues after the fix.

**Test Cases**:
1. **Display Window Preservation**: Verify pygame.display.set_mode() still creates 793x650 window for all scenes
2. **Scene Initialization Preservation**: Verify pygame.init(), screen, clock, and tmx_data initialization still work for all scenes
3. **Scene Transition Preservation**: Verify importing scenes in various orders doesn't cause crashes or display issues
4. **MainMenuPage Title Preservation**: Verify MainMenuPage.py still sets "Garden of Eden" title correctly

### Unit Tests

- Test that each of the six scene files no longer contains `pygame.display.set_caption()` calls (or only contains calls with "Garden of Eden")
- Test that importing each scene file does not change the window title from "Garden of Eden"
- Test that Prologue.main() does not change the window title from "Garden of Eden"
- Test that MainMenuPage.py and Start.py continue to set "Garden of Eden" title correctly
- Test edge case: Loading scenes in rapid succession maintains consistent title

### Property-Based Tests

- Generate random sequences of scene imports and verify window title remains "Garden of Eden" throughout
- Generate random scene load orders and verify display window creation (793x650) works correctly for all
- Generate random scene transitions and verify no crashes or pygame errors occur
- Test that pygame.display.get_caption()[0] always returns "Garden of Eden" after any scene operation

### Integration Tests

- Test full game flow from MainMenuPage → Prologue → Start → TheNaga → TheTwins → TheGuardian → TheStatues → TheGarden, verifying title stays "Garden of Eden"
- Test that scene gameplay, rendering, and event handling work correctly after the fix
- Test that visual display and window management remain unchanged
- Test that the fix works correctly when scenes are loaded as standalone modules (for development/testing)
