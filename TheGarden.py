import pygame
import sys
import os
import math
import random
import pytmx
from display_scaler import DisplayScaler
from resource_path import resource_path
from difficulty_manager import DifficultyManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

# Create display scaler for letterboxing/pillarboxing
scaler = DisplayScaler(WIDTH, HEIGHT)
# Create game surface at native resolution
game_surface = pygame.Surface((WIDTH, HEIGHT))

tmx_data = pytmx.load_pygame(resource_path("TheGardenMap.tmx"))

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK          = (0,   0,   0)
WHITE          = (255, 255, 255)
GOLD           = (212, 175,  55)
PLAYER_COL     = (200, 160,  80)
PLAYER_HEAD    = (210, 170, 120)
MIKHAIL_BORDER = (220, 190,  80)
RAZIEL_BORDER  = (160, 200, 240)
DIALOG_W       = 700
DIALOG_H       = 180
PORTRAIT_SIZE  = 140

# ── Grid ──────────────────────────────────────────────────────────────────────
T    = 13
COLS = WIDTH  // T
ROWS = HEIGHT // T

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_PATH = os.path.join(BASE_DIR, "font", "PixelifySans-VariableFont_wght.ttf")
font_sm   = pygame.font.Font(FONT_PATH, 15)
font_md   = pygame.font.Font(FONT_PATH, 19)
font_hud  = pygame.font.Font(FONT_PATH, 15)
font_lg   = pygame.font.Font(FONT_PATH, 32)

# ── Hearts ────────────────────────────────────────────────────────────────────
try:
    heart_full  = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "LifeHeart.png")).convert_alpha(), (20, 20))
    heart_empty = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "LifeHeartLoss.png")).convert_alpha(), (20, 20))
except Exception:
    heart_full = heart_empty = None

# ── Portraits ─────────────────────────────────────────────────────────────────
try:
    portrait_mikhail = pygame.transform.scale(
        pygame.image.load(
            os.path.join(BASE_DIR, "Sprites", "Mikhail", "mikhail.png")).convert_alpha(),
        (PORTRAIT_SIZE, PORTRAIT_SIZE))
except Exception:
    portrait_mikhail = None

try:
    portrait_raziel = pygame.transform.scale(
        pygame.image.load(
            os.path.join(BASE_DIR, "Sprites", "Raziel", "raziel.png")).convert_alpha(),
        (PORTRAIT_SIZE, PORTRAIT_SIZE))
except Exception:
    portrait_raziel = None

# ── Boss/God sprite sheet ─────────────────────────────────────────────────────
try:
    _boss_sheet = pygame.image.load(
        os.path.join(BASE_DIR, "Sprites", "boss", "bossSprite.png")).convert_alpha()
    _boss_fw    = _boss_sheet.get_width() // 5   # 215
    _boss_fh    = _boss_sheet.get_height()        # 232
    # Scale to display size — keep aspect ratio, ~80px wide
    _boss_scale = 80 / _boss_fw
    _boss_dw    = 160
    _boss_dh    = 200
    boss_frames = [
        pygame.transform.scale(
            _boss_sheet.subsurface((_boss_fw * i, 0, _boss_fw, _boss_fh)),
            (_boss_dw, _boss_dh)
        )
        for i in range(5)
    ]
except Exception:
    boss_frames = []

# ── Apple sprite ──────────────────────────────────────────────────────────────
try:
    apple_sprite = pygame.image.load(resource_path("apple.png")).convert_alpha()
    apple_sprite = pygame.transform.scale(apple_sprite, (16, 16))  # Scale to appropriate size
except Exception:
    apple_sprite = None

