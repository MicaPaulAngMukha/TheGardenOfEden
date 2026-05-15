import pygame
import sys
import random
import TheNaga
import pytmx
import os

# --- Init ---
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pygame.mixer.init()

# --- Colors ---
BLACK        = (0, 0, 0)
WHITE        = (255, 255, 255)
PLAYER_COLOR = (200, 160, 80)
DIALOG_BG    = (20, 20, 20, 210)
GOLD         = (212, 175, 55)
HUD_BG       = (15, 15, 15)
SHADOW       = (0, 0, 0, 80)

ANGEL_SIZE          = 20
ANGEL_TRIGGER_DIST  = 70
MIKHAIL_CHASE_SPEED = 3
ANGEL_PUSH_TILES    = 2
ANGEL_PUSH_TILES_3  = 4
TYPEWRITER_SPEED    = 2

MIKHAIL_COLOR  = (220, 200, 120)
MIKHAIL_HEAD   = (240, 220, 160)
RAZIEL_COLOR   = (160, 180, 220)
RAZIEL_HEAD    = (190, 210, 240)
MIKHAIL_BORDER = (220, 190, 80)
RAZIEL_BORDER  = (160, 200, 240)
DIALOG_W      = 700
DIALOG_H      = 180
PORTRAIT_SIZE = 140

DIALOGS = {
    "mikhail_1": [
        ("Mikhail", "Halt!"),
        ("Mikhail", "No human is allowed within Eden."),
        ("Mikhail", "Specially not the spawn of Adam and Eva."),
    ],
    "raziel_before_mikhail": [
        ("Raziel", "Oh.. a human."),
        ("Raziel", "Haven't seen one of you in a while."),
    ],
    "raziel_after_mikhail": [
        ("Raziel", "A human. Haven't seen any of you in a while."),
        ("Raziel", "It seems you haven't changed. Still as curious as your father and mother."),
    ],
    "mikhail_2": [
        ("Mikhail", "I'm warning you."),
        ("Mikhail", "Leave before you experience the wrath of the divine."),
        ("Mikhail", "There is nothing left for you in Eden."),
    ],
    "raziel_after_mikhail_2": [
        ("Raziel", "Eden's gates are locked from outsiders."),
        ("Raziel", "Frankly, even us. We lost the key long ago."),
        ("Raziel", "I think I dropped it somewhere."),
        ("Raziel", "Well, it's not like you'd get in anyways. Not with Mikhail around."),
    ],
    "mikhail_3": [
        ("Mikhail", "Enough!"),
        ("Mikhail", "Obviously, simple words are not enough to turn you away."),
    ],
    "raziel_roaming": [
        ("Raziel", "Don't mind me."),
        ("Raziel", "I'm just looking for something."),
        ("Raziel", "It should be yourself that you're worried about."),
    ],
    "raziel_during_chase": [
        ("Raziel", "I warned you."),
        ("Raziel", "Good luck though."),
    ],
    "gate_unlock": [
        ("Mikhail", "ARGHH!"),
        ("Raziel", "Ah.. They found the key."),
        ("Mikhail", "Why weren't you guarding the gates, Raziel!?"),
        ("Raziel", "I was looking for the key."),
        ("Mikhail", "And they found it!"),
        ("Raziel", "Relax, Mikey."),
        ("Raziel", "It's not like they can get through Eden."),
        ("Raziel", "It's been years since someone's been in there. And honestly, at this point..."),
        ("Raziel", "... Who knows what's lurking in there."),
        ("Raziel", "There are worse things than an angel's wrath. Don't get your feathers in a twist."),
    ],
}

STATE_ANGEL_DIALOG  = "angel_dialog"
STATE_GATE_DIALOG = "gate_dialog"

# --- Layout constants ---
MAP_LEFT   = 0
MAP_TOP    = 0
MAP_RIGHT  = WIDTH
MAP_BOTTOM = HEIGHT
MAP_W      = WIDTH
MAP_H      = HEIGHT

T = 13   # tile size in pixels (13)

TOP_WALL_H = 100
GATE_Y     = MAP_TOP + TOP_WALL_H

PATH_W     = 160
PATH_X     = WIDTH // 2 - PATH_W // 2

