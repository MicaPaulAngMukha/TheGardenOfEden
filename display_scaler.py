"""
Display Scaler - Letterboxing/Pillarboxing for Retro-Style Scaling

This module handles scaling the game's native resolution (793x650) to fit
any window size while maintaining aspect ratio and adding black bars
(letterboxing/pillarboxing) like classic retro games (e.g., Undertale).

Usage:
    from display_scaler import DisplayScaler
    
    scaler = DisplayScaler(native_width=793, native_height=650)
    
    # In your game loop:
    # 1. Draw everything to your game surface (793x650)
    # 2. Scale and display it:
    scaler.display(window_surface, game_surface)
"""

import pygame


class DisplayScaler:
    """Handles aspect-ratio-preserving scaling with letterboxing."""
    
    def __init__(self, native_width, native_height):
        """
        Initialize the display scaler.
        
        Args:
            native_width: The game's native width (e.g., 793)
            native_height: The game's native height (e.g., 650)
        """
        self.native_width = native_width
        self.native_height = native_height
        self.aspect_ratio = native_width / native_height
    
    def calculate_scaled_rect(self, window_width, window_height):
        """
        Calculate the rectangle where the game should be drawn.
        
        Returns a pygame.Rect that maintains aspect ratio and is centered
        in the window with black bars on the sides or top/bottom.
        
        Args:
            window_width: Current window width
            window_height: Current window height
            
        Returns:
            pygame.Rect: The rectangle where the scaled game should be drawn
        """
        window_aspect = window_width / window_height
        
        if window_aspect > self.aspect_ratio:
            # Window is wider than game - add pillarboxing (black bars on sides)
            scaled_height = window_height
            scaled_width = int(scaled_height * self.aspect_ratio)
            x_offset = (window_width - scaled_width) // 2
            y_offset = 0
        else:
            # Window is taller than game - add letterboxing (black bars on top/bottom)
            scaled_width = window_width
            scaled_height = int(scaled_width / self.aspect_ratio)
            x_offset = 0
            y_offset = (window_height - scaled_height) // 2
        
        return pygame.Rect(x_offset, y_offset, scaled_width, scaled_height)
    
    def display(self, window_surface, game_surface):
        """
        Display the game surface on the window surface with proper scaling.
        
        This fills the window with black, then draws the scaled game surface
        in the center with appropriate letterboxing/pillarboxing.
        
        Args:
            window_surface: The actual window surface (can be any size)
            game_surface: The game surface at native resolution (793x650)
        """
        # Fill window with black (creates the letterbox/pillarbox bars)
        window_surface.fill((0, 0, 0))
        
        # Calculate where to draw the scaled game
        window_width, window_height = window_surface.get_size()
        scaled_rect = self.calculate_scaled_rect(window_width, window_height)
        
        # Scale the game surface to fit the calculated rectangle
        scaled_game = pygame.transform.scale(game_surface, 
                                             (scaled_rect.width, scaled_rect.height))
        
        # Draw the scaled game centered in the window
        window_surface.blit(scaled_game, scaled_rect)
    
    def transform_mouse_pos(self, window_mouse_pos, window_width, window_height):
        """
        Transform mouse coordinates from window space to game space.
        
        This is needed because the mouse position is in window coordinates,
        but your game logic needs coordinates in the native 793x650 space.
        
        Args:
            window_mouse_pos: (x, y) tuple of mouse position in window
            window_width: Current window width
            window_height: Current window height
            
        Returns:
            (x, y) tuple of mouse position in game coordinates,
            or None if mouse is outside the game area (in the black bars)
        """
        mx, my = window_mouse_pos
        scaled_rect = self.calculate_scaled_rect(window_width, window_height)
        
        # Check if mouse is outside the game area (in the black bars)
        if not scaled_rect.collidepoint(mx, my):
            return None
        
        # Transform from window coordinates to game coordinates
        relative_x = mx - scaled_rect.x
        relative_y = my - scaled_rect.y
        
        game_x = int((relative_x / scaled_rect.width) * self.native_width)
        game_y = int((relative_y / scaled_rect.height) * self.native_height)
        
        return (game_x, game_y)
