import pygame
import sys
import math
import random
import time

pygame.init()

WIDTH, HEIGHT = 1200, 800
FPS = 60
CELL_SIZE = 40

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
DOOR_COLOR = (255, 100, 0)
DOOR_FRAME_COLOR = (200, 50, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("猎梦者")
clock = pygame.time.Clock()

font_names = ['microsoftyahei', 'simhei', 'msyh', 'arialunicode', 'simsun']
font = None
for font_name in font_names:
    try:
        font = pygame.font.SysFont(font_name, 24)
        break
    except:
        continue

if font is None:
    font = pygame.font.Font(None, 24)

small_font_names = ['microsoftyahei', 'simhei', 'msyh', 'arialunicode', 'simsun']
small_font = None
for font_name in small_font_names:
    try:
        small_font = pygame.font.SysFont(font_name, 18)
        break
    except:
        continue

if small_font is None:
    small_font = pygame.font.Font(None, 18)

title_font_names = ['microsoftyahei', 'simhei', 'msyh', 'arialunicode', 'simsun']
title_font = None
for font_name in title_font_names:
    try:
        title_font = pygame.font.SysFont(font_name, 48)
        break
    except:
        continue

if title_font is None:
    title_font = pygame.font.Font(None, 48)

class Grid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = width // cell_size
        self.rows = height // cell_size
        self.cells = {}
        self.dormitories = []
        self.corridors = []
        self.doors = []
        self.generate_map()

    def generate_map(self):
        self.cells = {}
        for x in range(self.cols):
            for y in range(self.rows):
                self.cells[(x, y)] = "empty"

        corridor_y = self.rows // 2
        for x in range(1, self.cols - 1):
            self.cells[(x, corridor_y)] = "corridor"
            self.corridors.append((x, corridor_y))

        dorm_positions = [
            (3, 3, 4, 3),
            (12, 3, 5, 4),
            (20, 3, 4, 3),
            (3, 12, 5, 4),
            (12, 12, 4, 5),
            (20, 12, 4, 3)
        ]

        inner_rooms = []
        if random.random() < 0.3:
            inner_rooms.append((4, 4, 2, 2))
        if random.random() < 0.3:
            inner_rooms.append((13, 4, 2, 2))
        if random.random() < 0.3:
            inner_rooms.append((4, 13, 2, 2))
        if random.random() < 0.3:
            inner_rooms.append((13, 13, 2, 2))

        for i, (start_x, start_y, width, height) in enumerate(dorm_positions):
            dorm = Dormitory(start_x, start_y, width, height, i + 1)
            self.dormitories.append(dorm)
            
            for dx in range(width):
                for dy in range(height):
                    self.cells[(start_x + dx, start_y + dy)] = "dormitory"
                    dorm.cells.append((start_x + dx, start_y + dy))
            
            door_x = start_x + width // 2
            door_y = start_y + height
            self.cells[(door_x, door_y)] = "door"
            door = Door(door_x, door_y, dorm)
            self.doors.append(door)
            dorm.door = door

        for i, (start_x, start_y, width, height) in enumerate(inner_rooms):
            inner_dorm = Dormitory(start_x, start_y, width, height, i + 10)
            self.dormitories.append(inner_dorm)
            
            for dx in range(width):
                for dy in range(height):
                    self.cells[(start_x + dx, start_y + dy)] = "inner_dormitory"
                    inner_dorm.cells.append((start_x + dx, start_y + dy))
            
            door_x = start_x + width // 2
            door_y = start_y - 1
            self.cells[(door_x, door_y)] = "inner_door"
            door = Door(door_x, door_y, inner_dorm)
            self.doors.append(door)
            inner_dorm.door = door

    def get_cell(self, x, y):
        cell_x = x // self.cell_size
        cell_y = y // self.cell_size
        return (cell_x, cell_y), self.cells.get((cell_x, cell_y), "empty")

    def is_walkable(self, cell_x, cell_y):
        cell_type = self.cells.get((cell_x, cell_y), "empty")
        return cell_type in ["empty", "corridor", "door", "inner_door"]

    def draw(self, surface):
        for x in range(self.cols):
            for y in range(self.rows):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                
                cell_type = self.cells.get((x, y), "empty")
                
                if cell_type == "corridor":
                    pygame.draw.rect(surface, LIGHT_GRAY, rect)
                    pygame.draw.rect(surface, GRAY, rect, 1)
                elif cell_type == "dormitory":
                    pygame.draw.rect(surface, BROWN, rect)
                    pygame.draw.rect(surface, DARK_BROWN, rect, 1)
                elif cell_type == "inner_dormitory":
                    pygame.draw.rect(surface, (100, 50, 0), rect)
                    pygame.draw.rect(surface, (80, 40, 0), rect, 1)
                elif cell_type == "door":
                    pygame.draw.rect(surface, DOOR_COLOR, rect)
                    pygame.draw.rect(surface, DOOR_FRAME_COLOR, rect, 3)
                elif cell_type == "inner_door":
                    pygame.draw.rect(surface, (255, 150, 50), rect)
                    pygame.draw.rect(surface, (200, 100, 0), rect, 2)
                else:
                    pygame.draw.rect(surface, WHITE, rect)
                    pygame.draw.rect(surface, GRAY, rect, 1)

        for dorm in self.dormitories:
            dorm.draw(surface)

    def update_doors(self):
        for door in self.doors:
            door.update()

        for door in self.doors:
            door.update()
            door.draw(surface)

class Dormitory:
    def __init__(self, start_x, start_y, width, height, level):
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.level = level
        self.cells = []
        self.door = None
        self.has_bed = True
        self.bed_level = level
        self.capacity = width * height
        self.current_occupants = 0
        self.bed_x = start_x + width // 2
        self.bed_y = start_y + height // 2

    def draw(self, surface):
        rect = pygame.Rect(
            self.start_x * CELL_SIZE,
            self.start_y * CELL_SIZE,
            self.width * CELL_SIZE,
            self.height * CELL_SIZE
        )
        
        if self.level >= 10:
            pygame.draw.rect(surface, (100, 50, 0), rect)
            pygame.draw.rect(surface, (80, 40, 0), rect, 3)
        else:
            pygame.draw.rect(surface, BROWN, rect)
            pygame.draw.rect(surface, DARK_BROWN, rect, 3)
        
        level_text = small_font.render(f"宿舍 Lv.{self.level}", True, WHITE)
        surface.blit(level_text, (rect.centerx - level_text.get_width() // 2, rect.centery - 15))
        
        if self.has_bed:
            bed_rect = pygame.Rect(
                self.bed_x * CELL_SIZE + 5,
                self.bed_y * CELL_SIZE + 5,
                CELL_SIZE - 10,
                CELL_SIZE - 10
            )
            pygame.draw.rect(surface, (200, 200, 200), bed_rect)
            pygame.draw.rect(surface, (150, 150, 150), bed_rect, 2)
            bed_text = small_font.render("床", True, BLACK)
            surface.blit(bed_text, (bed_rect.centerx - bed_text.get_width() // 2, bed_rect.centery - 8))

class Door:
    def __init__(self, cell_x, cell_y, dormitory):
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.x = cell_x * CELL_SIZE + CELL_SIZE // 2
        self.y = cell_y * CELL_SIZE + CELL_SIZE // 2
        self.dormitory = dormitory
        self.level = 1
        self.is_closed = False
        self.defense = self.level * 10
        self.slide_offset = 0
        self.target_slide_offset = 0

    def upgrade(self):
        self.level += 1
        self.defense = self.level * 10

    def update(self):
        if self.is_closed:
            self.target_slide_offset = CELL_SIZE - 5
        else:
            self.target_slide_offset = 0
        
        if self.slide_offset < self.target_slide_offset:
            self.slide_offset += 2
        elif self.slide_offset > self.target_slide_offset:
            self.slide_offset -= 2

    def draw(self, surface):
        self.update()
        
        rect = pygame.Rect(
            self.cell_x * CELL_SIZE,
            self.cell_y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        
        door_color = RED if self.is_closed else DOOR_COLOR
        pygame.draw.rect(surface, DOOR_FRAME_COLOR, rect, 4)
        
        door_rect = pygame.Rect(
            self.cell_x * CELL_SIZE + 2,
            self.cell_y * CELL_SIZE + 2 + self.slide_offset,
            CELL_SIZE - 4,
            CELL_SIZE - 4 - self.slide_offset
        )
        pygame.draw.rect(surface, door_color, door_rect)
        
        level_text = small_font.render(f"Lv.{self.level}", True, WHITE)
        surface.blit(level_text, (rect.centerx - level_text.get_width() // 2, rect.centery - 8))
        
        status_text = small_font.render("关" if self.is_closed else "开", True, WHITE)
        surface.blit(status_text, (rect.centerx - status_text.get_width() // 2, rect.centery + 8))

class Player:
    def __init__(self, x, y, is_human=False, name="AI玩家"):
        self.x = x
        self.y = y
        self.is_human = is_human
        self.name = name
        self.health = 100
        self.max_health = 100
        self.energy = 100
        self.max_energy = 100
        self.speed = 3
        self.radius = 15
        self.color = GREEN if is_human else BLUE
        self.gold = 100
        self.towers = []
        self.beds = []
        self.doors = []
        self.technology_level = 1
        self.power = 100
        self.max_power = 100
        self.power_production = 1
        self.alive = True
        self.in_dormitory = False
        self.current_dormitory = None
        self.bed_level = 1
        self.door_level = 1
        self.items = []
        self.shield = 0
        self.max_shield = 0
        self.is_dream_hunter = False
        self.alliance_fragments = 0

    def move(self, dx, dy, grid):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        cell_pos, cell_type = grid.get_cell(new_x, new_y)
        
        if not grid.is_walkable(cell_pos[0], cell_pos[1]):
            return
        
        if cell_type == "door" or cell_type == "inner_door":
            for door in grid.doors:
                if door.cell_x == cell_pos[0] and door.cell_y == cell_pos[1]:
                    if not door.is_closed:
                        self.enter_dormitory(door.dormitory)
                    return
        
        if cell_type == "dormitory" or cell_type == "inner_dormitory":
            for dorm in grid.dormitories:
                if (cell_pos[0], cell_pos[1]) in dorm.cells:
                    if not self.in_dormitory:
                        self.enter_dormitory(dorm)
                    return
        
        self.x = new_x
        self.y = new_y

    def enter_dormitory(self, dormitory):
        if self.in_dormitory:
            return
        
        self.in_dormitory = True
        self.current_dormitory = dormitory
        dormitory.current_occupants += 1

    def leave_dormitory(self):
        if not self.in_dormitory:
            return
        
        if self.current_dormitory:
            self.current_dormitory.current_occupants -= 1
            self.current_dormitory = None
        self.in_dormitory = False

    def rest_in_bed(self):
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + 1)
            return True
        return False

    def is_near_door(self, grid):
        for door in grid.doors:
            distance = math.sqrt((door.x - self.x) ** 2 + (door.y - self.y) ** 2)
            if distance < 50:
                return door
        return None

    def is_near_bed(self, grid):
        for dorm in grid.dormitories:
            if dorm.has_bed:
                bed_x = dorm.bed_x * CELL_SIZE + CELL_SIZE // 2
                bed_y = dorm.bed_y * CELL_SIZE + CELL_SIZE // 2
                distance = math.sqrt((bed_x - self.x) ** 2 + (bed_y - self.y) ** 2)
                if distance < 50:
                    return dorm
        return None

    def toggle_door(self, door):
        door.is_closed = not door.is_closed

    def use_bed(self, dorm):
        if not self.in_dormitory:
            self.enter_dormitory(dorm)
        self.rest_in_bed()

    def produce_gold(self):
        gold_per_second = self.bed_level
        return gold_per_second

    def upgrade_bed(self):
        if self.gold >= self.bed_level * 100:
            self.gold -= self.bed_level * 100
            self.bed_level += 1
            return True
        return False

    def upgrade_door(self):
        if self.gold >= self.door_level * 80:
            self.gold -= self.door_level * 80
            self.door_level += 1
            return True
        return False

    def draw(self, surface):
        color = MAGENTA if self.is_dream_hunter else self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        name_text = small_font.render(self.name, True, BLACK)
        surface.blit(name_text, (self.x - name_text.get_width() // 2, self.y - 30))
        
        health_bar_width = 40
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.x - health_bar_width // 2, self.y - self.radius - 15, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, GREEN, (self.x - health_bar_width // 2, self.y - self.radius - 15, health_bar_width * health_percentage, health_bar_height))
        
        if self.shield > 0:
            shield_bar_width = 40
            shield_bar_height = 3
            shield_percentage = self.shield / self.max_shield
            pygame.draw.rect(surface, BLUE, (self.x - shield_bar_width // 2, self.y - self.radius - 11, shield_bar_width, shield_bar_height))
            pygame.draw.rect(surface, CYAN, (self.x - shield_bar_width // 2, self.y - self.radius - 11, shield_bar_width * shield_percentage, shield_bar_height))
        
        energy_bar_width = 40
        energy_bar_height = 5
        energy_percentage = self.energy / self.max_energy
        pygame.draw.rect(surface, GRAY, (self.x - energy_bar_width // 2, self.y - self.radius - 8, energy_bar_width, energy_bar_height))
        pygame.draw.rect(surface, CYAN, (self.x - energy_bar_width // 2, self.y - self.radius - 8, energy_bar_width * energy_percentage, energy_bar_height))

class Tower:
    def __init__(self, x, y, level=1):
        self.x = x
        self.y = y
        self.level = level
        self.radius = 20
        self.range = 150
        self.damage = 20
        self.cooldown = 60
        self.current_cooldown = 0
        self.color = PURPLE

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.3)
        self.range = int(self.range * 1.1)
        self.cooldown = max(10, int(self.cooldown * 0.85))

    def update(self, enemies):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
        
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            distance = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
            if distance < self.range and self.current_cooldown <= 0:
                enemy.health -= self.damage
                self.current_cooldown = self.cooldown
                break

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        level_text = small_font.render(f"炮塔 Lv.{self.level}", True, WHITE)
        surface.blit(level_text, (self.x - level_text.get_width() // 2, self.y - 30))
        
        range_circle = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_circle, (self.color[0], self.color[1], self.color[2], 50), (self.range, self.range), self.range)
        surface.blit(range_circle, (self.x - self.range, self.y - self.range))

class Enemy:
    def __init__(self, x, y, difficulty=1):
        self.x = x
        self.y = y
        self.health = 50 * difficulty
        self.max_health = self.health
        self.speed = 2 + difficulty * 0.5
        self.radius = 15
        self.color = RED
        self.damage = 10 * difficulty
        self.alive = True
        self.target = None

    def move_towards(self, target):
        if not target or not target.alive:
            return
        
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def attack(self, target):
        if target.alive:
            damage = self.damage
            
            if target.shield > 0:
                shield_damage = min(target.shield, damage)
                target.shield -= shield_damage
                damage -= shield_damage
            
            if damage > 0:
                target.health -= damage
                if target.health <= 0:
                    target.alive = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        health_bar_width = 30
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.x - health_bar_width // 2, self.y - self.radius - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, GREEN, (self.x - health_bar_width // 2, self.y - self.radius - 10, health_bar_width * health_percentage, health_bar_height))

class Item:
    def __init__(self, name, cost, effect_type, effect_value):
        self.name = name
        self.cost = cost
        self.effect_type = effect_type
        self.effect_value = effect_value

class Shop:
    def __init__(self):
        self.items = [
            Item("恢复药水", 50, "health", 30),
            Item("能量饮料", 30, "energy", 50),
            Item("护盾发生器", 200, "shield", 50),
            Item("速度提升", 100, "speed", 1.5),
            Item("攻击力提升", 150, "damage", 10),
            Item("生命值提升", 120, "max_health", 20),
            Item("联盟碎片", 150, "alliance_fragment", 1)
        ]

class Game:
    def __init__(self):
        self.state = "menu"
        self.difficulty = 1
        self.difficulty_names = ["简单", "普通", "困难", "炼狱"]
        self.players = []
        self.human_player = None
        self.enemies = []
        self.towers = []
        self.shop = Shop()
        self.round = 1
        self.max_rounds = 5
        self.gold_timer = 0
        self.game_over = False
        self.winner = None
        self.grid = None
        self.preparation_time = 20
        self.preparation_timer = 0
        self.game_started = False

    def start_game(self, difficulty, player_count):
        self.difficulty = difficulty
        self.round = 1
        self.game_over = False
        self.winner = None
        self.game_started = False
        self.preparation_timer = self.preparation_time
        
        self.grid = Grid(WIDTH, HEIGHT - 100, CELL_SIZE)
        
        self.players = []
        self.human_player = Player(100, 400, True, "幸存者")
        self.players.append(self.human_player)
        
        for i in range(player_count - 1):
            ai_player = Player(100 + i * 50, 400 + i * 30, False, f"AI玩家{i+1}")
            self.players.append(ai_player)
        
        self.enemies = []
        self.spawn_enemies()
        
        self.towers = []
        for player in self.players:
            player.towers = []
            player.beds = []
            player.doors = []

    def spawn_enemies(self):
        count = 3 + self.difficulty * 2
        for i in range(count):
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 150)
            enemy = Enemy(x, y, self.difficulty)
            self.enemies.append(enemy)

    def update(self):
        if not self.game_started:
            return
        
        if self.game_over:
            return
        
        self.gold_timer += 1
        if self.gold_timer >= 60:
            for player in self.players:
                if player.alive and player.in_dormitory and player.current_dormitory.has_bed:
                    gold_produced = player.produce_gold()
                    player.gold += gold_produced
            self.gold_timer = 0
        
        for player in self.players:
            if not player.alive:
                continue
            
            if player == self.human_player:
                continue
            
            self.ai_player_action(player)
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            closest_player = None
            closest_distance = 500
            
            for player in self.players:
                if not player.alive:
                    continue
                
                distance = math.sqrt((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player = player
            
            if closest_player:
                enemy.target = closest_player
                enemy.move_towards(closest_player)
                
                distance = math.sqrt((closest_player.x - enemy.x) ** 2 + (closest_player.y - enemy.y) ** 2)
                if distance < 30:
                    enemy.attack(closest_player)
        
        for player in self.players:
            if not player.alive:
                continue
            
            for tower in player.towers:
                tower.update(self.enemies)
        
        self.check_game_over()

    def ai_player_action(self, player):
        if random.random() < 0.02:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            player.move(dx, dy, self.grid)
        
        if player.gold >= player.bed_level * 100 and random.random() < 0.01:
            player.upgrade_bed()
        
        if player.gold >= player.door_level * 80 and random.random() < 0.01:
            player.upgrade_door()
        
        if player.gold >= 100 and random.random() < 0.02:
            self.buy_tower_for_ai(player)
        
        if random.random() < 0.01:
            door = player.is_near_door(self.grid)
            if door:
                player.toggle_door(door)
        
        if random.random() < 0.02:
            dorm = player.is_near_bed(self.grid)
            if dorm:
                player.use_bed(dorm)

    def buy_tower_for_ai(self, player):
        if len(player.towers) < 3:
            tower = Tower(player.x + 30, player.y + 30, 1)
            player.towers.append(tower)
            player.gold -= 100

    def check_game_over(self):
        if not self.human_player.alive:
            self.game_over = True
            self.winner = None
            return
        
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) == 1:
            self.game_over = True
            self.winner = alive_players[0]

    def end_round(self):
        self.round += 1
        if self.round > self.max_rounds:
            self.game_over = True
            self.winner = self.human_player if self.human_player.alive else None

    def draw_menu(self, surface):
        surface.fill(WHITE)
        
        title_text = title_font.render("猎梦者", True, PURPLE)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        subtitle_text = font.render("选择游戏模式", True, BLACK)
        surface.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 180))
        
        button_y = 250
        for i, difficulty_name in enumerate(self.difficulty_names):
            button_rect = pygame.Rect(WIDTH // 2 - 150, button_y, 300, 50)
            pygame.draw.rect(surface, BLUE, button_rect)
            pygame.draw.rect(surface, BLACK, button_rect, 2)
            
            text = font.render(difficulty_name, True, WHITE)
            surface.blit(text, (button_rect.centerx - text.get_width() // 2, button_rect.centery - text.get_height() // 2))
            
            button_y += 70

        start_text = font.render("点击选择难度开始游戏", True, GREEN)
        surface.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 100))

    def draw_preparation(self, surface):
        self.grid.draw(surface)
        
        for player in self.players:
            if player.alive:
                player.draw(surface)
        
        overlay = pygame.Surface((WIDTH, 200))
        overlay.set_alpha(230)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, HEIGHT // 2 - 100))
        
        title_text = title_font.render("准备时间", True, YELLOW)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        
        timer_text = title_font.render(f"{int(self.preparation_timer)}", True, RED)
        surface.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, HEIGHT // 2 - 20))
        
        instruction_text = font.render("移动鼠标选择宿舍，倒计时结束后游戏开始", True, LIGHT_GRAY)
        surface.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2 + 50))

    def draw_game(self, surface):
        self.grid.draw(surface)
        
        for player in self.players:
            if player.alive:
                player.draw(surface)
        
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(surface)
        
        for player in self.players:
            for tower in player.towers:
                tower.draw(surface)
        
        self.draw_ui(surface)

    def draw_ui(self, surface):
        ui_height = 100
        pygame.draw.rect(surface, DARK_GRAY, (0, HEIGHT - ui_height, WIDTH, ui_height))
        
        if self.human_player.alive:
            gold_text = font.render(f"金币: {self.human_player.gold}", True, YELLOW)
            lives_text = font.render(f"生命: {self.human_player.health}/{self.human_player.max_health}", True, RED)
            energy_text = font.render(f"精力: {self.human_player.energy}/{self.human_player.max_energy}", True, CYAN)
            power_text = font.render(f"电力: {self.human_player.power}/{self.human_player.max_power}", True, (255, 255, 0))
            round_text = font.render(f"轮次: {self.round}/{self.max_rounds}", True, WHITE)
            difficulty_text = font.render(f"难度: {self.difficulty_names[self.difficulty-1]}", True, ORANGE)
            
            surface.blit(gold_text, (20, HEIGHT - 80))
            surface.blit(lives_text, (200, HEIGHT - 80))
            surface.blit(energy_text, (400, HEIGHT - 80))
            surface.blit(power_text, (600, HEIGHT - 80))
            surface.blit(round_text, (800, HEIGHT - 80))
            surface.blit(difficulty_text, (1000, HEIGHT - 80))
            
            bed_upgrade_cost = self.human_player.bed_level * 100
            door_upgrade_cost = self.human_player.door_level * 80
            
            bed_text = small_font.render(f"床 Lv.{self.human_player.bed_level} (升级: {bed_upgrade_cost}金币)", True, GREEN)
            door_text = small_font.render(f"门 Lv.{self.human_player.door_level} (升级: {door_upgrade_cost}金币)", True, ORANGE)
            tower_text = small_font.render(f"炮塔数量: {len(self.human_player.towers)} (建造: 100金币)", True, PURPLE)
            fragment_text = small_font.render(f"联盟碎片: {self.human_player.alliance_fragments}/5", True, MAGENTA if self.human_player.is_dream_hunter else WHITE)
            
            surface.blit(bed_text, (20, HEIGHT - 50))
            surface.blit(door_text, (20, HEIGHT - 30))
            surface.blit(tower_text, (250, HEIGHT - 50))
            surface.blit(fragment_text, (250, HEIGHT - 30))
            
            next_round_button = pygame.Rect(WIDTH - 400, HEIGHT - 80, 180, 70)
            pygame.draw.rect(surface, GREEN, next_round_button)
            pygame.draw.rect(surface, BLACK, next_round_button, 2)
            
            next_text = font.render("下一轮", True, WHITE)
            surface.blit(next_text, (next_round_button.centerx - next_text.get_width() // 2, next_round_button.centery - next_text.get_height() // 2))
            
            shop_button = pygame.Rect(WIDTH - 200, HEIGHT - 80, 180, 70)
            pygame.draw.rect(surface, PURPLE, shop_button)
            pygame.draw.rect(surface, BLACK, shop_button, 2)
            
            shop_text = font.render("商店", True, WHITE)
            surface.blit(shop_text, (shop_button.centerx - shop_text.get_width() // 2, shop_button.centery - shop_text.get_height() // 2))

    def draw_shop(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        title_text = title_font.render("商店", True, WHITE)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        item_y = 200
        for i, item in enumerate(self.shop.items):
            item_rect = pygame.Rect(200, item_y, 800, 60)
            pygame.draw.rect(surface, LIGHT_GRAY, item_rect)
            pygame.draw.rect(surface, BLACK, item_rect, 2)
            
            name_text = font.render(item.name, True, BLACK)
            cost_text = font.render(f"{item.cost}金币", True, YELLOW)
            effect_text = small_font.render(f"{item.effect_type}: +{item.effect_value}", True, GREEN)
            
            surface.blit(name_text, (item_rect.x + 20, item_rect.centery - 10))
            surface.blit(cost_text, (item_rect.right - 150, item_rect.centery - 10))
            surface.blit(effect_text, (item_rect.x + 20, item_rect.centery + 15))
            
            item_y += 80
        
        close_text = font.render("按ESC关闭商店", True, WHITE)
        surface.blit(close_text, (WIDTH // 2 - close_text.get_width() // 2, HEIGHT - 100))

    def draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        if self.winner:
            if self.winner == self.human_player:
                game_over_text = title_font.render("恭喜！你赢了！", True, GREEN)
            else:
                game_over_text = title_font.render(f"{self.winner.name} 获胜！", True, RED)
        else:
            game_over_text = title_font.render("游戏结束", True, RED)
        
        surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        
        restart_text = font.render("按R键重新开始", True, WHITE)
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

def main():
    game = Game()
    
    running = True
    shop_open = False
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif game.state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    button_y = 250
                    for i in range(len(game.difficulty_names)):
                        button_rect = pygame.Rect(WIDTH // 2 - 150, button_y, 300, 50)
                        if button_rect.collidepoint(x, y):
                            game.start_game(i + 1, 2)
                            game.state = "preparation"
                        button_y += 70
            
            elif game.state == "preparation":
                if event.type == pygame.MOUSEMOTION:
                    if game.human_player.alive:
                        x, y = pygame.mouse.get_pos()
                        dx = 0
                        dy = 0
                        
                        if x < game.human_player.x - 10:
                            dx = -1
                        elif x > game.human_player.x + 10:
                            dx = 1
                        
                        if y < game.human_player.y - 10:
                            dy = -1
                        elif y > game.human_player.y + 10:
                            dy = 1
                        
                        if dx != 0 or dy != 0:
                            game.human_player.move(dx, dy, game.grid)
            
            elif game.state == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        shop_open = not shop_open
                    
                    elif event.key == pygame.K_SPACE:
                        if game.human_player.in_dormitory:
                            game.human_player.rest_in_bed()
                    
                    elif event.key == pygame.K_r and game.game_over:
                        game.state = "menu"
                    
                    elif event.key == pygame.K_n and not game.game_over:
                        game.end_round()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = pygame.mouse.get_pos()
                        
                        if not shop_open and y < HEIGHT - 100:
                            door = game.human_player.is_near_door(game.grid)
                            if door:
                                game.human_player.toggle_door(door)
                            
                            dorm = game.human_player.is_near_bed(game.grid)
                            if dorm:
                                game.human_player.use_bed(dorm)
                        
                        if shop_open:
                            item_y = 200
                            for item in game.shop.items:
                                item_rect = pygame.Rect(200, item_y, 800, 60)
                                if item_rect.collidepoint(x, y):
                                    if game.human_player.gold >= item.cost:
                                        game.human_player.gold -= item.cost
                                        if item.effect_type == "health":
                                            game.human_player.health = min(game.human_player.max_health, game.human_player.health + item.effect_value)
                                        elif item.effect_type == "energy":
                                            game.human_player.energy = min(game.human_player.max_energy, game.human_player.energy + item.effect_value)
                                        elif item.effect_type == "shield":
                                            game.human_player.max_shield += item.effect_value
                                            game.human_player.shield = game.human_player.max_shield
                                        elif item.effect_type == "speed":
                                            game.human_player.speed = min(6, game.human_player.speed + item.effect_value)
                                        elif item.effect_type == "damage":
                                            for tower in game.human_player.towers:
                                                tower.damage += item.effect_value
                                        elif item.effect_type == "max_health":
                                            game.human_player.max_health += item.effect_value
                                            game.human_player.health += item.effect_value
                                        elif item.effect_type == "alliance_fragment":
                                            game.human_player.alliance_fragments += item.effect_value
                                            if game.human_player.alliance_fragments >= 5:
                                                game.human_player.is_dream_hunter = True
                                                game.human_player.name = "猎梦者"
                                item_y += 80
                        elif y > HEIGHT - 100:
                            shop_button = pygame.Rect(WIDTH - 200, HEIGHT - 80, 180, 70)
                            if shop_button.collidepoint(x, y):
                                shop_open = not shop_open
                            
                            next_round_button = pygame.Rect(WIDTH - 400, HEIGHT - 80, 180, 70)
                            if next_round_button.collidepoint(x, y):
                                game.end_round()
                            
                            tower_button = pygame.Rect(250, HEIGHT - 50, 250, 20)
                            if tower_button.collidepoint(x, y):
                                if game.human_player.gold >= 100 and len(game.human_player.towers) < 5:
                                    game.human_player.gold -= 100
                                    tower = Tower(game.human_player.x + 30, game.human_player.y + 30, 1)
                                    game.human_player.towers.append(tower)
                        else:
                            if game.human_player.gold >= game.human_player.bed_level * 100:
                                bed_button = pygame.Rect(20, HEIGHT - 50, 200, 20)
                                if bed_button.collidepoint(x, y):
                                    game.human_player.upgrade_bed()
                            
                            if game.human_player.gold >= game.human_player.door_level * 80:
                                door_button = pygame.Rect(20, HEIGHT - 30, 200, 20)
                                if door_button.collidepoint(x, y):
                                    game.human_player.upgrade_door()
                
                elif event.type == pygame.MOUSEMOTION:
                    if game.human_player.alive:
                        x, y = pygame.mouse.get_pos()
                        dx = 0
                        dy = 0
                        
                        if x < game.human_player.x - 10:
                            dx = -1
                        elif x > game.human_player.x + 10:
                            dx = 1
                        
                        if y < game.human_player.y - 10:
                            dy = -1
                        elif y > game.human_player.y + 10:
                            dy = 1
                        
                        if dx != 0 or dy != 0:
                            game.human_player.move(dx, dy, game.grid)
        
        if game.state == "menu":
            game.draw_menu(screen)
        elif game.state == "preparation":
            game.preparation_timer -= 1 / FPS
            game.grid.update_doors()
            game.draw_preparation(screen)
            
            if game.preparation_timer <= 0:
                game.game_started = True
                game.state = "game"
        elif game.state == "game":
            if not shop_open:
                game.update()
                game.grid.update_doors()
                game.draw_game(screen)
                if game.game_over:
                    game.draw_game_over(screen)
            else:
                game.draw_game(screen)
                game.draw_shop(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
