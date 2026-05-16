import os
import pygame
import sys
from display_scaler import DisplayScaler

# --- Init ---
pygame.init()
WIDTH, HEIGHT = 793, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Garden of Eden - Characters")
clock = pygame.time.Clock()

# Create display scaler for letterboxing/pillarboxing
scaler = DisplayScaler(WIDTH, HEIGHT)
# Create game surface at native resolution
game_surface = pygame.Surface((WIDTH, HEIGHT))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE_DIR, "font", "PixelifySans-VariableFont_wght.ttf")

background = pygame.image.load(os.path.join(BASE_DIR, "GardenBG.jpg")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# --- Colors ---
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
GOLD        = (255, 251, 243)
GOLD_HOVER  = (255, 227, 161)
DARK_GOLD   = (222, 143, 21)
RED         = (220, 50, 50)

# --- Fonts ---
title_font  = pygame.font.Font(FONT, 60)
name_font   = pygame.font.Font(FONT, 52)  # Bigger name font
desc_font   = pygame.font.Font(FONT, 20)
button_font = pygame.font.Font(FONT, 40)

# --- Character Data ---
CHARACTERS = [
    {
        "name": "Mikhail",
        "image": "Sprites/Mikhail/MikhailFull.png",
        "description": "The strict angel. One of the Guards of the gates of Eden. Takes his job seriously. Don't take his anger personally."
    },
    {
        "name": "Raziel",
        "image": "Sprites/Raziel/RazielFull.png",
        "description": "The laid back angel. Despite working beside Mikhail, he is seen as the more calmer one. Takes his job seriously if you are a threat. Don't mistake his casual nature for passivity."
    },
    {
        "name": "The Serpent",
        "image": "Sprites/Naga/NagaFull.png",
        "description": "Deceiver. The one who caused the fall of humanity. Or did he? Doesn't fully believe he's at fault."
    },
    {
        "name": "Cain",
        "image": "Sprites/Cain/CainFull.png",
        "description": "Older brother of Abel. Was once a farmer with his brother. Jealousy caused him to spiral and commit the first Murder. Upon reuniting at death, he vows to protect his brother and pay for his sins. Promised to take back Eden."
    },
    {
        "name": "Abel",
        "image": "Sprites/Abel/AbelFull.png",
        "description": "Younger brother of Cain. Doesn't fully forgive his brother, but doesn't fully resent him either. Worked as a shepherd. Ever since he reunited with his brother upon death, it has both been tense and calm. Aids his brother in taking back Eden."
    },
    {
        "name": "The Guardian",
        "image": "Sprites/Guardian/GuardianFull.png",
        "description": "A cherubim sent down to guard the tree of knowledge. Much more strict than Mikhail, works under him. Still has mercy to humans, give them a chance to walk away from the path of sin."
    },
    {
        "name": "--. --- -..",
        "image": "Sprites/boss/BossFull.png",
        "description": "You have committed a grave mistake.",
        "special_color": RED
    }
]

# Load character images
for char in CHARACTERS:
    try:
        img = pygame.image.load(os.path.join(BASE_DIR, char["image"])).convert_alpha()
        
        # Special case: Abel needs to be stretched taller (he's too short!)
        if char["name"] == "Abel":
            # Stretch Abel vertically by 1.3x to make him taller
            original_w = img.get_width()
            original_h = img.get_height()
            new_h = int(original_h * 1.3)
            char["loaded_image"] = pygame.transform.scale(img, (original_w, new_h))
            # Then scale to fit display area
            char["loaded_image"] = pygame.transform.scale(char["loaded_image"], (320, 480))
        else:
            # Scale to fit in the display area (left side)
            char["loaded_image"] = pygame.transform.scale(img, (320, 480))
    except:
        # Fallback if image not found
        char["loaded_image"] = None

# --- UI Layout ---
BACK_BUTTON_SIZE = 60
ARROW_SIZE = 50
IMAGE_AREA_W = 340
IMAGE_AREA_X = 60
IMAGE_AREA_Y = 150

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def draw_characters_screen(current_index, mouse_pos):
    # Draw background
    game_surface.blit(background, (0, 0))
    
    # Add dark overlay to bring focus to characters
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Dark semi-transparent overlay
    game_surface.blit(overlay, (0, 0))
    
    char = CHARACTERS[current_index]
    
    # --- Back Button (top left) ---
    back_rect = pygame.Rect(20, 20, BACK_BUTTON_SIZE, BACK_BUTTON_SIZE)
    back_hovered = back_rect.collidepoint(mouse_pos)
    back_color = GOLD_HOVER if back_hovered else GOLD
    
    # Draw back arrow with border
    pygame.draw.rect(game_surface, back_color, back_rect, width=3, border_radius=4)
    # Draw < symbol
    back_text = button_font.render("<", True, back_color)
    back_text_rect = back_text.get_rect(center=back_rect.center)
    game_surface.blit(back_text, back_text_rect)
    
    # --- Title ---
    title_surf = title_font.render("Characters", True, GOLD)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 60))
    game_surface.blit(title_surf, title_rect)
    
    # --- Decorative line under title ---
    line_y = 100
    pygame.draw.line(game_surface, DARK_GOLD, (100, line_y), (WIDTH - 100, line_y), 2)
    
    # --- Character Image (left side) - NO BACKGROUND, just the transparent PNG ---
    if char["loaded_image"]:
        # Center the image in the left area
        img_x = IMAGE_AREA_X + IMAGE_AREA_W // 2 - char["loaded_image"].get_width() // 2
        img_y = IMAGE_AREA_Y + 240 - char["loaded_image"].get_height() // 2
        game_surface.blit(char["loaded_image"], (img_x, img_y))
    
    # --- Left Arrow (more visible, below image) ---
    left_arrow_x = IMAGE_AREA_X + IMAGE_AREA_W // 2 - 70
    left_arrow_y = IMAGE_AREA_Y + 500
    left_arrow_rect = pygame.Rect(left_arrow_x, left_arrow_y, ARROW_SIZE, ARROW_SIZE)
    left_hovered = left_arrow_rect.collidepoint(mouse_pos)
    left_color = GOLD_HOVER if left_hovered else GOLD
    
    # Fill background for visibility
    if left_hovered:
        pygame.draw.rect(game_surface, left_color, left_arrow_rect, border_radius=4)
        arrow_color = BLACK
    else:
        pygame.draw.rect(game_surface, (0, 0, 0, 200), left_arrow_rect, border_radius=4)
        arrow_color = left_color
    
    pygame.draw.rect(game_surface, left_color, left_arrow_rect, width=3, border_radius=4)
    left_text = button_font.render("<", True, arrow_color)
    left_text_rect = left_text.get_rect(center=left_arrow_rect.center)
    game_surface.blit(left_text, left_text_rect)
    
    # --- Right Arrow (more visible, below image) ---
    right_arrow_x = IMAGE_AREA_X + IMAGE_AREA_W // 2 + 20
    right_arrow_y = IMAGE_AREA_Y + 500
    right_arrow_rect = pygame.Rect(right_arrow_x, right_arrow_y, ARROW_SIZE, ARROW_SIZE)
    right_hovered = right_arrow_rect.collidepoint(mouse_pos)
    right_color = GOLD_HOVER if right_hovered else GOLD
    
    # Fill background for visibility
    if right_hovered:
        pygame.draw.rect(game_surface, right_color, right_arrow_rect, border_radius=4)
        arrow_color = BLACK
    else:
        pygame.draw.rect(game_surface, (0, 0, 0, 200), right_arrow_rect, border_radius=4)
        arrow_color = right_color
    
    pygame.draw.rect(game_surface, right_color, right_arrow_rect, width=3, border_radius=4)
    right_text = button_font.render(">", True, arrow_color)
    right_text_rect = right_text.get_rect(center=right_arrow_rect.center)
    game_surface.blit(right_text, right_text_rect)
    
    # --- Character Info (right side) ---
    info_x = IMAGE_AREA_X + IMAGE_AREA_W + 40
    info_y = IMAGE_AREA_Y + 20
    info_w = WIDTH - info_x - 40
    
    # Character Name (bigger, no "Description" label)
    name_color = char.get("special_color", GOLD)
    name_surf = name_font.render(char["name"], True, name_color)
    name_rect = name_surf.get_rect(midtop=(info_x + info_w // 2, info_y))
    game_surface.blit(name_surf, name_rect)
    
    # Description text (wrapped) - starts right after name
    desc_y = info_y + 80
    desc_color = char.get("special_color", WHITE)
    wrapped_lines = wrap_text(char["description"], desc_font, info_w - 20)
    
    for line in wrapped_lines:
        line_surf = desc_font.render(line, True, desc_color)
        line_rect = line_surf.get_rect(midtop=(info_x + info_w // 2, desc_y))
        game_surface.blit(line_surf, line_rect)
        desc_y += 30
    
    # --- Character counter ---
    counter_text = f"{current_index + 1} / {len(CHARACTERS)}"
    counter_surf = desc_font.render(counter_text, True, GOLD)
    counter_rect = counter_surf.get_rect(center=(IMAGE_AREA_X + IMAGE_AREA_W // 2, HEIGHT - 30))
    game_surface.blit(counter_surf, counter_rect)
    
    # Scale and display the game surface with letterboxing/pillarboxing
    scaler.display(screen, game_surface)
    pygame.display.flip()
    
    return back_rect, left_arrow_rect, right_arrow_rect

def main():
    current_index = 0
    
    while True:
        # Get window mouse position and transform to game coordinates
        window_mouse_pos = pygame.mouse.get_pos()
        window_width, window_height = screen.get_size()
        mouse_pos = scaler.transform_mouse_pos(window_mouse_pos, window_width, window_height)
        
        # If mouse is in black bars, use a position outside the game area
        if mouse_pos is None:
            mouse_pos = (-1, -1)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Return to main menu
                elif event.key == pygame.K_LEFT:
                    current_index = (current_index - 1) % len(CHARACTERS)
                elif event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % len(CHARACTERS)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Transform click position to game coordinates
                click_pos = scaler.transform_mouse_pos(event.pos, window_width, window_height)
                if click_pos is None:
                    continue  # Click was in black bars, ignore it
                
                back_rect, left_rect, right_rect = draw_characters_screen(current_index, mouse_pos)
                
                if back_rect.collidepoint(click_pos):
                    return  # Return to main menu
                elif left_rect.collidepoint(click_pos):
                    current_index = (current_index - 1) % len(CHARACTERS)
                elif right_rect.collidepoint(click_pos):
                    current_index = (current_index + 1) % len(CHARACTERS)
        
        draw_characters_screen(current_index, mouse_pos)
        clock.tick(60)

if __name__ == "__main__":
    main()
