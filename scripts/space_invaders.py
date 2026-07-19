import pygame
from random import choice, randint
from enum import Enum, auto
pygame.init()

WIDTH = 1024
HEIGHT = 1024
FPS = 60
FONT_SIZE = 36

SHAPE = [
    '  xxxxxxxx  ',
    ' xxxxxxxxxx ',
    'xxxxxxxxxxxx',
    'xxxxxxxxxxxx',
    'xxx      xxx',
    'xx        xx'
]

BLOCK_SIZE = 8
LIVES_X_OFFSET = 32
LIVES_Y_OFFSET = 48
SCORE_X_OFFSET = 32
EXTRA_VALUE = 500
EXTRA_MIN_TIME = 7
EXTRA_MAX_TIME = 15
EXTRA_Y_POSITION = 128
ALIEN_LAZER_TIMER = 750

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    WIN = auto()

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

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(topleft = (x,y))

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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('space invaders')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('font/Pixeled.ttf', FONT_SIZE)

        self.live_surf = pygame.image.load('images/player.png').convert_alpha()
        self.live_position = WIDTH - (self.live_surf.get_size()[0] + LIVES_X_OFFSET)

        player_sprite = Player()
        self.player = pygame.sprite.GroupSingle(player_sprite)

        self.obstacle_y_position = int((HEIGHT*7)//8)
        self.blocks = pygame.sprite.Group()
        self.create_multiple_obstacles()

        self.aliens = pygame.sprite.Group()
        self.aliens_lasers = pygame.sprite.Group()

        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(EXTRA_MIN_TIME, EXTRA_MAX_TIME)

        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.125)
        music.play(loops = -1)

        self.laser_sound = pygame.mixer.Sound('audio/audio_laser.wav')
        self.laser_sound.set_volume(0.25)
        self.explosion_sound = pygame.mixer.Sound('audio/audio_explosion.wav')
        self.explosion_sound.set_volume(0.25)

        self.ALIENLAZER = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ALIENLAZER, ALIEN_LAZER_TIMER)

        self.running = True
        self.reset()
        self.state = GameState.MENU

    def reset(self):
        self.score = 0
        self.lives = 3

        self.alien_direction = 1

        self.player.sprite.restart()

        self.blocks.empty()
        self.create_multiple_obstacles()

        self.aliens.empty()
        # self.spawn_aliens(6, 8)
        self.spawn_aliens(1, 1)

        self.aliens_lasers.empty()
        self.extra.empty()

        self.state = GameState.PLAYING

    def create_obstacle(self, x, y):
        for row_index, row in enumerate(SHAPE):
            for index, sign in enumerate(row):
                if sign == 'x':
                    self.blocks.add(Block(x + index * BLOCK_SIZE, y + row_index * BLOCK_SIZE))

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
                alien.y += distance
                alien.rect.y = round(alien.y)

    def aliens_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= WIDTH:
                self.alien_direction = -1
                self.aliens_move_down(3)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.aliens_move_down(3)

    def alien_shoot(self):
        if self.aliens:
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 360)
            self.aliens_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_timer(self, dt):
        self.extra_spawn_time -= dt
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right', 'left'])))
            self.extra_spawn_time = randint(EXTRA_MIN_TIME, EXTRA_MAX_TIME)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state == GameState.PLAYING:
                if event.type == self.ALIENLAZER:
                    self.alien_shoot()
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()
                if event.key == pygame.K_q:
                    self.running = False

    def update(self, dt):
        if self.state == GameState.PLAYING:
            self.update_objects(dt)
            self.collision_checks()
            self.check_game_state()
        else:
            return None

    def update_objects(self, dt):
        self.player.update(dt)
        self.aliens.update(self.alien_direction, dt)
        self.aliens_position_checker()
        self.aliens_lasers.update(dt)
        self.extra_timer(dt)
        self.extra.update(dt)

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

            if pygame.sprite.spritecollide(laser, self.extra, True):
                self.score += EXTRA_VALUE
                laser.kill()

    def alien_laser_collision(self):
        for laser in self.aliens_lasers:
            if pygame.sprite.spritecollide(laser, self.blocks, True):
                laser.kill()
                continue

            if pygame.sprite.spritecollide(laser, self.player, False):
                laser.kill()
                self.lives -= 1

    def alien_collision(self):
        for alien in self.aliens:
            pygame.sprite.spritecollide(alien, self.blocks, True)

            if pygame.sprite.spritecollide(alien, self.player, False):
                self.state = GameState.GAME_OVER

    def draw(self):
        self.screen.fill((0,0,0))
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_objects()
            self.draw_score()
            self.draw_lives()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.WIN:
            self.draw_victory()
        pygame.display.flip()

    def draw_objects(self):
        self.player.sprite.lasers.draw(self.screen)
        self.player.draw(self.screen)
        self.blocks.draw(self.screen)
        self.aliens.draw(self.screen)
        self.aliens_lasers.draw(self.screen)
        self.extra.draw(self.screen)

    def draw_score(self):
        score_surface = self.font.render(f"score: {self.score}", False, (255,255,255))
        score_rect = score_surface.get_rect(topleft=(SCORE_X_OFFSET,0))
        self.screen.blit(score_surface, score_rect)

    def draw_lives(self):
        for live in range(self.lives - 1):
            x = self.live_position - (live * (self.live_surf.get_size()[0] + LIVES_X_OFFSET))
            self.screen.blit(self.live_surf,(x, LIVES_Y_OFFSET))

    def draw_menu(self):
        self.draw_message('SPACE INVADERS', 'up')
        self.draw_message('PRESS ENTER TO START')
        self.draw_message('OR Q TO QUIT', 'down')

    def draw_victory(self):
        self.draw_message('CONGRATULATIONS', 'up')
        self.draw_message('YOU WON!')
        self.draw_message('PRESS Q TO QUIT', 'down')

    def draw_game_over(self):
        self.draw_message('YOU LOST!', 'up')
        self.draw_message('PRESS R TO RESTART')
        self.draw_message('OR Q TO QUIT', 'down')

    def draw_message(self, message, position='mid'):
        self.surf = self.font.render(message, False, (255,255,255))
        if position == 'up':
            self.rect = self.surf.get_rect(center = (WIDTH//2,HEIGHT//2 - 64))
        elif position == 'down':
            self.rect = self.surf.get_rect(center = (WIDTH//2,HEIGHT//2 + 64))
        else:
            self.rect = self.surf.get_rect(center = (WIDTH//2,HEIGHT//2))
        self.screen.blit(self.surf, self.rect)

    def check_game_state(self):
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        elif not self.aliens:
            self.state = GameState.WIN

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()