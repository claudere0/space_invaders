from config import WIDTH, HEIGHT, LIVES_X_OFFSET, LIVES_Y_OFFSET, SCORE_X_OFFSET

def draw_lives(screen, lives, live_surf, live_position):
    for live in range(lives - 1):
        x = live_position - (live * (live_surf.get_size()[0] + LIVES_X_OFFSET))
        screen.blit(live_surf,(x, LIVES_Y_OFFSET))

def draw_score(screen, score, font):
    surf = font.render(f"Score: {score}", False, (255, 255, 255))
    screen.blit(surf, (SCORE_X_OFFSET, 0))

def draw_menu(screen, font):
    draw_message(screen, 'SPACE INVADERS', font, 'up')
    draw_message(screen, 'PRESS ENTER TO START', font)
    draw_message(screen, 'OR Q TO QUIT', font, 'down')

def draw_victory(screen, font):
    draw_message(screen, 'CONGRATULATIONS', font, 'up')
    draw_message(screen, 'YOU WON!', font)
    draw_message(screen, 'PRESS Q TO QUIT', font, 'down')

def draw_game_over(screen, font):
    draw_message(screen, 'YOU LOST!', font, 'up')
    draw_message(screen, 'PRESS R TO RESTART', font)
    draw_message(screen, 'OR Q TO QUIT', font, 'down')

def draw_message(screen, message, font, position='mid'):
    surf = font.render(message, False, (255,255,255))
    if position == 'up':
        rect = surf.get_rect(center = (WIDTH//2,HEIGHT//2 - 64))
    elif position == 'down':
        rect = surf.get_rect(center = (WIDTH//2,HEIGHT//2 + 64))
    else:
        rect = surf.get_rect(center = (WIDTH//2,HEIGHT//2))
    screen.blit(surf, rect)
