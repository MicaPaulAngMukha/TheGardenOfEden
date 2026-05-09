import pygame
import sys
import os
import math
import random
import pytmx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Garden")
clock = pygame.time.Clock()

tmx_data = pytmx.load_pygame(os.path.join(BASE_DIR, "TheGardenMap.tmx"))

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
GOLD         = (212, 175,  55)
PLAYER_COL   = (200, 160,  80)
PLAYER_HEAD  = (210, 170, 120)
MIKHAIL_BORDER = (220, 190, 80)
RAZIEL_BORDER  = (160, 200, 240)
DIALOG_W      = 700
DIALOG_H      = 180
PORTRAIT_SIZE = 140

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

# ── Key / Apple image ─────────────────────────────────────────────────────────
try:
    key_img = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "Key.png")).convert_alpha(), (16, 16))
except Exception:
    key_img = None

# ── Portraits ─────────────────────────────────────────────────────────────────
try:
    portrait_mikhail = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Mikhail", "mikhail.png")).convert_alpha(),
        (PORTRAIT_SIZE, PORTRAIT_SIZE))
except Exception:
    portrait_mikhail = None

try:
    portrait_raziel = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Raziel", "raziel.png")).convert_alpha(),
        (PORTRAIT_SIZE, PORTRAIT_SIZE))
except Exception:
    portrait_raziel = None

