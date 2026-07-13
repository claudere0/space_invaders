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

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
            self.screen.fill((0,0,0))
            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()