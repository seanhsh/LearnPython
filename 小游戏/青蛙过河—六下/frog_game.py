import pygame
import sys
import random
from words import word_database
from config import *

class LilyPad:
    def __init__(self, word_data, lane, speed):
        self.word = word_data['word']
        self.meaning = word_data['meaning']
        self.first_letter = word_data['firstLetter']
        self.lane = lane
        self.speed = speed
        self.x = 150 + lane * 200
        self.y = SCREEN_HEIGHT + 100
        self.width = PAD_WIDTH
        self.height = PAD_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_correct = False
        self.animation_timer = 0

    def update(self):
        self.y -= self.speed
        self.rect.y = int(self.y)
        
        if self.is_correct:
            self.animation_timer += 1
            if self.animation_timer > 15:
                return True
        return False

    def draw(self, screen, font):
        color = GOLD_COLOR if self.is_correct else GREEN_COLOR
        
        if self.is_correct:
            scale = 1.0 + 0.1 * (1 - self.animation_timer / 15)
            scaled_width = int(self.width * scale)
            scaled_height = int(self.height * scale)
            scaled_x = self.x - (scaled_width - self.width) // 2
            scaled_y = self.y - (scaled_height - self.height) // 2
            pygame.draw.ellipse(screen, color, (scaled_x, scaled_y, scaled_width, scaled_height))
        else:
            pygame.draw.ellipse(screen, color, self.rect)
        
        text = font.render(self.word, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

class Frog:
    def __init__(self):
        self.reset_position()
        self.target_x = self.x
        self.target_y = self.y
        self.is_jumping = False
        self.jump_progress = 0

    def reset_position(self):
        self.x = SCREEN_WIDTH // 2 - FROG_SIZE // 2
        self.y = SCREEN_HEIGHT - 150
        self.target_x = self.x
        self.target_y = self.y
        self.is_jumping = False
        self.jump_progress = 0

    def jump_to(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.is_jumping = True
        self.jump_progress = 0

    def update(self):
        if self.is_jumping:
            self.jump_progress += 0.1
            if self.jump_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.is_jumping = False
                self.jump_progress = 0
            else:
                self.x = self.x + (self.target_x - self.x) * self.jump_progress
                self.y = self.y + (self.target_y - self.y) * self.jump_progress

    def draw(self, screen):
        frog_rect = pygame.Rect(int(self.x), int(self.y), FROG_SIZE, FROG_SIZE)
        
        body_color = FROG_GREEN
        pygame.draw.ellipse(screen, body_color, frog_rect)
        
        eye_radius = 8
        eye_y = int(self.y - 10)
        pygame.draw.circle(screen, body_color, (int(self.x + 15), eye_y), eye_radius)
        pygame.draw.circle(screen, body_color, (int(self.x + FROG_SIZE - 15), eye_y), eye_radius)
        
        pupil_radius = 4
        pygame.draw.circle(screen, BLACK, (int(self.x + 15), eye_y), pupil_radius)
        pygame.draw.circle(screen, BLACK, (int(self.x + FROG_SIZE - 15), eye_y), pupil_radius)
        
        mouth_rect = pygame.Rect(int(self.x + 20), int(self.y + 35), 20, 10)
        pygame.draw.arc(screen, DARK_GREEN, mouth_rect, 3.14, 6.28, 2)

class FrogGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('青蛙过河 - 背单词游戏')
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        self.game_state = 'menu'
        self.last_key = ''

    def reset_game(self):
        self.score = 0
        self.level = 1
        self.lives = 3
        self.pad_speed = BASE_SPEED
        self.frog = Frog()
        self.lily_pads = []
        self.spawn_timer = 0
        self.game_over = False
        self.game_won = False
        self.last_key = ''

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == 'menu':
                    if event.key == pygame.K_SPACE:
                        self.game_state = 'playing'
                        self.reset_game()
                
                elif self.game_state == 'playing':
                    if event.key == pygame.K_p:
                        self.game_state = 'paused'
                    else:
                        key_name = pygame.key.name(event.key)
                        if len(key_name) == 1 and key_name.isalpha():
                            key_char = key_name.lower()
                            self.last_key = key_char
                            self.check_word(key_char)
                
                elif self.game_state == 'paused':
                    if event.key == pygame.K_p:
                        self.game_state = 'playing'
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = 'menu'
                
                elif self.game_state in ['gameover', 'gamewon']:
                    if event.key == pygame.K_SPACE:
                        self.game_state = 'menu'

    def check_word(self, key_char):
        if not key_char or not key_char.isalpha():
            return
        
        for pad in self.lily_pads:
            if not pad.is_correct and pad.first_letter == key_char:
                pad.is_correct = True
                self.score += 10
                self.frog.jump_to(pad.x + 30, pad.y + 10)
                break

    def spawn_lily_pad(self):
        lane = random.randint(0, 2)
        words = word_database[f'level{self.level}']
        word_data = random.choice(words)
        speed = self.pad_speed + random.uniform(0, 1)
        pad = LilyPad(word_data, lane, speed)
        self.lily_pads.append(pad)

    def update(self):
        if self.game_state != 'playing':
            return

        self.spawn_timer += 1
        if self.spawn_timer >= SPAWN_INTERVAL:
            self.spawn_lily_pad()
            self.spawn_timer = 0

        self.frog.update()

        pads_to_remove = []
        for pad in self.lily_pads:
            should_remove = pad.update()
            if should_remove or pad.y < -PAD_HEIGHT:
                pads_to_remove.append(pad)
        
        for pad in pads_to_remove:
            if pad in self.lily_pads:
                self.lily_pads.remove(pad)

        if self.frog.y <= 50:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.pad_speed += 0.5
        self.frog.reset_position()
        
        if self.level > 3:
            self.game_won = True
            self.game_state = 'gamewon'

    def draw_background(self):
        self.screen.fill(BLUE_COLOR)
        
        pygame.draw.rect(self.screen, STONE_COLOR, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        pygame.draw.rect(self.screen, STONE_COLOR, (0, 0, SCREEN_WIDTH, 100))
        
        pygame.draw.circle(self.screen, STONE_DARK, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50), 40)
        pygame.draw.circle(self.screen, STONE_DARK, (SCREEN_WIDTH // 2, 50), 40)

    def draw_ui(self):
        score_text = self.font.render(f'得分: {self.score}', True, WHITE)
        level_text = self.font.render(f'关卡: {self.level}', True, WHITE)
        lives_text = self.font.render(f'生命: {self.lives}', True, WHITE)
        key_text = self.small_font.render(f'按键: {self.last_key.upper() if self.last_key else "无"}', True, WHITE)
        
        self.screen.blit(score_text, (20, 10))
        self.screen.blit(level_text, (200, 10))
        self.screen.blit(lives_text, (380, 10))
        self.screen.blit(key_text, (550, 10))

    def draw_menu(self):
        self.draw_background()
        
        title_text = self.title_font.render('青蛙过河', True, WHITE)
        subtitle_text = self.font.render('背单词游戏', True, WHITE)
        instruction_text = self.small_font.render('按空格键开始游戏', True, WHITE)
        help_text = self.small_font.render('敲击键盘上单词的首字母，青蛙会跳到对应的荷叶上！', True, WHITE)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(instruction_text, instruction_rect)
        self.screen.blit(help_text, help_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.title_font.render('游戏结束', True, RED_COLOR)
        score_text = self.font.render(f'最终得分: {self.score}', True, WHITE)
        level_text = self.font.render(f'到达关卡: {self.level}', True, WHITE)
        restart_text = self.small_font.render('按空格键重新开始', True, WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(level_text, level_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_game_won(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        win_text = self.title_font.render('恭喜通关！', True, GOLD_COLOR)
        score_text = self.font.render(f'最终得分: {self.score}', True, WHITE)
        restart_text = self.small_font.render('按空格键重新开始', True, WHITE)
        
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        
        self.screen.blit(win_text, win_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_paused(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        paused_text = self.title_font.render('游戏暂停', True, WHITE)
        continue_text = self.small_font.render('按 P 继续游戏', True, WHITE)
        menu_text = self.small_font.render('按 ESC 返回菜单', True, WHITE)
        
        paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        
        self.screen.blit(paused_text, paused_rect)
        self.screen.blit(continue_text, continue_rect)
        self.screen.blit(menu_text, menu_rect)

    def draw(self):
        if self.game_state == 'menu':
            self.draw_menu()
        elif self.game_state == 'playing':
            self.draw_background()
            self.draw_ui()
            
            for pad in self.lily_pads:
                pad.draw(self.screen, self.font)
            
            self.frog.draw(self.screen)
        elif self.game_state == 'paused':
            self.draw_background()
            self.draw_ui()
            
            for pad in self.lily_pads:
                pad.draw(self.screen, self.font)
            
            self.frog.draw(self.screen)
            self.draw_paused()
        elif self.game_state == 'gameover':
            self.draw_background()
            self.draw_ui()
            self.draw_game_over()
        elif self.game_state == 'gamewon':
            self.draw_background()
            self.draw_ui()
            self.draw_game_won()
        
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    game = FrogGame()
    game.run()