# ── Constants ─────────────────────────────────────────────────────────────────
PLAYER_SIZE       = 14
MAX_LIVES         = 3
PLAYER_SPAWN      = (WIDTH // 2, HEIGHT - 60)  # enters from bottom

TREE_SHAKE_NEEDED = 3        # shakes before apple falls
DOOR_KICK_MIN     = 4        # min kicks to break door
DOOR_KICK_MAX     = 8        # max kicks
INVINCIBLE_FRAMES = 90
TYPEWRITER_SPEED  = 2

# God constants
GOD_SPEED         = 0.9      # slow but inevitable — ignores walls
GOD_SMITE_RANGE   = 90       # instant-kill radius in pixels
LIGHTNING_COUNT   = 5
LIGHTNING_COOLDOWN = 90      # frames between bolt volleys

WALL_LAYERS = {"Walls", "WallsBack", "Walls_Side", "Path", "Path2", "Path3"}

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
    tree_tile      = None    # (col, row) of the tree interact tile
    door_tile      = None    # (col, row) of the exit door tile
    entrance_tiles = []

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
            elif layer.name == "TreeInteract":
                tree_tile = (x, y)
            elif layer.name == "DoorBreak":
                door_tile = (x, y)
            elif layer.name in ("Entrance", "Entrance2"):
                entrance_tiles.append(r)

    return walls, wall_set, tree_tile, door_tile, entrance_tiles


# =============================================================================
# PLAYER
# =============================================================================
class Player:
    SPEED = 3

    def __init__(self):
        self.lives      = MAX_LIVES
        self.has_apple  = False
        self.inv_timer  = 0
        self.rect       = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = PLAYER_SPAWN

    def move(self, keys, walls, restrict_top=False):
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  self.SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -self.SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  self.SPEED

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

        if restrict_top and self.rect.top < 4 * T:
            self.rect.top = 4 * T

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def near_tile(self, tile_pos, radius=2):
        if tile_pos is None:
            return False
        r = pygame.Rect(tile_pos[0] * T, tile_pos[1] * T, T, T)
        return r.inflate(T * radius, T * radius).colliderect(self.rect)

    def draw(self, surface):
        if self.inv_timer > 0 and (self.inv_timer // 5) % 2 == 0:
            return
        pygame.draw.rect(surface, PLAYER_COL, self.rect, border_radius=3)
        pygame.draw.circle(surface, PLAYER_HEAD,
                           (self.rect.centerx, self.rect.top + 4), 5)
        if self.has_apple:
            # Small red circle above player = apple
            pygame.draw.circle(surface, (200, 40, 40),
                               (self.rect.centerx, self.rect.top - 8), 5)
            pygame.draw.circle(surface, (240, 80, 80),
                               (self.rect.centerx - 1, self.rect.top - 9), 3)


# =============================================================================
# LIGHTNING BOLT
# =============================================================================
class Lightning:
    LINGER = 30   # frames to show before disappearing

    def __init__(self, tx, ty):
        # Strike at (tx, ty) from sky
        self.x      = tx
        self.y      = ty
        self.timer  = self.LINGER
        self.warned = False   # warning circle shown before strike
        self.warn_timer = 45  # frames of warning before landing

    def update(self):
        if self.warn_timer > 0:
            self.warn_timer -= 1
            return False   # not live yet
        if self.timer > 0:
            self.timer -= 1
            return False   # still displaying
        return True        # done, remove

    @property
    def is_live(self):
        """True while the bolt itself is on screen (not just warning)."""
        return self.warn_timer <= 0 and self.timer > 0

    def hits(self, rect):
        if not self.is_live:
            return False
        return pygame.Rect(self.x - 12, self.y - 12, 24, 24).colliderect(rect)

    def draw(self, surface):
        if self.warn_timer > 0:
            # Faint red warning ring
            alpha = int(180 * (1 - self.warn_timer / 45))
            warn_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(warn_surf, (255, 60, 60, alpha), (25, 25), 22, 3)
            surface.blit(warn_surf, (self.x - 25, self.y - 25))
            return

        if self.timer <= 0:
            return

        # Jagged bolt from top of screen to strike point
        bright = min(255, int(255 * (self.timer / self.LINGER)))
        pts = [(self.x, 0)]
        cy = 0
        while cy < self.y:
            cy += random.randint(18, 34)
            ox = random.randint(-14, 14)
            pts.append((self.x + ox, min(cy, self.y)))
        pts.append((self.x, self.y))
        if len(pts) >= 2:
            pygame.draw.lines(surface, (bright, bright, 60), False, pts, 3)
            pygame.draw.lines(surface, (255, 255, 200), False, pts, 1)

        # Impact glow
        glow = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 240, 80, bright // 2), glow.get_rect())
        surface.blit(glow, (self.x - 30, self.y - 20))


# =============================================================================
# GOD  (the divine presence — ignores all walls, floats toward player)
# =============================================================================
class God:
    SIZE = 20

    def __init__(self):
        # Spawns from the centre top of the map, descends
        self.rect   = pygame.Rect(WIDTH // 2 - self.SIZE // 2, -60,
                                  self.SIZE, self.SIZE)
        self.alive  = True
        self.bolt_timer = LIGHTNING_COOLDOWN // 2

    def update(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        self.rect.x += int((dx / dist) * GOD_SPEED)
        self.rect.y += int((dy / dist) * GOD_SPEED)
        # No clamping — God can be anywhere

    def in_smite_range(self, player_rect):
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        return math.sqrt(dx * dx + dy * dy) < GOD_SMITE_RANGE

    def try_spawn_bolts(self, player_rect):
        """Returns a list of new Lightning objects if it's time to strike."""
        self.bolt_timer -= 1
        if self.bolt_timer > 0:
            return []
        self.bolt_timer = LIGHTNING_COOLDOWN
        bolts = []
        for _ in range(LIGHTNING_COUNT):
            # Random positions biased toward player
            tx = player_rect.centerx + random.randint(-120, 120)
            ty = player_rect.centery + random.randint(-80, 80)
            tx = max(T, min(WIDTH - T, tx))
            ty = max(T * 4, min(HEIGHT - T, ty))
            bolts.append(Lightning(tx, ty))
        return bolts

    def draw(self, surface):
        if not self.alive:
            return
        cx, cy = self.rect.centerx, self.rect.centery

        # Divine glow — large white/gold aura
        ticks = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(ticks / 200)
        glow_r = int(55 + 15 * pulse)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 255, 200, int(60 + 30 * pulse)), glow.get_rect())
        surface.blit(glow, (cx - glow_r, cy - glow_r))

        # Outer ring
        pygame.draw.circle(surface, (255, 240, 160), (cx, cy), 22, 2)
        # Body — tall pillar of light
        pygame.draw.rect(surface, (240, 230, 180),
                         pygame.Rect(cx - 8, cy - 14, 16, 28), border_radius=4)
        # Head
        pygame.draw.circle(surface, (255, 250, 220), (cx, cy - 20), 10)
        # Inner white core
        pygame.draw.circle(surface, WHITE, (cx, cy - 20), 6)
        # Radiant lines
        for angle in range(0, 360, 45):
            rad = math.radians(angle + ticks / 10)
            x1 = cx + int(math.cos(rad) * 24)
            y1 = (cy - 20) + int(math.sin(rad) * 24)
            x2 = cx + int(math.cos(rad) * 34)
            y2 = (cy - 20) + int(math.sin(rad) * 34)
            pygame.draw.line(surface, (255, 240, 120), (x1, y1), (x2, y2), 2)


# =============================================================================
# SCREEN SHAKE
# =============================================================================
class ScreenShake:
    def __init__(self):
        self.timer    = 0
        self.strength = 0

    def start(self, frames, strength=6):
        self.timer    = frames
        self.strength = strength

    def update(self):
        if self.timer > 0:
            self.timer -= 1

    @property
    def offset(self):
        if self.timer <= 0:
            return (0, 0)
        return (random.randint(-self.strength, self.strength),
                random.randint(-self.strength, self.strength))


# =============================================================================
# DRAW SCENE
# =============================================================================
def draw_scene(surface, player, god, lightning_bolts,
               gate_open, entrance_closed,
               tree_tile, door_tile, door_kicks, door_kicks_needed,
               apple_on_ground, apple_pos,
               red_flash_alpha, shake,
               god_spawned):

    # Apply screen shake by blitting to a temp surface
    ox, oy = shake.offset
    draw_surf = pygame.Surface((WIDTH, HEIGHT))

    # ── TMX layers ────────────────────────────────────────────────────────────
    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        if layer.name in ("Entracne - Open", "Entrance2 - Open") and entrance_closed:
            continue
        if layer.name in ("Entrance", "Entrance2") and not entrance_closed:
            continue
        if layer.name in ("Exit - Open", "Exit2 - Open") and not gate_open:
            continue
        if layer.name in ("Exit", "Exit2") and gate_open:
            continue
        for x, y, gid in layer:
            tile_img = tmx_data.get_tile_image_by_gid(gid)
            if tile_img:
                draw_surf.blit(tile_img, (x * T, y * T))

    # ── Tree interact hint glow ───────────────────────────────────────────────
    if tree_tile and not god_spawned:
        tr = pygame.Rect(tree_tile[0] * T, tree_tile[1] * T, T, T)
        ticks = pygame.time.get_ticks()
        alpha = int(80 + 60 * math.sin(ticks / 400))
        glow = pygame.Surface((T + 10, T + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (80, 200, 80, alpha), glow.get_rect(), border_radius=3)
        draw_surf.blit(glow, (tr.x - 5, tr.y - 5))

    # ── Apple on ground ───────────────────────────────────────────────────────
    if apple_on_ground and apple_pos:
        ax, ay = apple_pos
        pygame.draw.circle(draw_surf, (200, 40, 40), (ax, ay), 6)
        pygame.draw.circle(draw_surf, (240, 80, 80), (ax - 1, ay - 2), 3)
        pygame.draw.line(draw_surf, (80, 140, 40), (ax, ay - 6), (ax + 3, ay - 10), 2)

    # ── Door damage indicator ─────────────────────────────────────────────────
    if door_tile and god_spawned and not gate_open:
        dr = pygame.Rect(door_tile[0] * T, door_tile[1] * T, T * 2, T * 2)
        progress = door_kicks / max(door_kicks_needed, 1)
        # Crack lines intensify as door gets weaker
        crack_col = (int(200 * progress), int(100 * (1 - progress)), 0)
        pygame.draw.rect(draw_surf, crack_col, dr, 2, border_radius=2)
        # Progress bar above door
        bar_w = T * 2
        bar_x = dr.x
        bar_y = dr.y - 8
        pygame.draw.rect(draw_surf, (60, 20, 20), (bar_x, bar_y, bar_w, 5))
        pygame.draw.rect(draw_surf, (220, 80, 40),
                         (bar_x, bar_y, int(bar_w * progress), 5))

        # Kick hint
        if player.near_tile(door_tile, radius=3):
            hint = font_sm.render(f"[E] Kick door  ({door_kicks}/{door_kicks_needed})", True, WHITE)
            hbg  = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8), pygame.SRCALPHA)
            hbg.fill((10, 10, 10, 180))
            draw_surf.blit(hbg,  (WIDTH // 2 - hbg.get_width() // 2,  HEIGHT - 44))
            draw_surf.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

    # ── Lightning bolts ───────────────────────────────────────────────────────
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

    # Interact hint (tree, non-god phase)
    if not god_spawned and tree_tile and player.near_tile(tree_tile, radius=3):
        hint = font_sm.render("[E] Interact with the tree", True, WHITE)
        hbg  = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8), pygame.SRCALPHA)
        hbg.fill((10, 10, 10, 180))
        draw_surf.blit(hbg,  (WIDTH // 2 - hbg.get_width() // 2,  HEIGHT - 44))
        draw_surf.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 36)))

    # ── Red flash overlay ─────────────────────────────────────────────────────
    if red_flash_alpha > 0:
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash.fill((200, 0, 0, int(red_flash_alpha)))
        draw_surf.blit(flash, (0, 0))

    surface.blit(draw_surf, (ox, oy))


