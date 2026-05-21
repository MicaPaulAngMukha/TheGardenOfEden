import pygame
import sys
import os
import math
import random
import pytmx
import collections
import TheStatues
import TheGarden
from display_scaler import DisplayScaler
from resource_path import resource_path
from difficulty_manager import DifficultyManager
from god_entity import GodEntity, Lightning

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

# Create display scaler for letterboxing/pillarboxing
scaler = DisplayScaler(WIDTH, HEIGHT)
# Create game surface at native resolution
game_surface = pygame.Surface((WIDTH, HEIGHT))

tmx_data = pytmx.load_pygame(resource_path("TheGuardianMap.tmx"))

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
GOLD         = (212, 175,  55)
PLAYER_COL   = (200, 160,  80)
PLAYER_HEAD  = (210, 170, 120)
GUARD_BORDER = (200, 200, 255)
KEY_GLOW     = (255, 240, 120)

STATE_PROMPT = "prompt"

# ── Grid ──────────────────────────────────────────────────────────────────────
T    = 13
COLS = WIDTH  // T
ROWS = HEIGHT // T

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_PATH = os.path.join(BASE_DIR, "font", "PixelifySans-VariableFont_wght.ttf")
font_sm   = pygame.font.Font(FONT_PATH, 15)
font_md   = pygame.font.Font(FONT_PATH, 19)
font_hud  = pygame.font.Font(FONT_PATH, 15)

# ── Hearts ────────────────────────────────────────────────────────────────────
try:
    heart_full  = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "LifeHeart.png")).convert_alpha(), (20, 20))
    heart_empty = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "LifeHeartLoss.png")).convert_alpha(), (20, 20))
except Exception:
    heart_full = heart_empty = None

# ── Key image ─────────────────────────────────────────────────────────────────
try:
    key_img = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "Key.png")).convert_alpha(), (16, 16))
except Exception:
    key_img = None

# ── Guardian portrait ─────────────────────────────────────────────────────────
PORTRAIT_SIZE = 140
DIALOG_W      = 700
DIALOG_H      = 180

try:
    portrait_guardian = pygame.transform.scale(
        pygame.image.load(
            os.path.join(BASE_DIR, "Sprites", "Guardian", "Guardian.png")
        ).convert_alpha(),
        (PORTRAIT_SIZE, PORTRAIT_SIZE))
except Exception:
    portrait_guardian = None

