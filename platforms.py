import pygame
from commands import *
pygame.init()

# --- PLATFORM --- #
class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, sprite):
        super().__init__()
        self.image = pygame.image.load(sprite).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(topleft=pos)

platforms = []

def create_level(level):
    global platforms
    plat_size = 64
    plat_list_val = -1
    for plat_list in fetch_level_data(level):
        platforms.append([])
        plat_list_val += 1
        plat_val = -1
        for plat in plat_list:
            plat_val += 1
            if plat != 'Empty':
                platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), f"Assets/Images/Platforms/Ground-Based Platforms/{plat} Platform.png"))

plat_group = pygame.sprite.Group()

def plat_to_group():
    global plat_group
    for plat_list in platforms:
        for plat in plat_list:
            plat_group.add(plat)