GATE_W     = 80
GATE_H     = 24
GATE_X     = WIDTH // 2 - GATE_W // 2
GATE_RECT  = pygame.Rect(GATE_X, GATE_Y - GATE_H // 2, GATE_W, GATE_H)

key_img = pygame.image.load("Key.png").convert_alpha()
key_img = pygame.transform.scale(key_img, (16, 16))

font = os.path.join(BASE_DIR, "font", "PixelifySans-VariableFont_wght.ttf")

# --- Fonts ---
font_sm  = pygame.font.Font(font, 16)
font_md  = pygame.font.Font(font, 20)
font_lg  = pygame.font.Font(font, 28)

# --- Load portraits once ---
try:
    portrait_mikhail = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Mikhail", "mikhail.png")).convert_alpha(),
        (PORTRAIT_SIZE, PORTRAIT_SIZE))
except:
    portrait_mikhail = None

try:
    portrait_raziel = pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Raziel", "raziel.png")).convert_alpha(),
        (PORTRAIT_SIZE, PORTRAIT_SIZE))
except:
    portrait_raziel = None

tmx_data = pytmx.load_pygame("StartMap.tmx")
MAP_TW   = tmx_data.tilewidth   # 13
MAP_TH   = tmx_data.tileheight  # 13
MAP_PW   = tmx_data.width  * MAP_TW   # 61*13 = 793
MAP_PH   = tmx_data.height * MAP_TH   # 50*13 = 650

def fade_to_black():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)


# --- Player ---
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

class Player:
    SIZE = 20
    SPEED = 3

    def __init__(self):
        self.lives = 3
        self.rect = pygame.Rect(WIDTH // 2 - self.SIZE // 2,
                                MAP_BOTTOM - 60, self.SIZE, self.SIZE)
        self.has_key = False
        self.sprites = PlayerSprites(scale=1)
        self._moving = False

    def move(self, keys, bushes):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  self.SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -self.SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  self.SPEED

        self._moving = (dx != 0 or dy != 0)

        # Update direction and animation
        if dx != 0 or dy != 0:
            if abs(dx) > abs(dy):
                self.sprites.set_anim("run", "right" if dx > 0 else "left")
            else:
                self.sprites.set_anim("run", "down" if dy > 0 else "up")
        else:
            self.sprites.set_anim("idle")

        self.rect.x += dx
        self._clamp()
        for b in bushes:
            if self.rect.colliderect(b["rect"]):
                if dx > 0: self.rect.right  = b["rect"].left
                if dx < 0: self.rect.left   = b["rect"].right

        self.rect.y += dy
        self._clamp()
        for b in bushes:
            if self.rect.colliderect(b["rect"]):
                if dy > 0: self.rect.bottom = b["rect"].top
                if dy < 1: self.rect.top    = b["rect"].bottom

        if not self.has_key:
            if self.rect.top < GATE_Y + 5:
                self.rect.top = GATE_Y + 5

    def _clamp(self):
        self.rect.clamp_ip(pygame.Rect(MAP_LEFT, MAP_TOP, MAP_W, MAP_H))

    def check_key_pickup(self, bushes):
        for b in bushes:
            if b["has_key"] and self.rect.inflate(10, 10).colliderect(b["rect"]):
                b["has_key"] = False
                self.has_key = True
                return True
        return False

    def near_gate(self):
        trigger = GATE_RECT.inflate(60, 50)
        return trigger.collidepoint(self.rect.centerx, self.rect.centery)

    def trigger_hurt(self):
        self.sprites.show_hurt()

    def draw(self, surface):
        self.sprites.update()
        frame = self.sprites.get_frame()
        # Centre sprite on the player rect
        draw_x = self.rect.centerx - frame.get_width() // 2
        draw_y = self.rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))
        if self.has_key:
            surface.blit(key_img, (self.rect.centerx - 8, self.rect.top - 20))

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


