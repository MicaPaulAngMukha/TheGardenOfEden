import os.path

import pygame
import sys
import collections
import random
import pytmx
import os
import TheTwins
import math

pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock  = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pygame.mixer.init()

tmx_data = pytmx.load_pygame("TheNagaMap.tmx")

heart_full = pygame.image.load("LifeHeart.png").convert_alpha()
heart_empty = pygame.image.load("LifeHeartLoss.png").convert_alpha()

try:
    portrait_naga = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Naga", "Naga.png")).convert_alpha(),
        (140, 140))
except:
    portrait_naga = None

DIALOGS = {
    "naga_intro": [
        ("Narrator", "You come face to face with..."),
        ("Naga", "...?"),
        ("Naga", "A human..."),
        ("Naga", "You don't look like the ones who lived here before."),
        ("Naga", "You look... different."),
        ("Naga", "How did you get into the garden?"),
        ("Narrator", "The Naga chuckles."),
        ("Naga", "You're here for the fruit, aren't you? The fruit of knowledge?"),
        ("Naga", "Hm... You don't really look as tough as your ancestors."),
        ("Naga", "You look small... Weak."),
        ("Naga", "...Like your mother."),
        ("Naga", "Bet you're a good kid. Following orders, following your parents..."),
        ("Naga", "Unlike your parents."),
        ("Naga", "So why don't you... scurry off. Come on."),
        ("Naga", "I'll even help you."),
        ("Naga", "Don't worry. I don't bite."),
        ("Narrator", "!!!"),
    ],
}

# ── Colors ───────────────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
WALL_COLOR  = (100, 100, 110)
WALL_BORDER = (60,  60,  70)
GOLD        = (212, 175,  55)
HUD_BG      = (15,  15,  15)
NAGA_HEAD   = (60,  160,  60)
NAGA_BODY   = (40,  120,  40)
NAGA_EYE    = (220, 220,  40)
PLAYER_COL  = (200, 160,  80)
PLAYER_HEAD = (210, 170, 120)
LEVER_ON    = (220, 200,  60)
LEVER_OFF   = (160, 140,  50)

# ── Grid ─────────────────────────────────────────────────────────────────────
T    = 13
COLS = WIDTH  // T
ROWS = HEIGHT // T

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_sm  = pygame.font.Font("C:/Users/Mica/PycharmProjects/TheGardenOfEden/font/PixelifySans-VariableFont_wght.ttf", 15)
font_md  = pygame.font.Font("C:/Users/Mica/PycharmProjects/TheGardenOfEden/font/PixelifySans-VariableFont_wght.ttf", 19)
font_hud = pygame.font.Font("C:/Users/Mica/PycharmProjects/TheGardenOfEden/font/PixelifySans-VariableFont_wght.ttf", 15)

