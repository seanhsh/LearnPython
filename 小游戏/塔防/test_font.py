import pygame

# 初始化pygame
pygame.init()

# 创建一个小窗口
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("字体测试")

# 尝试使用默认字体
font = pygame.font.Font(None, 36)

# 渲染测试文字
test_text = font.render("测试文字 - 中文显示", True, (255, 255, 255))

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 填充背景
    screen.fill((30, 30, 50))
    
    # 绘制文字
    screen.blit(test_text, (50, 100))
    
    # 更新显示
    pygame.display.flip()

# 退出pygame
pygame.quit()
