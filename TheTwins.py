import pygame
import sys
import os
import math
import random
import pytmx
import collections
import TheGuardian

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Twins")
clock  = pygame.time.Clock()

tmx_data = pytmx.load_pygame(os.path.join(BASE_DIR, "TheTwinsMap.tmx"))

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GOLD        = (212, 175,  55)
HUD_BG      = (15,  15,  15)
PLAYER_COL  = (200, 160,  80)
PLAYER_HEAD = (210, 170, 120)
CAIN_COL    = (160,  60,  60)
CAIN_HEAD   = (200,  80,  80)
ABEL_COL    = (60,   90, 160)
ABEL_HEAD   = (80,  120, 200)
SPEAR_COL   = (180, 140,  60)
FRAG_COL    = (220, 200, 100)
FRAG_GLOW   = (255, 240, 160)
ENRAGE_COL  = (255,  50,  50)
STUN_COL    = (100, 180, 255)

# ── Grid ──────────────────────────────────────────────────────────────────────
T    = 13
COLS = WIDTH  // T
ROWS = HEIGHT // T

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_PATH = os.path.join(BASE_DIR, "font", "PixelifySans-VariableFont_wght.ttf")
font_sm  = pygame.font.Font(FONT_PATH, 15)
font_md  = pygame.font.Font(FONT_PATH, 19)
font_hud = pygame.font.Font(FONT_PATH, 15)

# ── Hearts ────────────────────────────────────────────────────────────────────
try:
    heart_full  = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "LifeHeart.png")).convert_alpha(), (20, 20))
    heart_empty = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "LifeHeartLoss.png")).convert_alpha(), (20, 20))
except:
    heart_full = heart_empty = None