# ── Player spawn ──────────────────────────────────────────────────────────────
PLAYER_SPAWN = (21 * T + T // 2, 4 * T + 6)

# ── Exit zone ─────────────────────────────────────────────────────────────────
EXIT_COL_START = 28
EXIT_COL_END   = 34
B = 2

# ─────────────────────────────────────────────────────────────────────────────

def tile_rect(col, row, w=1, h=1):
    return pygame.Rect(col * T, row * T, w * T, h * T)

def build_from_tmx():
    walls        = []
    green_walls  = []
    red_walls    = []
    green_lever  = None
    red_lever    = None
    naga_spawn   = None
    empty_tiles  = []

    WALL_LAYERS = {"Walls", "WallsBack", "Walls_Maze",
                   "Walls_Maze2", "Walls_Maze3", "Walls_Side",
                   "Statue", "Design", "Design2"}

    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        for x, y, gid in layer:
            if gid == 0:
                continue
            r = pygame.Rect(x * T, y * T, T, T)
            if layer.name in WALL_LAYERS:
                walls.append(r)
            elif layer.name == "Green_walls":
                green_walls.append(r)
            elif layer.name == "Red_Walls":
                red_walls.append(r)
            elif layer.name == "Green_Lever":
                green_lever = (x, y)
            elif layer.name == "Red_Lever":
                red_lever = (x, y)
            elif layer.name == "NagaSpawn":
                naga_spawn = (x, y)
            elif layer.name == "Ground":
                empty_tiles.append((x, y))

    return walls, green_walls, red_walls, green_lever, red_lever, naga_spawn, empty_tiles

class SpriteSheet:
    def __init__(self, path, frame_w, frame_h, num_frames, row=0, scale=1):
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
        self.speed = 8

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

# ─────────────────────────────────────────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────────────────────────────────────────
class PlayerSprites:
    # Adjust row order to match your sheet
    ROWS = {"up": 0, "left": 1, "down": 2, "right": 3}

    def __init__(self, scale=1):
        base = os.path.join(BASE_DIR, "Sprites", "Player")

        def load_dir(filename, frames_per_row):
            path = os.path.join(base, filename)
            return {
                dir: SpriteSheet(path, 64, 64, frames_per_row, row=row, scale=scale)
                for dir, row in self.ROWS.items()
            }

        self.anims = {
            "idle": load_dir("idle.png", 2),
            "run":  load_dir("run.png",  6),   # adjust frame count if needed
        }
        # Hurt is a single row, no direction
        hurt_path = os.path.join(base, "hurt.png")
        self.hurt_anim = SpriteSheet(hurt_path, 64, 64, 6, row=0, scale=scale)

        self.current_anim = "idle"
        self.current_dir  = "up"   # ← starts facing up (back to screen)
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
                self.showing_hurt = False  # snap back after hurt plays once
        elif self.current_anim in self.anims:
            self.anims[self.current_anim][self.current_dir].update()

    def get_frame(self):
        if self.showing_hurt:
            return self.hurt_anim.current()
        return self.anims[self.current_anim][self.current_dir].current()

PLAYER_SIZE = 14
MAX_LIVES   = 3

class Player:
    SPEED = 6

    def __init__(self):
        self.lives = MAX_LIVES
        self.sprites = PlayerSprites(scale=1)
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = PLAYER_SPAWN
        self.sprites.set_anim("idle", "down")

    def near_lever(self, lever_tile):          # ← this was missing
        if lever_tile is None:
            return False
        interact_box = tile_rect(*lever_tile).inflate(T * 3, T * 3)
        return interact_box.colliderect(self.rect)

    def move(self, keys, solid_rects):
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

    def trigger_hurt(self):
        self.sprites.show_hurt()

    def draw(self, surface):
        self.sprites.update()
        frame = self.sprites.get_frame()
        draw_x = self.rect.centerx - frame.get_width() // 2
        draw_y = self.rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))

# ─────────────────────────────────────────────────────────────────────────────
# NAGA
# ─────────────────────────────────────────────────────────────────────────────
SEG_SIZE    = 16
SEG_SPACING = 5
NAGA_SPEED  = 5
HISTORY_LEN = 80

class NagaSprites:
    def __init__(self, scale=0.4):  # ← was scale=1, drop to 0.25
        base = os.path.join(BASE_DIR, "Sprites", "Naga")
        path = os.path.join(base, "Naga_Torso.png")
        sheet = pygame.image.load(path).convert_alpha()

        FRAME_W = 144
        FRAME_H = 215
        dir_col = {"down": 0, "left": 1, "right": 2, "up": 3}

        self.frames = {}
        for dir, col in dir_col.items():
            frame = sheet.subsurface((col * FRAME_W, 0, FRAME_W, FRAME_H))
            frame = pygame.transform.scale(
                frame, (int(FRAME_W * scale), int(FRAME_H * scale)))
            self.frames[dir] = frame

        self.current_dir = "down"

    def set_direction(self, direction):
        self.current_dir = direction

    def get_frame(self):
        return self.frames[self.current_dir]

