import pygame
import sys
import os
import math
import random
import pytmx
import collections
import TheGarden

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Statues")
clock = pygame.time.Clock()

tmx_data = pytmx.load_pygame(os.path.join(BASE_DIR, "TheStatuesMap.tmx"))

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
GOLD         = (212, 175,  55)
PLAYER_COL   = (200, 160,  80)
PLAYER_HEAD  = (210, 170, 120)
HAMMER_COL   = (180, 120,  40)
HAMMER_GLOW  = (220, 160,  60)

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

# ── Statue image ──────────────────────────────────────────────────────────────
try:
    _statue_raw = pygame.image.load(os.path.join(BASE_DIR, "Statue.png")).convert_alpha()
    # Made bigger: was 28 wide, now 42 wide
    STATUE_DRAW_W = 42
    STATUE_DRAW_H = int(_statue_raw.get_height() * (STATUE_DRAW_W / _statue_raw.get_width()))
    statue_img = pygame.transform.scale(_statue_raw, (STATUE_DRAW_W, STATUE_DRAW_H))
    # Dark variant — no dark overlay rectangle; just the base image tinted via per-pixel
    statue_img_dark = statue_img.copy()
    # Use a subtle color-multiply tint instead of a filled rectangle overlay
    # so there's no visible black box artifact
    for px in range(statue_img_dark.get_width()):
        for py in range(statue_img_dark.get_height()):
            r, g, b, a = statue_img_dark.get_at((px, py))
            if a > 0:
                statue_img_dark.set_at((px, py), (r // 2, g // 2, b // 2, a))
except Exception:
    statue_img      = None
    statue_img_dark = None

# ── Stone scrape sound ────────────────────────────────────────────────────────
try:
    stone_scrape_sfx = pygame.mixer.Sound(os.path.join(BASE_DIR, "audio", "Stone_Scrape.mp3"))
    stone_scrape_sfx.set_volume(0.55)
except Exception:
    stone_scrape_sfx = None

# ── Constants ─────────────────────────────────────────────────────────────────
PLAYER_SIZE       = 14
MAX_LIVES         = 3
PLAYER_SPAWN      = (WIDTH // 2, 40)

STATUE_BASE_SPEED  = 1.6
INVINCIBLE_FRAMES  = 90
LIGHT_RADIUS       = 80

# Default pulse durations (modified when hammer is picked up)
PULSE_DARK_DURATION_DEFAULT  = 300
PULSE_LIGHT_DURATION_DEFAULT = 180
PULSE_DARK_DURATION_HAMMER   = 200   # more frequent flicker after hammer
PULSE_LIGHT_DURATION_HAMMER  = 90
PULSE_TRANSITION             = 40

WALL_LAYERS = {"Walls", "Walls_Side"}

# Skip ALL static statue TMX layers — moving sprites replace them entirely
STATUE_TMX_LAYERS = {f"Statue{i}" for i in range(1, 8)}

# ── Cutscene ──────────────────────────────────────────────────────────────────
# Simplified: 3 dialogue lines only
# ("tag", "text", action)
# actions: None | "lights_out_and_lurch" | "lights_flicker_on"
CUTSCENE = [
    ("NARRATE", "The room is filled with statues.", None),
    ("NARRATE", "Something feels off.",             None),
    # After this line: lights go out, statues lurch — no dialogue for that
    # Then lights flicker back on automatically, then "!!!"
    ("PLAYER",  "!!!",                              None),
]

# Indices at which special actions happen BEFORE showing the line
# We handle the lights-out + lurch + flicker-on between line 1 and line 2 (index 1→2)
CUTSCENE_AUTO_TRANSITION_AFTER = 1   # after line index 1, do the action sequence

TYPEWRITER_SPEED = 2


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
    statue_spawns  = {}   # "Statue1" … "Statue7" -> (col, row)
    hammer_pool    = []
    exit_tiles     = []
    entrance_tiles = []

    STATUE_SPAWN_MAP = {f"Statue{i}Spawn": f"Statue{i}" for i in range(1, 8)}

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
            elif layer.name in STATUE_SPAWN_MAP:
                statue_spawns[STATUE_SPAWN_MAP[layer.name]] = (x, y)
            elif layer.name == "HammerAndOilSpawnTiles":
                hammer_pool.append((x, y))
            elif layer.name in ("Exit", "Exit2"):
                exit_tiles.append(r)
            elif layer.name in ("Entrance", "Entrance2"):
                entrance_tiles.append(r)

    return walls, wall_set, statue_spawns, hammer_pool, exit_tiles, entrance_tiles


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
        self.has_key    = False
        self.has_hammer = False
        self.inv_timer  = 0
        self.sprites    = PlayerSprites(scale=1)
        self.rect       = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
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
        if self.has_hammer:
            pygame.draw.rect(surface, HAMMER_COL,
                             pygame.Rect(self.rect.right + 3, self.rect.top, 6, 10),
                             border_radius=2)
        if self.has_key and key_img:
            surface.blit(key_img, (self.rect.centerx - 8, self.rect.top - 20))


# =============================================================================
# STATUE
# =============================================================================
class Statue:
    SIZE = 14   # collision hitbox

    def __init__(self, name, spawn_tile):
        self.name        = name
        self.spawn_tile  = spawn_tile          # (col, row) — smash tile
        cx = spawn_tile[0] * T + T // 2
        cy = spawn_tile[1] * T + T // 2
        self.rect        = pygame.Rect(cx - self.SIZE // 2, cy - self.SIZE // 2,
                                       self.SIZE, self.SIZE)
        self.home        = (cx, cy)
        self.alive       = True
        self.moving      = False
        self.path        = []
        self.path_timer  = 0
        self.speed       = STATUE_BASE_SPEED
        # Cutscene lurch
        self.lurch_vx    = 0.0
        self.lurch_vy    = 0.0
        self.lurch_timer = 0
        self._scrape_played = False

    # ── Chase (dark phase) ────────────────────────────────────────────────────
    def update_chase(self, player_rect, wall_set):
        if not self.alive:
            return
        was_moving = self.moving
        self.path_timer += 1
        if self.path_timer >= 12:
            self.path_timer = 0
            sc = self.rect.centerx // T
            sr = self.rect.centery  // T
            gc = player_rect.centerx // T
            gr = player_rect.centery  // T
            self.path = find_path((sc, sr), (gc, gr), wall_set)

        dx_h = abs(self.rect.centerx - self.home[0])
        dy_h = abs(self.rect.centery  - self.home[1])
        self.moving = dx_h > 2 or dy_h > 2 or bool(self.path)

        if not was_moving and self.moving:
            self._play_scrape()

        self._move_path(self.speed)

    # ── Statues NO LONGER return home when lights come on ────────────────────
    # (removed return_home method entirely)

    # ── Cutscene lurch ────────────────────────────────────────────────────────
    def lurch_toward(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        frames = 30
        move   = min(dist * 0.35, 40)
        self.lurch_vx    = (dx / dist) * (move / frames)
        self.lurch_vy    = (dy / dist) * (move / frames)
        self.lurch_timer = frames
        self._play_scrape()

    def update_lurch(self):
        if self.lurch_timer > 0:
            self.lurch_timer -= 1
            self.rect.x += int(self.lurch_vx)
            self.rect.y += int(self.lurch_vy)
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _move_path(self, speed):
        if not self.path or len(self.path) < 2:
            return
        target_c, target_r = self.path[1]
        tx = target_c * T + T // 2
        ty = target_r * T + T // 2
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= speed:
            self.rect.centerx = tx
            self.rect.centery = ty
            self.path.pop(0)
        else:
            self.rect.x += int((dx / dist) * speed)
            self.rect.y += int((dy / dist) * speed)
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def _play_scrape(self):
        if stone_scrape_sfx and not self._scrape_played:
            stone_scrape_sfx.play()
            self._scrape_played = True

    def touches(self, player_rect):
        return self.alive and self.rect.inflate(6, 6).colliderect(player_rect)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, is_light_phase):
        if not self.alive:
            return
        img = statue_img if is_light_phase else statue_img_dark
        if img:
            draw_x = self.rect.centerx - img.get_width()  // 2
            draw_y = self.rect.centery - img.get_height() // 2
            surface.blit(img, (draw_x, draw_y))
        else:
            col = (160, 160, 170) if is_light_phase else (80, 80, 90)
            pygame.draw.rect(surface, col, self.rect, border_radius=2)
            pygame.draw.rect(surface, (200, 200, 220), self.rect, 1, border_radius=2)


# =============================================================================
# DARKNESS OVERLAY
# =============================================================================
def make_darkness(player_rect, radius=LIGHT_RADIUS, base_alpha=245):
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surf.fill((0, 0, 0, base_alpha))
    cx, cy = player_rect.centerx, player_rect.centery
    for r in range(radius, 0, -2):
        alpha = int(base_alpha * (1 - (r / radius) ** 0.4))
        pygame.draw.circle(surf, (0, 0, 0, alpha), (cx, cy), r)
    pygame.draw.circle(surf, (0, 0, 0, 0), (cx, cy), int(radius * 0.25))
    return surf


# =============================================================================
# DRAW SCENE
# =============================================================================
def draw_scene(surface, player, statues, hammer_pos, key_pos,
               gate_open, darkness_active, entrance_closed,
               pulse_alpha, is_light_phase):

    # ── TMX layers ────────────────────────────────────────────────────────────
    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        if layer.name in STATUE_TMX_LAYERS:
            continue   # replaced by moving sprites
        if layer.name in ("Entracne - Open", "Entrance2 - Open") and entrance_closed:
            continue
        if layer.name in ("Entrance", "Entrance2") and not entrance_closed:
            continue
        if layer.name in ("Exit - Open", "Exit2 - Open") and not gate_open:
            continue
        if layer.name in ("Exit", "Exit2") and gate_open:
            continue
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(tile, (x * T, y * T))

    # ── Smash-tile highlights — only in light phase when carrying hammer ──────
    if is_light_phase and player.has_hammer:
        for statue in statues:
            if statue.alive:
                col, row = statue.spawn_tile
                pygame.draw.rect(surface, (220, 60, 60),
                                 pygame.Rect(col * T, row * T, T, T), 2, border_radius=2)

    # ── Hammer and key — drawn invisibly; player discovers by walking over ──────
    # (No visual indicator for either pickup)

    # ── Moving statue sprites ─────────────────────────────────────────────────
    for statue in statues:
        statue.draw(surface, is_light_phase)

    # ── Player ────────────────────────────────────────────────────────────────
    player.draw(surface)

    # ── Darkness overlay ──────────────────────────────────────────────────────
    if darkness_active:
        surface.blit(make_darkness(player.rect, base_alpha=pulse_alpha), (0, 0))

    # ── HUD ───────────────────────────────────────────────────────────────────
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

    status = ""
    if player.has_hammer: status += "  [HAMMER]"
    if player.has_key:    status += "  [KEY]"
    if status:
        surface.blit(font_hud.render(status, True, GOLD), (hx + 4, hy + 2))

    alive_count = sum(1 for s in statues if s.alive)
    ctr = font_hud.render(f"Statues: {alive_count}", True, (200, 200, 220))
    surface.blit(ctr, (WIDTH - ctr.get_width() - 10, 8))

    # No hammer hint text shown


# =============================================================================
# CUTSCENE DRAWING
# =============================================================================
def draw_cutscene_line(surface, tag, typewriter):
    box_w, box_h = 560, 80
    box_x = WIDTH  // 2 - box_w // 2
    box_y = HEIGHT // 2 - box_h // 2

    if tag == "NARRATE":
        ov = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        ov.fill((10, 10, 10, 210))
        surface.blit(ov, (box_x, box_y))
        pygame.draw.rect(surface, (160, 160, 180),
                         (box_x, box_y, box_w, box_h), 2, border_radius=6)
        txt = font_md.render(typewriter.current, True, WHITE)
        surface.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    elif tag == "PLAYER":
        # "!!!" shown INSIDE a proper dialogue box, not floating
        ov = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        ov.fill((10, 10, 10, 210))
        surface.blit(ov, (box_x, box_y))
        pygame.draw.rect(surface, GOLD,
                         (box_x, box_y, box_w, box_h), 2, border_radius=6)
        big = pygame.font.Font(FONT_PATH, 40)
        txt = big.render(typewriter.current, True, GOLD)
        surface.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    ticks = pygame.time.get_ticks()
    if typewriter.done and (ticks // 500) % 2 == 0:
        p = font_sm.render("▶ Enter", True, (160, 160, 160))
        surface.blit(p, (box_x + box_w - p.get_width() - 12, box_y + box_h - p.get_height() - 8))


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
# FLASH HELPERS
# =============================================================================
def flash_to_black(duration_ms=300):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    for alpha in range(0, 256, 12):
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    pygame.time.wait(duration_ms)


def flash_from_black():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    for alpha in range(255, -1, -12):
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)


# =============================================================================
# STATES
# =============================================================================
STATE_CUTSCENE      = "cutscene"
STATE_PLAY          = "play"
STATE_HIT           = "hit"
STATE_GAME_OVER     = "gameover"
STATE_WIN           = "win"
STATE_PROMPT        = "prompt"
STATE_HAMMER_DIALOG = "hammer_dialog"


# =============================================================================
# MAIN
# =============================================================================
def main():
    import TheGuardian  # next level

    walls, wall_set, statue_spawns, hammer_pool, exit_tiles, entrance_tiles = build_from_tmx()

    statues    = [Statue(name, spawn) for name, spawn in statue_spawns.items()]
    # Filter hammer spawns: exclude wall tiles and the top area (row < 8) near the entrance
    safe_hammer_pool = [t for t in hammer_pool if t not in wall_set and t[1] >= 8]
    hammer_pos = random.choice(safe_hammer_pool) if safe_hammer_pool else (
        random.choice(hammer_pool) if hammer_pool else None
    )
    key_pos    = None

    pulse_timer = 0
    pulse_phase = "light"   # bright at cutscene start
    pulse_alpha = 0

    # Pulse durations — change when hammer is picked up
    pulse_dark_duration  = PULSE_DARK_DURATION_DEFAULT
    pulse_light_duration = PULSE_LIGHT_DURATION_DEFAULT

    player          = Player()
    darkness_active = False
    gate_open       = False
    entrance_closed = False
    inv_timer       = 0

    # Cutscene state
    # We only have 3 lines: index 0, 1, 2
    # Between index 1→2 we do: flash to black, statues lurch, wait, flash from black
    state      = STATE_CUTSCENE
    cs_index   = 0
    cs_auto_done = False   # flag to track if the auto-transition sequence ran
    typewriter = Typewriter()
    typewriter.set_text(CUTSCENE[0][1])

    try:
        pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "23. The Last Watch.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    while True:
        clock.tick(60)

        is_light_phase = (pulse_phase == "light")

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == STATE_CUTSCENE:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            cs_index += 1
                            if cs_index < len(CUTSCENE):
                                # Check if we need to do the auto-transition sequence
                                if cs_index == 2 and not cs_auto_done:
                                    cs_auto_done = True
                                    # Lights out
                                    flash_to_black(400)
                                    darkness_active = True
                                    pulse_phase = "dark"
                                    pulse_alpha = 245
                                    # Draw scene blacked out and make statues lurch
                                    for s in statues:
                                        s.lurch_toward(player.rect)
                                    # Animate lurch for ~30 frames
                                    for _ in range(35):
                                        draw_scene(screen, player, statues, hammer_pos, key_pos,
                                                   gate_open, True, entrance_closed,
                                                   245, False)
                                        for s in statues:
                                            s.update_lurch()
                                        pygame.display.flip()
                                        clock.tick(60)
                                    pygame.time.wait(200)
                                    # Lights flicker back on
                                    flash_from_black()
                                    darkness_active = False
                                    pulse_phase = "light"
                                    pulse_alpha = 0

                                tag, text, _ = CUTSCENE[cs_index]
                                typewriter.set_text(text)
                            else:
                                # Cutscene over — start gameplay
                                for s in statues:
                                    s.lurch_timer    = 0
                                    s._scrape_played = False
                                darkness_active = True
                                pulse_phase     = "dark"
                                pulse_alpha     = 245
                                pulse_timer     = 0
                                state           = STATE_PLAY

                elif state == STATE_PROMPT:
                    if event.key == pygame.K_y:
                        gate_open = True
                        state     = STATE_WIN
                    elif event.key == pygame.K_n:
                        state = STATE_PLAY

                elif state == STATE_HAMMER_DIALOG:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            state = STATE_PLAY

                elif state == STATE_HIT:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        player.rect.center = PLAYER_SPAWN
                        inv_timer          = INVINCIBLE_FRAMES
                        player.inv_timer   = INVINCIBLE_FRAMES
                        state              = STATE_PLAY

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        main(); return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == STATE_WIN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        try:
                            TheGuardian.main()
                        except Exception:
                            pass
                        pygame.quit(); sys.exit()

        # ── Cutscene tick ─────────────────────────────────────────────────────
        if state == STATE_CUTSCENE:
            typewriter.update()
            for s in statues:
                s.update_lurch()

        # ── Hammer dialog tick ────────────────────────────────────────────────
        if state == STATE_HAMMER_DIALOG:
            typewriter.update()

        # ── Gameplay ──────────────────────────────────────────────────────────
        if state == STATE_PLAY:
            keys = pygame.key.get_pressed()
            player.move(keys, walls)

            if not entrance_closed and player.rect.centery > 5 * T:
                entrance_closed = True

            if inv_timer        > 0: inv_timer        -= 1
            if player.inv_timer > 0: player.inv_timer -= 1

            # ── Pulse ──
            pulse_timer += 1
            if pulse_phase == "dark":
                pulse_alpha = 245
                if pulse_timer >= pulse_dark_duration:
                    pulse_timer = 0
                    pulse_phase = "to_light"
                    for s in statues:
                        s._scrape_played = False
            elif pulse_phase == "to_light":
                pulse_alpha = int(245 * (1 - pulse_timer / PULSE_TRANSITION))
                if pulse_timer >= PULSE_TRANSITION:
                    pulse_timer = 0
                    pulse_phase = "light"
                    pulse_alpha = 0
            elif pulse_phase == "light":
                pulse_alpha = 0
                if pulse_timer >= pulse_light_duration:
                    pulse_timer = 0
                    pulse_phase = "to_dark"
            elif pulse_phase == "to_dark":
                pulse_alpha = int(245 * (pulse_timer / PULSE_TRANSITION))
                if pulse_timer >= PULSE_TRANSITION:
                    pulse_timer = 0
                    pulse_phase = "dark"
                    pulse_alpha = 245

            is_light_phase = (pulse_phase == "light")

            # ── Statue AI — statues stay where they are in light phase ──
            for s in statues:
                if not s.alive:
                    continue
                # Only chase during dark; freeze in place during light
                if not is_light_phase and pulse_phase != "to_light":
                    s.update_chase(player.rect, wall_set)
                # During light/to_light: do nothing (statues stay put)

            # ── Hammer pickup ──
            if hammer_pos and not player.has_hammer:
                hcol, hrow = hammer_pos
                if player.rect.colliderect(pygame.Rect(hcol * T, hrow * T, T, T)):
                    player.has_hammer = True
                    hammer_pos        = None
                    # Make lights flicker more frequently
                    pulse_dark_duration  = PULSE_DARK_DURATION_HAMMER
                    pulse_light_duration = PULSE_LIGHT_DURATION_HAMMER
                    # Show pickup dialogue
                    typewriter.set_text(".... Maybe I can use this to destroy the statues.")
                    state = STATE_HAMMER_DIALOG

            # ── Smash statues (light + hammer + standing on spawn tile) ──
            if is_light_phase and player.has_hammer:
                for s in statues:
                    if not s.alive:
                        continue
                    scol, srow = s.spawn_tile
                    if player.rect.colliderect(pygame.Rect(scol * T, srow * T, T, T)):
                        s.alive = False
                        # Speed up remaining statues
                        alive_statues = [st for st in statues if st.alive]
                        speed_boost = 0.4 * (len(statues) - len(alive_statues))
                        for st in alive_statues:
                            st.speed = STATUE_BASE_SPEED + speed_boost
                        # Trigger immediate blackout
                        pulse_phase = "dark"
                        pulse_alpha = 245
                        pulse_timer = 0
                        if all(not st.alive for st in statues):
                            key_pos = s.spawn_tile

            # ── Key pickup ──
            if key_pos and not player.has_key:
                kcol, krow = key_pos
                if player.rect.colliderect(pygame.Rect(kcol * T, krow * T, T, T)):
                    player.has_key = True
                    key_pos        = None

            # ── Statue damage (dark phases only) ──
            if not is_light_phase and pulse_phase != "to_light":
                for s in statues:
                    if s.touches(player.rect) and inv_timer <= 0:
                        player.lives     -= 1
                        inv_timer         = INVINCIBLE_FRAMES
                        player.inv_timer  = INVINCIBLE_FRAMES
                        state = STATE_GAME_OVER if player.lives <= 0 else STATE_HIT
                        break

            # ── Exit ──
            if player.has_key and state == STATE_PLAY:
                exit_zone = pygame.Rect(0, HEIGHT - 4 * T, WIDTH, 4 * T)
                if player.rect.colliderect(exit_zone):
                    state = STATE_PROMPT

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_scene(screen, player, statues, hammer_pos, key_pos,
                   gate_open, darkness_active, entrance_closed,
                   pulse_alpha, is_light_phase)

        if state == STATE_CUTSCENE:
            tag, _, _ = CUTSCENE[cs_index]
            draw_cutscene_line(screen, tag, typewriter)

        elif state == STATE_PROMPT:
            draw_simple_dialog(screen,
                               ["You have the key.", "Escape the statue room?"],
                               [("Y", "Yes, escape"), ("N", "Not yet")])

        elif state == STATE_HAMMER_DIALOG:
            draw_cutscene_line(screen, "PLAYER", typewriter)

        elif state == STATE_HIT:
            draw_simple_dialog(screen,
                [f"A statue grabs you!  Lives: {player.lives}",
                 "You stumble back..."],
                [("Enter", "Continue")])

        elif state == STATE_GAME_OVER:
            draw_simple_dialog(screen,
                ["You were crushed by the statues.",
                 "The garden claims another soul."],
                [("R", "Try again"), ("Esc", "Quit")])

        elif state == STATE_WIN:
            pygame.mixer.music.fadeout(500)
            TheGarden.main()
            pygame.quit()


        pygame.display.flip()


if __name__ == "__main__":
    main()

# =============================================================================
# LIGHTNING  —  duplicated from TheGarden to avoid circular import
# =============================================================================
class Lightning:
    WARN_FRAMES   = 45
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
        return True

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
# GOD_MAIN  —  backtrack mode (god chasing player back through empty room)
# =============================================================================
def god_main(god, lives=MAX_LIVES):
    """
    Called from TheGarden when the player escapes back through the Garden exit.
    The statue room is empty — all statues already smashed. The god chases the
    player from the top of the map down to the bottom exit door, which must be
    kicked open. Music is already playing (Hostile_March_BattleTheme.wav).
    """
    import TheGuardian   # next level in the backtrack chain

    walls, wall_set, statue_spawns, hammer_pool, exit_tiles, entrance_tiles = build_from_tmx()
    # Reset god position and timers for this level
    god.rect.x = WIDTH // 2 - god.SIZE // 2
    god.rect.y = -120
    god.bolt_timer = 90


    LIGHTNING_COUNT = 5
    LIGHTNING_COOLDOWN = 90

    DOOR_KICK_MIN = 4
    DOOR_KICK_MAX = 8

    player = Player()
    player.lives = lives
    player.rect.x = 29 * T  # center of exit door columns 27-31
    player.rect.y = HEIGHT - 7 * T  # just above the bottom exit door # spawn at bottom (exit tiles area)
    door_rects = entrance_tiles # enters from top
    lightning_bolts = []
    inv_timer = 120
    player.inv_timer = 120

    door_kicks        = 0
    door_kicks_needed = random.randint(DOOR_KICK_MIN, DOOR_KICK_MAX)
    door_kick_cd      = 0
    door_open         = False

    # Bottom exit door — use exit_tiles as the breakable door
    door_rects = entrance_tiles   # these are the bottom exit tiles

    STATE_PLAY     = "play"
    STATE_GAME_OVER = "gameover"
    state          = STATE_PLAY

    while True:
        clock.tick(60)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == STATE_PLAY:
                    if event.key == pygame.K_e:
                        if not door_open and _near_door(player.rect, door_rects, radius=50) \
                                and door_kick_cd <= 0:
                            door_kicks += 1
                            door_kick_cd = 20
                            if door_kicks >= door_kicks_needed:
                                door_open = True

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        god_main(god); return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

        if state == STATE_PLAY:
            keys = pygame.key.get_pressed()
            if door_open and entrance_tiles:
                entrance_set = {(r.x, r.y) for r in entrance_tiles}
                active_walls = [w for w in walls if (w.x, w.y) not in entrance_set]
            else:
                active_walls = walls
            player.move(keys, active_walls)

            # Hold E to kick
            if door_kick_cd > 0: door_kick_cd -= 1
            if inv_timer    > 0: inv_timer    -= 1
            if player.inv_timer > 0: player.inv_timer -= 1

            # God movement
            god.update(player.rect)

            # God smite — instant game over
            if god.in_smite_range(player.rect) and inv_timer <= 0:
                state = STATE_GAME_OVER

            # Lightning volley
            for bolt in god.try_spawn_bolts(player.rect):
                lightning_bolts.append(bolt)

            for bolt in lightning_bolts[:]:
                done = bolt.update()
                if bolt.hits(player.rect) and inv_timer <= 0:
                    player.lives    -= 1
                    inv_timer        = INVINCIBLE_FRAMES
                    player.inv_timer = INVINCIBLE_FRAMES
                    if player.lives <= 0:
                        state = STATE_GAME_OVER
                if done:
                    lightning_bolts.remove(bolt)

            # Hold E kick while moving
            keys_held = pygame.key.get_pressed()
            if keys_held[pygame.K_e] and not door_open \
                    and _near_door(player.rect, door_rects, radius=50) \
                    and door_kick_cd <= 0:
                door_kicks += 1
                door_kick_cd = 20
                if door_kicks >= door_kicks_needed:
                    door_open = True

            # Player exits through the bottom
            if door_open:
                exit_zone = pygame.Rect(0, HEIGHT - 4 * T, WIDTH, 4 * T)
                if player.rect.colliderect(exit_zone):
                    TheGuardian.god_main(god, player.lives)
                    return

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BLACK)

        # TMX layers — draw map but skip all statue layers
        for layer in tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            if layer.name in STATUE_TMX_LAYERS:
                continue   # room is empty, statues gone
            # Show bottom exit as open if door kicked open, closed otherwise
            if layer.name in ("Entracne - Open", "Entrance2 - Open") and not door_open:
                continue  # hide open variant until kicked
            if layer.name in ("Entrance", "Entrance2") and door_open:
                continue  # hide closed variant once kicked open
            # Exit (bottom) — player entered from here, always show as open
            if layer.name in ("Exit", "Exit2"):
                continue
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * T, y * T))

        # Door kick UI
        if not door_open and door_rects:
            door_union = door_rects[0].unionall(door_rects[1:])
            progress   = door_kicks / max(door_kicks_needed, 1)
            crack_col  = (int(220 * progress), int(80 * (1 - progress)), 0)
            pygame.draw.rect(screen, crack_col, door_union.inflate(4, 4), 2, border_radius=2)

            bx, by, bw = door_union.x, door_union.y - 10, door_union.width
            pygame.draw.rect(screen, (50, 20, 20), (bx, by, bw, 5))
            pygame.draw.rect(screen, (220, 80, 40), (bx, by, int(bw * progress), 5))

            if _near_door(player.rect, door_rects, radius=50):
                hint = font_sm.render(
                    f"[E] Kick the door  ({door_kicks}/{door_kicks_needed})", True, WHITE)
                hbg = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8),
                                      pygame.SRCALPHA)
                hbg.fill((10, 10, 10, 180))
                screen.blit(hbg,  (WIDTH // 2 - hbg.get_width() // 2, HEIGHT - 44))
                screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

        # Lightning bolts
        for bolt in lightning_bolts:
            bolt.draw(screen)

        # God
        god.draw(screen)

        # Player
        player.draw(screen)

        # HUD
        hx, hy = 8, 8
        for i in range(MAX_LIVES):
            if heart_full and heart_empty:
                img = heart_full if i < player.lives else heart_empty
                screen.blit(img, (hx, hy))
                hx += img.get_width() + 4
            else:
                col = (220, 50, 50) if i < player.lives else (80, 80, 80)
                pygame.draw.circle(screen, col, (hx + 8, hy + 8), 7)
                hx += 20

        if state == STATE_GAME_OVER:
            draw_simple_dialog(screen,
                ["The divine presence consumes you.",
                 "There is no escaping divine wrath."],
                [("R", "Try again"), ("Esc", "Quit")])

        pygame.display.flip()


def _near_door(player_rect, door_rects, radius=50):
    """Helper — true when player is close to any door tile."""
    if not door_rects:
        return False
    door_union = door_rects[0].unionall(door_rects[1:])
    return door_union.inflate(radius * 2, radius * 2).colliderect(player_rect)