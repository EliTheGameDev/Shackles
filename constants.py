import pygame
pygame.init()

# Colours
RED = (255, 0, 0)
ORANGE = (255, 150, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
DETECTION_BOX_OPACITY = 0

# Screen
screen_dimensions = pygame.display.Info()
WIDTH, HEIGHT = screen_dimensions.current_w, screen_dimensions.current_h
floor_level = HEIGHT - 100

# Groups
enemy_render_group = pygame.sprite.Group()

# Camera
camera_x = 0
camera_y = 0

# Font
rabid_science = pygame.font.Font("Assets/Fonts/Rabid Science.ttf", 24)
title_font = pygame.font.Font("Assets/Fonts/Rabid Science.ttf", 64)
simple_font = pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 24)

# Game State List
game_states = ["Title Screen", "Saves", "Game", "Pause"]

# Audio Lists
sword_slashes = [pygame.mixer.Sound("Assets/Sounds/SFX/Sword Slash 1.mp3"), pygame.mixer.Sound("Assets/Sounds/SFX/Sword Slash 2.mp3")]