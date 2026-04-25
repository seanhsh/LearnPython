import pygame
import sys

# 测试游戏导入
print("Testing game import...")
try:
    from plane_game import Game
    print("✓ Game imported successfully")
except Exception as e:
    print(f"✗ Error importing game: {e}")
    sys.exit(1)

# 测试pygame初始化
print("Testing pygame initialization...")
try:
    pygame.init()
    print(f"✓ Pygame initialized: {pygame.version.ver}")
except Exception as e:
    print(f"✗ Error initializing pygame: {e}")
    sys.exit(1)

# 测试游戏创建
print("Testing game creation...")
try:
    game = Game()
    print("✓ Game created successfully")
except Exception as e:
    print(f"✗ Error creating game: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("All tests passed! The game should run correctly.")
pygame.quit()
