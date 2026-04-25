import os
import time
import random
import msvcrt

WIDTH = 40
HEIGHT = 20

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 2
        self.lives = 3
        self.score = 0
        self.bombs = 3
        self.bullet_type = "normal"
    
    def move_left(self):
        if self.x > 0:
            self.x -= 1
    
    def move_right(self):
        if self.x < WIDTH - 1:
            self.x += 1
    
    def move_up(self):
        if self.y > 0:
            self.y -= 1
    
    def move_down(self):
        if self.y < HEIGHT - 1:
            self.y += 1

class Bullet:
    def __init__(self, x, y, bullet_type="normal"):
        self.x = x
        self.y = y
        self.type = bullet_type
    
    def update(self):
        self.y -= 1
        return self.y >= 0

class Enemy:
    def __init__(self, level):
        self.x = random.randint(0, WIDTH - 1)
        self.y = 0
        self.speed = 1 + level // 2
        self.health = 1 + level
        self.drop_item = random.random() < 0.1

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
    
    def update(self):
        self.y += 1
        return self.y < HEIGHT

class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.items = []
        self.level = 1
        self.max_level = 3
        self.enemy_spawn_rate = 20
        self.enemy_spawn_count = 0
        self.running = True
        self.game_over = False
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def draw(self):
        self.clear_screen()
        
        screen = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
        
        screen[self.player.y][self.player.x] = 'A'
        
        for bullet in self.bullets:
            if 0 <= bullet.y < HEIGHT and 0 <= bullet.x < WIDTH:
                screen[bullet.y][bullet.x] = '*'
        
        for enemy in self.enemies:
            if 0