# ── Constants ─────────────────────────────────────────────────────────────────
PLAYER_SIZE        = 24
MAX_LIVES          = 3
# Player enters from the bottom centre (same spawn logic as other levels)
PLAYER_SPAWN = (WIDTH // 2, 80)  # just below the top entrance

TREE_SHAKE_NEEDED  = 3
DOOR_KICK_MIN      = 4
DOOR_KICK_MAX      = 8
INVINCIBLE_FRAMES  = 90
TYPEWRITER_SPEED   = 2

GOD_SPEED          = 0.9      # slow, inevitable, ignores all walls
GOD_SMITE_RANGE    = 85       # instant-kill proximity in pixels
LIGHTNING_COUNT    = 5
LIGHTNING_COOLDOWN = 90       # frames between bolt volleys (~1.5 s)

STATE_CUTSCENE = "cutscene"

# Only true wall tiles block the player — everything else is decoration
WALL_LAYERS = {"Walls"}

# Layers that are purely decorative and always drawn (no logic attached)
DECOR_LAYERS = {
    "Ground", "Path", "Path2", "Path3",
    "TreeEden", "TreeDesign",
    "Furniture", "Furniture2",
    "Design", "Design2",
    "Bushes",
}

# ── Epilogue dialogue ─────────────────────────────────────────────────────────
EPILOGUE = [
    ("Mikhail", "And stay out!"),
    ("Mikhail", "Eden's gates are closed for you for good!"),
    ("Mikhail", "How did they even get in there?!"),
    ("Raziel",  "It matters not, Mikhail."),
    ("Raziel",  "Eden has always been open to humanity."),
    ("Mikhail", "!?!?"),
    ("Raziel",  "It's only closed to those it deemed a sinner."),
    ("Raziel",  "And this little human..."),
    ("Raziel",  "Just branded themselves to an eternal barricade from this point on."),
]

CUTSCENE = [
    ("NARRATE", "You enter a garden..."),
    ("NARRATE", "It looks peaceful."),
    ("NARRATE", "There seems to be no monsters here..."),
    ("NARRATE", "... and only a singular grand tree."),
]


# =============================================================================
# TYPEWRITER
# =============================================================================
class Typewriter:
    def __init__(self):
        self.full_text     = ""
        self.visible_chars = 0
        self.timer         = 0
        self.done          = False

    def set_text(self, text):
        self.full_text     = text
        self.visible_chars = 0
        self.timer         = 0
        self.done          = False

    def update(self):
        if self.done:
            return
        self.timer += 1
        if self.timer >= TYPEWRITER_SPEED:
            self.timer = 0
            self.visible_chars += 1
            if self.visible_chars >= len(self.full_text):
                self.visible_chars = len(self.full_text)
                self.done = True

    def skip(self):
        self.visible_chars = len(self.full_text)
        self.done = True

    @property
    def current(self):
        return self.full_text[:self.visible_chars]


# =============================================================================
# MAP BUILDER
# =============================================================================
def build_from_tmx():
    """
    Returns:
        walls       – list of pygame.Rect  (only "Walls" layer)
        wall_set    – set of (col, row) for fast lookup
        tree_center – pixel (cx, cy) of the TreeEden layer centroid
        door_tiles  – list of pygame.Rect for the entrance door area
                      (used as the breakable exit)
    """
    walls       = []
    wall_set    = set()
    tree_tiles  = []   # collect all TreeEden tiles to find centre
    door_rects  = []   # Entrance + Entrance2 tiles = the door to break

    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        for x, y, gid in layer:
            if gid == 0:
                continue
            r = pygame.Rect(x * T, y * T, T, T)
            if layer.name == "Walls":
                walls.append(r)
                wall_set.add((x, y))
            elif layer.name == "TreeEden":
                tree_tiles.append((x, y))
            elif layer.name in ("Entrance", "Entrance2"):
                door_rects.append(r)

    # Tree interact centre — average of all TreeEden tile centres
    if tree_tiles:
        avg_x = sum(x * T + T // 2 for x, y in tree_tiles) // len(tree_tiles)
        avg_y = sum(y * T + T // 2 for x, y in tree_tiles) // len(tree_tiles)
        tree_center = (avg_x, avg_y)
    else:
        tree_center = (WIDTH // 2, HEIGHT // 2)   # fallback

    return walls, wall_set, tree_center, door_rects


# =============================================================================
# PLAYER
# =============================================================================
class SpriteSheet:
    def __init__(self, path, frame_w, frame_h, num_frames, row=0, scale=1, speed=8):
        sheet = pygame.image.load(path).convert_alpha()
        sw, sh = sheet.get_size()

        # Derive safe dimensions directly from sheet size and frame counts
        num_rows = 4                          # all guardian sheets have 4 direction rows
        safe_fw  = sw // num_frames           # exact frame width
        safe_fh  = sh // num_rows             # exact frame height

        self.frames = []
        for i in range(num_frames):
            x_off = i * safe_fw
            y_off = row * safe_fh
            # Guard against any remaining OOB
            if x_off + safe_fw > sw or y_off + safe_fh > sh:
                break
            frame = sheet.subsurface((x_off, y_off, safe_fw, safe_fh))
            if scale != 1:
                frame = pygame.transform.scale(
                    frame, (int(safe_fw * scale), int(safe_fh * scale)))
            self.frames.append(frame)

        if not self.frames:
            fallback = pygame.Surface((max(safe_fw, 1), max(safe_fh, 1)), pygame.SRCALPHA)
            self.frames = [fallback]

        self.index = 0
        self.timer = 0
        self.speed = speed

    def update(self):
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def current(self):
        return self.frames[self.index]

    def reset(self):
        self.index = 0
        self.timer = 0

class PlayerSpriteSheet:
    def __init__(self, path, frame_w, frame_h, num_frames, row=0, scale=1, speed=8):
        sheet = pygame.image.load(path).convert_alpha()
        self.frames = []
        for i in range(num_frames):
            frame = sheet.subsurface((i * frame_w, row * frame_h, frame_w, frame_h))
            if scale != 1:
                frame = pygame.transform.scale(
                    frame, (int(frame_w * scale), int(frame_h * scale)))
            self.frames.append(frame)
        self.index = 0
        self.timer = 0
        self.speed = speed

    def update(self):
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def current(self):
        return self.frames[self.index]

    def reset(self):
        self.index = 0
        self.timer = 0

class PlayerSprites:
    ROWS = {"up": 0, "left": 1, "down": 2, "right": 3}

    def __init__(self, scale=1):
        base = os.path.join(BASE_DIR, "Sprites", "Player")

        def load_dir(filename, frames_per_row):
            path = os.path.join(base, filename)
            return {
                d: PlayerSpriteSheet(path, 64, 64, frames_per_row, row=row, scale=scale)
                for d, row in self.ROWS.items()
            }

        self.anims = {
            "idle": load_dir("idle.png", 2),
            "run":  load_dir("run.png",  6),
        }
        hurt_path = os.path.join(base, "hurt.png")
        self.hurt_anim = PlayerSpriteSheet(hurt_path, 64, 64, 6, row=0, scale=scale)

        self.current_anim = "idle"
        self.current_dir  = "down"
        self.showing_hurt = False

    def set_anim(self, anim, direction=None):
        if direction:
            self.current_dir = direction
        if anim != self.current_anim:
            self.current_anim = anim
            if anim in self.anims:
                self.anims[anim][self.current_dir].reset()

    def show_hurt(self):
        self.showing_hurt = True
        self.hurt_anim.reset()

    def update(self):
        if self.showing_hurt:
            self.hurt_anim.update()
            if self.hurt_anim.index == len(self.hurt_anim.frames) - 1:
                self.showing_hurt = False
        elif self.current_anim in self.anims:
            self.anims[self.current_anim][self.current_dir].update()

    def get_frame(self):
        if self.showing_hurt:
            return self.hurt_anim.current()
        return self.anims[self.current_anim][self.current_dir].current()

class Player:
    SPEED = 3

    def __init__(self):
        self.lives      = MAX_LIVES
        self.has_apple  = False
        self.inv_timer  = 0
        self.sprites    = PlayerSprites(scale=1)
        self.rect       = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = PLAYER_SPAWN
        self.sprites.set_anim("idle", "down")

    def move(self, keys, walls, block_top=True):
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  self.SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -self.SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  self.SPEED

        if dx != 0 or dy != 0:
            if abs(dx) > abs(dy):
                self.sprites.set_anim("run", "right" if dx > 0 else "left")
            else:
                self.sprites.set_anim("run", "down" if dy > 0 else "up")
        else:
            self.sprites.set_anim("idle")

        self.rect.x += dx
        for w in walls:
            if self.rect.colliderect(w):
                if dx > 0: self.rect.right = w.left
                else:      self.rect.left  = w.right

        self.rect.y += dy
        for w in walls:
            if self.rect.colliderect(w):
                if dy > 0: self.rect.bottom = w.top
                else:      self.rect.top    = w.bottom

        if block_top and self.rect.top < 2 * T:
            self.rect.top = 2 * T

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def near_point(self, px, py, radius=40):
        dx = self.rect.centerx - px
        dy = self.rect.centery - py
        return math.sqrt(dx * dx + dy * dy) < radius

    def near_door(self, door_rects, radius=50):
        if not door_rects:
            return False
        door_union = door_rects[0].unionall(door_rects[1:])
        return door_union.inflate(radius * 2, radius * 2).colliderect(self.rect)

    def trigger_hurt(self):
        self.sprites.show_hurt()

    def draw(self, surface):
        if self.inv_timer > 0 and (self.inv_timer // 5) % 2 == 0:
            return
        self.sprites.update()
        frame  = self.sprites.get_frame()
        draw_x = self.rect.centerx - frame.get_width()  // 2
        draw_y = self.rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))
        if self.has_apple and apple_sprite:
            # Draw apple sprite above player's head
            apple_x = self.rect.centerx - apple_sprite.get_width() // 2
            apple_y = self.rect.top - apple_sprite.get_height() - 4
            surface.blit(apple_sprite, (apple_x, apple_y))
        elif self.has_apple:
            # Fallback to drawing circle if sprite fails to load
            pygame.draw.circle(surface, (200, 40, 40),
                               (self.rect.centerx, self.rect.top - 8), 5)
        if self.has_apple:
            pygame.draw.circle(surface, (200, 40, 40),
                               (self.rect.centerx, self.rect.top - 8), 5)
            pygame.draw.circle(surface, (240, 80, 80),
                               (self.rect.centerx - 1, self.rect.top - 9), 3)


# =============================================================================
# LIGHTNING BOLT
# =============================================================================
class Lightning:
    WARN_FRAMES  = 45
    LINGER_FRAMES = 28

    def __init__(self, tx, ty):
        self.x          = tx
        self.y          = ty
        self.warn_timer = self.WARN_FRAMES
        self.live_timer = self.LINGER_FRAMES

    def update(self):
        if self.warn_timer > 0:
            self.warn_timer -= 1
            return False
        if self.live_timer > 0:
            self.live_timer -= 1
            return False
        return True   # finished — remove

    @property
    def is_live(self):
        return self.warn_timer <= 0 and self.live_timer > 0

    def hits(self, rect):
        if not self.is_live:
            return False
        return pygame.Rect(self.x - 14, self.y - 14, 28, 28).colliderect(rect)

    def draw(self, surface):
        if self.warn_timer > 0:
            alpha = int(200 * (1 - self.warn_timer / self.WARN_FRAMES))
            ws = pygame.Surface((52, 52), pygame.SRCALPHA)
            pygame.draw.circle(ws, (255, 60, 60, alpha), (26, 26), 24, 3)
            surface.blit(ws, (self.x - 26, self.y - 26))
            return
        if self.live_timer <= 0:
            return

        bright = int(255 * (self.live_timer / self.LINGER_FRAMES))
        pts = [(self.x, 0)]
        cy  = 0
        while cy < self.y:
            cy += random.randint(18, 34)
            pts.append((self.x + random.randint(-14, 14), min(cy, self.y)))
        pts.append((self.x, self.y))
        if len(pts) >= 2:
            pygame.draw.lines(surface, (bright, bright, 60), False, pts, 3)
            pygame.draw.lines(surface, (255, 255, 200),       False, pts, 1)
        glow = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 240, 80, bright // 2), glow.get_rect())
        surface.blit(glow, (self.x - 30, self.y - 20))


# =============================================================================
# GOD  — ignores all walls, floats straight toward player
# =============================================================================
class God:
    SIZE = 20

    def __init__(self, smite_range=GOD_SMITE_RANGE):
        # Spawns from the top-centre of the map
        self.rect       = pygame.Rect(WIDTH // 2 - self.SIZE // 2, -80,
                                      self.SIZE, self.SIZE)
        self.speed = GOD_SPEED
        self.lightning_cooldown = LIGHTNING_COOLDOWN
        self.lightning_count = LIGHTNING_COUNT
        self.bolt_timer = self.lightning_cooldown // 2
        self.smite_range = smite_range

        self.anim_index = 0
        self.anim_timer = 0
        self.ANIM_SPEED = 8  # frames per sprite frame

    def update(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        self.rect.x += (dx / dist) * self.speed
        self.rect.y += (dy / dist) * self.speed
        # intentionally no wall collision — God passes through everything

    def in_smite_range(self, player_rect):
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        return math.sqrt(dx * dx + dy * dy) < self.smite_range

    def try_spawn_bolts(self, player_rect):
        self.bolt_timer -= 1
        if self.bolt_timer > 0:
            return []
        self.bolt_timer = self.lightning_cooldown
        bolts = []
        for _ in range(self.lightning_count):
            tx = player_rect.centerx + random.randint(-130, 130)
            ty = player_rect.centery + random.randint(-90,  90)
            tx = max(T * 2, min(WIDTH  - T * 2, tx))
            ty = max(T * 4, min(HEIGHT - T * 2, ty))
            bolts.append(Lightning(tx, ty))
        return bolts

    def draw(self, surface):
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % max(len(boss_frames), 1)

        cx, cy = int(self.rect.centerx), int(self.rect.centery)
        ticks = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(ticks / 200)

        # ── Outer pulsing aura ────────────────────────────────────────────────────
        glow_r = int(80 + 20 * pulse)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 255, 200, int(40 + 30 * pulse)), glow.get_rect())
        surface.blit(glow, (cx - glow_r, cy - glow_r))

        # ── Radiant lines ─────────────────────────────────────────────────────────
        for angle in range(0, 360, 45):
            rad = math.radians(angle + ticks / 10)
            x1 = cx + int(math.cos(rad) * 55)
            y1 = cy + int(math.sin(rad) * 55)
            x2 = cx + int(math.cos(rad) * 75)
            y2 = cy + int(math.sin(rad) * 75)
            pygame.draw.line(surface, (255, 240, 120, 180), (x1, y1), (x2, y2), 2)

        # ── Sprite ────────────────────────────────────────────────────────────────
        if boss_frames:
            frame = boss_frames[self.anim_index]
            draw_x = cx - frame.get_width() // 2
            draw_y = cy - frame.get_height() // 2
            surface.blit(frame, (draw_x, draw_y))

        # ── Halo ring above the sprite head ──────────────────────────────────────
        halo_r = int(28 + 4 * pulse)
        halo_y = cy - (boss_frames[0].get_height() // 2) + 10 if boss_frames else cy - 50
        halo_surf = pygame.Surface((halo_r * 2 + 10, halo_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(halo_surf, (255, 240, 100, int(160 + 60 * pulse)),
                            halo_surf.get_rect(), 4)
        surface.blit(halo_surf, (cx - halo_r - 5, halo_y - halo_r - 5))


# =============================================================================
# SCREEN SHAKE
# =============================================================================
class ScreenShake:
    def __init__(self):
        self.timer    = 0
        self.strength = 0

    def start(self, frames, strength=6):
        self.timer    = max(self.timer, frames)
        self.strength = max(self.strength, strength)

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.strength = 0

    @property
    def offset(self):
        if self.timer <= 0:
            return (0, 0)
        return (random.randint(-self.strength, self.strength),
                random.randint(-self.strength, self.strength))


# =============================================================================
# DRAW SCENE
# =============================================================================
def draw_cutscene_line(surface, tag, typewriter):
    box_w, box_h = 560, 80
    box_x = WIDTH  // 2 - box_w // 2
    box_y = HEIGHT // 2 - box_h // 2

    ov = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    ov.fill((10, 10, 10, 210))
    surface.blit(ov, (box_x, box_y))
    pygame.draw.rect(surface, (160, 160, 180),
                     (box_x, box_y, box_w, box_h), 2, border_radius=6)
    txt = font_md.render(typewriter.current, True, WHITE)
    surface.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    ticks = pygame.time.get_ticks()
    if typewriter.done and (ticks // 500) % 2 == 0:
        p = font_sm.render("▶ Enter", True, (160, 160, 160))
        surface.blit(p, (box_x + box_w - p.get_width() - 12,
                         box_y + box_h - p.get_height() - 8))

def draw_scene(surface, player, god, lightning_bolts,
               door_open, entrance_closed,
               tree_center, door_rects,
               door_kicks, door_kicks_needed,
               apple_on_ground, apple_pos,
               red_flash_alpha, shake,
               god_spawned):

    ox, oy    = shake.offset
    draw_surf = pygame.Surface((WIDTH, HEIGHT))

    # ── TMX layers ────────────────────────────────────────────────────────────
    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue

        # Entrance doors — closed once player enters; open again after kick
        if layer.name in ("Entracne - Open", "Entrance2 - Open"):
            if not door_open:
                continue   # hide open-door tiles when door is closed/intact
        if layer.name in ("Entrance", "Entrance2"):
            if door_open:
                continue   # hide closed-door tiles when door is open

        for x, y, gid in layer:
            tile_img = tmx_data.get_tile_image_by_gid(gid)
            if tile_img:
                draw_surf.blit(tile_img, (x * T, y * T))

    # ── Tree interact glow (explore phase only) ───────────────────────────────
    if tree_center and not god_spawned:
        ticks = pygame.time.get_ticks()
        alpha = int(70 + 50 * math.sin(ticks / 400))
        glow  = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (80, 220, 80, alpha), glow.get_rect())
        tx, ty = tree_center
        draw_surf.blit(glow, (tx - 22, ty - 22))

    # ── Apple on ground ───────────────────────────────────────────────────────
    if apple_on_ground and apple_pos:
        ax, ay = apple_pos
        if apple_sprite:
            # Draw the apple sprite centered on the position
            draw_surf.blit(apple_sprite, (ax - apple_sprite.get_width() // 2, ay - apple_sprite.get_height() // 2))
        else:
            # Fallback to drawing circles if sprite fails to load
            pygame.draw.circle(draw_surf, (200,  40,  40), (ax, ay),  6)
            pygame.draw.circle(draw_surf, (240,  80,  80), (ax - 1, ay - 2), 3)
            pygame.draw.line(  draw_surf, ( 80, 140,  40), (ax, ay - 6), (ax + 3, ay - 10), 2)

    # ── Door kick UI (god phase) ──────────────────────────────────────────────
    if god_spawned and not door_open and door_rects:
        door_union = door_rects[0].unionall(door_rects[1:])
        progress   = door_kicks / max(door_kicks_needed, 1)
        crack_col  = (int(220 * progress), int(80 * (1 - progress)), 0)
        pygame.draw.rect(draw_surf, crack_col, door_union.inflate(4, 4), 2, border_radius=2)

        # Progress bar just above the door
        bx, by, bw = door_union.x, door_union.y - 10, door_union.width
        pygame.draw.rect(draw_surf, (50, 20, 20),          (bx, by, bw, 5))
        pygame.draw.rect(draw_surf, (220, 80, 40), (bx, by, int(bw * progress), 5))

        if player.near_door(door_rects, radius=50):
            hint = font_sm.render(
                f"[E] Kick the door  ({door_kicks}/{door_kicks_needed})", True, WHITE)
            hbg = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8),
                                  pygame.SRCALPHA)
            hbg.fill((10, 10, 10, 180))
            draw_surf.blit(hbg,  (WIDTH // 2 - hbg.get_width() // 2,  HEIGHT - 44))
            draw_surf.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

    # ── Lightning ─────────────────────────────────────────────────────────────
    for bolt in lightning_bolts:
        bolt.draw(draw_surf)

    # ── God ───────────────────────────────────────────────────────────────────
    if god_spawned:
        god.draw(draw_surf)

    # ── Player ────────────────────────────────────────────────────────────────
    player.draw(draw_surf)

    # ── HUD ───────────────────────────────────────────────────────────────────
    hx, hy = 8, 8
    for i in range(MAX_LIVES):
        if heart_full and heart_empty:
            img = heart_full if i < player.lives else heart_empty
            draw_surf.blit(img, (hx, hy))
            hx += img.get_width() + 4
        else:
            col = (220, 50, 50) if i < player.lives else (80, 80, 80)
            pygame.draw.circle(draw_surf, col, (hx + 8, hy + 8), 7)
            hx += 20

    # Tree approach hint (explore phase)
    if not god_spawned and tree_center:
        tx, ty = tree_center
        if player.near_point(tx, ty, radius=55):
            hint = font_sm.render("[E] Approach the tree", True, WHITE)
            hbg  = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8),
                                   pygame.SRCALPHA)
            hbg.fill((10, 10, 10, 180))
            draw_surf.blit(hbg,  (WIDTH // 2 - hbg.get_width() // 2,  HEIGHT - 44))
            draw_surf.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

    # ── Red flash ─────────────────────────────────────────────────────────────
    if red_flash_alpha > 0:
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash.fill((200, 0, 0, int(red_flash_alpha)))
        draw_surf.blit(flash, (0, 0))

    surface.blit(draw_surf, (ox, oy))


# =============================================================================
# DIALOG HELPERS
# =============================================================================
def draw_angel_dialog(surface, speaker, typewriter):
    is_mikhail = (speaker == "Mikhail")
    border_col = MIKHAIL_BORDER if is_mikhail else RAZIEL_BORDER

    box_x = WIDTH  // 2 - DIALOG_W // 2
    box_y = HEIGHT - DIALOG_H - 10

    ov = pygame.Surface((DIALOG_W, DIALOG_H), pygame.SRCALPHA)
    ov.fill((10, 10, 10, 230))
    surface.blit(ov, (box_x, box_y))
    pygame.draw.rect(surface, border_col,
                     (box_x, box_y, DIALOG_W, DIALOG_H), 3, border_radius=8)

    portrait_x = box_x + 10
    portrait_y = box_y + DIALOG_H // 2 - PORTRAIT_SIZE // 2
    pygame.draw.rect(surface, (20, 20, 20),
                     (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    pygame.draw.rect(surface, border_col,
                     (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE), 3)

    img = portrait_mikhail if is_mikhail else portrait_raziel
    if img:
        surface.blit(img, (portrait_x, portrait_y))
    else:
        ph = font_md.render("?", True, (70, 70, 70))
        surface.blit(ph, ph.get_rect(center=(portrait_x + PORTRAIT_SIZE // 2,
                                             portrait_y + PORTRAIT_SIZE // 2)))

    surface.blit(font_md.render(speaker, True, border_col),
                 (portrait_x, portrait_y - 22))

    text_x = portrait_x + PORTRAIT_SIZE + 18
    max_w  = DIALOG_W - PORTRAIT_SIZE - 36
    words  = typewriter.current.split(" ")
    lines, line = [], ""
    for word in words:
        test = line + (" " if line else "") + word
        if font_md.size(test)[0] <= max_w:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    y_off = box_y + DIALOG_H // 2 - (len(lines) * 26) // 2
    for ln in lines:
        surface.blit(font_md.render(ln, True, WHITE), (text_x, y_off))
        y_off += 26

    ticks = pygame.time.get_ticks()
    if typewriter.done:
        if (ticks // 500) % 2 == 0:
            p = font_sm.render("▶ Enter", True, (160, 160, 160))
            surface.blit(p, (box_x + DIALOG_W - p.get_width() - 12,
                              box_y + DIALOG_H - p.get_height() - 8))
    else:
        p = font_sm.render("▶ Skip", True, (100, 100, 100))
        surface.blit(p, (box_x + DIALOG_W - p.get_width() - 12,
                          box_y + DIALOG_H - p.get_height() - 8))


def draw_simple_dialog(surface, lines, options=None):
    box_w = 500
    box_h = 30 + len(lines) * 28 + (10 + len(options) * 30 if options else 0)
    box_x = WIDTH  // 2 - box_w // 2
    box_y = HEIGHT // 2 - box_h // 2
    ov = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    ov.fill((10, 10, 10, 220))
    surface.blit(ov, (box_x, box_y))
    pygame.draw.rect(surface, GOLD, (box_x, box_y, box_w, box_h), 2, border_radius=6)
    y = box_y + 16
    for line in lines:
        surface.blit(font_md.render(line, True, WHITE), (box_x + 20, y))
        y += 28
    if options:
        y += 8
        for key, label in options:
            surface.blit(font_md.render(f"[{key}]  {label}", True, GOLD),
                         (box_x + 30, y))
            y += 30


# =============================================================================
# STATES
# =============================================================================
STATE_EXPLORE      = "explore"
STATE_APPLE_DIALOG = "apple_dialog"
STATE_EATING       = "eating"
STATE_GOD_PHASE    = "god_phase"
STATE_GAME_OVER    = "gameover"
STATE_ESCAPED      = "escaped"
STATE_EPILOGUE     = "epilogue"
STATE_END          = "end"


# =============================================================================
# MAIN
# =============================================================================
def main():
    walls, wall_set, tree_center, door_rects = build_from_tmx()

    # ── Music ──
    try:
        pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "21. The Silent Lake.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    player          = Player()
    
    # Initialize difficulty manager
    difficulty_mgr = DifficultyManager(player, "TheGarden")
    
    # Apply difficulty modifiers to God parameters
    god_speed = difficulty_mgr.get_modifier("god_speed_multiplier", 1.0) * GOD_SPEED
    lightning_cooldown = int(LIGHTNING_COOLDOWN * difficulty_mgr.get_modifier("lightning_cooldown_multiplier", 1.0))
    lightning_count = difficulty_mgr.get_modifier("lightning_count", LIGHTNING_COUNT)
    god_smite_range = GOD_SMITE_RANGE * difficulty_mgr.get_modifier("god_smite_cooldown_multiplier", 1.0)
    
    god             = God(smite_range=god_smite_range)
    # Override God's speed and cooldown with difficulty modifiers
    god.speed = god_speed
    god.bolt_timer = lightning_cooldown // 2
    god.lightning_cooldown = lightning_cooldown
    god.lightning_count = lightning_count
    
    lightning_bolts = []
    shake           = ScreenShake()

    cs_index          = 0
    state             = STATE_CUTSCENE    # ← changed
    door_open         = False
    entrance_closed   = False
    god_spawned       = False
    inv_timer         = 0

    # Apply tree_shakes_required modifier
    tree_shakes_needed = difficulty_mgr.get_modifier("tree_shakes_required", TREE_SHAKE_NEEDED)
    tree_shakes       = 0
    apple_on_ground   = False
    apple_pos         = None

    door_kicks        = 0
    door_kicks_needed = random.randint(DOOR_KICK_MIN, DOOR_KICK_MAX)
    door_kick_cd      = 0

    red_flash_alpha   = 0
    eating_timer      = 0

    typewriter        = Typewriter()
    typewriter.set_text(CUTSCENE[0][1])   # ← changed
    epilogue_index    = 0

    while True:
        clock.tick(60)
        shake.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                # ── Cutscene ──────────────────────────────────────────────
                if state == STATE_CUTSCENE:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            cs_index += 1
                            if cs_index < len(CUTSCENE):
                                typewriter.set_text(CUTSCENE[cs_index][1])
                            else:
                                state = STATE_EXPLORE

                # ── Explore ───────────────────────────────────────────────
                elif state == STATE_EXPLORE:
                    if event.key == pygame.K_e:
                        tx, ty = tree_center
                        if player.near_point(tx, ty, radius=55) and not apple_on_ground:
                            tree_shakes += 1
                            shake.start(18, strength=4)
                            if tree_shakes >= tree_shakes_needed:
                                apple_on_ground = True
                                apple_pos       = (tx, ty + 24)
                        elif apple_on_ground and apple_pos:
                            ax, ay = apple_pos
                            if player.near_point(ax, ay, radius=22):
                                apple_on_ground  = False
                                apple_pos        = None
                                player.has_apple = True
                                typewriter.set_text(
                                    "You feel like you're making a terrible mistake.")
                                state = STATE_APPLE_DIALOG

                elif state == STATE_APPLE_DIALOG:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            player.has_apple = False
                            eating_timer     = 180
                            red_flash_alpha  = 0
                            shake.start(180, strength=7)
                            state = STATE_EATING
                            try:
                                pygame.mixer.music.fadeout(800)
                            except Exception:
                                pass

                elif state == STATE_GOD_PHASE:
                    if event.key == pygame.K_e:
                        if not door_open \
                                and player.near_door(door_rects, radius=50) \
                                and door_kick_cd <= 0:
                            door_kicks += 1
                            door_kick_cd = 20
                            shake.start(10, strength=3)
                            if door_kicks >= door_kicks_needed:
                                door_open = True

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        main(); return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == STATE_EPILOGUE:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            epilogue_index += 1
                            if epilogue_index < len(EPILOGUE):
                                typewriter.set_text(EPILOGUE[epilogue_index][1])
                            else:
                                state = STATE_END

                elif state == STATE_END:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        pygame.quit(); sys.exit()

        # ── Typewriter tick ───────────────────────────────────────────────
        if state in (STATE_CUTSCENE, STATE_APPLE_DIALOG, STATE_EPILOGUE):
            typewriter.update()
        
        # ── Update difficulty manager ─────────────────────────────────────
        difficulty_mgr.update()

        # ── Eating sequence ───────────────────────────────────────────────
        if state == STATE_EATING:
            eating_timer -= 1
            cycle = eating_timer % 30
            red_flash_alpha = 160 if cycle > 15 else 0

            if eating_timer <= 0:
                red_flash_alpha = 0
                shake.start(0)
                god_spawned     = True
                door_open       = False
                entrance_closed = True
                state           = STATE_GOD_PHASE
                try:
                    pygame.mixer.music.load(
                        os.path.join(BASE_DIR, "audio", "Hostile_March_BattleTheme.wav"))
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)
                except Exception:
                    pass

        # ── Explore movement ──────────────────────────────────────────────
        if state == STATE_EXPLORE:
            keys = pygame.key.get_pressed()
            player.move(keys, walls, block_top=True)

            if not entrance_closed and player.rect.centery < HEIGHT - 8 * T:
                entrance_closed = True
                door_open       = False

        # ── God phase movement & logic ────────────────────────────────────
        if state == STATE_GOD_PHASE:
            keys = pygame.key.get_pressed()
            active_walls = [w for w in walls if not any(
                w.colliderect(dr) for dr in door_rects)] if door_open else walls
            player.move(keys, active_walls, block_top=not door_open)

            if door_kick_cd  > 0: door_kick_cd  -= 1
            if inv_timer     > 0: inv_timer      -= 1
            if player.inv_timer > 0: player.inv_timer -= 1

            god.update(player.rect)

            if god.in_smite_range(player.rect) and inv_timer <= 0:
                state = STATE_GAME_OVER

            for bolt in god.try_spawn_bolts(player.rect):
                lightning_bolts.append(bolt)

            for bolt in lightning_bolts[:]:
                done = bolt.update()
                if bolt.hits(player.rect) and inv_timer <= 0:
                    player.lives    -= 1
                    inv_timer        = INVINCIBLE_FRAMES
                    player.inv_timer = INVINCIBLE_FRAMES
                    shake.start(20, strength=5)
                    if player.lives <= 0:
                        state = STATE_GAME_OVER
                if done:
                    lightning_bolts.remove(bolt)

            keys_held = pygame.key.get_pressed()
            if keys_held[pygame.K_e] and not door_open \
                    and player.near_door(door_rects, radius=50) \
                    and door_kick_cd <= 0:
                door_kicks += 1
                door_kick_cd = 20
                shake.start(10, strength=3)
                if door_kicks >= door_kicks_needed:
                    door_open = True

            if door_open and player.rect.top <= 4 * T:
                state = STATE_ESCAPED

        if state == STATE_ESCAPED:
            try:
                import TheStatues
                TheStatues.god_main(god, player.lives)
            except Exception as e:
                print(f"[ERROR transitioning to TheStatues.god_main]: {e}")
                import traceback
                traceback.print_exc()
            return

        # ── Draw ──────────────────────────────────────────────────────────
        draw_scene(game_surface, player, god, lightning_bolts,
                   door_open, entrance_closed,
                   tree_center, door_rects,
                   door_kicks, door_kicks_needed,
                   apple_on_ground, apple_pos,
                   red_flash_alpha, shake,
                   god_spawned)
        
        # ── Draw difficulty indicator ─────────────────────────────────────
        difficulty_mgr.draw_indicator(game_surface, font_md)

        if state == STATE_CUTSCENE:
            draw_cutscene_line(game_surface, "NARRATE", typewriter)

        elif state == STATE_APPLE_DIALOG:
            draw_simple_dialog(game_surface,
                ["You feel like you're making a terrible mistake.", "..."],
                [("Enter", "Take a bite anyway")])

        elif state == STATE_EATING:
            ticks = pygame.time.get_ticks()
            if (ticks // 200) % 2 == 0:
                warn = font_lg.render("!!!", True, (255, 200, 40))
                game_surface.blit(warn, warn.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        elif state == STATE_GAME_OVER:
            draw_simple_dialog(game_surface,
                ["The divine presence consumes you.",
                 "There is no escaping divine wrath."],
                [("R", "Try again"), ("Esc", "Quit")])

        elif state == STATE_EPILOGUE:
            speaker = EPILOGUE[epilogue_index][0]
            draw_angel_dialog(game_surface, speaker, typewriter)

        elif state == STATE_END:
            draw_simple_dialog(game_surface,
                ["You escaped Eden.",
                 "But something tells you...",
                 "...the garden will never forget."],
                [("Enter", "Fin.")])

        # Scale and display the game surface with letterboxing/pillarboxing
        scaler.display(screen, game_surface)
        pygame.display.flip()


if __name__ == "__main__":
    main()