# ── Constants ─────────────────────────────────────────────────────────────────
PLAYER_SIZE       = 24
MAX_LIVES         = 3
PLAYER_SPAWN = (WIDTH // 2, 40)

GUARD_SPEED_NORMAL = 1.8
GUARD_SPEED_LIGHT  = 3.4
GUARD_SPEED_LOUD   = 5.0
GUARD_SPEED_CHASE_BASE  = 3.0  # Base chase speed, will be modified by difficulty

LIGHT_RADIUS      = 70
INVINCIBLE_FRAMES = 90
TYPEWRITER_SPEED  = 2

PULSE_DARK_DURATION_BASE  = 300   # frames of darkness (5 seconds) - baseline
PULSE_LIGHT_DURATION_BASE = 180   # frames of light (3 seconds) - baseline
PULSE_TRANSITION     = 40    # frames to fade in/out

WALL_LAYERS = {"MazeWalls", "Walls", "WallsBack", "Walls_Side", "walls_exit"}
BUSH_LIGHT_LAYERS = {"BushDecorLight", "BushDecorLight2"}
BUSH_DENSE_LAYERS = {"BushDecorDense"}

# ── Sprite sheet measured dimensions ──────────────────────────────────────────
# guardian_idle.png  : 104 x 208  -> 2 cols x 4 rows -> frame 52 x 52
# guardian_slash.png : 624 x 272  -> 6 cols x 4 rows -> frame 104 x 68
# guardian_walk.png  : 531 x 212  -> 9 cols x 4 rows -> frame 59 x 53
IDLE_FW,  IDLE_FH,  IDLE_FRAMES  = 52,  52,  2
SLASH_FW, SLASH_FH, SLASH_FRAMES = 104, 68,  6
WALK_FW,  WALK_FH,  WALK_FRAMES  = 59,  53,  9

# ── Dialogue ──────────────────────────────────────────────────────────────────
DIALOGS = {
    "intro": [
        ("Guardian", ".... A human."),
        ("Guardian", "How did you get this far into Eden?"),
        ("Guardian", "Did those two idiots at the gate not stop you?"),
        ("Guardian", "It matters not what you answer."),
        ("Guardian", "Don't move."),
        ("Guardian", "Take a step further and you shall be punished."),
    ],
    "warning": [
        ("Guardian", "You want to be difficult?"),
        ("Guardian", "So be it."),
        ("Guardian", "Your journey shall end here."),
    ],
    "darkness": [
        ("Guardian", "Let's see if you can traverse through Eden now."),
    ],
}

# ── States ────────────────────────────────────────────────────────────────────
STATE_INTRO        = "intro"
STATE_PLAY         = "play"
STATE_WARNING      = "warning"
STATE_DARKNESS_DLG = "darkness_dlg"
STATE_HIT          = "hit"
STATE_GAME_OVER    = "gameover"
STATE_WIN          = "win"


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
    walls          = []
    wall_set       = set()
    bush_tiles     = []
    exit_tiles     = []
    entrance_tiles = []
    walls_exit = []

    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        for x, y, gid in layer:
            if gid == 0:
                continue
            r = pygame.Rect(x * T, y * T, T, T)
            if layer.name in WALL_LAYERS:
                walls.append(r)
                wall_set.add((x, y))

            elif layer.name == "walls_exit":  # ← separate collection
                walls_exit.append(r)
                wall_set.add((x, y))
            elif layer.name in BUSH_LIGHT_LAYERS:
                bush_tiles.append({"rect": r, "tile": (x, y),
                                   "layer_type": "light", "has_key": False,
                                   "triggered": False, "key_collected": False})
            elif layer.name in BUSH_DENSE_LAYERS:
                bush_tiles.append({"rect": r, "tile": (x, y),
                                   "layer_type": "dense", "has_key": False,
                                   "triggered": False, "key_collected": False})
            elif layer.name in ("Exit", "Exit2", "Exit - Open", "Exit2 - Open"):
                exit_tiles.append(r)
            elif layer.name in ("Entrance", "Entrance2",
                                "Entracne - Open", "Entrance2 - Open"):
                entrance_tiles.append(r)

    return walls, wall_set, bush_tiles, exit_tiles, entrance_tiles, walls_exit


def place_key(bush_tiles):
    if not bush_tiles:
        return
    for b in bush_tiles:
        b["has_key"] = False
    random.choice(bush_tiles)["has_key"] = True


# =============================================================================
# BFS PATHFINDER
# =============================================================================
def find_path(start, goal, wall_set):
    if start == goal:
        return [start]
    queue     = collections.deque([start])
    came_from = {start: None}
    while queue:
        curr = queue.popleft()
        if curr == goal:
            path = []
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            return path[::-1]
        c, r = curr
        for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nc, nr = c + dc, r + dr
            if (nc, nr) not in came_from and (nc, nr) not in wall_set:
                if 0 <= nc < COLS and 0 <= nr < ROWS:
                    came_from[(nc, nr)] = curr
                    queue.append((nc, nr))
    return []


# =============================================================================
# PLAYER
# =============================================================================
class Player:
    SPEED = 3

    def __init__(self):
        self.lives     = MAX_LIVES
        self.has_key   = False
        self.inv_timer = 0
        self.sprites   = PlayerSprites(scale=1)
        self.rect      = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = PLAYER_SPAWN
        self.sprites.set_anim("idle", "down")

    def move(self, keys, walls):
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

        moved = dx != 0 or dy != 0

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

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        return moved

    def trigger_hurt(self):
        self.sprites.show_hurt()

    def draw(self, surface):
        if self.inv_timer > 0 and (self.inv_timer // 5) % 2 == 0:
            return  # this is already correct — make sure inv_timer starts at 0
        self.sprites.update()
        frame = self.sprites.get_frame()
        draw_x = self.rect.centerx - frame.get_width() // 2
        draw_y = self.rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))
        if self.has_key and key_img:
            surface.blit(key_img, (self.rect.centerx - 8, self.rect.top - 20))


# =============================================================================
# SPRITE SHEET  — safe subsurface extraction
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
    """Simple sprite sheet loader for the player — does NOT assume 4 rows."""
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


