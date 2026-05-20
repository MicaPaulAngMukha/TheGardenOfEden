"""
Visual test to verify key sprites render correctly.
Run this to see all four keys displayed on screen.
Press ESC to exit.
"""

import pygame
import sys
from key_system import spawn_keys

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Key System Visual Test")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)

# Font
font = pygame.font.Font(None, 24)

# Spawn keys
keys = spawn_keys()

# Position keys in a row for display
x_start = 150
y_pos = HEIGHT // 2
spacing = 150

for i, key in enumerate(keys):
    key.rect.x = x_start + (i * spacing)
    key.rect.y = y_pos

print("Visual test running...")
print("You should see 4 keys displayed:")
print("  - Bronze (brown/copper color)")
print("  - Gold (yellow/golden color)")
print("  - Rusted (dark red/brown)")
print("  - Divine (white/bright)")
print("\nPress ESC to exit")

running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Draw
    screen.fill(BLACK)
    
    # Title
    title = font.render("Key System Visual Test", True, GOLD)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    # Draw keys and labels
    for key in keys:
        # Draw key sprite
        screen.blit(key.sprite, key.rect)
        
        # Draw label below key
        label = font.render(key.key_type.capitalize(), True, WHITE)
        label_x = key.rect.centerx - label.get_width() // 2
        label_y = key.rect.bottom + 10
        screen.blit(label, (label_x, label_y))
        
        # Draw bounding box
        pygame.draw.rect(screen, WHITE, key.rect, 1)
    
    # Instructions
    instructions = font.render("Press ESC to exit", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()

pygame.quit()
print("\n✅ Visual test complete!")