class Naga:
    N_SEGS = 3

    def __init__(self, spawn_tile):
        cx = spawn_tile[0] * T + T // 2
        cy = spawn_tile[1] * T + T // 2
        self.history = collections.deque(maxlen=HISTORY_LEN)
        for i in range(HISTORY_LEN):
            angle = i * 0.3  # spiral angle
            radius = max(4, 20 - i * 0.15)  # tightens toward center
            px = cx + math.cos(angle) * radius
            py = cy + math.sin(angle) * radius
            self.history.append((px, py))
        self.sprites = NagaSprites(scale=0.4)    # ← add this line
        self.current_dir = "down"
        # Path caching to fix performance issue
        self.cached_path = []
        self.path_recalc_timer = 0
        self.PATH_RECALC_INTERVAL = 3  # Recalculate path every 3 frames (balance between performance and smoothness)

    def find_path(self, start, goal, walls, green_walls, red_walls, green_active, red_active):
        if start == goal:
            return [start]

        def is_solid(c, r):
            if c < 0 or c >= COLS or r < 0 or r >= ROWS:
                return True
            test = pygame.Rect(c * T, r * T, T, T)
            for w in walls:
                if test.colliderect(w): return True
            if not green_active:
                for gw in green_walls:
                    if test.colliderect(gw): return True
            if not red_active:
                for rw in red_walls:
                    if test.colliderect(rw): return True
            return False

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
                if (nc, nr) not in came_from and not is_solid(nc, nr):
                    came_from[(nc, nr)] = curr
                    queue.append((nc, nr))
        return []

    def update(self, player_rect, walls, green_walls, red_walls, green_active, red_active):
        hx, hy = self.history[0]
        naga_c, naga_r = int(hx // T), int(hy // T)
        play_c, play_r = player_rect.centerx // T, player_rect.centery // T

        # Only recalculate path periodically to improve performance
        self.path_recalc_timer -= 1
        if self.path_recalc_timer <= 0 or not self.cached_path:
            self.cached_path = self.find_path((naga_c, naga_r), (play_c, play_r),
                                              walls, green_walls, red_walls, green_active, red_active)
            self.path_recalc_timer = self.PATH_RECALC_INTERVAL

        path = self.cached_path

        if path and len(path) > 1:
            curr_c, curr_r = path[0]
            target_c, target_r = path[1]

            center_x = curr_c * T + T / 2.0
            center_y = curr_r * T + T / 2.0
            next_x   = target_c * T + T / 2.0
            next_y   = target_r * T + T / 2.0

            if target_c != curr_c:
                if abs(hy - center_y) > 0.5:
                    tx, ty = hx, center_y
                else:
                    hy = center_y
                    tx, ty = next_x, next_y
            elif target_r != curr_r:
                if abs(hx - center_x) > 0.5:
                    tx, ty = center_x, hy
                else:
                    hx = center_x
                    tx, ty = next_x, next_y
            else:
                tx, ty = next_x, next_y
        else:
            tx, ty = player_rect.centerx, player_rect.centery

        dx, dy = tx - hx, ty - hy
        dist = max(0.001, (dx ** 2 + dy ** 2) ** 0.5)
        step = min(NAGA_SPEED, dist)

        # ── Direction update ──────────────────────────────────────────────
        if abs(dx) > abs(dy):
            self.current_dir = "right" if dx > 0 else "left"
        elif abs(dy) > 0.01:
            self.current_dir = "down" if dy > 0 else "up"
        self.sprites.set_direction(self.current_dir)
        # ─────────────────────────────────────────────────────────────────

        if dist > 0.1:
            self.history.appendleft((hx + (dx / dist) * step, hy + (dy / dist) * step))
        else:
            self.history.appendleft((hx, hy))

    def segments(self):
        return [self.history[min(i * SEG_SPACING, len(self.history)-1)]
                for i in range(self.N_SEGS)]

    def head_rect(self):
        hx, hy = self.history[0]
        return pygame.Rect(hx - SEG_SIZE//2, hy - SEG_SIZE//2, SEG_SIZE, SEG_SIZE)

    def draw(self, surface):
        # More points = longer, more terrifying tail
        num_points = 60  # was 25, increase for length
        points = [(int(sx), int(sy)) for sx, sy in
                  [self.history[min(i * 3, len(self.history) - 1)]
                   for i in range(num_points)]]

        if len(points) >= 2:
            # Draw tapering tail — thick at torso, thin at tip
            for i in range(len(points) - 1):
                progress = i / len(points)  # 0 at head, 1 at tail tip
                thickness = max(2, int(18 * (1 - progress)))  # tapers from 18 to 2

                p1 = points[i]
                p2 = points[i + 1]

                # Layered colors for depth
                pygame.draw.line(surface, (20, 70, 20), p1, p2, thickness + 3)
                pygame.draw.line(surface, NAGA_BODY, p1, p2, thickness)
                pygame.draw.line(surface, (70, 180, 70), p1, p2, max(1, thickness - 5))

            # Pointed tip — small triangle at the very end
            tip = points[-1]
            prev = points[-2]
            dx = tip[0] - prev[0]
            dy = tip[1] - prev[1]
            dist = max(0.001, (dx ** 2 + dy ** 2) ** 0.5)
            nx, ny = dx / dist, dy / dist  # normalized direction
            px, py = -ny, nx  # perpendicular

            tri = [
                (tip[0] + int(nx * 8), tip[1] + int(ny * 8)),  # point
                (tip[0] + int(px * 3), tip[1] + int(py * 3)),  # left base
                (tip[0] - int(px * 3), tip[1] - int(py * 3)),  # right base
            ]
            pygame.draw.polygon(surface, (20, 70, 20), tri)

        # Torso on top
        frame = self.sprites.get_frame()
        hx, hy = self.history[0]
        draw_x = int(hx) - frame.get_width() // 2
        draw_y = int(hy) - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))

