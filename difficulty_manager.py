"""
Difficulty Manager Module

Manages difficulty state for a level and provides visual feedback.
Reads player's held key and applies appropriate difficulty modifiers.
"""

import pygame
from difficulty_config import get_difficulty_from_key, get_modifiers, EASY, NORMAL, HARD, GOD_MODE


# Display colors for each difficulty mode
DIFFICULTY_COLORS = {
    EASY: (205, 127, 50),      # Bronze
    NORMAL: (212, 175, 55),    # Gold
    HARD: (183, 65, 14),       # Rust
    GOD_MODE: (255, 255, 255), # White
}

# Display names for each difficulty mode
DIFFICULTY_NAMES = {
    EASY: "Bronze Key - Easy Mode",
    NORMAL: "Gold Key - Normal Mode",
    HARD: "Rusted Key - Hard Mode",
    GOD_MODE: "Divine Key - God Mode",
}


class DifficultyManager:
    """
    Manages difficulty state and provides visual feedback.
    
    Reads the player's held key at initialization and determines the appropriate
    difficulty mode. Provides methods to query modifiers and display difficulty
    indicators to the player.
    """
    
    def __init__(self, player, level_name):
        """
        Initialize difficulty manager for a level.
        
        Args:
            player: Player object with held_key attribute
            level_name: str - Name of the current level
        """
        try:
            self.player = player
            self.level_name = level_name
            
            # Handle missing held_key attribute
            if not hasattr(player, 'held_key'):
                print(f"WARNING: Player object missing 'held_key' attribute in {level_name}. Defaulting to Normal Mode.")
                player.held_key = None
            
            self.difficulty = get_difficulty_from_key(player.held_key)
            self.modifiers = get_modifiers(level_name, self.difficulty)
            
            # UI state - DISABLED to keep difficulty a surprise
            self.show_indicator = False  # Changed from True to False
            self.indicator_timer = 0  # No timer needed since we don't show it
        except Exception as e:
            print(f"ERROR: Exception during DifficultyManager initialization for {level_name}: {e}")
            print("Falling back to Normal Mode.")
            self.player = player
            self.level_name = level_name
            self.difficulty = NORMAL
            self.modifiers = {}
            self.show_indicator = False
            self.indicator_timer = 0
    
    def update(self):
        """Update indicator timer."""
        if self.indicator_timer > 0:
            self.indicator_timer -= 1
            if self.indicator_timer == 0:
                self.show_indicator = False
    
    def draw_indicator(self, surface, font):
        """
        Draw difficulty indicator at top-center of screen.
        
        Args:
            surface: pygame.Surface to draw on
            font: pygame.Font for text rendering
        """
        if not self.show_indicator:
            return
        
        name = DIFFICULTY_NAMES[self.difficulty]
        color = DIFFICULTY_COLORS[self.difficulty]
        
        text = font.render(name, True, color)
        x = surface.get_width() // 2 - text.get_width() // 2
        y = 10
        
        # God Mode gets a glow effect
        if self.difficulty == GOD_MODE:
            glow = pygame.Surface((text.get_width() + 20, text.get_height() + 10), 
                                  pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 60), glow.get_rect(), border_radius=5)
            surface.blit(glow, (x - 10, y - 5))
        
        surface.blit(text, (x, y))
    
    def get_modifier(self, key, default=None):
        """
        Get a specific modifier value.
        
        Args:
            key: str - Modifier key name
            default: Default value if modifier not present
            
        Returns:
            Modifier value or default
        """
        return self.modifiers.get(key, default)
    
    def should_spawn_god(self):
        """Check if God should spawn in this level."""
        return self.modifiers.get("spawn_god", False)
