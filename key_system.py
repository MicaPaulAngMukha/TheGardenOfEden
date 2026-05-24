"""
Key System Module for Raziel Key Dialogue System

This module contains the KeyEntity class and key spawning functionality
for the multi-difficulty key mechanic in the Garden of Eden game.
"""

import pygame
from resource_path import resource_path


# Tile size constant (matches Start.py)
T = 13

# Key spawn locations (tile coordinates)
KEY_SPAWN_LOCATIONS = {
    "bronze": (15 * T, 25 * T),  # Left side of map
    "gold": (45 * T, 25 * T),    # Right side of map
    "rusted": (20 * T, 35 * T),  # Lower left
    "divine": (40 * T, 35 * T)   # Lower right
}


def create_placeholder_sprite(key_type: str) -> pygame.Surface:
    """
    Create a colored rectangle as a placeholder sprite when the actual
    sprite file is missing.
    
    Args:
        key_type: The type of key ("bronze", "gold", "rusted", "divine")
    
    Returns:
        A pygame Surface with a colored rectangle representing the key
    """
    color_map = {
        "bronze": (205, 127, 50),
        "gold": (255, 215, 0),
        "rusted": (183, 65, 14),
        "divine": (255, 255, 255)
    }
    surface = pygame.Surface((16, 16))
    surface.fill(color_map.get(key_type, (128, 128, 128)))
    return surface


class KeyEntity:
    """
    Represents a physical key in the game world.
    
    Attributes:
        key_type: The type of key ("bronze", "gold", "rusted", "divine")
        rect: The pygame Rect for collision detection and positioning
        sprite: The visual representation of the key
        discovered: Whether the player has discovered this key
    """
    
    def __init__(self, key_type: str, position: tuple[int, int]):
        """
        Initialize a KeyEntity.
        
        Args:
            key_type: The type of key ("bronze", "gold", "rusted", "divine")
            position: The (x, y) pixel coordinates for the key's position
        """
        self.key_type = key_type
        self.rect = pygame.Rect(position[0], position[1], 16, 16)
        self.sprite = self._load_sprite()
        self.discovered = False
        self.pickup_cooldown = 0  # Cooldown to prevent dialogue spam
    
    def _load_sprite(self) -> pygame.Surface:
        """
        Load the appropriate sprite based on key_type.
        Falls back to placeholder sprite if file is missing.
        
        Returns:
            A pygame Surface containing the key sprite
        """
        sprite_map = {
            "bronze": "bronze_key.png",
            "gold": "Key.png",
            "rusted": "rusted_key.png",
            "divine": "divine_key.png"
        }
        
        try:
            sprite_path = sprite_map[self.key_type]
            sprite = pygame.image.load(resource_path(sprite_path))
            # Try to convert_alpha if display is initialized, otherwise just use the loaded image
            try:
                sprite = sprite.convert_alpha()
            except pygame.error:
                # No video mode set, use the image as-is
                pass
            # Scale to 16x16 if needed
            if sprite.get_width() != 16 or sprite.get_height() != 16:
                sprite = pygame.transform.scale(sprite, (16, 16))
            return sprite
        except (FileNotFoundError, KeyError, pygame.error) as e:
            print(f"Warning: Could not load sprite for {self.key_type} key: {e}")
            return create_placeholder_sprite(self.key_type)
    
    def near_player(self, player_rect: pygame.Rect, radius: int = 30) -> bool:
        """
        Check if player is within interaction range of this key.
        
        Args:
            player_rect: The player's pygame Rect
            radius: The interaction radius in pixels (default: 30)
        
        Returns:
            True if player is within range, False otherwise
        """
        return self.rect.inflate(radius * 2, radius * 2).colliderect(player_rect)


def spawn_keys() -> list[KeyEntity]:
    """
    Spawn all four keys at designated locations.
    Called when Mikhail chase is triggered.
    
    Returns:
        A list of KeyEntity objects (one for each key type)
    """
    keys = []
    for key_type, position in KEY_SPAWN_LOCATIONS.items():
        try:
            key = KeyEntity(key_type, position)
            keys.append(key)
        except Exception as e:
            print(f"Warning: Error creating {key_type} key: {e}")
            # Still create the key with placeholder sprite
            key = KeyEntity(key_type, position)
            keys.append(key)
    
    return keys


class RazielDialoguePool:
    """
    Manages Raziel's dynamic dialogue cycling for key-related conversations.
    
    The dialogue pool cycles through five different key-related dialogues,
    ensuring variety in Raziel's interactions with the player.
    
    Attributes:
        dialogue_keys: List of dialogue keys to cycle through
        current_index: Current position in the dialogue cycle
        seen_dialogues: Set of dialogue keys that have been displayed
    """
    
    def __init__(self):
        """Initialize the dialogue pool with all key-related dialogues."""
        self.dialogue_keys = [
            "raziel_key_intro",
            "raziel_key_gold",
            "raziel_key_bronze",
            "raziel_key_rusted",
            "raziel_key_divine"
        ]
        self.current_index = 0
        self.seen_dialogues = set()
    
    def get_next_dialogue(self, dialogs_dict: dict) -> list[tuple[str, str]]:
        """
        Return the next dialogue in the pool, cycling through all options.
        Falls back to a default dialogue if the key is missing from the dictionary.
        
        Args:
            dialogs_dict: The DIALOGS dictionary containing all dialogue entries
        
        Returns:
            A list of (speaker, text) tuples representing the dialogue
        """
        dialogue_key = self.dialogue_keys[self.current_index]
        self.seen_dialogues.add(dialogue_key)
        self.current_index = (self.current_index + 1) % len(self.dialogue_keys)
        
        # Fallback if dialogue key doesn't exist
        if dialogue_key not in dialogs_dict:
            print(f"Warning: Dialogue key '{dialogue_key}' not found in DIALOGS")
            return [("Raziel", "...")]
        
        return dialogs_dict[dialogue_key]
