import pygame
pygame.init()

WIDTH = 600
HEIGHT = 600
FPS = 60

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('space invaders')
        self.clock = pygame.time.Clock()

        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False

    def update(self):
        pass

    def draw(self):
        self.screen.fill((0,0,0))
        # all game objects
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