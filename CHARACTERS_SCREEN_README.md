# Characters Screen Implementation

## Overview
The Characters screen has been successfully implemented for the Garden of Eden game. Players can now browse through all 7 characters and read their descriptions.

## Features

### Navigation
- **Back Button** (top left): Returns to Main Menu
- **Left Arrow** (< button): Browse to previous character
- **Right Arrow** (> button): Browse to next character
- **Keyboard Support**: 
  - ESC key: Return to Main Menu
  - Left Arrow key: Previous character
  - Right Arrow key: Next character

### UI Layout
- **Title**: "Characters" centered at top with decorative gold line
- **Character Image**: Left side (320x480px) with dark background and gold border
- **Character Info**: Right side showing:
  - Character name (large font)
  - "Description" label
  - Wrapped description text
- **Character Counter**: Shows current position (e.g., "1 / 7")

### Characters Included

1. **Mikhail** - The strict angel, Guard of Eden's gates
2. **Raziel** - The laid back angel, calmer counterpart to Mikhail
3. **The Serpent** - The deceiver who caused humanity's fall
4. **Cain** - Older brother, first murderer seeking redemption
5. **Abel** - Younger brother, shepherd aiding Cain
6. **The Guardian** - Cherubim guarding the tree of knowledge
7. **--. --- -..** (God) - Special character with red text

## Files Created

### CharactersPage.py
Main implementation file containing:
- Character data structure with names, images, and descriptions
- UI rendering logic
- Navigation controls
- Text wrapping for long descriptions

### test_characters_page.py
Comprehensive test suite verifying:
- All 7 characters are defined
- All character images exist
- All descriptions are present
- Special character (God) has red color
- Text wrapping functionality
- Descriptions match specification

## Integration

### MainMenuPage.py Updates
- Imported `CharactersPage` module
- Enabled "Characters" button (changed from `enabled: False` to `enabled: True`)
- Added click handler to open Characters screen
- Music continues playing when returning from Characters screen

### Test Updates
- Updated `test_mainmenu_prologue_transition.py` to reflect enabled Characters button
- All 64 tests pass successfully

## Styling
The Characters screen matches the game's aesthetic:
- **Colors**: Gold (#FFF7F3), Dark Gold (#DE8F15), Black, White, Red (for God)
- **Font**: PixelifySans (same as Main Menu)
- **Background**: Same Garden background as Main Menu
- **Hover Effects**: Gold highlight on interactive elements

## Usage

### From Main Menu
1. Click "Characters" button
2. Browse characters using arrow buttons or keyboard
3. Press Back button or ESC to return to Main Menu

### Standalone Testing
```bash
python CharactersPage.py
```

### Run Tests
```bash
python -m pytest test_characters_page.py -v
```

## Character Images
All character "Full" images are located in their respective sprite folders:
- `Sprites/Mikhail/MikhailFull.png`
- `Sprites/Raziel/RazielFull.png`
- `Sprites/Naga/NagaFull.png`
- `Sprites/Cain/CainFull.png`
- `Sprites/Abel/AbelFull.png`
- `Sprites/Guardian/GuardianFull.png`
- `Sprites/boss/BossFull.png`

## Technical Details

### Text Wrapping
Long descriptions are automatically wrapped to fit within the display area (max width ~300px). The `wrap_text()` function ensures no words are cut off mid-word.

### Image Scaling
Character images are scaled to 320x480px to fit consistently in the display area while maintaining aspect ratio.

### Navigation Loop
Character browsing wraps around (after last character, goes to first; before first character, goes to last).

## Future Enhancements
Potential improvements:
- Add character voice lines or sound effects
- Include character stats or abilities
- Add animation transitions between characters
- Include character relationships or story connections
