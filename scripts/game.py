import pygame
from random import choice, randint
from enum import Enum, auto

from config import *
from player import Player
from laser import Laser
from block import Block
from alien import Alien
from extra import Extra
import hud
pygame.init()

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    WIN = auto()

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
                elif self.state == GameState.GAME_OVER or self.state == GameState.WIN:
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
            hud.draw_menu(self.screen, self.font)
        elif self.state == GameState.PLAYING:
            self.draw_objects()
            hud.draw_score(self.screen, self.score, self.font)
            hud.draw_lives(self.screen, self.lives, self.live_surf, self.live_position)
        elif self.state == GameState.GAME_OVER:
            hud.draw_game_over(self.screen, self.font)
        elif self.state == GameState.WIN:
            hud.draw_victory(self.screen, self.font)
        pygame.display.flip()

    def draw_objects(self):
        self.player.sprite.lasers.draw(self.screen)
        self.player.draw(self.screen)
        self.blocks.draw(self.screen)
        self.aliens.draw(self.screen)
        self.aliens_lasers.draw(self.screen)
        self.extra.draw(self.screen)

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
