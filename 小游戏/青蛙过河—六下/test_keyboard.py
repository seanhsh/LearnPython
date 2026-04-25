import pygame
import sys

def test_keyboard_input():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption('键盘输入测试')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    last_keys = []
    last_key_info = ""
    
    running = True
    while running:
        screen.fill((50, 50, 50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                unicode_char = event.unicode
                
                info = f"键码: {event.key}, 名称: {key_name}, Unicode: '{unicode_char}'"
                last_key_info = info
                
                if unicode_char:
                    last_keys.insert(0, f"{unicode_char} (键码: {event.key})")
                    if len(last_keys) > 10:
                        last_keys.pop()
        
        title_text = font.render('键盘输入测试', True, (255, 255, 255))
        instruction_text = small_font.render('按下任意键查看输入信息', True, (200, 200, 200))
        
        screen.blit(title_text, (300 - title_text.get_width() // 2, 20))
        screen.blit(instruction_text, (300 - instruction_text.get_width() // 2, 70))
        
        if last_key_info:
            info_text = small_font.render(last_key_info, True, (255, 255, 0))
            screen.blit(info_text, (20, 120))
        
        if last_keys:
            history_title = small_font.render('最近按键历史:', True, (200, 200, 200))
            screen.blit(history_title, (20, 170))
            
            for i, key_info in enumerate(last_keys):
                key_text = small_font.render(f"{i+1}. {key_info}", True, (255, 255, 255))
                screen.blit(key_text, (20, 200 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    test_keyboard_input()