# ── Constants ─────────────────────────────────────────────────────────────────
PLAYER_SIZE    = 14
MAX_LIVES      = 3
PLAYER_SPAWN = (29 * T + T // 2, 3 * T)

CAIN_SPEED_NORMAL   = 2.5
CAIN_SPEED_ENRAGED  = 3.5
ABEL_SPEED_NORMAL   = 3.6
ABEL_SPEED_ENRAGED  = 5.5

CAIN_THROW_RANGE_NORMAL  = 8   # tiles
CAIN_THROW_RANGE_ENRAGED = 16   # tiles
CAIN_THROW_COOLDOWN      = 180  # frames (~3s)

ABEL_STUN_FRAMES     = 90
ABEL_PUSH_DISTANCE   = 2 * T   # pixels
INVINCIBLE_FRAMES    = 90

FRAGMENTS_NEEDED     = 3  # per twin

WALL_LAYERS = {"Walls", "WallsBack", "Walls_Side", "MazeTileHorizontal", "MazeTileVertical"}

# ─────────────────────────────────────────────────────────────────────────────

def tile_rect(col, row, w=1, h=1):
    return pygame.Rect(col * T, row * T, w * T, h * T)

def build_from_tmx():
    walls            = []
    abel_ban_tile    = None
    cain_ban_tile    = None
    abel_spawn       = None
    cain_spawn       = None
    interactive_tiles = []
    exit_tiles       = []

    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        for x, y, gid in layer:
            if gid == 0:
                continue
            r = pygame.Rect(x * T, y * T, T, T)
            if layer.name in WALL_LAYERS:
                walls.append(r)
            elif layer.name == "AbelBanishmentTile":
                abel_ban_tile = (x, y)
            elif layer.name == "CainBanishmentTile":
                cain_ban_tile = (x, y)
            elif layer.name == "AbelSpawn":
                abel_spawn = (x, y)
            elif layer.name == "Cain1Spawn":
                cain_spawn = (x, y)
            elif layer.name in ("InteractiveItemsLayer", "InteractiveTileLayer2"):
                interactive_tiles.append((x, y))
            elif layer.name in ("Ground", "GRass"):
                exit_tiles.append(r)

    # Build wall set for fast BFS lookup
    wall_set = set()
    for w in walls:
        wall_set.add((w.x // T, w.y // T))

    return walls, wall_set, abel_ban_tile, cain_ban_tile, abel_spawn, cain_spawn, interactive_tiles

def spawn_fragments(interactive_tiles, wall_set, count=6):
    safe = [(x, y) for (x, y) in interactive_tiles if (x, y) not in wall_set]
    if not safe:
        return []

    # Divide map into a grid of zones and pick one tile per zone
    zone_cols = 3
    zone_rows = 2
    zone_w = COLS / zone_cols
    zone_h = ROWS / zone_rows

    zones = {(zc, zr): [] for zc in range(zone_cols) for zr in range(zone_rows)}
    for (x, y) in safe:
        zc = min(int(x / zone_w), zone_cols - 1)
        zr = min(int(y / zone_h), zone_rows - 1)
        zones[(zc, zr)].append((x, y))

    chosen = []
    zone_keys = [k for k, v in zones.items() if v]  # only zones with tiles
    random.shuffle(zone_keys)

    for zk in zone_keys:
        if len(chosen) >= count:
            break
        tile = random.choice(zones[zk])
        chosen.append(tile)

    # If zones didn't give enough, fill remainder from unused safe tiles
    if len(chosen) < count:
        used = set(chosen)
        remaining = [t for t in safe if t not in used]
        random.shuffle(remaining)
        chosen += remaining[:count - len(chosen)]

    frags = []
    for (x, y) in chosen:
        frags.append({
            "rect": pygame.Rect(x * T + 2, y * T + 2, T - 4, T - 4),
            "tile": (x, y),
            "collected": False
        })
    return frags

# ─────────────────────────────────────────────────────────────────────────────
# BFS PATHFINDER
# ─────────────────────────────────────────────────────────────────────────────
def find_path(start, goal, wall_set, extra_walls=None):
    if start == goal:
        return [start]

    blocked = set()
    for (wx, wy) in wall_set:
        blocked.add((wx, wy))
    if extra_walls:
        for r in extra_walls:
            blocked.add((r.x // T, r.y // T))

    queue = collections.deque([start])
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
        for dc, dr in [(0,-1),(0,1),(-1,0),(1,0)]:
            nc, nr = c+dc, r+dr
            if (nc, nr) not in came_from and (nc, nr) not in blocked:
                if 0 <= nc < COLS and 0 <= nr < ROWS:
                    came_from[(nc, nr)] = curr
                    queue.append((nc, nr))
    return []

# ─────────────────────────────────────────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────────────────────────────────────────
class Player:
    SPEED = 5

    def __init__(self):
        self.lives      = MAX_LIVES
        self.stun_timer = 0
        self.push_vx    = 0
        self.push_vy    = 0
        self.abel_caught = False  # first catch flag
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = PLAYER_SPAWN

    def move(self, keys, solid_rects):
        if self.stun_timer > 0:
            # Being pushed
            self.stun_timer -= 1
            nx = self.rect.x + self.push_vx
            ny = self.rect.y + self.push_vy
            test = self.rect.copy()
            test.x = int(nx)
            hit_wall = any(test.colliderect(r) for r in solid_rects)
            test.x = self.rect.x
            test.y = int(ny)
            hit_wall_y = any(test.colliderect(r) for r in solid_rects)

            if hit_wall or hit_wall_y:
                self.lives -= 1
                self.stun_timer = 0
                self.push_vx = self.push_vy = 0
                return True  # signal life lost from wall
            self.rect.x = int(nx)
            self.rect.y = int(ny)
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
            return False

        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  self.SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -self.SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  self.SPEED

        self.rect.x += dx
        for r in solid_rects:
            if self.rect.colliderect(r):
                if dx > 0: self.rect.right = r.left
                else:      self.rect.left  = r.right

        self.rect.y += dy
        for r in solid_rects:
            if self.rect.colliderect(r):
                if dy > 0: self.rect.bottom = r.top
                else:      self.rect.top    = r.bottom

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        return False

    def apply_push(self, from_x, from_y):
        dx = self.rect.centerx - from_x
        dy = self.rect.centery - from_y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        speed = ABEL_PUSH_DISTANCE / (ABEL_STUN_FRAMES / 2)
        self.push_vx = (dx / dist) * speed
        self.push_vy = (dy / dist) * speed
        self.stun_timer = ABEL_STUN_FRAMES // 2

    def near_tile(self, tile_pos, radius=2):
        if tile_pos is None:
            return False
        return tile_rect(*tile_pos).inflate(T*radius, T*radius).colliderect(self.rect)

    def draw(self, surface, inv_timer):
        if inv_timer > 0 and (inv_timer // 5) % 2 == 0:
            return  # flash during invincibility
        pygame.draw.rect(surface, PLAYER_COL, self.rect, border_radius=3)
        pygame.draw.circle(surface, PLAYER_HEAD,
                           (self.rect.centerx, self.rect.top + 4), 5)
        if self.stun_timer > 0:
            pygame.draw.circle(surface, STUN_COL,
                               (self.rect.centerx, self.rect.top - 8), 5, 2)

# ─────────────────────────────────────────────────────────────────────────────
# SPEAR
# ─────────────────────────────────────────────────────────────────────────────
class Spear:
    SPEED = 4

    def __init__(self, x, y, tx, ty):
        self.rect = pygame.Rect(x - 3, y - 3, 6, 6)
        dx = tx - x
        dy = ty - y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        self.vx = (dx / dist) * self.SPEED
        self.vy = (dy / dist) * self.SPEED
        self.angle = math.degrees(math.atan2(-dy, dx))

    def update(self, walls):
        self.rect.x += self.vx
        self.rect.y += self.vy
        for w in walls:
            if self.rect.colliderect(w):
                return True  # hit wall, remove
        if not pygame.Rect(0, 0, WIDTH, HEIGHT).colliderect(self.rect):
            return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, SPEAR_COL, self.rect, border_radius=2)
        pygame.draw.rect(surface, (220, 180, 80), self.rect, 1, border_radius=2)

# ─────────────────────────────────────────────────────────────────────────────
# TWIN BASE
# ─────────────────────────────────────────────────────────────────────────────
class Twin:
    SIZE = 12

    def __init__(self, spawn_tile, speed, color, head_color):
        self.speed      = speed
        self.color      = color
        self.head_color = head_color
        self.banished   = False
        self.enraged    = False
        cx = spawn_tile[0] * T + T // 2
        cy = spawn_tile[1] * T + T // 2
        self.rect = pygame.Rect(cx - self.SIZE//2, cy - self.SIZE//2,
                                self.SIZE, self.SIZE)
        self.path       = []
        self.path_timer = 0

    def move_along_path(self, walls):
        if not self.path or len(self.path) < 2:
            return
        target_c, target_r = self.path[1]
        tx = target_c * T + T // 2
        ty = target_r * T + T // 2
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)

        if dist <= self.speed:
            # Snap exactly to tile center, pop the tile
            self.rect.centerx = tx
            self.rect.centery = ty
            self.path.pop(0)
        else:
            self.rect.x += int((dx/dist) * self.speed)
            self.rect.y += int((dy/dist) * self.speed)

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def update_path(self, player_rect, wall_set, extra_walls=None):
        self.path_timer += 1
        if self.path_timer >= 10:
            self.path_timer = 0
            sc = self.rect.centerx // T
            sr = self.rect.centery  // T
            gc = player_rect.centerx // T
            gr = player_rect.centery  // T
            self.path = find_path((sc, sr), (gc, gr), wall_set, extra_walls)

    def draw(self, surface):
        if self.banished:
            return
        c = ENRAGE_COL if self.enraged else self.color
        h = self.head_color  # ← never override head with enrage color
        pygame.draw.rect(surface, c, self.rect, border_radius=4)
        pygame.draw.circle(surface, h, (self.rect.centerx, self.rect.top + 5), 6)
        if self.enraged:
            pygame.draw.circle(surface, (255, 200, 0),
                               (self.rect.centerx, self.rect.top - 6), 4, 2)

class SpriteSheet:
    def __init__(self, path, frame_w, frame_h, num_frames, row=0, scale=1, speed=9.8):
        sheet = pygame.image.load(path).convert_alpha()
        self.frames = []
        for i in range(num_frames):
            frame = sheet.subsurface((i * frame_w, row * frame_h, frame_w, frame_h))
            if scale != 1:
                frame = pygame.transform.scale(frame,
                    (int(frame_w * scale), int(frame_h * scale)))
            self.frames.append(frame)
        self.index = 0
        self.timer = 0
        self.speed = speed   # ← use parameter

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

class CainSprites:
    ROWS = {"up": 0, "right": 3, "down": 2, "left": 1}

    def __init__(self, scale=1):
        base = os.path.join(BASE_DIR, "Sprites", "Cain")

        def load(filename, fw, fh, frames_per_row, speed=12):
            path = os.path.join(base, filename)
            return {
                dir: SpriteSheet(path, fw, fh, frames_per_row, row=row, scale=scale)
                for dir, row in self.ROWS.items()
            }

        self.anims = {
            "idle": load("cain_idle.png", 30, 50, 2),
            "walk": load("cain_walk.png", 54, 49, 9, speed = 162),
            "thrust": load("cain_thrust.png", 54, 64, 8, speed = 160),
        }
        self.current_anim = "idle"
        self.current_dir = "down"

    def set_anim(self, anim, direction=None):
        if direction:
            self.current_dir = direction
        if anim != self.current_anim:
            self.current_anim = anim
            self.anims[anim][self.current_dir].reset()
        # ← removed the reset on direction change

    def update(self):
        self.anims[self.current_anim][self.current_dir].update()

    def draw(self, surface, rect):
        frame = self.anims[self.current_anim][self.current_dir].current()
        draw_x = rect.centerx - frame.get_width() // 2
        draw_y = rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))

class AbelSprites:
    ROWS = {"up": 0, "right": 3, "down": 2, "left": 1}

    def __init__(self, scale=1):
        base = os.path.join(BASE_DIR, "Sprites", "Abel")

        def load(filename, fw, fh, frames_per_row, speed=12):
            path = os.path.join(base, filename)
            return {
                dir: SpriteSheet(path, fw, fh, frames_per_row, row=row, scale=scale)
                for dir, row in self.ROWS.items()
            }

        self.anims = {
            "idle": load("abel_idle.png", 30, 49, 2),
            "walk": load("abel_walk.png", 37, 49, 9, speed=120),
        }
        self.current_anim = "idle"
        self.current_dir  = "down"

    def set_anim(self, anim, direction=None):
        if direction:
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

# ─────────────────────────────────────────────────────────────────────────────
# CAIN  (slower, throws spears)
# ─────────────────────────────────────────────────────────────────────────────
class Cain(Twin):
    def __init__(self, spawn_tile):
        super().__init__(spawn_tile, CAIN_SPEED_NORMAL, CAIN_COL, CAIN_HEAD)
        self.throw_cooldown = CAIN_THROW_COOLDOWN // 2
        self.throw_range    = CAIN_THROW_RANGE_NORMAL
        self.sprites        = CainSprites(scale=1)

    def enrage(self):
        self.enraged     = True
        self.speed       = CAIN_SPEED_ENRAGED
        self.throw_range = CAIN_THROW_RANGE_ENRAGED

    def try_throw(self, player_rect, walls):
        if self.banished:
            return None

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist_tiles = math.sqrt(dx * dx + dy * dy) / T

        # Set thrust direction when in range
        if dist_tiles <= self.throw_range:
            if abs(dx) > abs(dy):
                self.sprites.set_anim("thrust", "right" if dx > 0 else "left")
            else:
                self.sprites.set_anim("thrust", "down" if dy > 0 else "up")

        self.throw_cooldown -= 1
        if self.throw_cooldown > 0:
            return None
        if dist_tiles <= self.throw_range:
            self.throw_cooldown = CAIN_THROW_COOLDOWN
            return Spear(self.rect.centerx, self.rect.centery,
                         player_rect.centerx, player_rect.centery)
        return None

    def draw(self, surface):
        if self.banished:
            return
        if self.enraged:
            glow = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 80, 80, 80), glow.get_rect())
            surface.blit(glow, (self.rect.x - 19, self.rect.y - 19))
        self.sprites.update()
        self.sprites.draw(surface, self.rect)