class Angel:
    def __init__(self, pos, color, head_color):
        self.rect = pygame.Rect(pos[0], pos[1], 14, 26)
        self.color      = color
        self.head_color = head_color

    def draw(self, surface):
        cx = self.rect.centerx
        cy = self.rect.centery

        # Wings (spread out on sides)
        pygame.draw.ellipse(surface, self.color,
                            (cx - 22, cy - 4, 16, 10))  # left wing
        pygame.draw.ellipse(surface, self.color,
                            (cx + 6, cy - 4, 16, 10))  # right wing

        # Body (taller, narrower)
        pygame.draw.rect(surface, self.color,
                         (cx - 7, cy - 6, 14, 20), border_radius=4)

        # Head
        pygame.draw.circle(surface, self.head_color, (cx, cy - 12), 8)

        # Halo
        pygame.draw.ellipse(surface, (255, 245, 150),
                            (cx - 9, cy - 22, 18, 5), 2)

        # Glow aura
        glow = pygame.Surface((52, 52), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*self.color, 40), glow.get_rect())
        surface.blit(glow, (cx - 26, cy - 20))

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


class MikhailSprites:
    # Row order in your sheets — adjust if wrong
    ROWS = {"up": 0, "right": 3, "down": 2, "left": 1}

    def __init__(self, scale=2):
        base = os.path.join(BASE_DIR, "Sprites", "Mikhail")

        def load_all(filename, frames_per_row):
            path = os.path.join(base, filename)
            return {
                dir: SpriteSheet(path, 64, 64, frames_per_row, row=row, scale=scale)
                for dir, row in self.ROWS.items()
            }

        self.anims = {
            "idle":   load_all("mikhail_idle.png",   2),
            "walk":   load_all("mikhail_walk.png",   9),
            "attack": load_all("mikhail_attack.png", 6),
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
        frame = self.anims[self.current_anim][self.current_dir].current()
        # Centre the sprite on the rect
        draw_x = rect.centerx - frame.get_width() // 2
        draw_y = rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))

class RazielSprites:
    ROWS = {"up": 0, "right": 3, "down": 2, "left": 1}  # adjust if needed

    def __init__(self, scale=1):
        base = os.path.join(BASE_DIR, "Sprites", "Raziel")

        def load_all(filename, frames_per_row):
            path = os.path.join(base, filename)
            return {
                dir: SpriteSheet(path, 64, 64, frames_per_row, row=row, scale=scale)
                for dir, row in self.ROWS.items()
            }

        self.anims = {
            "idle":    load_all("raziel_idle.png",    2),
            "walk":    load_all("raziel_walk.png",    9),
            "looking": load_all("raziel_looking.png", 8),
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
        frame = self.anims[self.current_anim][self.current_dir].current()
        draw_x = rect.centerx - frame.get_width() // 2
        draw_y = rect.centery - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))

class Mikhail(Angel):
    def __init__(self):
            pos = (PATH_X - 36, GATE_Y + 8)
            super().__init__(pos, MIKHAIL_COLOR, MIKHAIL_HEAD)
            self.chasing = False
            self.approach = 0
            self.sprites = MikhailSprites(scale=1)  # scale=2 doubles the size

    def near_player(self, player_rect):
        dx = abs(self.rect.centerx - player_rect.centerx)
        dy = abs(self.rect.centery - player_rect.centery)
        return dx < ANGEL_TRIGGER_DIST and dy < ANGEL_TRIGGER_DIST

    def chase(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = max(1, (dx**2 + dy**2)**0.5)
        self.rect.x += int((dx / dist) * MIKHAIL_CHASE_SPEED)
        self.rect.y += int((dy / dist) * MIKHAIL_CHASE_SPEED)

        # Set walk direction
        if abs(dx) > abs(dy):
            self.sprites.set_anim("walk", "right" if dx > 0 else "left")
        else:
            self.sprites.set_anim("walk", "down" if dy > 0 else "up")

    def draw(self, surface):
        if self.chasing:
            glow = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 80, 80, 90), glow.get_rect())
            surface.blit(glow, (self.rect.x - 20, self.rect.y - 20))
        self.sprites.update()
        self.sprites.draw(surface, self.rect)


