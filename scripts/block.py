import pygame
from config import BLOCK_SIZE

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(topleft = (x,y))