# =============================================================================
# GUARDIAN SPRITES
# =============================================================================
class GuardianSprites:
    # Standard LPC layout: up=0, left=1, down=2, right=3
    ROWS = {"up": 0, "left": 1, "down": 2, "right": 3}

    def __init__(self, scale=1):
        base = os.path.join(BASE_DIR, "Sprites", "Guardian")

        def load(filename, fw, fh, num_frames, speed=8):
            path = os.path.join(base, filename)
            return {
                d: SpriteSheet(path, fw, fh, num_frames,
                               row=row, scale=scale, speed=speed)
                for d, row in self.ROWS.items()
            }

        self.anims = {
            # idle  : 104x208 -> 2 cols x 4 rows -> 52x52 per frame
            "idle":  load("guardian_idle.png",
                          IDLE_FW, IDLE_FH, IDLE_FRAMES, speed=14),
            # walk  : 531x212 -> 9 cols x 4 rows -> 59x53 per frame
            "walk":  load("guardian_walk.png",
                          WALK_FW, WALK_FH, WALK_FRAMES, speed=8),
            # slash : 624x272 -> 6 cols x 4 rows -> 104x68 per frame
            "slash": {"up":    SpriteSheet(os.path.join(base, "guardian_slash.png"), SLASH_FW, SLASH_FH, SLASH_FRAMES, row=0, scale=1, speed=7),
              "left":  SpriteSheet(os.path.join(base, "guardian_slash.png"), SLASH_FW, SLASH_FH, SLASH_FRAMES, row=0, scale=1, speed=7),
              "down":  SpriteSheet(os.path.join(base, "guardian_slash.png"), SLASH_FW, SLASH_FH, SLASH_FRAMES, row=0, scale=1, speed=7),
              "right": SpriteSheet(os.path.join(base, "guardian_slash.png"), SLASH_FW, SLASH_FH, SLASH_FRAMES, row=0, scale=1, speed=7)},
            }

        self.current_anim = "idle"
        self.current_dir  = "up"

    def set_anim(self, anim, direction=None):
        if direction and direction in self.ROWS:
            self.current_dir = direction
        if anim != self.current_anim:
            self.current_anim = anim
            self.anims[anim][self.current_dir].reset()

    def update(self):
        self.anims[self.current_anim][self.current_dir].update()

    def draw(self, surface, rect):
        frame  = self.anims[self.current_anim][self.current_dir].current()
        draw_x = rect.centerx - frame.get_width()  // 2
        draw_y = rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))


# =============================================================================
# GUARDIAN
# =============================================================================
class Guardian:
    SIZE = 14

    def __init__(self):
        cx = WIDTH // 2
        cy = HEIGHT - 8 * T
        self.rect        = pygame.Rect(cx - self.SIZE // 2, cy - self.SIZE // 2,
                                       self.SIZE, self.SIZE)
        self.speed       = GUARD_SPEED_NORMAL
        self.path        = []
        self.path_timer  = 0
        self.chasing     = False
        self.alert_speed = None
        self.sprites     = GuardianSprites(scale=1)
        self.roam_target = None
        self.roam_timer  = 0

    def _pick_roam_target(self, wall_set):
        for _ in range(30):
            tx = random.randint(2, COLS - 2)
            ty = random.randint(2, ROWS - 2)
            if (tx, ty) not in wall_set:
                self.roam_target = (tx, ty)
                self.roam_timer  = random.randint(180, 360)
                return
        self.roam_target = (COLS // 2, ROWS // 2)
        self.roam_timer  = 200

    def update_roam(self, wall_set):
        self.roam_timer -= 1
        if self.roam_timer <= 0 or self.roam_target is None:
            self._pick_roam_target(wall_set)
            self.path = []
            return
        if not self.path or self.path_timer >= 20:
            self.path_timer = 0
            sc = self.rect.centerx // T
            sr = self.rect.centery  // T
            self.path = find_path((sc, sr), self.roam_target, wall_set)
        self.path_timer += 1
        self._move_path()
        if self.roam_target:
            dx = self.roam_target[0] * T - self.rect.centerx
            dy = self.roam_target[1] * T - self.rect.centery
            self._set_walk_dir(dx, dy)

    def update_chase(self, player_rect, wall_set):
        if self.path_timer >= 10:
            self.path_timer = 0
            sc = self.rect.centerx // T
            sr = self.rect.centery  // T
            gc = player_rect.centerx // T
            gr = player_rect.centery  // T
            self.path = find_path((sc, sr), (gc, gr), wall_set)
        self.path_timer += 1
        self._move_path()
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        self._set_walk_dir(dx, dy)

    def _move_path(self):
        if not self.path or len(self.path) < 2:
            return
        target_c, target_r = self.path[1]
        tx = target_c * T + T // 2
        ty = target_r * T + T // 2
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        spd  = self.alert_speed if self.alert_speed else self.speed
        if dist <= spd:
            self.rect.centerx = tx
            self.rect.centery = ty
            self.path.pop(0)
        else:
            self.rect.x += int((dx / dist) * spd)
            self.rect.y += int((dy / dist) * spd)
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def _set_walk_dir(self, dx, dy):
        d = ("right" if dx > 0 else "left") if abs(dx) > abs(dy) \
            else ("down" if dy > 0 else "up")
        self.sprites.set_anim("walk", d)

    def touches(self, player_rect):
        return self.rect.inflate(4, 4).colliderect(player_rect)

    def draw(self, surface):
        if self.chasing:
            glow = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 80, 80, 80), glow.get_rect())
            surface.blit(glow, (self.rect.x - 23, self.rect.y - 23))
        self.sprites.update()
        self.sprites.draw(surface, self.rect)