class Raziel(Angel):
    ROAM_SPEED = 1.2

    def __init__(self):
        pos = (PATH_X + PATH_W + 14, GATE_Y + 8)
        super().__init__(pos, RAZIEL_COLOR, RAZIEL_HEAD)
        self.spoken_count = 0
        self.roaming      = False
        self.roam_target  = None
        self.roam_timer   = 0
        self.is_paused    = False   # ← track when he's paused looking
        self.sprites      = RazielSprites(scale=1)

    def start_roaming(self):
        self.roaming = True
        self._pick_target()

    def _pick_target(self):
        tx = random.randint(MAP_LEFT + 20, MAP_RIGHT - 20)
        ty = random.randint(GATE_Y + 20, MAP_BOTTOM - 20)
        self.roam_target = (tx, ty)
        self.roam_timer  = random.randint(120, 300)

    def update(self):
        if not self.roaming or self.roam_target is None:
            self.sprites.set_anim("idle")
            return

        self.roam_timer -= 1
        if self.roam_timer <= 0:
            # Pause and look around before picking new target
            if not self.is_paused:
                self.is_paused = True
                self.roam_timer = 60   # look for 1 second
                self.sprites.set_anim("looking")
            else:
                self.is_paused = False
                self._pick_target()
            return

        if self.is_paused:
            self.sprites.set_anim("looking")
            return

        tx, ty = self.roam_target
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = max(1, (dx**2 + dy**2)**0.5)
        if dist < 4:
            self._pick_target()
            return

        self.rect.x += int((dx / dist) * self.ROAM_SPEED)
        self.rect.y += int((dy / dist) * self.ROAM_SPEED)

        # Set walk direction
        if abs(dx) > abs(dy):
            self.sprites.set_anim("walk", "right" if dx > 0 else "left")
        else:
            self.sprites.set_anim("walk", "down" if dy > 0 else "up")

    def near_player(self, player_rect):
        dx = abs(self.rect.centerx - player_rect.centerx)
        dy = abs(self.rect.centery - player_rect.centery)
        return dx < ANGEL_TRIGGER_DIST and dy < ANGEL_TRIGGER_DIST

    def draw(self, surface):
        self.sprites.update()
        self.sprites.draw(surface, self.rect)


def compute_push(player_rect, from_rect, tiles):
    dx = player_rect.centerx - from_rect.centerx
    dy = player_rect.centery - from_rect.centery
    dist   = max(1, (dx**2 + dy**2)**0.5)
    frames = 18
    vx = (dx / dist) * ((tiles * T) / frames)
    vy = (dy / dist) * ((tiles * T) / frames)
    return vx, vy, frames


