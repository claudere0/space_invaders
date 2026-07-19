import pygame
from config import WIDTH, EXTRA_Y_POSITION

class Extra(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.image = pygame.image.load('images/extra.png').convert_alpha()

        if side == 'right':
            x = WIDTH + 32
            self.speed = -240
        else:
            x = -32
            self.speed = 240

        self.x = float(x)
        self.rect = self.image.get_rect(topleft = (x, EXTRA_Y_POSITION))

    def update(self, dt):
        self.x += self.speed * dt
        self.rect.x = round(self.x)
        