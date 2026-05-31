import pygame
pygame.init()

# Colours
RED = (255, 0, 0)
ORANGE = (255, 150, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)

# Screen
screen_dimensions = pygame.display.Info()
WIDTH, HEIGHT = screen_dimensions.current_w, screen_dimensions.current_h
floor_level = 1856

# Difficulties
difficulties = ["Brain Freeze", "Headache", "Migraine", "Cluster", "Thunderclap"]

# Groups
enemy_render_group = pygame.sprite.Group()

# Camera
camera_x = 0
camera_y = 0

# Other Universal Vars
item_selected = False

# Font
rabid_science = pygame.font.Font("Assets/Fonts/Rabid Science.ttf", 48)
title_font = pygame.font.Font("Assets/Fonts/Rabid Science.ttf", 192)
subtitle_font = pygame.font.Font("Assets/Fonts/Rabid Science.ttf", 128)
simple_font = pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 24)
common_simple_font = pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 48)

# Game State List
game_states = ["Title Screen", "Saves", "Game", "Pause", "Game Over", "Settings", "Save Creator", "Chest UI", "Sword UI"]
game_save = 0

class GameState:
    current = game_states[0]

# Audio Lists
sword_slashes = [pygame.mixer.Sound("Assets/Sounds/SFX/Sword Slash 1.mp3"), pygame.mixer.Sound("Assets/Sounds/SFX/Sword Slash 2.mp3")]