# =============================================================================
# DARKNESS OVERLAY
# =============================================================================
def make_darkness(player_rect, radius=LIGHT_RADIUS, guardian_dist=None, base_alpha=245):
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surf.fill((0, 0, 0, base_alpha))
    cx, cy = player_rect.centerx, player_rect.centery
    for r in range(radius, 0, -2):
        alpha = int(base_alpha * (1 - (r / radius) ** 0.4))
        pygame.draw.circle(surf, (0, 0, 0, alpha), (cx, cy), r)
    pygame.draw.circle(surf, (0, 0, 0, 0), (cx, cy), int(radius * 0.25))

    if guardian_dist is not None and base_alpha > 100:
        WARN_START = 200
        WARN_CLOSE = 60
        if guardian_dist < WARN_START:
            t = 1.0 - max(0.0, (guardian_dist - WARN_CLOSE) / (WARN_START - WARN_CLOSE))
            ring_alpha = int(180 * t)
            ring_r     = int(radius * 0.28 + 4)
            ring_col   = (int(255 * t), int(60 * (1 - t)), int(60 * (1 - t)), ring_alpha)
            pygame.draw.circle(surf, ring_col, (cx, cy), ring_r, 3)
    return surf


# =============================================================================
# DRAW SCENE
# =============================================================================
def draw_scene(surface, player, guardian, bush_tiles,
               gate_open, darkness_active, entrance_closed, pulse_alpha=245):

    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        if layer.name in ("Exit - Open", "Exit2 - Open") and not gate_open:
            continue
        if layer.name in ("Exit", "Exit2") and gate_open:
            continue
        if layer.name in ("Entracne - Open", "Entrance2 - Open") and entrance_closed:
            continue
        if layer.name in ("Entrance", "Entrance2") and not entrance_closed:
            continue
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(tile, (x * T, y * T))

    guardian.draw(surface)
    player.draw(surface)

    if darkness_active:
        dx = guardian.rect.centerx - player.rect.centerx
        dy = guardian.rect.centery - player.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        surface.blit(make_darkness(player.rect, guardian_dist=dist,
                                   base_alpha=pulse_alpha), (0, 0))

    hx, hy = 8, 8
    for i in range(MAX_LIVES):
        if heart_full and heart_empty:
            img = heart_full if i < player.lives else heart_empty
            surface.blit(img, (hx, hy))
            hx += img.get_width() + 4
        else:
            col = (220, 50, 50) if i < player.lives else (80, 80, 80)
            pygame.draw.circle(surface, col, (hx + 8, hy + 8), 7)
            hx += 20

    if player.has_key:
        surface.blit(font_hud.render("  KEY", True, GOLD), (hx + 8, hy + 2))


