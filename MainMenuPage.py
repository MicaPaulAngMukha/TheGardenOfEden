import os.path

import pygame
import sys
import Start
import os

# --- Init ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Garden of Eden")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE_DIR, "font", "PixelifySans-VariableFont_wght.ttf")

background = pygame.image.load(os.path.join(BASE_DIR, "GardenBG.jpg")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

pygame.mixer.init()
pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "GoldenBrown_ChipTune.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# --- Colors ---
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
GOLD        = (255, 251, 243)
GOLD_HOVER  = (255, 227, 161)
DARK_GOLD   = (222, 143, 21)
GRAY        = (211, 199, 212)
GRAY_TEXT   = (211, 199, 212)

# --- Fonts ---
title_font  = pygame.font.Font(FONT, 72)
menu_font   = pygame.font.Font(FONT, 36)

# --- Button config ---
BUTTON_W, BUTTON_H = 260, 56
buttons = [
    {"label": "Start",      "id": "start",      "enabled": True},
    {"label": "Characters", "id": "characters", "enabled": False},  # Unclickable
    {"label": "Exit",       "id": "exit",       "enabled": True},
]

def get_button_rects():
    rects = []
    total_h = len(buttons) * BUTTON_H + (len(buttons) - 1) * 20
    start_y = HEIGHT // 2 - total_h // 2 + 30
    for i in range(len(buttons)):
        x = WIDTH // 2 - BUTTON_W // 2
        y = start_y + i * (BUTTON_H + 20)
        rects.append(pygame.Rect(x, y, BUTTON_W, BUTTON_H))
    return rects

def draw_menu(mouse_pos):
    screen.blit(background, (0, 0))

    # --- Decorative horizontal rule ---
    rule_y = HEIGHT // 2 - 130
    pygame.draw.line(screen, DARK_GOLD, (WIDTH // 2 - 200, rule_y), (WIDTH // 2 + 200, rule_y), 1)

    # --- Title ---
    title_surf = title_font.render("Garden of Eden", True, GOLD)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(title_surf, title_rect)

    # --- Decorative rule below title ---
    pygame.draw.line(screen, DARK_GOLD, (WIDTH // 2 - 200, rule_y + 10), (WIDTH // 2 + 200, rule_y + 10), 1)

    # --- Buttons ---
    rects = get_button_rects()
    for i, (btn, rect) in enumerate(zip(buttons, rects)):
        hovered   = rect.collidepoint(mouse_pos) and btn["enabled"]
        enabled   = btn["enabled"]

        # Choose colors
        if not enabled:
            border_col = GRAY
            text_col   = GRAY_TEXT
            fill_col   = None
        elif hovered:
            border_col = GOLD_HOVER
            text_col   = BLACK
            fill_col   = GOLD_HOVER
        else:
            border_col = GOLD
            text_col   = GOLD
            fill_col   = None

        # Fill on hover
        if fill_col:
            pygame.draw.rect(screen, fill_col, rect, border_radius=4)

        # Border
        pygame.draw.rect(screen, border_col, rect, width=2, border_radius=4)

        # Label
        label_surf = menu_font.render(btn["label"], True, text_col)
        label_rect = label_surf.get_rect(center=rect.center)
        screen.blit(label_surf, label_rect)

        # "Soon" tag for disabled
        if not enabled:
            soon_font = pygame.font.SysFont("Georgia", 13, italic=True)
            soon_surf = soon_font.render("coming soon", True, GRAY_TEXT)
            soon_rect = soon_surf.get_rect(midleft=(rect.right + 10, rect.centery))
            screen.blit(soon_surf, soon_rect)

    pygame.display.flip()

# --- Main Loop ---
def main():
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                rects = get_button_rects()
                for btn, rect in zip(buttons, rects):
                    if rect.collidepoint(event.pos) and btn["enabled"]:
                        if btn["id"] == "exit":
                            pygame.quit()
                            sys.exit()
                        elif btn["id"] == "start":
                             Start.main()
                             sys.exit()


        draw_menu(mouse_pos)
        clock.tick(60)

if __name__ == "__main__":
    main()