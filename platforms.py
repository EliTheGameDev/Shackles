import pygame
pygame.init()

# --- PLATFORM --- #
class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, sprite):
        super().__init__()
        self.image = pygame.image.load(sprite).convert_alpha()
        #self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(center=pos)