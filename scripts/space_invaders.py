import pygame
pygame.init()

WIDTH = 512
HEIGHT = 512
FPS = 60

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/player.png').convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.restart()
    
    def restart(self):
        self.x = (WIDTH - self.width) // 2
        self.y = HEIGHT - self.height
        self.rect = self.image.get_rect(topleft = (self.x, self.y))
        self.speed = 6
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and self.rect.x <= WIDTH - self.width:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT] and self.rect.x >= 0:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.ready:
            # self.shoot_laser()
            self.ready = False

    # recharge
    def reachage(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True
    # shoot_lazer
    
    def update(self):
        self.get_input()
        # recharge
        # lasers.update()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('space invaders')
        self.clock = pygame.time.Clock()
        
        player_sprite = Player()
        self.player = pygame.sprite.GroupSingle(player_sprite)

        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False

    def update(self):
        # update objects
        self.player.update()
        # check collisions

        # check game state

        pass

    def draw(self):
        self.screen.fill((0,0,0))
        # all game objects
        self.player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()