# ─────────────────────────────────────────────────────────────────────────────
# DRAW
# ─────────────────────────────────────────────────────────────────────────────
def draw_lever(surface, tile, active):
    r   = tile_rect(*tile).inflate(-4, -4)
    col = LEVER_ON if active else LEVER_OFF
    pygame.draw.rect(surface, col, r, border_radius=3)
    pygame.draw.rect(surface, WHITE, r, 1, border_radius=3)
    lbl = font_sm.render("✓" if active else "E", True, WHITE)
    surface.blit(lbl, lbl.get_rect(center=r.center))

def draw_scene(surface, green_walls, red_walls,
               green_active, red_active, player, naga, lives, hint,
               green_lever_pos, red_lever_pos, items_on_map, entrance_closed):

    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        if layer.name in ("Entracne - Open", "Entrance2 - Open") and entrance_closed:
            continue
        if layer.name in ("Entrance", "Entrance2") and not entrance_closed:
            continue
        if layer.name in ("Exit - Open", "Exit2 - Open") and not red_active:
            continue
        if layer.name in ("Exit", "Exit2") and red_active:
            continue
        if layer.name == "Green_walls" and green_active:
            continue
        if layer.name == "Red_Walls" and red_active:
            continue
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(tile, (x * T, y * T))

    # Levers
    if green_lever_pos: draw_lever(surface, green_lever_pos, green_active)
    if red_lever_pos:   draw_lever(surface, red_lever_pos,   red_active)

    # Items
    for item in items_on_map:
        color  = (255, 50, 50) if item['type'] == 'life' else (50, 200, 255)
        center = item['rect'].center
        pygame.draw.circle(surface, color, center, (T // 2) - 1)
        pygame.draw.circle(surface, WHITE, (center[0]-2, center[1]-2), 2)

    naga.draw(surface)
    player.draw(surface)

    heart_x = 8
    heart_y = 8
    for i in range(MAX_LIVES):
        img = heart_full if i < lives else heart_empty
        surface.blit(img, (heart_x, heart_y))
        heart_x += img.get_width() + 4

    interact_txt = font_hud.render("[E] interact", True, GOLD)
    surface.blit(interact_txt, (heart_x + 8, heart_y + img.get_height() // 2 - interact_txt.get_height() // 2))

    if hint:
        ht  = font_md.render(hint, True, WHITE)
        hbg = pygame.Surface((ht.get_width() + 20, ht.get_height() + 10), pygame.SRCALPHA)
        hbg.fill((10, 10, 10, 200))
        surface.blit(hbg, (WIDTH//2 - hbg.get_width()//2, HEIGHT - 48))
        surface.blit(ht, ht.get_rect(center=(WIDTH//2, HEIGHT - 40)))

def draw_dialog(surface, lines, options=None):
    box_w = 460
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

NAGA_BORDER = (60, 160, 60)  # green to match him
DIALOG_W    = 700
DIALOG_H    = 180
PORTRAIT_SIZE = 140

def draw_naga_dialog(surface, speaker, typewriter):
    if speaker == "Narrator":
        # Simple centered box, no portrait
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
        return

    # Naga lines — portrait box
    is_naga = (speaker == "Naga")
    border_col = NAGA_BORDER if is_naga else GOLD

    box_x = WIDTH  // 2 - DIALOG_W // 2
    box_y = HEIGHT - DIALOG_H - 10

    ov = pygame.Surface((DIALOG_W, DIALOG_H), pygame.SRCALPHA)
    ov.fill((10, 10, 10, 230))
    surface.blit(ov, (box_x, box_y))
    pygame.draw.rect(surface, border_col, (box_x, box_y, DIALOG_W, DIALOG_H), 3, border_radius=8)

    portrait_x = box_x + 10
    portrait_y = box_y + DIALOG_H // 2 - PORTRAIT_SIZE // 2
    pygame.draw.rect(surface, (20, 20, 20), (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    pygame.draw.rect(surface, border_col, (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE), 3)

    if portrait_naga:
        surface.blit(portrait_naga, (portrait_x, portrait_y))

    name_surf = font_md.render(speaker, True, border_col)
    surface.blit(name_surf, (portrait_x, portrait_y - 22))

    text_x = portrait_x + PORTRAIT_SIZE + 18
    max_w  = DIALOG_W - PORTRAIT_SIZE - 30
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

# ─────────────────────────────────────────────────────────────────────────────
# STATES / MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────
STATE_PLAY      = "play"
STATE_HIT       = "hit"
STATE_GAME_OVER = "gameover"
STATE_WIN       = "win"
STATE_LEVER_G   = "lever_g"
STATE_LEVER_R   = "lever_r"
STATE_INTRO_DIALOG = "intro_dialog"
STATE_INTRO_WAIT   = "intro_wait"  # player frozen before dialog triggers

INVINCIBLE_FRAMES = 90

TYPEWRITER_SPEED = 2

class Typewriter:
    def __init__(self):
        self.full_text     = ""
        self.visible_chars = 1
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

def main():
    walls, green_walls, red_walls, GREEN_LEVER_POS, RED_LEVER_POS, naga_tile, empty_tiles = build_from_tmx()

    pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "Moonlight_DungeonTheme.wav"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    wall_set = set()
    for w in walls:
        wall_set.add((w.x // T, w.y // T))
    for gw in green_walls:
        wall_set.add((gw.x // T, gw.y // T))
    for rw in red_walls:
        wall_set.add((rw.x // T, rw.y // T))

    empty_tiles = [(x, y) for (x, y) in empty_tiles if (x, y) not in wall_set]

    player          = Player()
    naga            = Naga(naga_tile)
    green_active    = False
    red_active      = False
    state           = STATE_PLAY
    inv_timer       = 0
    entrance_closed = False

    items_on_map      = []
    item_spawn_timer  = 180
    naga_freeze_timer = 0

    typewriter = Typewriter()
    naga_dialog = []
    dialog_index = 0
    intro_done = False
    intro_triggered = False

    while True:
        clock.tick(60)

        solid = list(walls)
        if not green_active: solid += green_walls
        if not red_active:   solid += red_walls
        path_timer = 0

        hint = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == STATE_PLAY:
                    if event.key in (pygame.K_e, pygame.K_SPACE):
                        if not green_active and player.near_lever(GREEN_LEVER_POS):
                            state = STATE_LEVER_G
                        elif not red_active and player.near_lever(RED_LEVER_POS):
                            state = STATE_LEVER_R

                elif state in (STATE_HIT, STATE_LEVER_G, STATE_LEVER_R):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                        if state == STATE_LEVER_G:
                            green_active = True
                        elif state == STATE_LEVER_R:
                            red_active = True
                        elif state == STATE_HIT:
                            player.reset()
                            inv_timer = INVINCIBLE_FRAMES
                        state = STATE_PLAY

                elif state == STATE_INTRO_DIALOG:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            dialog_index += 1
                            if dialog_index < len(naga_dialog):
                                typewriter.set_text(naga_dialog[dialog_index][1])
                            else:
                                # Chase begins
                                intro_done = True
                                state = STATE_PLAY

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        main(); return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                elif state == STATE_WIN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        pygame.quit(); sys.exit()

        if state == STATE_PLAY:
            keys = pygame.key.get_pressed()
            player.move(keys, solid)

            # Close entrance once player walks past row 4
            if not entrance_closed and player.rect.centery > 4 * T:
                entrance_closed = True
                if not intro_triggered:
                    intro_triggered = True
                    naga_dialog = DIALOGS["naga_intro"]
                    dialog_index = 0
                    typewriter.set_text(naga_dialog[0][1])
                    state = STATE_INTRO_DIALOG

            if naga_freeze_timer > 0:
                naga_freeze_timer -= 1
            elif intro_done:
                naga.update(player.rect, walls, green_walls, red_walls, green_active, red_active)

            if inv_timer <= 0:
                if naga.head_rect().colliderect(player.rect):
                    player.lives -= 1
                    player.trigger_hurt()  # ← add this
                    state = STATE_GAME_OVER if player.lives <= 0 else STATE_HIT
            else:
                inv_timer -= 1

            item_spawn_timer -= 1
            if item_spawn_timer <= 0:
                item_spawn_timer = random.randint(300, 600)
                if len(items_on_map) < 3 and empty_tiles:
                    spawn_col, spawn_row = random.choice(empty_tiles)
                    if player.lives < 3 and empty_tiles:
                        item_type = random.choice(['life', 'freeze'])

                    else:
                        item_type = 'freeze'

                    item_rect = pygame.Rect(spawn_col * T + 2, spawn_row * T + 2, T - 4, T - 4)
                    items_on_map.append({'type': item_type, 'rect': item_rect})

            for item in items_on_map[:]:
                if player.rect.colliderect(item['rect']):
                    if item['type'] == 'life':
                        player.lives = min(MAX_LIVES + 1, player.lives + 1)
                    elif item['type'] == 'freeze':
                        naga_freeze_timer = 180
                    items_on_map.remove(item)

            if not green_active and player.near_lever(GREEN_LEVER_POS):
                hint = "Press [E] to pull the lever"
            elif not red_active and player.near_lever(RED_LEVER_POS):
                hint = "Press [E] to pull the lever"

            exit_rect = pygame.Rect(EXIT_COL_START * T, (ROWS - B) * T,
                                    (EXIT_COL_END - EXIT_COL_START) * T, B * T)
            if red_active and player.rect.colliderect(exit_rect):
                state = STATE_WIN

        draw_scene(screen, green_walls, red_walls,
                   green_active, red_active, player, naga, player.lives, hint,
                   GREEN_LEVER_POS, RED_LEVER_POS, items_on_map, entrance_closed)

        if state == STATE_HIT:
            draw_dialog(screen,
                [f"The Naga strikes!  Lives: {player.lives}",
                 "You respawn at the entrance..."],
                [("Enter", "Continue")])
        elif state == STATE_GAME_OVER:
            draw_dialog(screen,
                ["The Naga has consumed you.",
                 "You have no lives left."],
                [("R", "Try again"), ("Esc", "Quit")])
        elif state == STATE_LEVER_G:
            draw_dialog(screen,
                ["You find a lever.", "Pull it?"],
                [("E / Enter", "Yes")])
        elif state == STATE_LEVER_R:
            draw_dialog(screen,
                ["You find a lever.", "Pull it?"],
                [("E / Enter", "Yes")])
        elif state == STATE_WIN:
            pygame.mixer.music.fadeout(500)
            TheTwins.main()
            pygame.quit()

        if state == STATE_INTRO_DIALOG and dialog_index < len(naga_dialog):
            speaker, _ = naga_dialog[dialog_index]
            typewriter.update()
            draw_naga_dialog(screen, speaker, typewriter)

        pygame.display.flip()

# =============================================================================
# LIGHTNING  —  duplicated to avoid circular import
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
# GOD_MAIN  —  backtrack mode (naga gone, god chasing player to top entrance)
# =============================================================================
def _near_door_naga(player_rect, door_rects, radius=50):
    if not door_rects:
        return False
    door_union = door_rects[0].unionall(door_rects[1:])
    return door_union.inflate(radius * 2, radius * 2).colliderect(player_rect)


def god_main(god, lives=MAX_LIVES):
    """
    Backtrack pass through The Naga's Lair.
    - No naga, no levers, no items.
    - Player spawns at bottom (from Twins), kicks top entrance to exit.
    - On exit: calls Start.god_epilogue() — Mikhail/Raziel epilogue.
    """
    walls, green_walls, red_walls, green_lever, red_lever, naga_spawn, empty_tiles = build_from_tmx()

    # Collect entrance/exit tiles inline
    entrance_tiles = []
    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        for x, y, gid in layer:
            if gid == 0:
                continue
            r = pygame.Rect(x * T, y * T, T, T)
            if layer.name in ("Entrance", "Entrance2"):
                entrance_tiles.append(r)

    # All walls active — no levers in backtrack
    all_walls = walls

    player           = Player()
    player.lives     = lives
    player.rect.x    = WIDTH // 2 - PLAYER_SIZE // 2
    player.rect.y    = HEIGHT - 8 * T
    player.sprites.set_anim("idle", "down")

    lightning_bolts  = []
    inv_timer        = 120

    DOOR_KICK_MIN     = 4
    DOOR_KICK_MAX     = 8
    door_kicks        = 0
    door_kicks_needed = random.randint(DOOR_KICK_MIN, DOOR_KICK_MAX)
    door_kick_cd      = 0
    door_open         = False
    door_rects        = [t for t in entrance_tiles if t.y < HEIGHT // 2]

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
                                and _near_door_naga(player.rect, door_rects) \
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

            # Remove entrance walls when door is open
            if door_open and door_rects:
                entrance_set = {(r.x, r.y) for r in door_rects}
                active_walls = [w for w in all_walls if (w.x, w.y) not in entrance_set]
            else:
                active_walls = all_walls
            player.move(keys, active_walls)

            if door_kick_cd > 0: door_kick_cd -= 1
            if inv_timer     > 0: inv_timer    -= 1

            keys_held = pygame.key.get_pressed()
            if keys_held[pygame.K_e] and not door_open \
                    and _near_door_naga(player.rect, door_rects) \
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
                    player.lives -= 1
                    inv_timer     = INVINCIBLE_FRAMES
                    if player.lives <= 0:
                        state = STATE_DEAD
                if done:
                    lightning_bolts.remove(bolt)

            # Exit through top → epilogue
            if door_open:
                exit_zone = pygame.Rect(0, 0, WIDTH, 4 * T)
                if player.rect.colliderect(exit_zone):
                    import Start
                    Start.god_epilogue()
                    return

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BLACK)

        for layer in tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            if layer.name in ("NagaSpawn", "Green_Lever", "Red_Lever"):
                continue
            # Add these — skip lever-gated walls and lever tiles entirely
            if layer.name in ("Green_walls", "Red_Walls"):
                continue
            # Also skip the closed exit/entrance as before
            if layer.name in ("Entracne - Open", "Entrance2 - Open") and not door_open:
                continue
            if layer.name in ("Entrance", "Entrance2") and door_open:
                continue
            if layer.name in ("Exit", "Exit2"):
                continue
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * T, y * T))

        # Door kick UI — below the top door
        if not door_open and door_rects:
            door_union = door_rects[0].unionall(door_rects[1:])
            progress   = door_kicks / max(door_kicks_needed, 1)
            crack_col  = (int(220 * progress), int(80 * (1 - progress)), 0)
            pygame.draw.rect(screen, crack_col, door_union.inflate(4, 4), 2, border_radius=2)

            bx, by, bw = door_union.x, door_union.bottom + 4, door_union.width
            pygame.draw.rect(screen, (50, 20, 20), (bx, by, bw, 5))
            pygame.draw.rect(screen, (220, 80, 40), (bx, by, int(bw * progress), 5))

            if _near_door_naga(player.rect, door_rects):
                hint = font_sm.render(
                    f"[E] Kick the door  ({door_kicks}/{door_kicks_needed})", True, WHITE)
                hbg = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8),
                                      pygame.SRCALPHA)
                hbg.fill((10, 10, 10, 180))
                screen.blit(hbg,  (WIDTH // 2 - hbg.get_width() // 2, HEIGHT - 44))
                screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

        for bolt in lightning_bolts:
            bolt.draw(screen)

        god.draw(screen)
        player.draw(screen)

        hx, hy = 8, 8
        for i in range(MAX_LIVES):
            img = heart_full if i < player.lives else heart_empty
            screen.blit(img, (hx, hy))
            hx += img.get_width() + 4

        if state == STATE_DEAD:
            draw_dialog(screen,
                ["The divine presence consumes you.",
                 "There is no escaping divine wrath."],
                [("R", "Try again"), ("Esc", "Quit")])

        pygame.display.flip()


if __name__ == "__main__":
    main()