# ─────────────────────────────────────────────────────────────────────────────
# ABEL  (faster, stuns on first catch)
# ─────────────────────────────────────────────────────────────────────────────
class Abel(Twin):
    def __init__(self, spawn_tile):
        super().__init__(spawn_tile, ABEL_SPEED_NORMAL, ABEL_COL, ABEL_HEAD)
        self.first_catch_done = False
        self.sprites = AbelSprites(scale=1)   # ← add this

    def enrage(self):
        self.enraged = True
        self.speed   = ABEL_SPEED_ENRAGED

    def check_catch(self, player):
        if self.banished or player.stun_timer > 0:
            return False
        return self.rect.colliderect(player.rect)

    def draw(self, surface):
        if self.banished:
            return
        if self.enraged:
            glow = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (80, 120, 255, 80), glow.get_rect())
            surface.blit(glow, (self.rect.x - 19, self.rect.y - 19))
        self.sprites.update()
        self.sprites.draw(surface, self.rect)

# ─────────────────────────────────────────────────────────────────────────────
# DRAW
# ─────────────────────────────────────────────────────────────────────────────
def draw_scene(surface, walls,
               abel_banished, cain_banished,
               player, cain, abel, spears,
               fragments, lives, inv_timer,
               hint, entrance_closed,
               cain_frags, abel_frags,
               abel_ban_tile, cain_ban_tile):

    # ── TMX layers ──
    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        # Entrance doors
        if layer.name in ("Entracne - Open", "Entrance2 - Open") and entrance_closed:
            continue
        if layer.name in ("Entrance", "Entrance2") and not entrance_closed:
            continue
        # Exit doors
        if layer.name in ("Exit - Open", "Exit2 - Open") and not (abel_banished and cain_banished):
            continue
        if layer.name in ("Exit", "Exit2") and (abel_banished and cain_banished):
            continue
        # Banishment true tiles — only show after banishment
        if layer.name == "AbelBanishmentTrue" and not abel_banished:
            continue
        if layer.name == "CainBanishmentTrue" and not cain_banished:
            continue
        # Skip NagaSpawn-style marker layers
        if layer.name in ("AbelSpawn", "Cain1Spawn"):
            continue

        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(tile, (x * T, y * T))

    # ── Prayer fragments ──
    for frag in fragments:
        if not frag["collected"]:
            dist_x = abs(player.rect.centerx - frag["rect"].centerx)
            dist_y = abs(player.rect.centery - frag["rect"].centery)
            if dist_x < T * 4 and dist_y < T * 4:
                pygame.draw.circle(surface, FRAG_GLOW, frag["rect"].center, (T // 2))
                pygame.draw.circle(surface, FRAG_COL, frag["rect"].center, (T // 2) - 2)
                pygame.draw.circle(surface, WHITE,
                                   (frag["rect"].centerx - 2, frag["rect"].centery - 2), 2)

    # ── Banishment tile prompts ──
    if abel_ban_tile and not abel_banished:
        r = tile_rect(*abel_ban_tile).inflate(4, 4)
        pygame.draw.rect(surface, (80, 120, 200), r, 2, border_radius=3)
    if cain_ban_tile and not cain_banished:
        r = tile_rect(*cain_ban_tile).inflate(4, 4)
        pygame.draw.rect(surface, (200, 80, 80), r, 2, border_radius=3)

    # ── Spears ──
    for spear in spears:
        spear.draw(surface)

    # ── Twins ──
    cain.draw(surface)
    abel.draw(surface)

    # ── Player ──
    player.draw(surface, inv_timer)

    # ── HUD ──
    heart_x = 8
    heart_y = 8
    for i in range(MAX_LIVES):
        if heart_full and heart_empty:
            img = heart_full if i < lives else heart_empty
            surface.blit(img, (heart_x, heart_y))
            heart_x += img.get_width() + 4
        else:
            col = (220, 50, 50) if i < lives else (80, 80, 80)
            pygame.draw.circle(surface, col, (heart_x + 8, heart_y + 8), 7)
            heart_x += 20

    # Fragment counters
    cf_txt = font_hud.render(
        f"  Abel: {abel_frags}/3  Cain: {cain_frags}/3", True, GOLD)
    surface.blit(cf_txt, (heart_x + 10, heart_y + 2))

    # Hint
    if hint:
        ht  = font_md.render(hint, True, WHITE)
        hbg = pygame.Surface((ht.get_width() + 20, ht.get_height() + 10), pygame.SRCALPHA)
        hbg.fill((10, 10, 10, 200))
        surface.blit(hbg, (WIDTH//2 - hbg.get_width()//2, HEIGHT - 48))
        surface.blit(ht, ht.get_rect(center=(WIDTH//2, HEIGHT - 40)))

def draw_dialog(surface, lines, options=None):
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
            surface.blit(font_md.render(f"[{key}]  {label}", True, GOLD), (box_x + 30, y))
            y += 30

# ─────────────────────────────────────────────────────────────────────────────
# STATES
# ─────────────────────────────────────────────────────────────────────────────
STATE_PLAY         = "play"
STATE_HIT          = "hit"
STATE_GAME_OVER    = "gameover"
STATE_WIN          = "win"
STATE_ABEL_CAUGHT  = "abel_caught"
STATE_BANISH_ABEL  = "banish_abel"
STATE_BANISH_CAIN  = "banish_cain"
STATE_ABEL_BANISHED= "abel_banished_msg"
STATE_CAIN_BANISHED= "cain_banished_msg"
STATE_BOTH_BANISHED= "both_banished"

INVINCIBLE_FRAMES = 90

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    walls, wall_set, abel_ban_tile, cain_ban_tile, \
        abel_spawn, cain_spawn, interactive_tiles = build_from_tmx()

    fragments = spawn_fragments(interactive_tiles, wall_set, 6)

    pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "Moonlight_DungeonTheme.wav"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    player  = Player()
    abel = Abel((5, 7))
    cain = Cain((55, 7))
    print(cain.sprites.anims["walk"]["down"].speed)
    spears  = []

    abel_banished   = False
    cain_banished   = False
    abel_frags      = 0   # fragments collected toward Abel banishment
    cain_frags      = 0   # fragments collected toward Cain banishment
    state           = STATE_PLAY
    inv_timer       = 0
    entrance_closed = False

    while True:
        clock.tick(60)

        solid = list(walls)
        hint  = None

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == STATE_PLAY:
                    if event.key == pygame.K_e:
                        # Banish Abel
                        if abel_frags >= FRAGMENTS_NEEDED and not abel_banished \
                                and player.near_tile(abel_ban_tile):
                            state = STATE_BANISH_ABEL
                        # Banish Cain
                        elif cain_frags >= FRAGMENTS_NEEDED and not cain_banished \
                                and player.near_tile(cain_ban_tile):
                            state = STATE_BANISH_CAIN

                elif state == STATE_ABEL_CAUGHT:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = STATE_PLAY


                elif state == STATE_BANISH_ABEL:

                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):

                        abel.banished = True

                        abel_banished = True

                        if not cain_banished:

                            cain.enrage()

                            state = STATE_ABEL_BANISHED

                        else:

                            state = STATE_BOTH_BANISHED


                elif state == STATE_BANISH_CAIN:

                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):

                        cain.banished = True

                        cain_banished = True

                        if not abel_banished:

                            abel.enrage()

                            state = STATE_CAIN_BANISHED

                        else:

                            state = STATE_BOTH_BANISHED

                elif state in (STATE_ABEL_BANISHED, STATE_CAIN_BANISHED):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if abel_banished and cain_banished:
                            exit_zone = pygame.Rect(27 * T, (ROWS - 2) * T, 5 * T, 2 * T)
                            if player.rect.colliderect(exit_zone):
                                state = STATE_WIN
                        else:
                            state = STATE_PLAY

                elif state == STATE_BOTH_BANISHED:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = STATE_PLAY

                elif state == STATE_HIT:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        player.reset()
                        inv_timer = INVINCIBLE_FRAMES
                        state = STATE_PLAY

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        main(); return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == STATE_WIN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        pygame.quit(); sys.exit()

        # ── Game logic ───────────────────────────────────────────────────────
        if state == STATE_PLAY:
            keys = pygame.key.get_pressed()
            hit_wall = player.move(keys, solid)

            if hit_wall and player.lives <= 0:
                state = STATE_GAME_OVER
            elif hit_wall:
                state = STATE_HIT

            # Close entrance
            if not entrance_closed and player.rect.centery > 4 * T:
                entrance_closed = True

            # Fragment pickup
            for frag in fragments:
                if not frag["collected"] and player.rect.colliderect(frag["rect"]):
                    frag["collected"] = True
                    # Alternate between abel and cain frags
                    if abel_frags <= cain_frags and not abel_banished:
                        abel_frags += 1
                    elif not cain_banished:
                        cain_frags += 1
                    else:
                        abel_frags += 1

            # Invincibility countdown
            if inv_timer > 0:
                inv_timer -= 1

            # Cain update
            if not cain.banished:
                cain.update_path(player.rect, wall_set)
                cain.move_along_path(walls)

                # Set walk animation direction
                dx = player.rect.centerx - cain.rect.centerx
                dy = player.rect.centery - cain.rect.centery
                dist_tiles = math.sqrt(dx * dx + dy * dy) / T
                if dist_tiles > cain.throw_range:
                    if abs(dx) > abs(dy):
                        new_dir = "right" if dx > 0 else "left"
                    else:
                        new_dir = "down" if dy > 0 else "up"
                    if new_dir != cain.sprites.current_dir or cain.sprites.current_anim != "walk":
                        cain.sprites.set_anim("walk", new_dir)

                # Spear throw
                new_spear = cain.try_throw(player.rect, walls)

            # Spear update
            for spear in spears[:]:
                remove = spear.update(walls)
                if not remove and inv_timer <= 0 and spear.rect.colliderect(player.rect):
                    player.lives -= 1
                    inv_timer = INVINCIBLE_FRAMES
                    spears.remove(spear)
                    state = STATE_GAME_OVER if player.lives <= 0 else STATE_HIT
                elif remove:
                    if spear in spears:
                        spears.remove(spear)

            # Abel update
            if not abel.banished:
                abel.update_path(player.rect, wall_set)
                abel.move_along_path(walls)

                # ← add direction update
                dx = player.rect.centerx - abel.rect.centerx
                dy = player.rect.centery - abel.rect.centery
                if abs(dx) > abs(dy):
                    new_dir = "right" if dx > 0 else "left"
                else:
                    new_dir = "down" if dy > 0 else "up"
                if new_dir != abel.sprites.current_dir or abel.sprites.current_anim != "walk":
                    abel.sprites.set_anim("walk", new_dir)

                if abel.check_catch(player):
                    if not abel.first_catch_done:
                        abel.first_catch_done = True
                        player.apply_push(abel.rect.centerx, abel.rect.centery)
                        state = STATE_ABEL_CAUGHT
                    else:
                        if inv_timer <= 0:
                            player.lives -= 1
                            inv_timer = INVINCIBLE_FRAMES
                            state = STATE_GAME_OVER if player.lives <= 0 else STATE_HIT

            # Hints
            if abel_frags >= FRAGMENTS_NEEDED and not abel_banished \
                    and player.near_tile(abel_ban_tile):
                hint = "Press [E] to banish Abel"
            elif cain_frags >= FRAGMENTS_NEEDED and not cain_banished \
                    and player.near_tile(cain_ban_tile):
                hint = "Press [E] to banish Cain"
            elif any(not f["collected"] and
                     player.rect.inflate(T*2, T*2).colliderect(f["rect"])
                     for f in fragments):
                hint = "Walk over the prayer fragment to collect it"

            # Win condition — both banished, reach exit
            if abel_banished and cain_banished:
                exit_zone = pygame.Rect(27 * T, (ROWS - 2) * T, 5 * T, 2 * T)
                if player.rect.colliderect(exit_zone):
                    state = STATE_WIN

        # ── Draw ─────────────────────────────────────────────────────────────
        draw_scene(screen, walls,
                   abel_banished, cain_banished,
                   player, cain, abel, spears,
                   fragments, player.lives, inv_timer,
                   hint, entrance_closed,
                   cain_frags, abel_frags,
                   abel_ban_tile, cain_ban_tile)

        if state == STATE_ABEL_CAUGHT:
            draw_dialog(screen,
                ["Abel grabs you and hurls you back!",
                 "He narrows his eyes... next time won't be so merciful."],
                [("Enter", "Continue")])

        elif state == STATE_BANISH_ABEL:
            draw_dialog(screen,
                ["You have gathered the prayer fragments.",
                 "Banish Abel?"],
                [("Enter", "Yes — banish him"), ("Esc", "Not yet")])

        elif state == STATE_BANISH_CAIN:
            draw_dialog(screen,
                ["You have gathered the prayer fragments.",
                 "Banish Cain?"],
                [("Enter", "Yes — banish him"), ("Esc", "Not yet")])

        elif state == STATE_ABEL_BANISHED:
            draw_dialog(screen,
                ["Abel fades into the light...",
                 "Cain roars with grief — his throws grow wilder and farther!"],
                [("Enter", "Continue")])

        elif state == STATE_CAIN_BANISHED:
            draw_dialog(screen,
                ["Cain is cast out...",
                 "Abel's eyes burn — he moves with terrifying speed!"],
                [("Enter", "Continue")])

        elif state == STATE_BOTH_BANISHED:
            draw_dialog(screen,
                ["Both twins have been banished.",
                 "A key falls to the ground...",
                 "The exit is open."],
                [("Enter", "Continue")])

        elif state == STATE_HIT:
            draw_dialog(screen,
                [f"You are wounded!  Lives: {player.lives}",
                 "Gather yourself..."],
                [("Enter", "Continue")])

        elif state == STATE_GAME_OVER:
            draw_dialog(screen,
                ["You have fallen in the garden.",
                 "The twins stand triumphant."],
                [("R", "Try again"), ("Esc", "Quit")])

        elif state == STATE_WIN:
            TheGuardian.main()

        pygame.display.flip()


if __name__ == "__main__":
    main()