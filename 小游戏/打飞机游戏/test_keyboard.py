import pygame

pygame.init()

WIDTH, HEIGHT = 400, 300
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("键盘测试")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.SysFont(None, 36)

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            print(f"按键被按下: {pygame.key.name(event.key)} (键码: {event.key})")
            if event.key == pygame.K_ESCAPE:
                running = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        print("W键被持续按下")
    if keys[pygame.K_a]:
        print("A键被持续按下")
    if keys[pygame.K_s]:
        print("S键被持续按下")
    if keys[pygame.K_d]:
        print("D键被持续按下")
    
    WIN.fill(WHITE)
    text = font.render("按下WASD键测试", True, BLACK)
    WIN.blit(text, (50, 100))
    pygame.display.update()

pygame.quit()