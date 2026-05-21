"""
Portable God entity that can be spawned in any level for God Mode.
Ignores walls, chases player, spawns lightning bolts.
"""

import pygame
import math
import random
import os


class GodEntity:
    """
    Portable God entity that can be spawned in any level.
    Ignores walls, chases player, spawns lightning bolts.
    """
    
    SIZE = 20
    
    def __init__(self, spawn_x=None, spawn_y=None, 
                 speed=0.9, smite_range=85, 
                 lightning_count=5, lightning_cooldown=90):
        """
        Initialize God entity.
        
        Args:
            spawn_x: X spawn position (defaults to screen center-top)
            spawn_y: Y spawn position (defaults to -80, off-screen top)
            speed: Movement speed (pixels per frame)
            smite_range: Instant-kill range (pixels)
            lightning_count: Number of bolts per volley
            lightning_cooldown: Frames between volleys
        """
        # Get screen dimensions from pygame display
        screen = pygame.display.get_surface()
        width = screen.get_width() if screen else 793
        
        if spawn_x is None:
            spawn_x = width // 2 - self.SIZE // 2
        if spawn_y is None:
            spawn_y = -80
        
        self.rect = pygame.Rect(spawn_x, spawn_y, self.SIZE, self.SIZE)
        self.speed = speed
        self.smite_range = smite_range
        self.lightning_count = lightning_count
        self.lightning_cooldown = lightning_cooldown
        self.bolt_timer = lightning_cooldown // 2
        
        # Animation state
        self.anim_index = 0
        self.anim_timer = 0
        self.ANIM_SPEED = 8  # frames per sprite frame
        
        # Load sprite frames if available
        self.frames = self._load_frames()
    
    def _load_frames(self):
        """Load God sprite frames (same as TheGarden.py)."""
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            sheet = pygame.image.load(
                os.path.join(BASE_DIR, "Sprites", "boss", "bossSprite.png")
            ).convert_alpha()
            
            fw = sheet.get_width() // 5
            fh = sheet.get_height()
            dw, dh = 160, 200
            
            return [
                pygame.transform.scale(
                    sheet.subsurface((fw * i, 0, fw, fh)),
                    (dw, dh)
                )
                for i in range(5)
            ]
        except Exception:
            return []
    
    def update(self, player_rect):
        """
        Update God position (chase player, ignore walls).
        
        Args:
            player_rect: pygame.Rect of player position
        """
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        
        self.rect.x += (dx / dist) * self.speed
        self.rect.y += (dy / dist) * self.speed
        # Intentionally no wall collision
    
    def in_smite_range(self, player_rect):
        """
        Check if player is within instant-kill range.
        
        Args:
            player_rect: pygame.Rect of player position
            
        Returns:
            bool: True if player is in smite range
        """
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        return math.sqrt(dx * dx + dy * dy) < self.smite_range
    
    def try_spawn_bolts(self, player_rect):
        """
        Attempt to spawn lightning bolt volley.
        
        Args:
            player_rect: pygame.Rect of player position
            
        Returns:
            list: List of Lightning objects (empty if on cooldown)
        """
        self.bolt_timer -= 1
        if self.bolt_timer > 0:
            return []
        
        self.bolt_timer = self.lightning_cooldown
        bolts = []
        
        # Get screen dimensions
        screen = pygame.display.get_surface()
        width = screen.get_width() if screen else 793
        height = screen.get_height() if screen else 650
        T = 13  # Tile size
        
        for _ in range(self.lightning_count):
            tx = player_rect.centerx + random.randint(-130, 130)
            ty = player_rect.centery + random.randint(-90, 90)
            tx = max(T * 2, min(width - T * 2, tx))
            ty = max(T * 4, min(height - T * 2, ty))
            bolts.append(Lightning(tx, ty))
        
        return bolts
    
    def draw(self, surface):
        """
        Draw God entity with visual effects.
        
        Args:
            surface: pygame.Surface to draw on
        """
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % max(len(self.frames), 1)
        
        cx, cy = int(self.rect.centerx), int(self.rect.centery)
        ticks = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(ticks / 200)
        
        # Outer pulsing aura
        glow_r = int(80 + 20 * pulse)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 255, 200, int(40 + 30 * pulse)), 
                           glow.get_rect())
        surface.blit(glow, (cx - glow_r, cy - glow_r))
        
        # Radiant lines
        for angle in range(0, 360, 45):
            rad = math.radians(angle + ticks / 10)
            x1 = cx + int(math.cos(rad) * 55)
            y1 = cy + int(math.sin(rad) * 55)
            x2 = cx + int(math.cos(rad) * 75)
            y2 = cy + int(math.sin(rad) * 75)
            pygame.draw.line(surface, (255, 240, 120, 180), (x1, y1), (x2, y2), 2)
        
        # Sprite
        if self.frames:
            frame = self.frames[self.anim_index]
            draw_x = cx - frame.get_width() // 2
            draw_y = cy - frame.get_height() // 2
            surface.blit(frame, (draw_x, draw_y))
        
        # Halo ring
        halo_r = int(28 + 4 * pulse)
        halo_y = cy - (self.frames[0].get_height() // 2) + 10 if self.frames else cy - 50
        halo_surf = pygame.Surface((halo_r * 2 + 10, halo_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(halo_surf, (255, 240, 100, int(160 + 60 * pulse)),
                           halo_surf.get_rect(), 4)
        surface.blit(halo_surf, (cx - halo_r - 5, halo_y - halo_r - 5))


class Lightning:
    """Lightning bolt entity (same as TheGarden.py)."""
    
    WARN_FRAMES = 45
    LINGER_FRAMES = 28
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.warn_timer = self.WARN_FRAMES
        self.live_timer = self.LINGER_FRAMES
    
    def update(self):
        """
        Update lightning state.
        
        Returns:
            bool: True if lightning is finished and should be removed
        """
        if self.warn_timer > 0:
            self.warn_timer -= 1
            return False
        if self.live_timer > 0:
            self.live_timer -= 1
            return False
        return True  # finished — remove
    
    def is_done(self):
        """Check if lightning is finished."""
        return self.warn_timer <= 0 and self.live_timer <= 0
    
    @property
    def is_live(self):
        """Check if lightning is in strike phase (can damage)."""
        return self.warn_timer <= 0 and self.live_timer > 0
    
    def get_damage_rect(self):
        """
        Get damage rectangle if lightning is in strike phase.
        
        Returns:
            pygame.Rect or None: Damage rectangle if live, None otherwise
        """
        if self.is_live:
            return pygame.Rect(self.x - 14, self.y - 14, 28, 28)
        return None
    
    def hits(self, rect):
        """
        Check if lightning hits a rectangle.
        
        Args:
            rect: pygame.Rect to check collision with
            
        Returns:
            bool: True if lightning is live and hits the rect
        """
        if not self.is_live:
            return False
        return pygame.Rect(self.x - 14, self.y - 14, 28, 28).colliderect(rect)
    
    def draw(self, surface):
        """
        Draw lightning bolt.
        
        Args:
            surface: pygame.Surface to draw on
        """
        if self.warn_timer > 0:
            # Warning indicator
            alpha = int(200 * (1 - self.warn_timer / self.WARN_FRAMES))
            ws = pygame.Surface((52, 52), pygame.SRCALPHA)
            pygame.draw.circle(ws, (255, 60, 60, alpha), (26, 26), 24, 3)
            surface.blit(ws, (self.x - 26, self.y - 26))
            return
        
        if self.live_timer <= 0:
            return
        
        # Strike effect
        bright = int(255 * (self.live_timer / self.LINGER_FRAMES))
        pts = [(self.x, 0)]
        cy = 0
        while cy < self.y:
            cy += random.randint(18, 34)
            pts.append((self.x + random.randint(-14, 14), min(cy, self.y)))
        pts.append((self.x, self.y))
        
        if len(pts) >= 2:
            pygame.draw.lines(surface, (bright, bright, 60), False, pts, 3)
            pygame.draw.lines(surface, (255, 255, 200), False, pts, 1)
        
        glow = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 240, 80, bright // 2), glow.get_rect())
        surface.blit(glow, (self.x - 30, self.y - 20))
