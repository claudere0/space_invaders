import pygame
from config import HEIGHT

class Laser(pygame.sprite.Sprite):
    def __init__(self, position, speed):
        super().__init__()
        self.image = pygame.Surface((8,32))
        self.image.fill((255,255,255))
        self.speed = speed
        self.rect = self.image.get_rect(center=position)
        self.y = position[1]

    def destroy(self):
        if self.rect.y <= -32 or self.rect.y >= HEIGHT + 32:
            self.kill()

    def update(self, dt):
        self.y += self.speed * dt
        self.rect.y = round(self.y)
        self.destroy()
        