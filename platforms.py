import pygame
from commands import *
pygame.init()

# --- PLATFORM --- #
class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, sprite, isCheckPoint=False, isChest=False, isSolid=True, isExit=False, bouncer=0):
        super().__init__()
        self.image = pygame.image.load(sprite).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(topleft=pos)
        self.isCheckPoint = isCheckPoint
        self.isSolid = isSolid
        self.isChest = isChest
        self.isExit = isExit
        self.bouncer = bouncer

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
                try:
                    platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), f"Assets/Images/Platforms/Ground-Based Platforms/{plat} Platform.png"))
                except FileNotFoundError:
                    if "Obelisk" in plat:
                        plat = list(plat)
                        if plat[-1] != 'k':
                            checkpoint = plat.pop(-1)
                        else:
                            checkpoint = 0
                        plat = str(plat).replace("[", "").replace("]", "").replace(", ", "").replace("'", "")
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), f"Assets/Images/Platforms/Checkpoints/{plat.replace(" ", "_")}.png", isCheckPoint=checkpoint))
                    elif "Chest" in plat:
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), "Assets/Images/Items and Blocks/Chest.png", isChest=True))
                    elif "Activator Panel" in plat:
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), "Assets/Images/Platforms/Non-Solid Platforms/Activator_Panel.png", isSolid=False))
                    elif "Springboard" in plat:
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), "Assets/Images/Platforms/Functional Platforms/Springboard.png", bouncer=10))
                    elif "Background" in plat:
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), f"Assets/Images/Platforms/Non-Solid Platforms/{plat.replace(" Background", "_BG")}.png", isSolid=False))
                    elif "Door" in plat:
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), f"Assets/Images/Platforms/Non-Solid Platforms/{plat.replace(" 1", "1").replace(" ", "_")}.png", isSolid=False))
                    elif "Exit Portal" in plat:
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), f"Assets/Images/Items and Blocks/Exit_Portal.png", isSolid=False, isExit=True))
                    elif "Wood Wall" in plat:
                        platforms[plat_list_val].append(Platform((plat_list_val*plat_size, plat_val*plat_size), f"Assets/Images/Platforms/Structural Platforms/Wood_Wall.png"))

plat_group = pygame.sprite.Group()

def plat_to_group():
    global plat_group
    for plat_list in platforms:
        for plat in plat_list:
            plat_group.add(plat)