# =============================================================================
# DIALOG DRAWING
# =============================================================================
def draw_guardian_dialog(surface, typewriter):
    box_x = WIDTH  // 2 - DIALOG_W // 2
    box_y = HEIGHT - DIALOG_H - 10

    ov = pygame.Surface((DIALOG_W, DIALOG_H), pygame.SRCALPHA)
    ov.fill((10, 10, 10, 230))
    surface.blit(ov, (box_x, box_y))
    pygame.draw.rect(surface, GUARD_BORDER,
                     (box_x, box_y, DIALOG_W, DIALOG_H), 3, border_radius=8)

    portrait_x = box_x + 10
    portrait_y = box_y + DIALOG_H // 2 - PORTRAIT_SIZE // 2
    pygame.draw.rect(surface, (20, 20, 20),
                     (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    pygame.draw.rect(surface, GUARD_BORDER,
                     (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE), 3)
    if portrait_guardian:
        surface.blit(portrait_guardian, (portrait_x, portrait_y))
    else:
        ph = font_md.render("?", True, (70, 70, 70))
        surface.blit(ph, ph.get_rect(center=(portrait_x + PORTRAIT_SIZE // 2,
                                             portrait_y + PORTRAIT_SIZE // 2)))

    surface.blit(font_md.render("Guardian", True, GUARD_BORDER),
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
    box_w = 480
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
# FLASH TO BLACK
# =============================================================================
def flash_to_black(surface, clk):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    for alpha in range(0, 256, 8):
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0, 0))
        pygame.display.flip()
        clk.tick(60)
    pygame.time.wait(300)


# =============================================================================
# MAIN
# =============================================================================
def main():
    exit_unlocked = False

    walls, wall_set, bush_tiles, exit_tiles, entrance_tiles, walls_exit = build_from_tmx()
    place_key(bush_tiles)

    pulse_timer = 0
    pulse_phase = "dark"  # "dark", "to_light", "light", "to_dark"
    pulse_alpha = 245  # current darkness alpha
    heard_timer = 0  # how long guardian chases last known pos
    last_known_pos = None

    try:
        pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "30. The Hidden Glade.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    try:
        bush_rustle = pygame.mixer.Sound(os.path.join(BASE_DIR, "audio", "bush_rustle.mp3"))
        bush_rustle.set_volume(0.6)
    except Exception:
        bush_rustle = None

    player   = Player()
    guardian = Guardian()

    # Initialize difficulty system
    difficulty_mgr = DifficultyManager(player, "TheGuardian")
    
    # Apply difficulty modifiers
    disable_enrage = difficulty_mgr.get_modifier("disable_enrage", False)
    PULSE_LIGHT_DURATION = difficulty_mgr.get_modifier("light_phase_duration", PULSE_LIGHT_DURATION_BASE)
    PULSE_DARK_DURATION = difficulty_mgr.get_modifier("dark_phase_duration", PULSE_DARK_DURATION_BASE)
    guardian_chase_speed_multiplier = difficulty_mgr.get_modifier("guardian_chase_speed_multiplier", 1.0)
    GUARD_SPEED_CHASE = GUARD_SPEED_CHASE_BASE * guardian_chase_speed_multiplier
    
    # Spawn God if God Mode is active
    god = None
    lightning_bolts = []
    if difficulty_mgr.should_spawn_god():
        god = GodEntity()

    darkness_active  = False
    gate_open        = False
    entrance_closed  = False
    chase_active     = False
    player_has_moved = False

    state          = STATE_INTRO
    current_dialog = DIALOGS["intro"]
    dialog_index   = 0
    typewriter     = Typewriter()
    typewriter.set_text(current_dialog[0][1])

    alert_timer  = 0

    slash_playing    = False
    slash_done_timer = SLASH_FRAMES * 7

    while True:
        clock.tick(60)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state in (STATE_INTRO, STATE_WARNING, STATE_DARKNESS_DLG):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            dialog_index += 1
                            if dialog_index < len(current_dialog):
                                typewriter.set_text(current_dialog[dialog_index][1])
                            else:
                                if state == STATE_INTRO:
                                    state = STATE_PLAY
                                    guardian.sprites.set_anim("idle")


                                elif state == STATE_WARNING:
                                    guardian.sprites.set_anim("slash", "down")
                                    slash_playing = True
                                    slash_done_timer = SLASH_FRAMES * 7
                                    state = STATE_PLAY


                                elif state == STATE_DARKNESS_DLG:
                                    darkness_active = True
                                    chase_active = False  # ← was True
                                    guardian.chasing = False  # ← was True
                                    guardian.speed = GUARD_SPEED_NORMAL
                                    state = STATE_PLAY

                elif state == STATE_PROMPT:
                    if event.key == pygame.K_y:
                        gate_open = True
                        state = STATE_WIN
                    elif event.key == pygame.K_n:
                        state = STATE_PLAY

                elif state == STATE_HIT:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        player.rect.center = PLAYER_SPAWN
                        player.inv_timer = INVINCIBLE_FRAMES
                        state = STATE_PLAY

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        main(); return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == STATE_WIN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        pygame.quit(); sys.exit()

        # ── Typewriter tick ───────────────────────────────────────────────────
        if state in (STATE_INTRO, STATE_WARNING, STATE_DARKNESS_DLG):
            typewriter.update()

        # ── Game logic ────────────────────────────────────────────────────────
        if state == STATE_PLAY:
            # Update difficulty manager
            difficulty_mgr.update()
            
            # Build the effective wall list each frame
            active_walls = walls + (walls_exit if not exit_unlocked else [])

            # Slash animation playing — hold screen until done
            if slash_playing:
                slash_done_timer -= 1
                guardian.sprites.update()
                if slash_done_timer <= 0:
                    slash_playing = False
                    darkness_active = True
                    chase_active = False  # ← was True
                    guardian.chasing = False  # ← was True
                    guardian.speed = GUARD_SPEED_NORMAL
                    flash_to_black(screen, clock)
                    pygame.mixer.music.fadeout(500)  # ← add
                    pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "Hostile_March_BattleTheme.wav"))  # ← add
                    pygame.mixer.music.set_volume(0.5)  # ← add
                    pygame.mixer.music.play(-1)
                    state = STATE_PLAY

                draw_scene(screen, player, guardian, bush_tiles,
                           gate_open, darkness_active, entrance_closed)
                pygame.display.flip()
                continue

            keys  = pygame.key.get_pressed()
            moved = player.move(keys, active_walls)

            # First movement after intro triggers warning
            if moved and not player_has_moved and not chase_active:
                player_has_moved = True
                current_dialog   = DIALOGS["warning"]
                dialog_index     = 0
                typewriter.set_text(current_dialog[0][1])
                state = STATE_WARNING

            if player.inv_timer > 0:
                player.inv_timer -= 1

            if not entrance_closed and player.rect.centery > 5 * T:
                entrance_closed = True

            # Bush interaction — only after darkness
            if darkness_active:
                for b in bush_tiles:
                    if not b["triggered"] and player.rect.colliderect(b["rect"]):
                        b["triggered"] = True
                        if bush_rustle:  # ← add this
                            bush_rustle.play()  # ← add this
                        # Inside the bush interaction block, after player.has_key = True:
                        if b["has_key"] and not b["key_collected"]:
                            b["key_collected"] = True
                            player.has_key = True
                            exit_unlocked = True  # ← this is all you need
                        if b["layer_type"] == "dense":
                            guardian.alert_speed = GUARD_SPEED_LOUD if not disable_enrage else None
                            alert_timer = 180 if not disable_enrage else 0
                            last_known_pos = player.rect.center if not disable_enrage else None
                        else:
                            guardian.alert_speed = GUARD_SPEED_LIGHT if not disable_enrage else None
                            alert_timer = 120 if not disable_enrage else 0
                            last_known_pos = player.rect.center if not disable_enrage else None

            if alert_timer > 0:
                alert_timer -= 1
                if alert_timer == 0:
                    guardian.alert_speed = None

            # Replace: if chase_active: guardian.update_chase(...)
            # With:

            if darkness_active:
                pulse_timer += 1

                if pulse_phase == "dark":
                    pulse_alpha = 245
                    if pulse_timer >= PULSE_DARK_DURATION:
                        pulse_timer = 0
                        pulse_phase = "to_light"

                elif pulse_phase == "to_light":
                    pulse_alpha = int(245 * (1 - pulse_timer / PULSE_TRANSITION))
                    if pulse_timer >= PULSE_TRANSITION:
                        pulse_timer = 0
                        pulse_phase = "light"
                        pulse_alpha = 0

                elif pulse_phase == "light":
                    pulse_alpha = 0
                    if pulse_timer >= PULSE_LIGHT_DURATION:
                        pulse_timer = 0
                        pulse_phase = "to_dark"

                elif pulse_phase == "to_dark":
                    pulse_alpha = int(245 * (pulse_timer / PULSE_TRANSITION))
                    if pulse_timer >= PULSE_TRANSITION:
                        pulse_timer = 0
                        pulse_phase = "dark"
                        pulse_alpha = 245

                # ── Guardian movement ──
                if pulse_phase == "light":
                    # Light is on — guardian can see, chases player directly
                    guardian.chasing = True
                    guardian.speed = GUARD_SPEED_CHASE
                    guardian.update_chase(player.rect, wall_set)
                elif alert_timer > 0:
                    # Dark but heard a bush — bolt to last known position
                    guardian.chasing = True
                    guardian.speed = GUARD_SPEED_LOUD
                    if last_known_pos:
                        target = pygame.Rect(last_known_pos[0], last_known_pos[1], 1, 1)
                        guardian.update_chase(target, wall_set)
                else:
                    # Dark and quiet — wander
                    guardian.chasing = False
                    guardian.speed = GUARD_SPEED_NORMAL
                    guardian.update_roam(wall_set)


            else:
                if player_has_moved:
                    guardian.update_roam(wall_set)

            # Update God entity if spawned
            if god:
                god.update(player.rect)
                
                # Check God smite range for instant-kill
                if god.in_smite_range(player.rect) and player.inv_timer <= 0:
                    player.lives = 0
                    state = STATE_GAME_OVER
                
                # Spawn lightning bolts from God
                new_bolts = god.try_spawn_bolts(player.rect)
                lightning_bolts.extend(new_bolts)
            
            # Update lightning bolts
            for bolt in lightning_bolts[:]:
                bolt.update()
                if bolt.is_done():
                    lightning_bolts.remove(bolt)
                elif bolt.hits(player.rect) and player.inv_timer <= 0:
                    player.lives -= 1
                    player.inv_timer = INVINCIBLE_FRAMES
                    if player.lives <= 0:
                        state = STATE_GAME_OVER

            if darkness_active and guardian.touches(player.rect) and player.inv_timer <= 0:
                player.lives -= 1
                player.inv_timer = INVINCIBLE_FRAMES
                state = STATE_GAME_OVER if player.lives <= 0 else STATE_HIT

            if player.has_key and player.rect.top >= HEIGHT - 2 * T:
                exit_zone = pygame.Rect(0, HEIGHT - 4 * T, WIDTH, 4 * T)
                if player.rect.colliderect(exit_zone) and state == STATE_PLAY:
                    state = STATE_PROMPT

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_scene(game_surface, player, guardian, bush_tiles,
                   gate_open, darkness_active, entrance_closed, pulse_alpha)

        # Draw lightning bolts
        if god:
            for bolt in lightning_bolts:
                bolt.draw(game_surface)
        
        # Draw God entity
        if god:
            god.draw(game_surface)
        
        # Draw difficulty indicator
        difficulty_mgr.draw_indicator(game_surface, font_md)

        if state in (STATE_INTRO, STATE_WARNING, STATE_DARKNESS_DLG):
            draw_guardian_dialog(game_surface, typewriter)


        elif state == STATE_PROMPT:

            draw_simple_dialog(game_surface,
                               ["You have the key.",
                                "Unlock the gate and escape?"],
                               [("Y", "Yes, unlock it"),
                                ("N", "Not yet")])

        elif state == STATE_HIT:
            draw_simple_dialog(game_surface,
                [f"The Guardian strikes you!  Lives: {player.lives}",
                 "You stumble back..."],
                [("Enter", "Continue")])

        elif state == STATE_GAME_OVER:
            draw_simple_dialog(game_surface,
                ["You have fallen in the Garden.",
                 "The Guardian stands triumphant."],
                [("R", "Try again"), ("Esc", "Quit")])

        elif state == STATE_WIN:
            pygame.mixer.music.fadeout(500)
            TheStatues.main()
            pygame.quit()

        # Scale and display the game surface with letterboxing/pillarboxing
        scaler.display(screen, game_surface)
        pygame.display.flip()


if __name__ == "__main__":
    main()

# =============================================================================
# GOD_MAIN  —  backtrack mode (guardian disabled, god chasing player to bottom)
# =============================================================================
def _near_door_guardian(player_rect, door_rects, radius=50):
    if not door_rects:
        return False
    door_union = door_rects[0].unionall(door_rects[1:])
    return door_union.inflate(radius * 2, radius * 2).colliderect(player_rect)


def god_main(god, lives=MAX_LIVES):
    DOOR_KICK_MIN = 4
    DOOR_KICK_MAX = 8

    walls, wall_set, bush_tiles, exit_tiles, entrance_tiles, walls_exit = build_from_tmx()

    player           = Player()
    player.lives     = lives
    player.rect.x    = WIDTH // 2 - PLAYER_SIZE // 2
    player.rect.y    = HEIGHT - 8 * T   # spawn in open area near bottom

    lightning_bolts  = []
    inv_timer        = 120
    player.inv_timer = 120

    door_kicks        = 0
    door_kicks_needed = random.randint(DOOR_KICK_MIN, DOOR_KICK_MAX)
    door_kick_cd      = 0
    door_open         = False
    door_rects        = [t for t in entrance_tiles if t.y < HEIGHT // 2]  # top entrance

    god.rect.x     = WIDTH // 2 - god.SIZE // 2
    god.rect.y     = -120
    god.bolt_timer = 90

    STATE_RUN  = "run"
    STATE_DEAD = "dead"
    state      = STATE_RUN

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == STATE_RUN:
                    if event.key == pygame.K_e:
                        if not door_open \
                                and _near_door_guardian(player.rect, door_rects) \
                                and door_kick_cd <= 0:
                            door_kicks += 1
                            door_kick_cd = 20
                            if door_kicks >= door_kicks_needed:
                                door_open = True

                elif state == STATE_DEAD:
                    if event.key == pygame.K_r:
                        god_main(god, lives); return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

        if state == STATE_RUN:
            keys = pygame.key.get_pressed()

            # Remove entrance walls when door is open so player can pass through
            if door_open and door_rects:
                entrance_set = {(r.x, r.y) for r in door_rects}
                active_walls = [w for w in walls if (w.x, w.y) not in entrance_set]
            else:
                active_walls = walls
            player.move(keys, active_walls)

            if door_kick_cd  > 0: door_kick_cd  -= 1
            if inv_timer     > 0: inv_timer      -= 1
            if player.inv_timer > 0: player.inv_timer -= 1

            keys_held = pygame.key.get_pressed()
            if keys_held[pygame.K_e] and not door_open \
                    and _near_door_guardian(player.rect, door_rects) \
                    and door_kick_cd <= 0:
                door_kicks += 1
                door_kick_cd = 20
                if door_kicks >= door_kicks_needed:
                    door_open = True

            god.update(player.rect)

            if god.in_smite_range(player.rect) and inv_timer <= 0:
                state = STATE_DEAD

            for bolt in god.try_spawn_bolts(player.rect):
                lightning_bolts.append(bolt)

            for bolt in lightning_bolts[:]:
                done = bolt.update()
                if bolt.hits(player.rect) and inv_timer <= 0:
                    player.lives    -= 1
                    inv_timer        = INVINCIBLE_FRAMES
                    player.inv_timer = INVINCIBLE_FRAMES
                    if player.lives <= 0:
                        state = STATE_DEAD
                if done:
                    lightning_bolts.remove(bolt)

            # Exit through top once entrance is kicked open
            if door_open:
                exit_zone = pygame.Rect(0, 0, WIDTH, 4 * T)
                if player.rect.colliderect(exit_zone):
                    import TheTwins
                    TheTwins.god_main(god, player.lives)
                    return

        # ── Draw ──────────────────────────────────────────────────────────────
        game_surface.fill(BLACK)

        for layer in tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            # Entrance (top) — door being kicked, toggle with door_open
            if layer.name in ("Entracne - Open", "Entrance2 - Open") and not door_open:
                continue
            if layer.name in ("Entrance", "Entrance2") and door_open:
                continue
            # Exit (bottom) — player entered from here, always show as open
            if layer.name in ("Exit", "Exit2"):
                continue
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    game_surface.blit(tile, (x * T, y * T))

        # Door kick UI — progress bar BELOW the top door
        if not door_open and door_rects:
            door_union = door_rects[0].unionall(door_rects[1:])
            progress   = door_kicks / max(door_kicks_needed, 1)
            crack_col  = (int(220 * progress), int(80 * (1 - progress)), 0)
            pygame.draw.rect(game_surface, crack_col, door_union.inflate(4, 4), 2, border_radius=2)

            bx = door_union.x
            by = door_union.bottom + 4   # below the door, not above
            bw = door_union.width
            pygame.draw.rect(game_surface, (50, 20, 20), (bx, by, bw, 5))
            pygame.draw.rect(game_surface, (220, 80, 40), (bx, by, int(bw * progress), 5))

            if _near_door_guardian(player.rect, door_rects):
                hint = font_sm.render(
                    f"[E] Kick the door  ({door_kicks}/{door_kicks_needed})", True, WHITE)
                hbg = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8),
                                      pygame.SRCALPHA)
                hbg.fill((10, 10, 10, 180))
                game_surface.blit(hbg,  (WIDTH // 2 - hbg.get_width() // 2, HEIGHT - 44))
                game_surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

        for bolt in lightning_bolts:
            bolt.draw(game_surface)

        god.draw(game_surface)
        player.draw(game_surface)

        hx, hy = 8, 8
        for i in range(MAX_LIVES):
            if heart_full and heart_empty:
                img = heart_full if i < player.lives else heart_empty
                game_surface.blit(img, (hx, hy))
                hx += img.get_width() + 4
            else:
                col = (220, 50, 50) if i < player.lives else (80, 80, 80)
                pygame.draw.circle(game_surface, col, (hx + 8, hy + 8), 7)
                hx += 20

        if state == STATE_DEAD:
            draw_simple_dialog(game_surface,
                ["The divine presence consumes you.",
                 "There is no escaping divine wrath."],
                [("R", "Try again"), ("Esc", "Quit")])

        # Scale and display the game surface with letterboxing/pillarboxing
        scaler.display(screen, game_surface)
        pygame.display.flip()