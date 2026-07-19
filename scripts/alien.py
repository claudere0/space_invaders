import pygame

class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        file_path = 'images/' + color + '.png'
        self.image = pygame.image.load(file_path).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))
        self.x = float(x)
        self.y = float(y)
        self.speed = 120

        if color == 'red':
            self.value = 100
        elif color == 'green':
            self.value = 200
        else: 
            self.value = 300

    def update(self, direction, dt):
        self.x += direction * self.speed * dt
        self.rect.x = round(self.x)
