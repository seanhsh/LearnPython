import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 1200, 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

# 直接使用pygame的内置默认字体，避免触发系统字体初始化
# 内置默认字体不依赖系统字体注册表，应该能够正确显示基本文字
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 20)

# 测试字体渲染
print("Font created:", font)
print("Small font created:", small_font)

# 游戏模式配置
GAME_MODES = {
    "easy": {
        "name": "Easy Mode",
        "description": "For beginners, weaker enemies, fewer waves",
        "total_waves": 10,
        "enemy_health_mult": 0.7,
        "enemy_speed_mult": 0.8,
        "enemy_damage_mult": 0.5,
        "gold_mult": 1.5,
        "start_gold": 200,
        "start_lives": 30,
        "color": GREEN,
        "path_type": "simple"  # Simple map
    },
    "normal": {
        "name": "Normal Mode",
        "description": "Standard difficulty, balanced gameplay",
        "total_waves": 15,
        "enemy_health_mult": 1.0,
        "enemy_speed_mult": 1.0,
        "enemy_damage_mult": 1.0,
        "gold_mult": 1.0,
        "start_gold": 150,
        "start_lives": 20,
        "color": BLUE,
        "path_type": "normal"  # Normal map
    },
    "hard": {
        "name": "Hard Mode",
        "description": "Stronger enemies, more waves",
        "total_waves": 20,
        "enemy_health_mult": 1.3,
        "enemy_speed_mult": 1.2,
        "enemy_damage_mult": 1.5,
        "gold_mult": 0.8,
        "start_gold": 120,
        "start_lives": 15,
        "color": ORANGE,
        "path_type": "hard"  # Hard map
    },
    "hell": {
        "name": "Hell Mode",
        "description": "Extremely challenging, only for experts",
        "total_waves": 25,
        "enemy_health_mult": 1.8,
        "enemy_speed_mult": 1.4,
        "enemy_damage_mult": 2.0,
        "gold_mult": 0.6,
        "start_gold": 100,
        "start_lives": 10,
        "color": RED,
        "path_type": "hell"  # Hell map
    },
    "endless": {
        "name": "Endless Mode",
        "description": "Infinite waves, see how long you can last",
        "total_waves": -1,  # -1 means infinite
        "enemy_health_mult": 1.0,
        "enemy_speed_mult": 1.0,
        "enemy_damage_mult": 1.0,
        "gold_mult": 1.0,
        "start_gold": 150,
        "start_lives": 20,
        "color": PURPLE,
        "path_type": "random"  # Random map
    }
}

# 地图配置 - 按难度分类
# 所有路径都是线性设计：从左边进入，从右边出去
PATH_CONFIGS = {
    "simple": [
        # 简单地图：直线路径，转弯少
        [(0, 300), (1000, 300)],
        [(0, 200), (500, 200), (500, 400), (1000, 400)],
        [(0, 350), (300, 350), (300, 200), (700, 200), (700, 350), (1000, 350)],
    ],
    "normal": [
        # 普通地图：S形，之字形
        [(0, 100), (200, 100), (200, 400), (400, 400), (400, 200), (600, 200), (600, 500), (800, 500), (800, 300), (1000, 300)],
        [(0, 500), (300, 500), (300, 100), (600, 100), (600, 400), (900, 400), (900, 250), (1000, 250)],
        [(0, 400), (200, 400), (200, 200), (400, 200), (400, 500), (600, 500), (600, 100), (800, 100), (800, 350), (1000, 350)],
    ],
    "hard": [
        # 困难地图：螺旋形，多转弯
        [(0, 300), (150, 300), (150, 150), (350, 150), (350, 450), (550, 450), (550, 250), (750, 250), (750, 350), (950, 350), (950, 200), (1000, 200)],
        [(0, 150), (150, 150), (150, 450), (300, 450), (300, 100), (500, 100), (500, 350), (700, 350), (700, 200), (900, 200), (900, 400), (1000, 400)],
        [(0, 500), (100, 500), (100, 100), (400, 100), (400, 500), (500, 500), (500, 150), (750, 150), (750, 450), (900, 450), (900, 250), (1000, 250)],
    ],
    "hell": [
        # 炼狱地图：复杂迷宫，超长路径
        [(0, 300), (50, 300), (50, 100), (200, 100), (200, 500), (350, 500), (350, 150), (500, 150), (500, 450), (650, 450), (650, 100), (800, 100), (800, 400), (950, 400), (950, 250), (1000, 250)],
        [(0, 100), (100, 100), (100, 500), (250, 500), (250, 150), (400, 150), (400, 550), (550, 550), (550, 100), (700, 100), (700, 500), (850, 500), (850, 200), (1000, 200)],
        [(0, 400), (80, 400), (80, 150), (200, 150), (200, 500), (320, 500), (320, 100), (440, 100), (440, 450), (560, 450), (560, 150), (680, 150), (680, 500), (800, 500), (800, 200), (920, 200), (920, 350), (1000, 350)],
    ]
}

