import pygame
import sys
import random
import TheNaga
import pytmx

# --- Init ---
pygame.init()
WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden")
clock = pygame.time.Clock()

# --- Colors ---
BLACK        = (0, 0, 0)
WHITE        = (255, 255, 255)
PLAYER_COLOR = (200, 160, 80)
DIALOG_BG    = (20, 20, 20, 210)
GOLD         = (212, 175, 55)
HUD_BG       = (15, 15, 15)
SHADOW       = (0, 0, 0, 80)

# --- Layout constants ---
MAP_LEFT   = 0
MAP_TOP    = 0
MAP_RIGHT  = WIDTH
MAP_BOTTOM = HEIGHT
MAP_W      = WIDTH
MAP_H      = HEIGHT

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

# --- Fonts ---
font_sm  = pygame.font.Font("C:/Users/Mica/PycharmProjects/TheGardenOfEden/font/PixelifySans-VariableFont_wght.ttf", 16)
font_md  = pygame.font.Font("C:/Users/Mica/PycharmProjects/TheGardenOfEden/font/PixelifySans-VariableFont_wght.ttf", 20)
font_lg  = pygame.font.Font("C:/Users/Mica/PycharmProjects/TheGardenOfEden/font/PixelifySans-VariableFont_wght.ttf", 28)

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
class Player:
    SIZE = 20
    SPEED = 3

    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - self.SIZE // 2,
                                MAP_BOTTOM - 60, self.SIZE, self.SIZE)
        self.has_key = False

    def move(self, keys, bushes):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  self.SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -self.SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  self.SPEED

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

    def draw(self, surface):
        shadow_surf = pygame.Surface((self.SIZE + 6, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect())
        surface.blit(shadow_surf, (self.rect.x - 3, self.rect.bottom - 4))
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect, border_radius=5)
        pygame.draw.circle(surface, (210, 170, 120),
                           (self.rect.centerx, self.rect.top + 5), 7)
        if self.has_key:
            surface.blit(key_img, (self.rect.centerx - 8, self.rect.top - 20))


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
    bushes = get_bush_rects()
    random.choice(bushes)["has_key"] = True  # hide key in random bush
    player    = Player()
    gate_open = False
    state     = STATE_EXPLORE

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

        if state == STATE_EXPLORE:
            keys = pygame.key.get_pressed()
            player.move(keys, [])  # no collision with bushes

            if not player.has_key:
                if player.check_key_pickup(bushes):
                    state = STATE_PICKUP

            elif gate_open:
                if player.rect.top < GATE_Y:
                    fade_to_black()
                    TheNaga.main()
                    return

            elif player.near_gate():
                state = STATE_PROMPT if player.has_key else STATE_LOCKED

        draw_map(screen, player, gate_open)
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

        pygame.display.flip()


if __name__ == "__main__":
    main()