# =============================================================================
# DIALOG DRAWING
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

    portrait_img = portrait_mikhail if is_mikhail else portrait_raziel
    if portrait_img:
        surface.blit(portrait_img, (portrait_x, portrait_y))
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
# STATES
# =============================================================================
STATE_EXPLORE      = "explore"        # normal exploration
STATE_TREE_HINT    = "tree_hint"      # shake 1/2 narration
STATE_APPLE_DIALOG = "apple_dialog"   # "You feel like you're making a terrible mistake."
STATE_EATING       = "eating"         # flash/shake sequence
STATE_GOD_PHASE    = "god_phase"      # God descends, player must flee & kick door
STATE_GAME_OVER    = "gameover"
STATE_ESCAPED      = "escaped"        # player left map — epilogue
STATE_EPILOGUE     = "epilogue"       # Mikhail/Raziel dialogue
STATE_END          = "end"


# =============================================================================
# MAIN
# =============================================================================
def main():
    walls, wall_set, tree_tile, door_tile, entrance_tiles = build_from_tmx()

    # ── Music ──
    try:
        pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "2. Echoes of the Keep.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    try:
        thunder_sfx = pygame.mixer.Sound(os.path.join(BASE_DIR, "audio", "Hostile_March_BattleTheme.wav"))
        thunder_sfx.set_volume(0.0)   # used as thunder trigger stub; replace with real sfx
    except Exception:
        thunder_sfx = None

    player          = Player()
    god             = God()
    lightning_bolts = []
    shake           = ScreenShake()

    state              = STATE_EXPLORE
    entrance_closed    = False
    gate_open          = False
    god_spawned        = False
    inv_timer          = 0

    tree_shakes        = 0
    apple_on_ground    = False
    apple_pos          = None    # pixel center of apple

    door_kicks         = 0
    door_kicks_needed  = random.randint(DOOR_KICK_MIN, DOOR_KICK_MAX)
    door_kick_cooldown = 0

    red_flash_alpha    = 0
    eating_timer       = 0       # countdown for the eating sequence

    typewriter         = Typewriter()
    dialog_lines       = []      # current simple dialog queue (tree shakes)
    epilogue_index     = 0

    while True:
        clock.tick(60)
        shake.update()

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                # ── Explore: tree & apple interaction ──
                if state == STATE_EXPLORE:
                    if event.key in (pygame.K_e, pygame.K_SPACE):
                        # Tree interaction
                        if tree_tile and player.near_tile(tree_tile, radius=3) and not apple_on_ground:
                            tree_shakes += 1
                            shake.start(20, strength=4)
                            if tree_shakes < TREE_SHAKE_NEEDED:
                                # Nothing falls yet — just a hint
                                pass
                            else:
                                # Apple falls!
                                apple_on_ground = True
                                tx = tree_tile[0] * T + T // 2
                                ty = tree_tile[1] * T + T * 2
                                apple_pos = (tx, ty)

                        # Apple pickup
                        elif apple_on_ground and apple_pos:
                            ax, ay = apple_pos
                            apple_rect = pygame.Rect(ax - 8, ay - 8, 16, 16)
                            if player.rect.colliderect(apple_rect):
                                apple_on_ground = False
                                apple_pos       = None
                                player.has_apple = True
                                # Show the warning dialog
                                typewriter.set_text(
                                    "You feel like you're making a terrible mistake.")
                                state = STATE_APPLE_DIALOG

                        # Door kick (god phase)
                        elif god_spawned and not gate_open and door_tile \
                                and player.near_tile(door_tile, radius=3) \
                                and door_kick_cooldown <= 0:
                            door_kicks += 1
                            door_kick_cooldown = 20
                            shake.start(10, strength=3)
                            if door_kicks >= door_kicks_needed:
                                gate_open = True

                elif state == STATE_APPLE_DIALOG:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            # Player takes a bite — trigger the eating sequence
                            player.has_apple = False
                            eating_timer     = 180   # 3 seconds of chaos
                            red_flash_alpha  = 0
                            shake.start(180, strength=7)
                            state = STATE_EATING
                            try:
                                pygame.mixer.music.fadeout(800)
                            except Exception:
                                pass

                elif state == STATE_GOD_PHASE:
                    if event.key in (pygame.K_e,):
                        if not gate_open and door_tile \
                                and player.near_tile(door_tile, radius=3) \
                                and door_kick_cooldown <= 0:
                            door_kicks += 1
                            door_kick_cooldown = 20
                            shake.start(10, strength=3)
                            if door_kicks >= door_kicks_needed:
                                gate_open = True

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

        # ── Typewriter tick ───────────────────────────────────────────────────
        if state in (STATE_APPLE_DIALOG, STATE_EPILOGUE):
            typewriter.update()

        # ── Eating sequence ───────────────────────────────────────────────────
        if state == STATE_EATING:
            eating_timer -= 1

            # Pulse red flash
            cycle = eating_timer % 30
            if cycle > 15:
                red_flash_alpha = min(180, red_flash_alpha + 14)
            else:
                red_flash_alpha = max(0, red_flash_alpha - 14)

            if eating_timer <= 0:
                # Sequence done — God descends
                red_flash_alpha = 0
                shake.start(0)
                god_spawned = True
                god_spawned = True
                state       = STATE_GOD_PHASE
                try:
                    pygame.mixer.music.load(
                        os.path.join(BASE_DIR, "audio", "Hostile_March_BattleTheme.wav"))
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)
                except Exception:
                    pass

        # ── God phase ─────────────────────────────────────────────────────────
        if state == STATE_GOD_PHASE:
            keys = pygame.key.get_pressed()
            player.move(keys, walls)

            if door_kick_cooldown > 0:
                door_kick_cooldown -= 1
            if inv_timer > 0:
                inv_timer -= 1
            if player.inv_timer > 0:
                player.inv_timer -= 1

            # Close entrance when player moves up
            if not entrance_closed and player.rect.centery < HEIGHT - 6 * T:
                entrance_closed = True

            god.update(player.rect)

            # God smite — instant game over if in range
            if god.in_smite_range(player.rect) and inv_timer <= 0:
                state = STATE_GAME_OVER

            # Lightning bolts
            new_bolts = god.try_spawn_bolts(player.rect)
            lightning_bolts.extend(new_bolts)

            # Update bolts and check hits
            for bolt in lightning_bolts[:]:
                done = bolt.update()
                if bolt.hits(player.rect) and inv_timer <= 0:
                    player.lives -= 1
                    inv_timer         = INVINCIBLE_FRAMES
                    player.inv_timer  = INVINCIBLE_FRAMES
                    shake.start(20, strength=5)
                    if player.lives <= 0:
                        state = STATE_GAME_OVER
                if done:
                    lightning_bolts.remove(bolt)

            # E to kick door
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_e] and not gate_open and door_tile \
                    and player.near_tile(door_tile, radius=3) \
                    and door_kick_cooldown <= 0:
                door_kicks += 1
                door_kick_cooldown = 20
                shake.start(10, strength=3)
                if door_kicks >= door_kicks_needed:
                    gate_open = True

            # Player escapes — top of screen
            if gate_open and player.rect.top <= 0:
                state = STATE_ESCAPED

        # ── Explore phase (before eating) ──────────────────────────────────────
        if state == STATE_EXPLORE:
            keys = pygame.key.get_pressed()
            player.move(keys, walls, restrict_top=True)

            if not entrance_closed and player.rect.centery < HEIGHT - 6 * T:
                entrance_closed = True

        # ── Escaped — epilogue ────────────────────────────────────────────────
        if state == STATE_ESCAPED:
            # Small pause then start epilogue
            try:
                pygame.mixer.music.fadeout(600)
                pygame.mixer.music.load(
                    os.path.join(BASE_DIR, "audio", "2. Echoes of the Keep.mp3"))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
            except Exception:
                pass
            god_spawned    = False
            lightning_bolts = []
            typewriter.set_text(EPILOGUE[0][1])
            epilogue_index = 0
            state          = STATE_EPILOGUE

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_scene(screen, player, god, lightning_bolts,
                   gate_open, entrance_closed,
                   tree_tile, door_tile, door_kicks, door_kicks_needed,
                   apple_on_ground, apple_pos,
                   red_flash_alpha, shake,
                   god_spawned)

        # ── Overlaid UI ───────────────────────────────────────────────────────
        if state == STATE_APPLE_DIALOG:
            draw_simple_dialog(screen,
                ["You feel like you're making a terrible mistake.",
                 "..."],
                [("Enter", "Take a bite anyway")])

        elif state == STATE_EATING:
            # Big divine warning text during eating chaos
            ticks = pygame.time.get_ticks()
            if (ticks // 200) % 2 == 0:
                warn = font_lg.render("!!!", True, (255, 200, 40))
                screen.blit(warn, warn.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        elif state == STATE_GAME_OVER:
            draw_simple_dialog(screen,
                ["The divine presence consumes you.",
                 "There is no escaping divine wrath."],
                [("R", "Try again"), ("Esc", "Quit")])

        elif state == STATE_EPILOGUE:
            speaker, _ = EPILOGUE[epilogue_index]
            draw_angel_dialog(screen, speaker, typewriter)

        elif state == STATE_END:
            draw_simple_dialog(screen,
                ["You escaped Eden.",
                 "But something tells you...",
                 "...the garden will never forget."],
                [("Enter", "Fin.")])

        pygame.display.flip()


if __name__ == "__main__":
    main()