class Enemy:
    def __init__(self, path, enemy_type="normal", wave=1, mode_config=None):
        self.path = path
        self.path_index = 0
        self.x, self.y = path[0]
        self.enemy_type = enemy_type
        self.alive = True
        self.reached_end = False
        
        # 获取模式配置
        if mode_config is None:
            mode_config = GAME_MODES["normal"]
        
        health_mult = mode_config["enemy_health_mult"]
        speed_mult = mode_config["enemy_speed_mult"]
        damage_mult = mode_config["enemy_damage_mult"]
        gold_mult = mode_config["gold_mult"]
        
        # 后期波次增强系数 (波次10以后显著增强)
        late_game_multiplier = 1.0 + max(0, (wave - 10) * 0.15)
        
        if enemy_type == "normal":
            self.speed = (1.5 + (wave - 1) * 0.05) * speed_mult
            self.original_speed = self.speed
            self.health = int((100 + (wave - 1) * 25) * late_game_multiplier * health_mult)
            self.max_health = self.health
            self.radius = 15
            self.color = RED
            self.reward = int((40 + (wave - 1) * 10) * gold_mult)
            self.attack_damage = int(5 * late_game_multiplier * damage_mult)
            self.attack_range = 30
            self.attack_cooldown = 60
            self.current_attack_cooldown = 0
        elif enemy_type == "fast":
            self.speed = (2.5 + (wave - 1) * 0.12) * speed_mult
            self.original_speed = self.speed
            self.health = int((60 + (wave - 1) * 15) * late_game_multiplier * health_mult)
            self.max_health = self.health
            self.radius = 12
            self.color = YELLOW
            self.reward = int((50 + (wave - 1) * 12) * gold_mult)
            self.attack_damage = int(3 * late_game_multiplier * damage_mult)
            self.attack_range = 25
            self.attack_cooldown = 40
            self.current_attack_cooldown = 0
        elif enemy_type == "tank":
            self.speed = (0.8 + (wave - 1) * 0.03) * speed_mult
            self.original_speed = self.speed
            self.health = int((300 + (wave - 1) * 80) * late_game_multiplier * health_mult)
            self.max_health = self.health
            self.radius = 25
            self.color = BLUE
            self.reward = int((80 + (wave - 1) * 20) * gold_mult)
            self.attack_damage = int(15 * late_game_multiplier * damage_mult)
            self.attack_range = 35
            self.attack_cooldown = 90
            self.current_attack_cooldown = 0
        elif enemy_type == "elite":
            self.speed = (1.8 + (wave - 1) * 0.08) * speed_mult
            self.original_speed = self.speed
            self.health = int((200 + (wave - 1) * 50) * late_game_multiplier * health_mult)
            self.max_health = self.health
            self.radius = 20
            self.color = PURPLE
            self.reward = int((120 + (wave - 1) * 30) * gold_mult)
            self.attack_damage = int(10 * late_game_multiplier * damage_mult)
            self.attack_range = 40
            self.attack_cooldown = 50
            self.current_attack_cooldown = 0
        
        # 后期怪物可以攻击防御塔
        self.can_attack_towers = wave >= 5  # 第5波开始可以攻击塔
        self.target_tower = None

    def move(self):
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            
            if distance < self.speed:
                self.path_index += 1
                if self.path_index >= len(self.path) - 1:
                    self.reached_end = True
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

    def find_target_tower(self, towers):
        """寻找攻击范围内的防御塔"""
        if not self.can_attack_towers:
            return None
        
        closest_tower = None
        closest_distance = self.attack_range
        
        for tower in towers:
            distance = math.sqrt((tower.x - self.x) ** 2 + (tower.y - self.y) ** 2)
            if distance < closest_distance:
                closest_distance = distance
                closest_tower = tower
        
        return closest_tower

    def attack_tower(self, tower):
        """攻击防御塔"""
        if self.current_attack_cooldown <= 0 and tower:
            tower.health -= self.attack_damage
            self.current_attack_cooldown = self.attack_cooldown
            return True
        return False

    def update(self, towers):
        """更新怪物状态，包括攻击冷却"""
        if self.current_attack_cooldown > 0:
            self.current_attack_cooldown -= 1
        
        # 寻找并攻击防御塔
        if self.can_attack_towers:
            target = self.find_target_tower(towers)
            if target:
                self.attack_tower(target)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        health_bar_width = 30
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.x - health_bar_width // 2, self.y - self.radius - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, GREEN, (self.x - health_bar_width // 2, self.y - self.radius - 10, health_bar_width * health_percentage, health_bar_height))

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.radius = 20  # 恢复正常塔的半径
        self.range = 150
        self.damage = 10
        self.cooldown = 60
        self.current_cooldown = 0
        self.color = GREEN
        self.projectiles = []
        self.level = 1
        self.max_level = 5
        
        # 塔的生命值
        self.max_health = 100
        self.health = self.max_health
        
        # 特殊效果
        self.slow_effect = 0  # 减速效果
        self.splash_radius = 0  # 范围伤害半径
        self.chain_targets = 0  # 连锁目标数
        self.piercing = False  # 穿透攻击
        
        if tower_type == "basic":
            self.range = 120
            self.damage = 15
            self.cooldown = 45
            self.color = GREEN
            self.upgrade_cost = 30
            self.max_health = 120
        elif tower_type == "sniper":
            self.range = 250
            self.damage = 50
            self.cooldown = 90
            self.color = PURPLE
            self.upgrade_cost = 60
            self.max_health = 80
        elif tower_type == "rapid":
            self.range = 100
            self.damage = 5
            self.cooldown = 15
            self.color = BLUE
            self.upgrade_cost = 40
            self.max_health = 100
        elif tower_type == "freeze":
            self.range = 130
            self.damage = 8
            self.cooldown = 50
            self.color = (100, 200, 255)  # 冰蓝色
            self.upgrade_cost = 50
            self.max_health = 90
            self.slow_effect = 0.5  # 减速50%
        elif tower_type == "cannon":
            self.range = 140
            self.damage = 40
            self.cooldown = 80
            self.color = (139, 69, 19)  # 棕色
            self.upgrade_cost = 80
            self.max_health = 150
            self.splash_radius = 50  # 范围伤害
        elif tower_type == "laser":
            self.range = 180
            self.damage = 25
            self.cooldown = 30
            self.color = (255, 0, 255)  # 洋红色
            self.upgrade_cost = 70
            self.max_health = 70
            self.piercing = True  # 穿透攻击
        elif tower_type == "electric":
            self.range = 150
            self.damage = 15
            self.cooldown = 60
            self.color = (255, 255, 0)  # 黄色
            self.upgrade_cost = 65
            self.max_health = 85
            self.chain_targets = 3  # 连锁3个目标
        
        self.health = self.max_health

    def find_target(self, enemies):
        closest_enemy = None
        closest_distance = self.range
        
        for enemy in enemies:
            if enemy.alive and not enemy.reached_end:
                distance = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_enemy = enemy
        
        return closest_enemy

    def shoot(self, target):
        if self.current_cooldown <= 0 and target:
            self.projectiles.append(Projectile(self.x, self.y, target, self.damage, self))
            self.current_cooldown = self.cooldown

    def update(self, enemies):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
        
        target = self.find_target(enemies)
        self.shoot(target)
        
        for projectile in self.projectiles[:]:
            projectile.update(enemies)
            if projectile.hit:
                if projectile.target in enemies and projectile.target.health <= 0:
                    projectile.target.alive = False
                self.projectiles.remove(projectile)
            elif projectile.x < 0 or projectile.x > WIDTH or projectile.y < 0 or projectile.y > HEIGHT:
                self.projectiles.remove(projectile)

    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1
            self.damage = int(self.damage * 1.3)
            self.range = int(self.range * 1.1)
            self.cooldown = max(5, int(self.cooldown * 0.85))
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
            return True
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), self.radius, 2)
        
        level_text = small_font.render(f"Lv.{self.level}", True, WHITE)
        surface.blit(level_text, (self.x - level_text.get_width() // 2, self.y - level_text.get_height() // 2))
        
        # 绘制塔的生命值条
        if self.health < self.max_health:
            health_bar_width = 30
            health_bar_height = 4
            health_percentage = self.health / self.max_health
            pygame.draw.rect(surface, RED, (self.x - health_bar_width // 2, self.y - self.radius - 8, health_bar_width, health_bar_height))
            pygame.draw.rect(surface, GREEN, (self.x - health_bar_width // 2, self.y - self.radius - 8, health_bar_width * health_percentage, health_bar_height))
        
        for projectile in self.projectiles:
            projectile.draw(surface)

class Projectile:
    def __init__(self, x, y, target, damage, tower=None):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = 8
        self.hit = False
        self.radius = 5
        self.tower = tower
        self.hit_enemies = []  # 已命中的敌人（用于穿透）
        
        # 根据塔类型设置颜色
        if tower:
            if tower.tower_type == "freeze":
                self.color = (100, 200, 255)
            elif tower.tower_type == "cannon":
                self.color = (139, 69, 19)
                self.radius = 8
            elif tower.tower_type == "laser":
                self.color = (255, 0, 255)
            elif tower.tower_type == "electric":
                self.color = (255, 255, 0)
            else:
                self.color = YELLOW
        else:
            self.color = YELLOW

    def update(self, enemies=None):
        if not self.target.alive or self.target.reached_end:
            self.hit = True
            return
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance < self.speed:
            self.hit = True
            self.apply_damage(enemies)
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def apply_damage(self, enemies):
        """应用伤害和特殊效果"""
        if not self.target:
            return
        
        # 基础伤害
        self.target.health -= self.damage
        self.hit_enemies.append(self.target)
        
        # 减速效果
        if self.tower and self.tower.slow_effect > 0:
            self.target.speed = self.target.original_speed * (1 - self.tower.slow_effect)
        
        # 范围伤害
        if self.tower and self.tower.splash_radius > 0:
            if enemies:
                for enemy in enemies:
                    if enemy != self.target and enemy.alive:
                        dist = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
                        if dist < self.tower.splash_radius:
                            enemy.health -= self.damage * 0.5  # 范围伤害减半
        
        # 连锁攻击
        if self.tower and self.tower.chain_targets > 0:
            if enemies:
                chain_enemies = []
                for enemy in enemies:
                    if enemy != self.target and enemy.alive and enemy not in self.hit_enemies:
                        dist = math.sqrt((enemy.x - self.target.x) ** 2 + (enemy.y - self.target.y) ** 2)
                        if dist < 100:  # 连锁范围
                            chain_enemies.append((enemy, dist))
                chain_enemies.sort(key=lambda x: x[1])
                for i, (enemy, _) in enumerate(chain_enemies[:self.tower.chain_targets]):
                    enemy.health -= self.damage * 0.6  # 连锁伤害递减

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Drop:
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.amount = amount
        self.radius = 8
        self.lifetime = 300
        self.collected = False

    def update(self):
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        amount_text = small_font.render(str(self.amount), True, BLACK)
        surface.blit(amount_text, (self.x - amount_text.get_width() // 2, self.y - amount_text.get_height() // 2))

class ShopItem:
    def __init__(self, name, description, cost, effect_type, effect_value, icon_color):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.icon_color = icon_color
        self.purchased = False

class Shop:
    def __init__(self, wave=1):
        self.wave = wave
        # buff配置: (名称, 效果类型, 图标颜色, 基础价格, 效果值范围)
        self.buff_configs = [
            ("Heal", "heal", GREEN, 40, [(3, 50), (5, 80), (8, 120), (12, 180)]),
            ("Gold Bonus", "gold_bonus", YELLOW, 60, [(1.5, 70), (2.0, 100), (2.5, 150), (3.0, 220)]),
            ("Damage Boost", "damage_boost", RED, 80, [(0.15, 90), (0.25, 140), (0.40, 220), (0.60, 350)]),
            ("Range Boost", "range_boost", BLUE, 90, [(20, 100), (35, 160), (55, 250), (80, 380)]),
            ("Speed Boost", "speed_boost", PURPLE, 100, [(0.20, 120), (0.35, 200), (0.50, 320), (0.70, 500)]),
            ("Extra Lives", "max_lives", ORANGE, 150, [(2, 180), (4, 320), (7, 550), (10, 850)]),
        ]
        self.items = []
        self.generate_items()
        self.gold_bonus_active = False
        self.damage_boost = 0
        self.range_boost = 0
        self.speed_boost = 0
    
    def generate_items(self):
        """根据波次生成随机buff，波次越高可能出现更好的buff"""
        self.items = []
        # 根据波次确定可用的buff等级 (0-3)
        max_tier = min(3, (self.wave - 1) // 2)  # 每2波解锁一个更高等级
        
        # 随机选择3-4个buff显示
        num_items = random.randint(3, 4)
        selected_configs = random.sample(self.buff_configs, min(num_items, len(self.buff_configs)))
        
        for name, effect_type, color, base_cost, tiers in selected_configs:
            # 随机选择buff等级 (0到max_tier之间)
            available_tiers = tiers[:max_tier + 1]
            tier_index = random.randint(0, len(available_tiers) - 1)
            effect_value, cost = available_tiers[tier_index]
            
            # 生成描述
            if effect_type == "heal":
                desc = f"Heal {effect_value} HP"
            elif effect_type == "gold_bonus":
                desc = f"x{effect_value} gold next wave"
            elif effect_type == "damage_boost":
                desc = f"All towers +{int(effect_value * 100)}% damage"
            elif effect_type == "range_boost":
                desc = f"All towers +{effect_value} range"
            elif effect_type == "speed_boost":
                desc = f"All towers +{int(effect_value * 100)}% attack speed"
            elif effect_type == "max_lives":
                desc = f"Permanently +{effect_value} max lives"
            else:
                desc = ""
            
            self.items.append(ShopItem(name, desc, cost, effect_type, effect_value, color))
    
    def reset_buffs(self):
        self.gold_bonus_active = False
        self.damage_boost = 0
        self.range_boost = 0
        self.speed_boost = 0
    
    def apply_item(self, item, game):
        if item.effect_type == "heal":
            game.lives = min(game.lives + item.effect_value, 20)
        elif item.effect_type == "gold_bonus":
            self.gold_bonus_active = True
        elif item.effect_type == "damage_boost":
            self.damage_boost = item.effect_value
            for tower in game.towers:
                tower.damage = int(tower.damage * (1 + self.damage_boost))
        elif item.effect_type == "range_boost":
            self.range_boost = item.effect_value
            for tower in game.towers:
                tower.range += self.range_boost
        elif item.effect_type == "speed_boost":
            self.speed_boost = item.effect_value
            for tower in game.towers:
                tower.cooldown = max(5, int(tower.cooldown * (1 - self.speed_boost)))
        elif item.effect_type == "max_lives":
            game.lives += item.effect_value

class Game:
    def __init__(self, mode="normal"):
        self.mode = mode
        self.mode_config = GAME_MODES.get(mode, GAME_MODES["normal"])
        
        self.gold = self.mode_config["start_gold"]
        self.lives = self.mode_config["start_lives"]
        self.max_lives = self.lives
        self.wave = 1
        self.total_waves = self.mode_config["total_waves"]  # 总波数，-1表示无尽
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.drops = []
        self.selected_tower_type = None
        self.game_over = False
        self.game_won = False  # 游戏胜利标志
        self.wave_in_progress = False
        self.enemies_spawned = 0
        self.enemies_to_spawn = 5
        self.spawn_timer = 0
        self.spawn_delay = 60
        
        self.max_towers = 15
        self.tower_slot_cost = 100
        self.tower_slot_increase = 5
        self.game_started = False
        self.in_menu = True  # 是否在主菜单
        
        self.shop = Shop(self.wave)
        self.in_shop = False
        self.show_shop_button = False  # 是否显示商店按钮
        
        self.decorations = []
        self.selected_decoration = None
        
        # 根据难度选择地图
        path_type = self.mode_config.get("path_type", "normal")
        if path_type == "random":
            # 无尽模式：随机选择所有地图
            all_paths = []
            for paths in PATH_CONFIGS.values():
                all_paths.extend(paths)
            self.path = random.choice(all_paths)
        else:
            # 其他模式：从对应难度的地图中随机选择
            available_paths = PATH_CONFIGS.get(path_type, PATH_CONFIGS["normal"])
            self.path = random.choice(available_paths)
        
        # 所有塔的配置
        self.all_towers = {
            "basic": {"name": "Basic Tower", "cost": 50, "limit": -1, "unlock_wave": 1, "color": GREEN},
            "sniper": {"name": "Sniper Tower", "cost": 100, "limit": 5, "unlock_wave": 1, "color": PURPLE},
            "rapid": {"name": "Rapid Tower", "cost": 75, "limit": 8, "unlock_wave": 1, "color": BLUE},
            "freeze": {"name": "Freeze Tower", "cost": 80, "limit": 4, "unlock_wave": 3, "color": (100, 200, 255)},
            "cannon": {"name": "Cannon Tower", "cost": 120, "limit": 3, "unlock_wave": 5, "color": (139, 69, 19)},
            "laser": {"name": "Laser Tower", "cost": 100, "limit": 4, "unlock_wave": 7, "color": (255, 0, 255)},
            "electric": {"name": "Electric Tower", "cost": 90, "limit": 4, "unlock_wave": 4, "color": (255, 255, 0)},
        }
        
        self.tower_costs = {k: v["cost"] for k, v in self.all_towers.items()}
        self.tower_limits = {k: v["limit"] for k, v in self.all_towers.items()}
    
    def get_available_towers(self):
        """获取当前波次可用的塔"""
        available = []
        for tower_type, config in self.all_towers.items():
            if self.wave >= config["unlock_wave"]:
                available.append((config["name"], config["color"], tower_type, config["cost"]))
        return available

    def spawn_enemy(self):
        if self.enemies_spawned < self.enemies_to_spawn:
            enemy_type = "normal"
            rand = random.random()
            
            if self.wave >= 2:
                if rand < 0.3:
                    enemy_type = "fast"
                elif rand < 0.4 and self.wave >= 3:
                    enemy_type = "tank"
                elif rand < 0.5 and self.wave >= 4:
                    enemy_type = "elite"
            
            if self.wave >= 5:
                if rand < 0.4:
                    enemy_type = "fast"
                elif rand < 0.6:
                    enemy_type = "tank"
                elif rand < 0.75:
                    enemy_type = "elite"
            
            if self.wave >= 8:
                if rand < 0.3:
                    enemy_type = "fast"
                elif rand < 0.5:
                    enemy_type = "tank"
                elif rand < 0.7:
                    enemy_type = "elite"
            
            enemy = Enemy(self.path, enemy_type, self.wave, self.mode_config)
            self.enemies.append(enemy)
            self.enemies_spawned += 1

    def start_wave(self):
        if not self.wave_in_progress and not self.game_over:
            self.wave_in_progress = True
            self.enemies_spawned = 0
            self.enemies_to_spawn = 5 + self.wave * 2
            self.spawn_delay = max(20, 60 - (self.wave - 1) * 5)

    def update(self):
        if self.game_over:
            return
        
        if self.wave_in_progress:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_enemy()
                self.spawn_timer = 0
        
        # 更新敌人（移动和攻击）
        for enemy in self.enemies[:]:
            enemy.move()
            enemy.update(self.towers)  # 让怪物攻击防御塔
            
            if enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True
            elif not enemy.alive:
                reward = enemy.reward
                if self.shop.gold_bonus_active:
                    reward *= 2
                self.gold += reward
                
                if random.random() < 0.3:
                    drop_amount = random.randint(5, 15)
                    if self.shop.gold_bonus_active:
                        drop_amount *= 2
                    self.drops.append(Drop(enemy.x, enemy.y, drop_amount))
                
                self.enemies.remove(enemy)
        
        if self.wave_in_progress and len(self.enemies) == 0 and self.enemies_spawned >= self.enemies_to_spawn:
            self.wave_in_progress = False
            
            # 检查是否达到总波数（非无尽模式）
            if self.total_waves > 0 and self.wave >= self.total_waves:
                self.game_won = True
                self.game_over = True
            else:
                self.wave += 1
                # 重新创建商店，传入新的波次
                self.shop = Shop(self.wave)
                # 不自动打开商店，而是显示商店按钮
                self.show_shop_button = True
        
        # 更新防御塔并移除被摧毁的塔
        for tower in self.towers[:]:
            tower.update(self.enemies)
            if tower.health <= 0:
                self.towers.remove(tower)
        
        # 自动收集金币
        for drop in self.drops[:]:
            if drop.update():
                self.drops.remove(drop)
            else:
                # 自动收集：金币飞向玩家
                self.gold += drop.amount
                self.drops.remove(drop)

    def place_tower(self, x, y):
        if not self.selected_tower_type:
            return
        
        if self.gold < self.tower_costs[self.selected_tower_type]:
            return
        
        if len(self.towers) >= self.max_towers:
            return
        
        for tower in self.towers:
            distance = math.sqrt((tower.x - x) ** 2 + (tower.y - y) ** 2)
            if distance < 40 and tower.tower_type == self.selected_tower_type:
                if tower.level < tower.max_level:
                    self.gold -= self.tower_costs[self.selected_tower_type]
                    tower.upgrade()
                    self.selected_tower_type = None
                return
        
        current_count = sum(1 for tower in self.towers if tower.tower_type == self.selected_tower_type)
        tower_limit = self.tower_limits[self.selected_tower_type]
        if tower_limit > 0 and current_count >= tower_limit:  # -1表示无限制
            return
        
        if self.is_valid_placement(x, y, self.selected_tower_type):
            self.gold -= self.tower_costs[self.selected_tower_type]
            self.towers.append(Tower(x, y, self.selected_tower_type))
            self.selected_tower_type = None

    def is_valid_placement(self, x, y, tower_type):
        for tower in self.towers:
            distance = math.sqrt((tower.x - x) ** 2 + (tower.y - y) ** 2)
            if distance < 50 and tower.tower_type != tower_type:
                return False
        
        for point in self.path:
            distance = math.sqrt((point[0] - x) ** 2 + (point[1] - y) ** 2)
            if distance < 40:
                return False
        
        if x < 50 or x > WIDTH - 50 or y < 50 or y > HEIGHT - 50:
            return False
        
        return True

    def draw(self, surface):
        # 使用更美观的背景颜色
        surface.fill((100, 150, 100))  # 绿色背景
        
        # 绘制渐变背景效果
        for i in range(HEIGHT):
            alpha = i / HEIGHT * 50
            pygame.draw.rect(surface, (200, 220, 200, alpha), (0, i, WIDTH, 1))
        
        for i in range(len(self.path) - 1):
            pygame.draw.line(surface, GRAY, self.path[i], self.path[i + 1], 40)
        
        for i in range(len(self.path)):
            pygame.draw.circle(surface, DARK_GREEN, self.path[i], 20)
        
        for tower in self.towers:
            tower.draw(surface)
        
        for enemy in self.enemies:
            enemy.draw(surface)
        
        for drop in self.drops:
            drop.draw(surface)
        
        self.draw_ui(surface)
        
        # 显示商店按钮
        if self.show_shop_button and not self.in_shop:
            self.draw_shop_button(surface)
        
        if self.game_over:
            self.draw_game_over(surface)

    def draw_ui(self, surface):
        ui_height = 70
        pygame.draw.rect(surface, BLUE, (0, HEIGHT - ui_height, WIDTH, ui_height))
        
        gold_text = small_font.render(f"Gold: {self.gold}", True, YELLOW)
        lives_text = small_font.render(f"Lives: {self.lives}", True, RED)
        
        if self.total_waves == -1:
            wave_text = small_font.render(f"Wave: {self.wave} (Endless)", True, WHITE)
        else:
            wave_text = small_font.render(f"Wave: {self.wave}/{self.total_waves}", True, WHITE)
        towers_text = small_font.render(f"Towers: {len(self.towers)}/{self.max_towers}", True, WHITE)
        
        surface.blit(gold_text, (10, HEIGHT - 55))
        surface.blit(lives_text, (110, HEIGHT - 55))
        surface.blit(wave_text, (210, HEIGHT - 55))
        surface.blit(towers_text, (320, HEIGHT - 55))
        
        # 动态获取当前可用的塔
        tower_buttons = self.get_available_towers()
        
        button_x = 420
        button_width = 65
        for name, color, tower_type, cost in tower_buttons:
            button_rect = pygame.Rect(button_x, HEIGHT - 60, button_width, 50)
            pygame.draw.rect(surface, color, button_rect)
            pygame.draw.rect(surface, BLACK, button_rect, 2)
            
            # 显示简称（取前两个字）
            short_name = name[:2] if len(name) > 2 else name
            name_text = small_font.render(short_name, True, WHITE)
            cost_text = small_font.render(f"{cost}", True, WHITE)
            
            current_count = sum(1 for tower in self.towers if tower.tower_type == tower_type)
            limit = self.tower_limits[tower_type]
            if limit == -1:
                limit_text = small_font.render(f"{current_count}/∞", True, YELLOW)
            else:
                limit_text = small_font.render(f"{current_count}/{limit}", True, YELLOW)
            
            surface.blit(name_text, (button_x + button_width // 2 - name_text.get_width() // 2, HEIGHT - 50))
            surface.blit(cost_text, (button_x + button_width // 2 - cost_text.get_width() // 2, HEIGHT - 30))
            surface.blit(limit_text, (button_x + button_width // 2 - limit_text.get_width() // 2, HEIGHT - 15))
            
            if self.selected_tower_type == tower_type:
                pygame.draw.rect(surface, YELLOW, button_rect, 3)
            
            button_x += button_width + 3
        
        buy_slot_rect = pygame.Rect(WIDTH - 200, HEIGHT - 60, 80, 50)
        pygame.draw.rect(surface, ORANGE, buy_slot_rect)
        pygame.draw.rect(surface, BLACK, buy_slot_rect, 2)
        
        buy_text = small_font.render("Buy Slot", True, WHITE)
        cost_text = small_font.render(f"{self.tower_slot_cost}", True, WHITE)
        surface.blit(buy_text, (WIDTH - 200 + 40 - buy_text.get_width() // 2, HEIGHT - 50))
        surface.blit(cost_text, (WIDTH - 200 + 40 - cost_text.get_width() // 2, HEIGHT - 30))
        
        start_wave_rect = pygame.Rect(WIDTH - 110, HEIGHT - 60, 90, 50)
        pygame.draw.rect(surface, GREEN, start_wave_rect)
        pygame.draw.rect(surface, BLACK, start_wave_rect, 2)
        
        start_text = small_font.render("Next Wave", True, WHITE)
        surface.blit(start_text, (WIDTH - 110 + 45 - start_text.get_width() // 2, HEIGHT - 45))

    def draw_shop(self, surface):
        surface.fill((50, 50, 80))
        
        title_text = font.render("Shop - Wave Break", True, YELLOW)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
        
        gold_text = font.render(f"Current Gold: {self.gold}", True, YELLOW)
        surface.blit(gold_text, (WIDTH // 2 - gold_text.get_width() // 2, 80))
        
        item_width = 280
        item_height = 120
        items_per_row = 3
        start_x = (WIDTH - items_per_row * item_width - (items_per_row - 1) * 20) // 2
        start_y = 150
        
        for i, item in enumerate(self.shop.items):
            row = i // items_per_row
            col = i % items_per_row
            x = start_x + col * (item_width + 20)
            y = start_y + row * (item_height + 20)
            
            item_rect = pygame.Rect(x, y, item_width, item_height)
            
            if item.purchased:
                pygame.draw.rect(surface, (100, 100, 100), item_rect)
            elif self.gold >= item.cost:
                pygame.draw.rect(surface, (70, 70, 120), item_rect)
            else:
                pygame.draw.rect(surface, (50, 50, 70), item_rect)
            
            pygame.draw.rect(surface, WHITE, item_rect, 2)
            
            icon_rect = pygame.Rect(x + 10, y + 10, 40, 40)
            pygame.draw.rect(surface, item.icon_color, icon_rect)
            pygame.draw.rect(surface, BLACK, icon_rect, 2)
            
            name_text = font.render(item.name, True, WHITE)
            surface.blit(name_text, (x + 60, y + 10))
            
            cost_text = small_font.render(f"Price: {item.cost} Gold", True, YELLOW)
            surface.blit(cost_text, (x + 60, y + 35))
            
            desc_text = small_font.render(item.description, True, LIGHT_GRAY)
            surface.blit(desc_text, (x + 10, y + 60))
            
            if item.purchased:
                status_text = small_font.render("Purchased", True, GREEN)
                surface.blit(status_text, (x + 10, y + 85))
        
        continue_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 60)
        pygame.draw.rect(surface, GREEN, continue_rect)
        pygame.draw.rect(surface, BLACK, continue_rect, 2)
        
        continue_text = font.render("Continue", True, WHITE)
        surface.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT - 85))
        
        hint_text = small_font.render("Click items to purchase, click continue to start next wave", True, LIGHT_GRAY)
        surface.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 30))

    def draw_shop_button(self, surface):
        """绘制商店按钮（小图标）"""
        button_rect = pygame.Rect(WIDTH // 2 - 60, 20, 120, 40)
        pygame.draw.rect(surface, PURPLE, button_rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, button_rect, 2, border_radius=5)
        
        shop_text = font.render("Shop", True, WHITE)
        surface.blit(shop_text, (WIDTH // 2 - shop_text.get_width() // 2, 28))
        
        # 显示提示
        hint_text = small_font.render("Click to open shop", True, YELLOW)
        surface.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 65))
        
        return button_rect

    def draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        if self.game_won:
            title_text = font.render("Victory!", True, GREEN)
            subtitle_text = font.render(f"Successfully completed {self.total_waves} waves!", True, YELLOW)
        else:
            title_text = font.render("Game Over!", True, RED)
            subtitle_text = font.render(f"Reached wave: {self.wave}", True, WHITE)
        
        restart_text = small_font.render("Press R to restart", True, WHITE)
        menu_text = small_font.render("Press ESC to return to menu", True, YELLOW)
        
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        surface.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2 - 30))
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 30))
        surface.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 70))

    def draw_start_screen(self, surface):
        """绘制主菜单界面"""
        # 绘制渐变背景
        for i in range(HEIGHT):
            r = int(50 + i / HEIGHT * 50)
            g = int(80 + i / HEIGHT * 70)
            b = int(120 + i / HEIGHT * 30)
            pygame.draw.rect(surface, (r, g, b), (0, i, WIDTH, 1))
        
        # 添加装饰元素
        for i in range(0, WIDTH, 50):
            pygame.draw.circle(surface, (255, 255, 255, 50), (i, 50), 5)
            pygame.draw.circle(surface, (255, 255, 255, 50), (i, HEIGHT - 50), 5)
        
        # 标题
        title_text_large = pygame.font.Font(None, 64)
        title_text = title_text_large.render("Tower Defense", True, (255, 255, 255))
        # 添加标题阴影
        shadow_text = title_text_large.render("Tower Defense", True, (0, 0, 0, 100))
        surface.blit(shadow_text, (WIDTH // 2 - title_text.get_width() // 2 + 3, 43))
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 40))
        
        # 副标题
        subtitle_text = font.render("Select Game Mode", True, (255, 255, 255))
        surface.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 120))
        
        # 绘制模式选择按钮
        modes = list(GAME_MODES.keys())
        button_width = 220
        button_height = 120
        buttons_per_row = 3
        start_x = (WIDTH - buttons_per_row * button_width - (buttons_per_row - 1) * 20) // 2
        start_y = 150
        
        self.mode_buttons = []
        for i, mode_name in enumerate(modes):
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + col * (button_width + 20)
            y = start_y + row * (button_height + 20)
            
            mode_config = GAME_MODES[mode_name]
            button_rect = pygame.Rect(x, y, button_width, button_height)
            
            # 绘制按钮阴影
            shadow_rect = button_rect.copy()
            shadow_rect.move_ip(5, 5)
            pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=10)
            
            # 绘制按钮背景
            pygame.draw.rect(surface, mode_config["color"], button_rect, border_radius=10)
            pygame.draw.rect(surface, (255, 255, 255, 150), button_rect, 2, border_radius=10)
            
            # 模式名称
            name_text = font.render(mode_config["name"], True, WHITE)
            surface.blit(name_text, (x + button_width // 2 - name_text.get_width() // 2, y + 15))
            
            # 波数信息
            if mode_config["total_waves"] == -1:
                waves_text = small_font.render("Endless Waves", True, YELLOW)
            else:
                waves_text = small_font.render(f"{mode_config['total_waves']} Waves", True, YELLOW)
            surface.blit(waves_text, (x + button_width // 2 - waves_text.get_width() // 2, y + 40))
            
            # 描述 - 自动换行
            desc = mode_config["description"]
            lines = []
            current_line = ""
            for word in desc.split():
                test_line = current_line + " " + word if current_line else word
                if small_font.size(test_line)[0] <= button_width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # 绘制多行描述
            for j, line in enumerate(lines):
                desc_text = small_font.render(line, True, (255, 255, 255, 180))
                surface.blit(desc_text, (x + button_width // 2 - desc_text.get_width() // 2, y + 65 + j * 18))
            
            self.mode_buttons.append((button_rect, mode_name))
        
        # 底部说明
        y_offset = start_y + 2 * (button_height + 20) + 30
        instructions = [
            "Game Instructions:",
            "• Click to select game mode to start",
            "• Different difficulties have different enemy strength and waves",
            "• Endless mode allows unlimited challenges",
            "• Basic towers have no quantity limit",
        ]
        
        for instruction in instructions:
            text = small_font.render(instruction, True, (255, 255, 255, 150))
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 25

    def reset(self):
        self.gold = self.mode_config["start_gold"]
        self.lives = self.mode_config["start_lives"]
        self.max_lives = self.lives
        self.wave = 1
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.drops = []
        self.selected_tower_type = None
        self.game_over = False
        self.game_won = False
        self.wave_in_progress = False
        self.enemies_spawned = 0
        self.enemies_to_spawn = 5
        self.spawn_timer = 0
        self.in_shop = False
        self.show_shop_button = False
        # 游戏重启时重新随机选择地图
        path_type = self.mode_config.get("path_type", "normal")
        if path_type == "random":
            all_paths = []
            for paths in PATH_CONFIGS.values():
                all_paths.extend(paths)
            self.path = random.choice(all_paths)
        else:
            available_paths = PATH_CONFIGS.get(path_type, PATH_CONFIGS["normal"])
            self.path = random.choice(available_paths)
        self.shop = Shop(self.wave)
    
    def return_to_menu(self):
        """返回主菜单"""
        self.in_menu = True
        self.game_started = False
        self.game_over = False
        self.game_won = False
        self.reset()

def main():
    game = Game()
    
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 主菜单模式选择
            elif game.in_menu:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    # 检查是否点击了模式按钮
                    if hasattr(game, 'mode_buttons'):
                        for button_rect, mode_name in game.mode_buttons:
                            if button_rect.collidepoint(x, y):
                                game = Game(mode_name)
                                game.in_menu = False
                                game.game_started = True
                                break
            
            # 商店界面
            elif game.in_shop:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = pygame.mouse.get_pos()
                        
                        item_width = 280
                        item_height = 120
                        items_per_row = 3
                        start_x = (WIDTH - items_per_row * item_width - (items_per_row - 1) * 20) // 2
                        start_y = 150
                        
                        for i, item in enumerate(game.shop.items):
                            row = i // items_per_row
                            col = i % items_per_row
                            item_x = start_x + col * (item_width + 20)
                            item_y = start_y + row * (item_height + 20)
                            
                            item_rect = pygame.Rect(item_x, item_y, item_width, item_height)
                            if item_rect.collidepoint(x, y):
                                if not item.purchased and game.gold >= item.cost:
                                    game.gold -= item.cost
                                    game.shop.apply_item(item, game)
                                    item.purchased = True
                        
                        continue_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 60)
                        if continue_rect.collidepoint(x, y):
                            game.in_shop = False
                            game.show_shop_button = False
                            for item in game.shop.items:
                                item.purchased = False
            
            # 游戏结束界面
            elif game.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                    elif event.key == pygame.K_ESCAPE:
                        game.return_to_menu()
            
            # 游戏进行中
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = pygame.mouse.get_pos()
                        
                        # 检查商店按钮
                        if game.show_shop_button:
                            shop_button_rect = pygame.Rect(WIDTH // 2 - 60, 20, 120, 40)
                            if shop_button_rect.collidepoint(x, y):
                                game.in_shop = True
                                continue
                        
                        if y > HEIGHT - 70:
                            tower_buttons = game.get_available_towers()
                            button_width = 65
                            
                            button_x = 420
                            for name, color, tower_type, cost in tower_buttons:
                                button_rect = pygame.Rect(button_x, HEIGHT - 60, button_width, 50)
                                if button_rect.collidepoint(x, y):
                                    if game.gold >= cost:
                                        game.selected_tower_type = tower_type
                                button_x += button_width + 3
                            
                            buy_slot_rect = pygame.Rect(WIDTH - 200, HEIGHT - 60, 80, 50)
                            if buy_slot_rect.collidepoint(x, y):
                                if game.gold >= game.tower_slot_cost:
                                    game.gold -= game.tower_slot_cost
                                    game.max_towers += game.tower_slot_increase
                                    game.tower_slot_cost = int(game.tower_slot_cost * 1.5)
                            
                            start_wave_rect = pygame.Rect(WIDTH - 110, HEIGHT - 60, 90, 50)
                            if start_wave_rect.collidepoint(x, y):
                                game.show_shop_button = False
                                game.start_wave()
                        else:
                            if game.selected_tower_type:
                                game.place_tower(x, y)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.return_to_menu()
        
        # 绘制
        if game.in_menu:
            game.draw_start_screen(screen)
        elif game.in_shop:
            game.draw_shop(screen)
        else:
            game.update()
            game.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()