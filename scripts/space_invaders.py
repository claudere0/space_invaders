import pygame
pygame.init()

WIDTH = 1024
HEIGHT = 1024
FPS = 60

SHAPE = [
    '  xxxxxxxx  ',
    ' xxxxxxxxxx ',
    'xxxxxxxxxxxx',
    'xxxxxxxxxxxx',
    'xxx      xxx',
    'xx        xx'
]

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
        self.x = (WIDTH - self.width) // 2
        self.y = HEIGHT - self.height
        self.rect = self.image.get_rect(topleft = (self.x, self.y))
        self.speed = 6
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600
        self.lasers.empty()

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and self.rect.x <= WIDTH - self.width:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT] and self.rect.x >= 0:
            self.rect.x -= self.speed

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
        self.lasers.add(Laser(self.rect.center))

    def update(self):
        self.get_input()
        self.recharge()
        self.lasers.update()

class Laser(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((8,32))
        self.image.fill((255,255,255))
        self.speed = -12
        self.rect = self.image.get_rect(center=position)

    def destroy(self):
        if self.rect.y <= -32 or self.rect.y >= HEIGHT + 32:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(topleft = (x,y))

class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        file_path = 'images/' + color + '.png'
        self.image = pygame.image.load(file_path).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))

        if color == 'red' : self.value = 100
        elif color == 'yellow' : self.value = 200
        else: self.value = 300

    def update(self, direction):
        self.rect.x += direction * 10

class Extra(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.image = pygame.image.load('images/extra.png').convert_alpha()
        self.value = 500

        if side == 'right':
            x = WIDTH + 32
            self.speed = -3
        else:
            x = -32
            self.speed = 3

        self.rect = self.image.get_rect(topleft = (x, 64))

    def update(self):
        self.rect.x += self.speed

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('space invaders')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('font/Pixeled.ttf', 36)

        self.lives = 3
        player_sprite = Player()
        self.player = pygame.sprite.GroupSingle(player_sprite)

        self.blocks = pygame.sprite.Group()
        self.obstacle_y_position = int((HEIGHT*7)//8)
        self.create_multiple_obstacles()

        self.aliens = pygame.sprite.Group()
        self.aliens_lasers = pygame.sprite.Group()
        self.alien_direction = 1
        self.spawn_aliens(6, 8)
        self.alien_direction = 1

        self.explosion_sound = pygame.mixer.Sound('audio/audio_explosion.wav')
        self.explosion_sound.set_volume(0.25)

        self.score = 0
        self.running = True
        self.reset()

    def reset(self):
        pass # self.state = MENU or self.state = PLAYING

    def create_obstacle(self, x, y):
        for row_index, row in enumerate(SHAPE):
            for index, sign in enumerate(row):
                if sign == 'x':
                    self.blocks.add(Block(x + index * 8, y + row_index * 8))

    def create_multiple_obstacles(self, offset = 64):
        for i in range(7):
            if i % 2 == 0:
                self.create_obstacle(i * 128 + offset, self.obstacle_y_position)

    def spawn_aliens(self, rows, cols, width=64, height=48, x_offset = 32, y_offset = 32, starting_offset = 128):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * width + col_index * x_offset
                y = row_index * height + row_index * y_offset + starting_offset
                if row_index == 0: alien_sprite = Alien('yellow', x, y)
                elif 1 <=  row_index <= 2: alien_sprite = Alien('green', x, y)
                else: alien_sprite = Alien('red', x, y)
                self.aliens.add(alien_sprite)

    def aliens_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def aliens_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= WIDTH:
                self.alien_direction = -1
                self.aliens_move_down(5)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.aliens_move_down(5)

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
        self.aliens.update(self.alien_direction)
        self.aliens_position_checker()
        
        # check collisions
        self.collision_checks()
        # check game state


    def collision_checks(self):
        self.laser_collision()
        self.alien_laser_collision()
        self.alien_collision()

    def laser_collision(self):
        for laser in self.player.sprite.lasers:
            if pygame.sprite.spritecollide(laser, self.blocks, True):
                laser.kill()

            aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
            if aliens_hit:
                for alien in aliens_hit:
                    self.score += alien.value
                laser.kill()
                self.explosion_sound.play()

            # if pygame.sprite.spritecollide(laser, self.extra, True):
            #     self.score += 500
            #     laser.kill()

    def alien_laser_collision(self):
        for laser in self.aliens_lasers:
            if pygame.sprite.spritecollide(laser, self.blocks, True):
                laser.kill()
                continue

            if pygame.sprite.spritecollide(laser, self.player, False):
                laser.kill()
                self.lives -= 1
                if self.lives <= 0:
                    self.running = False

    def alien_collision(self):
        for alien in self.aliens:
            pygame.sprite.spritecollide(alien, self.blocks, True)

            if pygame.sprite.spritecollide(alien, self.player, False):
                self.running = False

    def draw(self):
        self.screen.fill((0,0,0))
        # all game objects
        self.player.sprite.lasers.draw(self.screen)
        self.player.draw(self.screen)
        self.blocks.draw(self.screen)
        self.aliens.draw(self.screen)
        # aliens lasers
        # extra
        # lives
        self.draw_score()
        # victory_message
        pygame.display.flip()

    def draw_score(self):
        score_surface = self.font.render(f"score: {self.score}", False, (255,255,255))
        score_rect = score_surface.get_rect(topleft=(32,0))
        self.screen.blit(score_surface, score_rect)

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