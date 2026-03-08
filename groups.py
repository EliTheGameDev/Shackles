from classes import *

# Player
player_group = pygame.sprite.Group()
player_group.add(player)

# UI
ui_group = pygame.sprite.Group()
ui_group.add(heart1, heart2, heart3)

# Enemies
foe = Swordsman((600, 400), False)
foe_sword = Sword(foe, old_set)
foe.weapon = foe_sword
radius = DetectionBox(foe, 192)
sight = VisionBasedDetectionBox(foe, (60, 50))
enemy_render_group.add(foe, foe_sword, radius, sight)

# Platforms
platform_group = pygame.sprite.Group()