def draw_angel_dialog(surface, speaker, typewriter):
    is_mikhail = (speaker == "Mikhail")
    border_col = MIKHAIL_BORDER if is_mikhail else RAZIEL_BORDER

    box_x = WIDTH  // 2 - DIALOG_W // 2
    box_y = HEIGHT - DIALOG_H - 10

    # Background
    ov = pygame.Surface((DIALOG_W, DIALOG_H), pygame.SRCALPHA)
    ov.fill((10, 10, 10, 230))
    surface.blit(ov, (box_x, box_y))
    pygame.draw.rect(surface, border_col,
                     (box_x, box_y, DIALOG_W, DIALOG_H), 3, border_radius=8)

    # Portrait — sits flush on the left, slightly taller than the box
    # Portrait — inside the box on the left
    portrait_x = box_x + 10
    portrait_y = box_y + DIALOG_H // 2 - PORTRAIT_SIZE // 2
    pygame.draw.rect(surface, (20, 20, 20),
                     (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    pygame.draw.rect(surface, border_col,
                     (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE), 3)

    # Load and draw portrait image
    portrait_img = portrait_mikhail if is_mikhail else portrait_raziel
    if portrait_img:
        surface.blit(portrait_img, (portrait_x, portrait_y))
    else:
        ph = font_md.render("?", True, (70, 70, 70))
        surface.blit(ph, ph.get_rect(center=(portrait_x + PORTRAIT_SIZE // 2,
                                             portrait_y + PORTRAIT_SIZE // 2)))

    # Speaker name
    name_surf = font_md.render(speaker, True, border_col)
    surface.blit(name_surf, (portrait_x, portrait_y - 22))

    # Text area
    text_x = portrait_x + PORTRAIT_SIZE + 18
    max_w  = DIALOG_W - PORTRAIT_SIZE - 30
    current = typewriter.current

    words = current.split(" ")
    lines = []
    line  = ""
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

    # Blinking prompt
    ticks = pygame.time.get_ticks()
    if typewriter.done:
        if (ticks // 500) % 2 == 0:
            prompt = font_sm.render("▶ Enter", True, (160, 160, 160))
            surface.blit(prompt, (box_x + DIALOG_W - prompt.get_width() - 12,
                                   box_y + DIALOG_H - prompt.get_height() - 8))
    else:
        prompt = font_sm.render("▶ Skip", True, (100, 100, 100))
        surface.blit(prompt, (box_x + DIALOG_W - prompt.get_width() - 12,
                               box_y + DIALOG_H - prompt.get_height() - 8))


# --- Draw functions ---
def draw_map(surface, player, gate_open):
    for layer in tmx_data.layers:        # ← changed from visible_layers to layers
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        if layer.name in ("DoorOpen1", "DoorOpen2") and not gate_open:
            continue
        if layer.name in ("Door", "door2") and gate_open:
            continue
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(tile, (x * MAP_TW, y * MAP_TH))


def draw_dialog(surface, lines, options=None):
    box_w, box_h = 460, 110 + (30 * len(options) if options else 0)
    box_x = WIDTH // 2 - box_w // 2
    box_y = HEIGHT // 2 - box_h // 2 + 60

    overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    overlay.fill((10, 10, 10, 220))
    surface.blit(overlay, (box_x, box_y))
    pygame.draw.rect(surface, GOLD, (box_x, box_y, box_w, box_h), 2, border_radius=6)

    y_off = box_y + 18
    for line in lines:
        txt = font_md.render(line, True, WHITE)
        surface.blit(txt, (box_x + 20, y_off))
        y_off += 28

    if options:
        y_off += 8
        for i, (key, label) in enumerate(options):
            opt_txt = font_md.render(f"[{key}]  {label}", True, GOLD)
            surface.blit(opt_txt, (box_x + 30, y_off))
            y_off += 30


# --- States ---
STATE_EXPLORE  = "explore"
STATE_LOCKED   = "locked"
STATE_PROMPT   = "prompt"
STATE_UNLOCKED = "unlocked"
STATE_PICKUP   = "pickup"
STATE_HIT      = "hit"
STATE_GAME_OVER = "gameover"

def get_bush_rects():
    """Scan Tile Layer 2 and return a rect for every bush tile found."""
    bushes = []
    for layer in tmx_data.visible_layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        if layer.name != "Tile Layer 2":
            continue
        for x, y, gid in layer:
            if gid != 0:
                r = pygame.Rect(x * MAP_TW, y * MAP_TH, MAP_TW, MAP_TH)
                bushes.append({"rect": r, "has_key": False})
    return bushes

def main():
    pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "2. Echoes of the Keep.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    bushes = get_bush_rects()
    random.choice(bushes)["has_key"] = True  # hide key in random bush
    player    = Player()
    gate_open = False
    state     = STATE_EXPLORE

    mikhail = Mikhail()

    # When not chasing, play idle
    if not mikhail.chasing:
        mikhail.sprites.set_anim("idle")

    raziel = Raziel()
    typewriter = Typewriter()
    angel_dialog = []
    dialog_index = 0
    push_vx = push_vy = 0
    push_timer = 0
    chase_paused = False
    raziel_cooldown = 0

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == STATE_LOCKED:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = STATE_EXPLORE

                elif state == STATE_PROMPT:
                    if event.key == pygame.K_y:
                        gate_open = True
                        state     = STATE_UNLOCKED
                    elif event.key == pygame.K_n:
                        state = STATE_EXPLORE

                elif state == STATE_UNLOCKED:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = STATE_EXPLORE

                elif state == STATE_PICKUP:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = STATE_EXPLORE


                elif state == STATE_ANGEL_DIALOG:

                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):

                        if not typewriter.done:

                            typewriter.skip()

                        else:

                            dialog_index += 1

                            if dialog_index < len(angel_dialog):

                                typewriter.set_text(angel_dialog[dialog_index][1])

                            else:

                                chase_paused = False

                                if mikhail.approach == 1 or mikhail.approach == 2:

                                    push_vx, push_vy, push_timer = compute_push(

                                        player.rect, mikhail.rect, ANGEL_PUSH_TILES)

                                    state = STATE_EXPLORE


                                elif mikhail.approach >= 3:

                                    push_vx, push_vy, push_timer = compute_push(

                                        player.rect, mikhail.rect, ANGEL_PUSH_TILES_3)

                                    mikhail.chasing = True

                                    pygame.mixer.music.fadeout(1000)

                                    pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "12. March of Iron.mp3"))

                                    pygame.mixer.music.set_volume(0.7)

                                    pygame.mixer.music.play(-1)

                                    state = STATE_EXPLORE

                                else:

                                    speaker, _ = angel_dialog[0]

                                    if speaker == "Raziel":
                                        push_vx, push_vy, push_timer = compute_push(

                                            player.rect, raziel.rect, ANGEL_PUSH_TILES)

                                        raziel_cooldown = 240

                                    state = STATE_EXPLORE

                elif state == STATE_GATE_DIALOG:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if not typewriter.done:
                            typewriter.skip()
                        else:
                            dialog_index += 1
                            if dialog_index < len(angel_dialog):
                                typewriter.set_text(angel_dialog[dialog_index][1])
                            else:
                                pygame.mixer.music.fadeout(500)
                                fade_to_black()
                                TheNaga.main()
                                pygame.quit()


                elif state == STATE_HIT:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        player.rect.center = (WIDTH // 2, MAP_BOTTOM - 60)
                        player.lives = max(0, player.lives)
                        state = STATE_EXPLORE

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        main()
                        return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit();
                        sys.exit()

        if state in (STATE_ANGEL_DIALOG, STATE_GATE_DIALOG):
            typewriter.update()

        if state == STATE_EXPLORE:
            keys = pygame.key.get_pressed()
            player.move(keys, [])

            # Push animation
            if push_timer > 0:
                push_timer -= 1
                player.rect.x += int(push_vx)
                player.rect.y += int(push_vy)
                player.rect.clamp_ip(pygame.Rect(MAP_LEFT, MAP_TOP, MAP_W, MAP_H))

            # Raziel roam update
            raziel.update()

            # Cooldown tick
            if raziel_cooldown > 0:
                raziel_cooldown -= 1

            # Mikhail chasing
            if mikhail.chasing and not chase_paused:
                mikhail.chase(player.rect)
                if mikhail.rect.colliderect(player.rect):
                    player.lives -= 1
                    player.trigger_hurt()  # ← add this
                    push_vx, push_vy, push_timer = compute_push(
                        player.rect, mikhail.rect, 2)
                    state = STATE_GAME_OVER if player.lives <= 0 else STATE_HIT

            # Raziel during chase
            elif mikhail.chasing and raziel.near_player(player.rect) \
                    and raziel.spoken_count < 3:
                angel_dialog = DIALOGS["raziel_during_chase"]
                raziel.spoken_count = 3
                dialog_index = 0
                typewriter.set_text(angel_dialog[0][1])
                chase_paused = True
                state = STATE_ANGEL_DIALOG

            # Mikhail approach
            elif not mikhail.chasing and push_timer == 0 \
                    and mikhail.near_player(player.rect):
                mikhail.approach += 1
                if mikhail.approach == 1:
                    angel_dialog = DIALOGS["mikhail_1"]
                elif mikhail.approach == 2:
                    angel_dialog = DIALOGS["mikhail_2"]
                else:
                    angel_dialog = DIALOGS["mikhail_3"]
                dialog_index = 0
                typewriter.set_text(angel_dialog[0][1])
                state = STATE_ANGEL_DIALOG

            # Raziel roaming interaction
            elif raziel.roaming and raziel.near_player(player.rect) \
                    and raziel.spoken_count == 2 and raziel_cooldown == 0:
                angel_dialog = DIALOGS["raziel_roaming"]
                raziel.spoken_count = 3  # ← prevent re-trigger
                raziel_cooldown = 300
                dialog_index = 0
                typewriter.set_text(angel_dialog[0][1])
                state = STATE_ANGEL_DIALOG

            # Raziel stationary
            elif not raziel.roaming and raziel.near_player(player.rect) \
                    and raziel_cooldown == 0:
                if raziel.spoken_count == 0 and mikhail.approach == 0:
                    angel_dialog = DIALOGS["raziel_before_mikhail"]
                    raziel.spoken_count = 1
                    raziel_cooldown = 300
                    dialog_index = 0
                    typewriter.set_text(angel_dialog[0][1])
                    state = STATE_ANGEL_DIALOG
                elif raziel.spoken_count == 0 and mikhail.approach >= 1:
                    angel_dialog = DIALOGS["raziel_after_mikhail"]
                    raziel.spoken_count = 1
                    dialog_index = 0
                    typewriter.set_text(angel_dialog[0][1])
                    state = STATE_ANGEL_DIALOG
                elif raziel.spoken_count == 1 and mikhail.approach >= 2:
                    angel_dialog = DIALOGS["raziel_after_mikhail_2"]
                    raziel.spoken_count = 2
                    dialog_index = 0
                    typewriter.set_text(angel_dialog[0][1])
                    raziel.start_roaming()
                    state = STATE_ANGEL_DIALOG

            # Key pickup and gate logic
            if not player.has_key:
                if player.check_key_pickup(bushes):
                    state = STATE_PICKUP


            elif gate_open:

                if player.rect.top < GATE_Y:
                    angel_dialog = DIALOGS["gate_unlock"]

                    dialog_index = 0

                    typewriter.set_text(angel_dialog[0][1])

                    gate_open = False

                    state = STATE_GATE_DIALOG

            elif player.near_gate():
                state = STATE_PROMPT if player.has_key else STATE_LOCKED

        draw_map(screen, player, gate_open)
        mikhail.draw(screen)
        raziel.draw(screen)
        player.draw(screen)

        if state == STATE_LOCKED:
            draw_dialog(screen,
                ["The gate is locked...",
                 "You need a key to pass."],
                [("Enter", "OK")])
        elif state == STATE_PROMPT:
            draw_dialog(screen,
                ["You have the key.",
                 "Unlock the gate?"],
                [("Y", "Yes, unlock it"),
                 ("N", "Not yet")])
        elif state == STATE_UNLOCKED:
            draw_dialog(screen,
                ["*click*",
                 "The gate swings open."],
                [("Enter", "Continue")])
        elif state == STATE_PICKUP:
            draw_dialog(screen,
                ["You found a hidden key!",
                 "It might open something nearby..."],
                [("Enter", "OK")])

        if state == STATE_HIT:
            draw_dialog(screen,
                        [f"Mikhail strikes you down!  Lives: {player.lives}",
                         "You stumble back..."],
                        [("Enter", "Continue")])

        elif state == STATE_GAME_OVER:
            draw_dialog(screen,
                        ["You have been cast out.",
                         "Mikhail stands triumphant."],
                        [("R", "Try again"), ("Esc", "Quit")])

        if state in (STATE_ANGEL_DIALOG, STATE_GATE_DIALOG) and dialog_index < len(angel_dialog):
            speaker, _ = angel_dialog[dialog_index]
            draw_angel_dialog(screen, speaker, typewriter)

        pygame.display.flip()

def god_epilogue():
    """
    Final epilogue — Mikhail and Raziel react after player escapes Eden.
    Called from TheNaga.god_main when player exits through the top.
    """
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

    mikhail = Mikhail()
    raziel  = Raziel()
    mikhail.sprites.set_anim("idle")
    raziel.sprites.set_anim("idle")

    typewriter     = Typewriter()
    epilogue_index = 0
    typewriter.set_text(EPILOGUE[0][1])

    try:
        pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "2. Echoes of the Keep.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    STATE_DIALOG = "dialog"
    STATE_END    = "end"
    state        = STATE_DIALOG

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == STATE_DIALOG:
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

        typewriter.update()
        raziel.update()

        draw_map(screen, None, True)   # gate open — player just ran through
        mikhail.draw(screen)
        raziel.draw(screen)

        if state == STATE_DIALOG and epilogue_index < len(EPILOGUE):
            speaker = EPILOGUE[epilogue_index][0]
            draw_angel_dialog(screen, speaker, typewriter)

        elif state == STATE_END:
            draw_dialog(screen,
                ["You escaped Eden.",
                 "But something tells you...",
                 "...the garden will never forget."],
                [("Enter", "Fin.")])

        pygame.display.flip()

if __name__ == "__main__":
    main()