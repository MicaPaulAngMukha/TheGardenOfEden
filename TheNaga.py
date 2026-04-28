import os.path

import pygame
import sys
import collections
import random
import pytmx
import os
import TheTwins

pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden – The Naga's Lair")
clock  = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pygame.mixer.init()

tmx_data = pytmx.load_pygame("TheNagaMap.tmx")

heart_full = pygame.image.load("LifeHeart.png").convert_alpha()
heart_empty = pygame.image.load("LifeHeartLoss.png").convert_alpha()

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

# ─────────────────────────────────────────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────────────────────────────────────────
PLAYER_SIZE = 14
MAX_LIVES   = 3

class Player:
    SPEED = 6

    def __init__(self):
        self.lives = MAX_LIVES
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = PLAYER_SPAWN

    def move(self, keys, solid_rects):
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

    def near_lever(self, lever_tile):
        if lever_tile is None:
            return False
        interact_box = tile_rect(*lever_tile).inflate(T * 3, T * 3)
        return interact_box.colliderect(self.rect)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COL, self.rect, border_radius=3)
        pygame.draw.circle(surface, PLAYER_HEAD,
                           (self.rect.centerx, self.rect.top + 4), 5)

# ─────────────────────────────────────────────────────────────────────────────
# NAGA
# ─────────────────────────────────────────────────────────────────────────────
SEG_SIZE    = 16
SEG_SPACING = 5
NAGA_SPEED  = 5
HISTORY_LEN = SEG_SPACING * 3 + 10

class Naga:
    N_SEGS = 3

    def __init__(self, spawn_tile):
        cx = spawn_tile[0] * T + T // 2
        cy = spawn_tile[1] * T + T // 2
        self.history = collections.deque(
            [(cx - i * SEG_SPACING, cy) for i in range(HISTORY_LEN)],
            maxlen=HISTORY_LEN
        )

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

        path = self.find_path((naga_c, naga_r), (play_c, play_r),
                              walls, green_walls, red_walls, green_active, red_active)

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
        dist   = max(0.001, (dx**2 + dy**2)**0.5)
        step   = min(NAGA_SPEED, dist)

        if dist > 0.1:
            self.history.appendleft((hx + (dx/dist)*step, hy + (dy/dist)*step))
        else:
            self.history.appendleft((hx, hy))

    def segments(self):
        return [self.history[min(i * SEG_SPACING, len(self.history)-1)]
                for i in range(self.N_SEGS)]

    def head_rect(self):
        hx, hy = self.history[0]
        return pygame.Rect(hx - SEG_SIZE//2, hy - SEG_SIZE//2, SEG_SIZE, SEG_SIZE)

    def draw(self, surface):
        for i, (sx, sy) in reversed(list(enumerate(self.segments()))):
            col = NAGA_HEAD if i == 0 else NAGA_BODY
            r   = max(3, SEG_SIZE//2 - i)
            pygame.draw.circle(surface, col, (int(sx), int(sy)), r)
            if i == 0:
                pygame.draw.circle(surface, NAGA_EYE, (int(sx)-3, int(sy)-2), 2)
                pygame.draw.circle(surface, NAGA_EYE, (int(sx)+3, int(sy)-2), 2)
                pygame.draw.circle(surface, BLACK,    (int(sx)-3, int(sy)-2), 1)
                pygame.draw.circle(surface, BLACK,    (int(sx)+3, int(sy)-2), 1)

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

# ─────────────────────────────────────────────────────────────────────────────
# STATES / MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────
STATE_PLAY      = "play"
STATE_HIT       = "hit"
STATE_GAME_OVER = "gameover"
STATE_WIN       = "win"
STATE_LEVER_G   = "lever_g"
STATE_LEVER_R   = "lever_r"

INVINCIBLE_FRAMES = 90

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

            if naga_freeze_timer > 0:
                naga_freeze_timer -= 1
            else:
                naga.update(player.rect, walls, green_walls, red_walls, green_active, red_active)

            if inv_timer <= 0:
                if naga.head_rect().colliderect(player.rect):
                    player.lives -= 1
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

        pygame.display.flip()


if __name__ == "__main__":
    main()