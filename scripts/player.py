import pygame
from config import WIDTH, HEIGHT
from laser import Laser

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/player.png').convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.lasers = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound('audio/audio_laser.wav')
        self.laser_sound.set_volume(0.25)

        self.restart()
    
    def restart(self):
        self.x = (WIDTH - self.width) / 2
        self.y = HEIGHT - self.height
        self.rect = self.image.get_rect(topleft = (self.x, self.y))
        self.speed = 360
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 500
        self.lasers.empty()

    def get_input(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and self.rect.x <= WIDTH - self.width:
            self.x += self.speed * dt
            self.x = min(self.x, WIDTH - self.width)
            self.rect.x = round(self.x)
        elif keys[pygame.K_LEFT] and self.rect.x >= 0:
            self.x -= self.speed * dt
            self.x = max(self.x, 0)
            self.rect.x = round(self.x)

        if keys[pygame.K_SPACE] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    # recharge
    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, -720))

    def update(self, dt):
        self.get_input(dt)
        self.recharge()
        self.lasers.update(dt)
        