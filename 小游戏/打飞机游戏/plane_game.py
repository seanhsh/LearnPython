# 导入所需模块
import pygame
import random
import math
import os

# 初始化pygame
pygame.init()
# 初始化音频
pygame.mixer.init()

# 加载背景音乐
try:
    # 尝试加载背景音乐
    pygame.mixer.music.load('Horizons.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # 循环播放
except:
    print("无法加载背景音乐，游戏将继续运行")

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600  # 窗口宽度和高度
FULLSCREEN = False  # 初始全屏状态
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # 创建游戏窗口
pygame.display.set_caption("Plane Game")  # Set window title

# 加载图片函数
def load_image(filename, size=None):
    """
    加载指定路径的图片，并可选地调整大小
    
    参数:
        filename: 图片文件名
        size: 可选，元组格式的目标大小 (width, height)
    
    返回:
        加载并调整大小的图片对象，如果加载失败则返回None
    """
    path = os.path.join('images', filename)
    if os.path.exists(path):
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    return None

# 加载游戏所需的图片资源
player_image = load_image('player_ship.png', (50, 60))  # 玩家飞机图片
enemy_image = load_image('enemy_ship.png', (40, 40))    # 敌人飞机图片
boss_image = load_image('boss_ship.png', (100, 100))     # BOSS飞机图片

# 颜色定义
WHITE = (255, 255, 255)    # 白色
BLACK = (0, 0, 0)          # 黑色
RED = (255, 0, 0)          # 红色
GREEN = (0, 255, 0)        # 绿色
BLUE = (0, 0, 255)         # 蓝色
YELLOW = (255, 255, 0)      # 黄色
ORANGE = (255, 165, 0)      # 橙色

class Player:
    """
    玩家类，负责处理玩家飞机的所有行为
    """
    def __init__(self):
        """
        初始化玩家飞机的属性
        """
        self.width = 50  # 玩家飞机宽度
        self.height = 60  # 玩家飞机高度
        self.x = WIDTH // 2 - self.width // 2  # 初始X位置（居中）
        self.y = HEIGHT - self.height - 10  # 初始Y位置（底部）
        self.vel = 5  # 移动速度
        self.bullets = []  # 玩家发射的子弹列表
        self.missiles = []  # 玩家发射的导弹列表
        self.bomb_count = 3  # 炸弹数量
        self.missile_count = 3  # 导弹数量
        self.score = 0  # 得分
        self.health = 1000 # 生命值
        self.level = 1  # 当前关卡
        self.shoot_delay = 20  # 射击延迟（帧）
        self.shoot_count = 0  # 射击计数器
        self.missile_delay = 60  # 导弹发射延迟（帧）
        self.missile_cooldown = 0  # 导弹冷却计数器
        self.bullet_type = "normal"  # 当前子弹类型
        # 跟踪每种子弹类型的升级次数
        self.bullet_upgrade_count = {"normal": 0, "double": 0, "triple": 0, "powerful": 0}
        self.shield = False  # 护盾状态
        self.shield_timer = 0  # 护盾持续时间计数器
    
    def draw(self, win):
        """
        在游戏窗口中绘制玩家飞机
        
        参数:
            win: 游戏窗口表面
        """
        # 使用加载的图片绘制玩家飞机
        if player_image:
            win.blit(player_image, (self.x, self.y))
        else:
            # 绘制特定的等腰三角形形状飞机
            # 大等腰三角形
            big_triangle = [
                (self.x + self.width//2, self.y),  # 顶点
                (self.x, self.y + self.height),  # 左下角
                (self.x + self.width, self.y + self.height)  # 右下角
            ]
            # 小等腰三角形（高为大三角形的1/4，底相同）
            small_height = self.height // 4
            small_triangle = [
                (self.x + self.width//2, self.y + self.height - small_height),  # 小三角形顶点
                (self.x, self.y + self.height),  # 左下角
                (self.x + self.width, self.y + self.height)  # 右下角
            ]
            
            # 绘制大三角形
            pygame.draw.polygon(win, BLUE, big_triangle)
            # 用背景色填充小三角形，形成挖空效果
            pygame.draw.polygon(win, BLACK, small_triangle)
            # 绘制飞机的细节
            pygame.draw.polygon(win, (0, 150, 255), big_triangle, 2)  # 边框
            pygame.draw.polygon(win, (0, 150, 255), small_triangle, 2)  # 挖空部分边框
            # 绘制驾驶舱
            cockpit_x = self.x + self.width//2 - 10
            cockpit_y = self.y + 15
            pygame.draw.ellipse(win, (200, 200, 255), (cockpit_x, cockpit_y, 20, 15))
            pygame.draw.ellipse(win, (50, 50, 100), (cockpit_x + 3, cockpit_y + 3, 14, 9))
            # 绘制机翼
            left_wing = [
                (self.x + self.width//2 - 5, self.y + self.height//2),
                (self.x - 15, self.y + self.height//2 + 10),
                (self.x + self.width//2 - 5, self.y + self.height//2 + 20)
            ]
            right_wing = [
                (self.x + self.width//2 + 5, self.y + self.height//2),
                (self.x + self.width + 15, self.y + self.height//2 + 10),
                (self.x + self.width//2 + 5, self.y + self.height//2 + 20)
            ]
            pygame.draw.polygon(win, (0, 100, 200), left_wing)
            pygame.draw.polygon(win, (0, 100, 200), right_wing)
            pygame.draw.polygon(win, (0, 150, 255), left_wing, 1)
            pygame.draw.polygon(win, (0, 150, 255), right_wing, 1)
        # 如果有护盾，绘制护盾效果
        if self.shield:
            pygame.draw.circle(win, (100, 100, 255), (self.x + self.width//2, self.y + self.height//2), self.width//2 + 5, 2)
            # 添加护盾的动态效果
            shield_pulse = int(math.sin(pygame.time.get_ticks() / 100) * 2) + 5
            pygame.draw.circle(win, (150, 150, 255), (self.x + self.width//2, self.y + self.height//2), self.width//2 + shield_pulse, 1)
    
    def move(self, keys):
        """
        根据键盘输入移动玩家飞机
        
        参数:
            keys: 键盘按键状态列表
        """
        # 左移 (左方向键)
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.vel
        # 右移 (右方向键)
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.vel
        # 上移 (上方向键)
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.vel
        # 下移 (下方向键)
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.vel
    
    def shoot(self):
        """
        玩家射击方法，根据当前子弹类型发射子弹
        """
        # 连发功能：只要shoot_count为0就可以发射
        if self.shoot_count == 0 and len(self.bullets) < 50:
            # 根据子弹类型的升级次数计算伤害值
            upgrade_count = self.bullet_upgrade_count.get(self.bullet_type, 0)
            base_damage = 1
            # 伤害值计算：基础伤害 * 2^(升级次数-1)，如果是第一次升级，伤害不变
            damage = base_damage * (2 ** (upgrade_count - 1)) if upgrade_count > 0 else base_damage
            
            # 根据不同子弹类型发射不同数量和方向的子弹
            if self.bullet_type == "normal":
                # 单发子弹：从中心发射
                self.bullets.append(Bullet(self.x + self.width//2 - 2, self.y, "normal", damage))
            elif self.bullet_type == "double":
                # 双发子弹：从左右两侧发射
                self.bullets.append(Bullet(self.x + self.width//4, self.y, "normal", damage))
                self.bullets.append(Bullet(self.x + 3*self.width//4, self.y, "normal", damage))
            elif self.bullet_type == "triple":
                # 三发子弹：从中心和左右两侧发射，形成扇形
                self.bullets.append(Bullet(self.x + self.width//2, self.y, "normal", damage))
                self.bullets.append(Bullet(self.x, self.y + 20, "diagonal_left", damage))
                self.bullets.append(Bullet(self.x + self.width, self.y + 20, "diagonal_right", damage))
            elif self.bullet_type == "five_way":
                # 五发子弹：从中心、左右两侧和更外侧发射，形成更宽的扇形
                self.bullets.append(Bullet(self.x + self.width//2, self.y, "normal", damage))
                self.bullets.append(Bullet(self.x + self.width//4, self.y, "normal", damage))
                self.bullets.append(Bullet(self.x + 3*self.width//4, self.y, "normal", damage))
                self.bullets.append(Bullet(self.x - 10, self.y + 20, "diagonal_left", damage))
                self.bullets.append(Bullet(self.x + self.width + 10, self.y + 20, "diagonal_right", damage))
            # 减少发射延迟，实现连发效果
            self.shoot_count = max(1, self.shoot_delay // 2)
    
    def update(self):
        """
        更新玩家飞机的状态
        """
        # 减少射击延迟计数器
        if self.shoot_count > 0:
            self.shoot_count -= 1
        
        # 减少导弹冷却计数器
        if self.missile_cooldown > 0:
            self.missile_cooldown -= 1
        
        # 更新护盾状态
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False
        
        # 更新子弹状态并移除出界的子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)
        
        # 移除出界的导弹
        for missile in self.missiles[:]:
            if missile.y < 0:
                self.missiles.remove(missile)
    
    def use_bomb(self):
        """
        使用炸弹
        
        返回:
            bool: 炸弹使用是否成功
        """
        if self.bomb_count > 0:
            self.bomb_count -= 1
            return True
        return False
    
    def shoot_missile(self):
        """
        发射导弹
        """
        if self.missile_count > 0 and self.missile_cooldown == 0 and len(self.missiles) < 10:
            self.missiles.append(Missile(self.x + self.width//2 - 3, self.y))
            self.missile_count -= 1
            self.missile_cooldown = self.missile_delay
    
    def upgrade_bullet(self, bullet_type, is_pickup=False):
        """
        升级或切换子弹类型
        
        参数:
            bullet_type: 新的子弹类型
            is_pickup: 是否通过拾取物品获得
        """
        # 定义子弹类型强度顺序（从弱到强）
        bullet_strength = {
            "normal": 1,
            "double": 2,
            "triple": 3,
            "powerful": 4,
            "five_way": 5
        }
        
        # 只有当不是拾取物品，或者新子弹类型比当前类型更强时，才切换子弹类型
        if not is_pickup or bullet_strength.get(bullet_type, 0) > bullet_strength.get(self.bullet_type, 0):
            self.bullet_type = bullet_type
        
        if is_pickup:
            # 只有当玩家真正获得新的子弹技能时（通过拾取物品），才增加升级次数
            self.bullet_upgrade_count[bullet_type] += 1  # 增加对应子弹类型的升级次数
        self.shoot_delay = 20
    
    def activate_shield(self):
        """
        激活护盾
        """
        self.shield = True
        self.shield_timer = 600  # 护盾持续时间（600帧 = 10秒）

class Bullet:
    """
    子弹类，负责处理子弹的所有行为
    """
    def __init__(self, x, y, bullet_type, damage=None):
        """
        初始化子弹属性
        
        参数:
            x: 子弹初始X坐标
            y: 子弹初始Y坐标
            bullet_type: 子弹类型
            damage: 子弹伤害值
        """
        self.x = x  # 子弹X坐标
        self.y = y  # 子弹Y坐标
        self.type = bullet_type  # 子弹类型
        
        # 根据子弹类型设置不同属性
        if bullet_type == "normal":
            self.vel = -10  # 速度（负值表示向上）
            self.width = 4  # 宽度
            self.height = 10  # 高度
            self.color = YELLOW  # 颜色
            self.damage = damage if damage is not None else 1  # 伤害
        elif bullet_type == "diagonal_left":
            self.vel = -8  # 速度
            self.width = 4  # 宽度
            self.height = 10  # 高度
            self.color = YELLOW  # 颜色
            self.angle = -math.pi/6  # 角度（向左上方）
            self.damage = damage if damage is not None else 1  # 伤害
        elif bullet_type == "diagonal_right":
            self.vel = -8  # 速度
            self.width = 4  # 宽度
            self.height = 10  # 高度
            self.color = YELLOW  # 颜色
            self.angle = math.pi/6  # 角度（向右上方）
            self.damage = damage if damage is not None else 1  # 伤害
        elif bullet_type == "four_way_up":
            self.vel = -8  # 速度（向上）
            self.width = 4  # 宽度
            self.height = 10  # 高度
            self.color = ORANGE  # 颜色
            self.damage = damage if damage is not None else 1  # 伤害
        elif bullet_type == "four_way_down":
            self.vel = 8  # 速度（向下）
            self.width = 4  # 宽度
            self.height = 10  # 高度
            self.color = ORANGE  # 颜色
            self.damage = damage if damage is not None else 1  # 伤害
        elif bullet_type == "four_way_left":
            self.vel = -8  # 速度（向左）
            self.width = 10  # 宽度
            self.height = 4  # 高度
            self.color = ORANGE  # 颜色
            self.damage = damage if damage is not None else 1  # 伤害
        elif bullet_type == "four_way_right":
            self.vel = 8  # 速度（向右）
            self.width = 10  # 宽度
            self.height = 4  # 高度
            self.color = ORANGE  # 颜色
            self.damage = damage if damage is not None else 1  # 伤害
    
    def update(self):
        """
        更新子弹位置
        """
        # 根据子弹类型更新位置
        if self.type in ["diagonal_left", "diagonal_right"]:
            # 斜向移动
            self.x += self.vel * math.sin(self.angle)
            self.y += self.vel * math.cos(self.angle)
        elif self.type == "four_way_left":
            # 向左移动
            self.x += self.vel
        elif self.type == "four_way_right":
            # 向右移动
            self.x += self.vel
        elif self.type == "four_way_down":
            # 向下移动
            self.y += self.vel
        else:
            # 向上移动
            self.y += self.vel
    
    def draw(self, win):
        """
        在游戏窗口中绘制子弹
        
        参数:
            win: 游戏窗口表面
        """
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

class Missile:
    """
    导弹类，负责处理导弹的所有行为，包括追踪目标和爆炸效果
    """
    def __init__(self, x, y):
        """
        初始化导弹属性
        
        参数:
            x: 导弹初始X坐标
            y: 导弹初始Y坐标
        """
        self.x = x  # 导弹X坐标
        self.y = y  # 导弹Y坐标
        self.vel = -8  # 初始速度（向上）
        self.width = 6  # 宽度
        self.height = 12  # 高度
        self.color = ORANGE  # 颜色
        self.target = None  # 目标
        self.damage = 10  # 直接命中伤害
        self.explosion_radius = 150  # 爆炸范围
        self.explosion_damage = 3  # 爆炸伤害
        self.aiming_time = 60  # 瞄准时间，60帧（1秒）
        self.aiming_timer = 0  # 瞄准计时器
    
    def find_target(self, enemies, boss):
        """
        寻找导弹的目标
        
        参数:
            enemies: 敌人列表
            boss: BOSS对象
        """
        # 优先选择BOSS作为目标
        if boss:
            self.target = boss
        elif enemies:
            # 优先选择未受到伤害的敌人
            unharmed_enemies = [enemy for enemy in enemies if enemy.hit_timer == 0]
            
            if unharmed_enemies:
                # 在未受到伤害的敌人中选择最近的
                closest_enemy = None
                min_distance = float('inf')
                for enemy in unharmed_enemies:
                    distance = math.sqrt((enemy.x + enemy.width//2 - self.x)**2 + (enemy.y + enemy.height//2 - self.y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
                self.target = closest_enemy
            else:
                # 如果所有敌人都受到了伤害，选择最近的敌人
                closest_enemy = None
                min_distance = float('inf')
                for enemy in enemies:
                    distance = math.sqrt((enemy.x + enemy.width//2 - self.x)**2 + (enemy.y + enemy.height//2 - self.y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
                self.target = closest_enemy
    
    def update(self, enemies, boss):
        """
        更新导弹状态和位置
        
        参数:
            enemies: 敌人列表
            boss: BOSS对象
        
        返回:
            tuple: (是否爆炸, 爆炸位置)
        """
        # 瞄准阶段
        if self.aiming_timer < self.aiming_time:
            self.aiming_timer += 1
            # 寻找目标
            if not self.target:
                self.find_target(enemies, boss)
            # 直线飞行，同时寻找目标
            self.y += self.vel
            return False, None
        
        # 检查目标是否仍然存在
        target_exists = False
        if self.target == boss:
            target_exists = (boss is not None)
        else:
            target_exists = any(enemy == self.target for enemy in enemies)
        
        if not target_exists:
            # 目标被淘汰，重新寻找目标
            self.find_target(enemies, boss)
        
        if not self.target:
            self.find_target(enemies, boss)
        
        if self.target:
            # 追踪目标
            dx = self.target.x + self.target.width//2 - self.x
            dy = self.target.y + self.target.height//2 - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                # 向目标方向移动
                self.x += (dx / distance) * 2
                self.y += (dy / distance) * 2
        else:
            # 如果没有目标，直线飞行
            self.y += self.vel
        
        return False, None
    
    def draw(self, win):
        """
        在游戏窗口中绘制导弹
        
        参数:
            win: 游戏窗口表面
        """
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        # 导弹尾部火焰
        pygame.draw.rect(win, YELLOW, (self.x + 1, self.y + self.height, self.width - 2, 4))

class Enemy:
    """
    敌人飞机类，负责处理敌人飞机的所有行为
    """
    def __init__(self, level):
        """
        初始化敌人飞机属性
        
        参数:
            level: 当前关卡
        """
        self.width = 40  # 敌人飞机宽度
        self.height = 40  # 敌人飞机高度
        self.x = random.randint(0, WIDTH - self.width)  # 随机X位置
        self.y = random.randint(-100, -50)  # 初始Y位置（屏幕上方）
        # 水平速度：关卡越高，速度越快
        self.vel_x = random.choice([-2, 2]) if level > 1 else random.choice([-1, 1])
        # 垂直速度：第一关较慢，后续关卡逐渐加快，每关增加0.2
        if level == 1:
            self.vel_y = 0.6  # 第一关小飞机下降速度更慢
        else:
            self.vel_y = 0.6 + level * 0.2  # 其他关卡的小飞机下降速度，每关增加0.2
        self.health = 2 + level * 1  # 生命值：关卡越高，生命值越多，每关增加1
        self.max_health = 2 + level * 1  # 最大生命值
        # 根据关卡选择飞机类型
        if level == 1:
            plane_types = ["red"]  # 第一关只有红色飞机
        elif level == 2:
            plane_types = ["red", "orange"]  # 第二关添加橙色飞机
        else:
            plane_types = ["red", "orange", "blue", "green", "purple"]  # 第三关及以后添加其他颜色
        self.plane_type = random.choice(plane_types)
        
        # 根据飞机类型设置颜色和行为
        if self.plane_type == "red":
            self.color = RED  # 红色飞机
            self.can_shoot = False  # 红色飞机不发射子弹
            self.score = 10  # 红色飞机得分
        elif self.plane_type == "orange":
            self.color = ORANGE  # 橙色飞机
            self.can_shoot = True  # 橙色飞机可以射击
            self.tracking_bullets = False  # 橙色飞机发射普通子弹
            self.score = 20  # 橙色飞机得分
        else:
            # 其他颜色飞机（蓝色、绿色、紫色）
            if self.plane_type == "blue":
                self.color = BLUE
            elif self.plane_type == "green":
                self.color = GREEN
            else:  # purple
                self.color = (128, 0, 128)
            self.can_shoot = True  # 其他颜色飞机可以射击
            self.tracking_bullets = True  # 其他颜色飞机发射跟踪子弹
            self.score = 30  # 其他颜色飞机得分
        
        self.drop_item = random.random() < 0.6  # 物品掉落概率（从30%增加到60%）
        self.hit_timer = 0  # 被击中计时器
        # 射击相关属性
        self.shoot_count = 0  # 射击计数器
        self.shoot_delay = 180 - level * 5  # 射击延迟，关卡越高延迟越短，但减少幅度降低，基础延迟增加
        # 波浪移动相关属性
        self.wave_offset = random.uniform(0, 2 * math.pi)
        self.wave_speed = random.uniform(0.05, 0.15)
        self.wave_amplitude = random.uniform(0.3, 0.8)
    
    def update(self):
        """
        更新敌人飞机状态和位置
        
        返回:
            list: 发射的子弹列表，如果没有射击则返回空列表
        """
        # 多样化移动
        # 1. 基础移动
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 2. 波浪移动效果
        self.wave_offset += self.wave_speed
        self.x += math.sin(self.wave_offset) * self.wave_amplitude
        
        # 3. 随机方向变化
        if random.random() < 0.01:  # 1%概率改变水平速度
            self.vel_x = random.uniform(-2, 2)
        
        # 边界检测：碰到左右边界反弹
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.vel_x *= -1
        # 减少被击中计时器
        if self.hit_timer > 0:
            self.hit_timer -= 1
        
        # 射击逻辑
        bullets = []
        if self.can_shoot:
            self.shoot_count += 1
            if self.shoot_count >= self.shoot_delay:
                self.shoot_count = 0
                bullets = self.shoot()
        
        return bullets
    
    def shoot(self):
        """
        小飞机射击方法
        
        返回:
            list: 发射的子弹列表
        """
        bullets = []
        if hasattr(self, 'tracking_bullets') and self.tracking_bullets:
            # 发射跟踪子弹
            bullets.append(EnemyBullet(self.x + self.width//2, self.y + self.height, math.pi/2, tracking=True))
        else:
            # 发射普通子弹
            bullets.append(EnemyBullet(self.x + self.width//2, self.y + self.height, math.pi/2))
        return bullets
    
    def draw(self, win):
        """
        在游戏窗口中绘制敌人飞机
        
        参数:
            win: 游戏窗口表面
        """
        # 使用加载的图片绘制敌人飞机
        if enemy_image:
            win.blit(enemy_image, (self.x, self.y))
        else:
            # 绘制更美观的敌人飞机形状
            if self.hit_timer > 0:
                current_color = (255, 100, 100)  # 被击中时的颜色
            else:
                current_color = self.color  # 正常颜色
            
            # 绘制敌人飞机的形状：正三角形（飞机头朝下）
            points = [
                (self.x + self.width//2, self.y + self.height),  # 底部（飞机头）
                (self.x, self.y),  # 左上角
                (self.x + self.width, self.y),  # 右上角
            ]
            pygame.draw.polygon(win, current_color, points)
            # 绘制飞机的细节
            pygame.draw.polygon(win, (100, 0, 0), points, 2)  # 边框
            # 绘制机翼
            wing_points1 = [
                (self.x + self.width//4, self.y + self.height//2),
                (self.x - 10, self.y + self.height//2 - 15),
                (self.x + self.width//4, self.y + self.height//2 - 30)
            ]
            wing_points2 = [
                (self.x + 3*self.width//4, self.y + self.height//2),
                (self.x + self.width + 10, self.y + self.height//2 - 15),
                (self.x + 3*self.width//4, self.y + self.height//2 - 30)
            ]
            pygame.draw.polygon(win, current_color, wing_points1)
            pygame.draw.polygon(win, current_color, wing_points2)
            pygame.draw.polygon(win, (100, 0, 0), wing_points1, 1)
            pygame.draw.polygon(win, (100, 0, 0), wing_points2, 1)
        
        # 绘制生命值条
        health_ratio = self.health / self.max_health
        pygame.draw.rect(win, (50, 50, 50), (self.x, self.y + self.height + 2, self.width, 3))  # 背景（移到飞机下方）
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y + self.height + 2, int(self.width * health_ratio), 3))  # 生命值（移到飞机下方）
    
    def hit(self):
        """
        处理敌人被击中的情况
        """
        self.hit_timer = 10  # 设置被击中计时器
        
class Boss:
    """
    BOSS类，负责处理BOSS的所有行为
    """
    def __init__(self, level):
        """
        初始化BOSS属性
        
        参数:
            level: 当前关卡
        """
        self.level = level  # 当前关卡
        # 根据关卡设置不同的boss属性
        if level == 1:
            # 第一关boss
            self.width = 100  # 宽度
            self.height = 100  # 高度
            self.x = WIDTH // 2 - self.width // 2  # 初始X位置（居中）
            self.y = -self.height  # 初始Y位置（屏幕上方）
            self.vel_y = 1  # 垂直移动速度
            self.vel_x = 2  # 水平移动速度
            self.health = 50  # 生命值
            self.max_health = 50  # 最大生命值
            self.color = (139, 0, 0)  # 颜色
            self.shoot_count = 0  # 射击计数器
            self.shoot_delay = 30  # 射击延迟（帧）
            self.hit_timer = 0  # 被击中计时器
            self.score = 500  # BOSS得分
        elif level == 2:
            # 第二关boss
            self.width = 120  # 宽度
            self.height = 120  # 高度
            self.x = WIDTH // 2 - self.width // 2  # 初始X位置（居中）
            self.y = -self.height  # 初始Y位置（屏幕上方）
            self.vel_y = 1  # 垂直移动速度
            self.vel_x = 2.5  # 水平移动速度
            self.health = 65  # 生命值
            self.max_health = 65  # 最大生命值
            self.color = (165, 42, 42)  # 颜色
            self.shoot_count = 0  # 射击计数器
            self.shoot_delay = 25  # 射击延迟（帧）
            self.hit_timer = 0  # 被击中计时器
            self.score = 750  # BOSS得分
        elif level == 3:
            # 第三关boss（最终boss）
            self.width = 150  # 宽度
            self.height = 150  # 高度
            self.x = WIDTH // 2 - self.width // 2  # 初始X位置（居中）
            self.y = -self.height  # 初始Y位置（屏幕上方）
            self.vel_y = 1  # 垂直移动速度
            self.vel_x = 3  # 水平移动速度
            self.health = 85  # 生命值
            self.max_health = 85  # 最大生命值
            self.color = (220, 20, 60)  # 颜色
            self.shoot_count = 0  # 射击计数器
            self.shoot_delay = 20  # 射击延迟（帧）
            self.hit_timer = 0  # 被击中计时器
            self.score = 1000  # BOSS得分
        else:
            # 处理level大于3的情况
            self.width = 150 + (level - 3) * 20  # 宽度随关卡增加
            self.height = 150 + (level - 3) * 20  # 高度随关卡增加
            self.x = WIDTH // 2 - self.width // 2  # 初始X位置（居中）
            self.y = -self.height  # 初始Y位置（屏幕上方）
            self.vel_y = 1  # 垂直移动速度
            self.vel_x = 3 + (level - 3) * 0.5  # 水平移动速度随关卡增加
            self.health = 85 + (level - 3) * 20  # 生命值随关卡增加，每关增加20
            self.max_health = 85 + (level - 3) * 20  # 最大生命值
            self.color = (220, 20, 60)  # 颜色
            self.shoot_count = 0  # 射击计数器
            self.shoot_delay = max(10, 20 - (level - 3) * 2)  # 射击延迟随关卡减少
            self.hit_timer = 0  # 被击中计时器
            self.score = 1000 + (level - 3) * 250  # BOSS得分随关卡增加
    
    def update(self):
        """
        更新BOSS状态和位置
        
        返回:
            bool: 是否需要射击
        """
        # 初始阶段：向下移动到指定位置
        if self.y < 50:
            self.y += self.vel_y
        else:
            # 正常阶段：左右移动
            self.x += self.vel_x
            # 边界检测：碰到左右边界反弹
            if self.x <= 0 or self.x >= WIDTH - self.width:
                self.vel_x *= -1
        
        # 减少被击中计时器
        if self.hit_timer > 0:
            self.hit_timer -= 1
        
        # 增加射击计数器
        self.shoot_count += 1
        # 检查是否需要射击
        if self.shoot_count >= self.shoot_delay:
            self.shoot_count = 0
            return True
        return False
    
    def shoot(self):
        """
        BOSS射击方法
        
        返回:
            list: 发射的子弹列表
        """
        bullets = []
        # 根据关卡设置不同的射击模式
        if hasattr(self, 'level'):
            level = self.level
        else:
            # 默认为第一关boss
            level = 1
        
        # 计算射击角度数量：关卡越高，角度越多
        if level == 1:
            angle_count = 5
        elif level == 2:
            angle_count = 8
        elif level == 3:
            angle_count = 10
        else:
            angle_count = 10 + (level - 3) * 2
        
        # 散射射击：向多个角度发射子弹
        for i in range(angle_count):
            angle = math.pi * 2 * i / angle_count
            bullets.append(EnemyBullet(self.x + self.width//2, self.y + self.height, angle))
        
        return bullets
    
    def draw(self, win):
        """
        在游戏窗口中绘制BOSS
        
        参数:
            win: 游戏窗口表面
        """
        # 使用加载的图片绘制BOSS飞机
        if boss_image:
            win.blit(boss_image, (self.x, self.y))
        else:
            # 如果图片加载失败，绘制圆形作为后备
            if self.hit_timer > 0:
                current_color = (255, 100, 100)  # 被击中时的颜色
            else:
                current_color = self.color  # 正常颜色
            
            # 主体 - 圆形
            pygame.draw.circle(win, current_color, (self.x + self.width//2, self.y + self.height//2), self.width//2)
        
        # 绘制生命值条
        health_ratio = self.health / self.max_health
        pygame.draw.rect(win, (50, 50, 50), (self.x, self.y - 10, self.width, 5))  # 背景
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y - 10, int(self.width * health_ratio), 5))  # 生命值
    
    def hit(self):
        """
        处理BOSS被击中的情况
        """
        self.hit_timer = 10  # 设置被击中计时器

class EnemyBullet:
    """
    敌人子弹类，负责处理敌人发射的子弹
    """
    def __init__(self, x, y, angle, tracking=False):
        """
        初始化敌人子弹属性
        
        参数:
            x: 子弹初始X坐标
            y: 子弹初始Y坐标
            angle: 子弹飞行角度
            tracking: 是否为跟踪子弹
        """
        self.x = x  # 子弹X坐标
        self.y = y  # 子弹Y坐标
        self.angle = angle  # 飞行角度
        self.vel = 5  # 飞行速度
        self.width = 3  # 宽度
        self.height = 3  # 高度
        self.color = GREEN  # 颜色
        self.tracking = tracking  # 是否为跟踪子弹
        self.tracking_delay = 3  # 跟踪延迟，每3帧更新一次方向
        self.tracking_counter = 0  # 跟踪计数器
    
    def update(self):
        """
        更新敌人子弹位置
        """
        if self.tracking:
            # 跟踪子弹：每几帧更新一次方向，追踪玩家
            self.tracking_counter += 1
            if self.tracking_counter >= self.tracking_delay:
                self.tracking_counter = 0
                # 假设玩家在屏幕底部中央附近
                player_x = WIDTH // 2
                player_y = HEIGHT - 100
                # 计算到玩家的方向
                dx = player_x - self.x
                dy = player_y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    # 更新角度朝向玩家
                    self.angle = math.atan2(dy, dx)
        
        # 根据角度计算移动方向
        self.x += self.vel * math.cos(self.angle)
        self.y += self.vel * math.sin(self.angle)
    
    def draw(self, win):
        """
        在游戏窗口中绘制敌人子弹
        
        参数:
            win: 游戏窗口表面
        """
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), 3)

class Item:
    """
    物品类，负责处理游戏中的掉落物品
    """
    def __init__(self, x, y, item_type, level):
        """
        初始化物品属性
        
        参数:
            x: 物品初始X坐标
            y: 物品初始Y坐标
            item_type: 物品类型
            level: 当前关卡
        """
        self.x = x  # 物品X坐标
        self.y = y  # 物品Y坐标
        self.vel_y = 3  # 下落速度
        self.item_type = item_type  # 物品类型
        self.level = level
        self.angle = 0  # 旋转角度
        self.angle_speed = 0.1  # 旋转速度
        self.scale = 1.0  # 缩放比例
        self.scale_dir = 1  # 缩放方向
        # 根据物品类型设置颜色和标签
        if item_type == "bomb":
            self.color = YELLOW  # 炸弹：黄色
            self.label = "B"
        elif item_type == "missile":
            self.color = ORANGE  # 导弹：橙色
            self.label = "M"
        elif item_type == "bullet_double":
            self.color = GREEN  # 双发子弹：绿色
            self.label = "D"
        elif item_type == "bullet_triple":
            self.color = BLUE  # 三发子弹：蓝色
            self.label = "T"
        elif item_type == "bullet_powerful":
            self.color = ORANGE  # 强力子弹：橙色
            self.label = "P"
        elif item_type == "shield":
            self.color = (100, 100, 255)  # 护盾：浅蓝色
            self.label = "S"
        elif item_type == "medkit":
            self.color = (255, 0, 0)  # 医疗包：红色
            self.label = "H"
        elif item_type == "bullet_four_way":
            self.color = (128, 0, 128)  # 四面子弹：紫色
            self.label = "4"
        elif item_type == "bullet_five_way":
            self.color = (255, 165, 0)  # 五发子弹：橙色
            self.label = "5"
    
    def update(self):
        """
        更新物品位置
        """
        self.y += self.vel_y  # 向下移动
        self.angle += self.angle_speed  # 旋转
        # 缩放动画
        self.scale += 0.02 * self.scale_dir
        if self.scale > 1.2 or self.scale < 0.8:
            self.scale_dir *= -1
    
    def draw(self, win):
        """
        在游戏窗口中绘制物品
        
        参数:
            win: 游戏窗口表面
        """
        # 保存当前状态
        original_pos = pygame.transform.rotate
        # 绘制物品主体
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), 8)
        # 绘制发光效果
        glow_radius = int(12 * self.scale)
        pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), glow_radius, 1)
        # 绘制旋转的边框
        rotated_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(rotated_surface, self.color, (15, 15), 10, 2)
        rotated_surface = pygame.transform.rotate(rotated_surface, self.angle * 57.3)  # 转换为度数
        rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        win.blit(rotated_surface, rect)
        # 绘制标签
        font = pygame.font.Font(None, 16)
        text = font.render(self.label, True, WHITE)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        win.blit(text, text_rect)

class Explosion:
    """
    爆炸类，负责处理爆炸效果
    """
    def __init__(self, x, y, size, is_missile=False):
        """
        初始化爆炸属性
        
        参数:
            x: 爆炸中心X坐标
            y: 爆炸中心Y坐标
            size: 爆炸大小
            is_missile: 是否为导弹爆炸
        """
        self.x = x  # 爆炸中心X坐标
        self.y = y  # 爆炸中心Y坐标
        self.size = size  # 爆炸大小
        self.stage = 0  # 爆炸阶段
        self.max_stages = 10  # 最大爆炸阶段
        self.is_missile = is_missile  # 是否为导弹爆炸
        # 初始化烟花粒子
        self.particles = []
        # 导弹爆炸粒子数量更多
        particle_count = 120 if is_missile else 60
        for _ in range(particle_count):  # 60或120个粒子（大幅增加粒子数量使烟花更密集）
            angle = random.uniform(0, 2 * math.pi)
            # 导弹爆炸速度更快
            speed = random.uniform(3, 8) if is_missile else random.uniform(2, 5)
            # 随机颜色，导弹爆炸颜色更鲜艳
            if is_missile:
                color = (random.randint(200, 255), random.randint(150, 255), random.randint(50, 150))
            else:
                color = (random.randint(200, 255), random.randint(100, 255), random.randint(0, 100))
            # 随机生命周期和衰减
            life = random.uniform(0.8, 1.2)
            decay = random.uniform(0.015, 0.06) if is_missile else random.uniform(0.02, 0.05)
            # 随机方向变化
            direction_change = random.uniform(-0.1, 0.1)
            self.particles.append({
                'x': x,
                'y': y,
                'angle': angle,
                'speed': speed,
                'color': color,
                'life': life,
                'decay': decay,
                'direction_change': direction_change
            })
        # 初始化烟雾粒子
        self.smoke_particles = []
        if is_missile:
            for _ in range(50):  # 导弹爆炸产生更多烟雾
                smoke_angle = random.uniform(0, 2 * math.pi)
                smoke_speed = random.uniform(1, 3)
                # 烟雾颜色
                smoke_color = (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150))
                self.smoke_particles.append({
                    'x': x,
                    'y': y,
                    'angle': smoke_angle,
                    'speed': smoke_speed,
                    'color': smoke_color,
                    'life': random.uniform(1.5, 2.5),
                    'decay': random.uniform(0.01, 0.03),
                    'size': random.uniform(3, 6)
                })
    
    def update(self):
        """
        更新爆炸状态
        
        返回:
            bool: 爆炸是否结束
        """
        self.stage += 1  # 增加爆炸阶段
        # 更新粒子
        for particle in self.particles:
            # 随机改变方向，使轨迹更不规则
            particle['angle'] += particle['direction_change']
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            # 速度逐渐减小
            particle['speed'] *= 0.98
            particle['life'] -= particle['decay']
        # 移除死亡的粒子
        self.particles = [p for p in self.particles if p['life'] > 0]
        # 更新烟雾粒子
        for smoke in self.smoke_particles:
            smoke['x'] += math.cos(smoke['angle']) * smoke['speed']
            smoke['y'] += math.sin(smoke['angle']) * smoke['speed']
            smoke['life'] -= smoke['decay']
            # 烟雾逐渐变大
            smoke['size'] *= 1.02
        # 移除死亡的烟雾粒子
        self.smoke_particles = [s for s in self.smoke_particles if s['life'] > 0]
        return self.stage >= self.max_stages and len(self.particles) == 0 and len(self.smoke_particles) == 0  # 检查爆炸是否结束
    
    def draw(self, win):
        """
        在游戏窗口中绘制爆炸效果
        
        参数:
            win: 游戏窗口表面
        """
        # 绘制中心爆炸效果
        if self.stage < self.max_stages:
            # 计算当前爆炸半径
            radius = self.size * (self.stage + 1) // self.max_stages
            # 随机调整中心爆炸的大小和颜色
            random_radius = radius + random.randint(-2, 2)
            if self.is_missile:
                # 导弹爆炸颜色更亮
                pygame.draw.circle(win, (255, 200, 100), (self.x, self.y), random_radius)
            else:
                pygame.draw.circle(win, ORANGE, (self.x, self.y), random_radius)
        # 绘制烟花粒子
        for particle in self.particles:
            if particle['life'] > 0:
                # 粒子大小随生命值减小
                size = int(particle['life'] * (4 if self.is_missile else 3))
                # 粒子颜色随生命值变化
                alpha = int(particle['life'] * 255)
                # 确保颜色值在有效范围内
                r = max(0, min(255, particle['color'][0]))
                g = max(0, min(255, particle['color'][1]))
                b = max(0, min(255, particle['color'][2]))
                a = max(0, min(255, alpha))
                particle_color = (r, g, b, a)
                # 创建半透明表面
                surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, particle_color, (size, size), size)
                win.blit(surface, (int(particle['x'] - size), int(particle['y'] - size)))
        # 绘制烟雾粒子
        for smoke in self.smoke_particles:
            if smoke['life'] > 0:
                # 烟雾大小随生命周期变化
                size = int(smoke['size'])
                # 烟雾透明度随生命值减小
                alpha = int(smoke['life'] * 100)  # 烟雾更透明
                # 确保颜色值在有效范围内
                r = max(0, min(255, smoke['color'][0]))
                g = max(0, min(255, smoke['color'][1]))
                b = max(0, min(255, smoke['color'][2]))
                a = max(0, min(255, alpha))
                smoke_color = (r, g, b, a)
                # 创建半透明表面
                surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, smoke_color, (size, size), size)
                win.blit(surface, (int(smoke['x'] - size), int(smoke['y'] - size)))

class Bomb:
    """
    炸弹类，负责处理炸弹效果
    """
    def __init__(self, x, y):
        """
        初始化炸弹属性
        
        参数:
            x: 炸弹中心X坐标
            y: 炸弹中心Y坐标
        """
        self.x = x  # 炸弹中心X坐标
        self.y = y  # 炸弹中心Y坐标
        self.radius = 0  # 当前爆炸半径
        self.max_radius = 150  # 最大爆炸半径
        self.expanding = True  # 是否正在扩展
        self.explosion = Explosion(x, y, 80, is_missile=True)  # 添加烟花爆炸效果
    
    def update(self):
        """
        更新炸弹状态
        
        返回:
            bool: 爆炸是否结束
        """
        # 更新烟花爆炸效果
        explosion_done = self.explosion.update()
        if self.expanding:
            self.radius += 10  # 增加爆炸半径
            if self.radius >= self.max_radius:
                self.expanding = False
                return explosion_done  # 爆炸结束
        return explosion_done  # 爆炸未结束
    
    def draw(self, win):
        """
        在游戏窗口中绘制炸弹效果
        
        参数:
            win: 游戏窗口表面
        """
        # 绘制烟花爆炸效果
        self.explosion.draw(win)
        # 保留原有的圆形爆炸视觉效果
        if self.expanding:
            # 增强炸弹视觉效果
            pygame.draw.circle(win, YELLOW, (self.x, self.y), self.radius, 3)  # 外层
            pygame.draw.circle(win, ORANGE, (self.x, self.y), self.radius // 2, 3)  # 中层
            pygame.draw.circle(win, RED, (self.x, self.y), self.radius // 4, 3)  # 内层
            # 添加爆炸光芒效果
            for i in range(8):
                angle = math.pi * 2 * i / 8
                x = self.x + math.cos(angle) * self.radius
                y = self.y + math.sin(angle) * self.radius
                pygame.draw.line(win, YELLOW, (self.x, self.y), (x, y), 2)

class Game:
    """
    游戏主类，负责处理游戏的核心逻辑
    """
    
    def _init_font(self, size):
        """
        安全地初始化字体，避免pygame系统字体问题
        """
        # 尝试使用系统字体，但避免使用列表形式（可能触发pygame bug）
        font_names = ["Microsoft YaHei", "SimHei", "SimSun", "Arial", "sans-serif"]
        
        # 首先尝试直接使用 pygame 的默认字体，这通常是最可靠的
        try:
            font = pygame.font.Font(None, size)
            # 测试中文字符
            test_surface = font.render("中文测试", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                return font
        except:
            pass
        
        # 尝试系统字体
        for font_name in font_names:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试中文字符
                test_surface = font.render("中文测试", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # 最后的备选方案 - 强制使用默认字体
        try:
            return pygame.font.Font(None, size)
        except:
            # 终极备选
            return pygame.font.SysFont("arial", size)
    
    def _init_clouds(self):
        """
        初始化云
        """
        import random
        for i in range(5):
            cloud = {
                'x': random.randint(-100, WIDTH),
                'y': random.randint(50, 200),
                'speed': random.uniform(0.2, 0.5),
                'size': random.randint(30, 60)
            }
            self.clouds.append(cloud)
    
    def _init_background_planes(self):
        """
        初始化背景飞机
        """
        import random
        for i in range(3):
            plane = {
                'x': random.randint(-100, WIDTH),
                'y': random.randint(200, 400),
                'speed': random.uniform(1, 2),
                'size': random.randint(20, 30)
            }
            self.background_planes.append(plane)
    
    def _draw_decorations(self):
        """
        绘制装饰元素
        """
        import pygame
        import random
        
        # 绘制云
        for cloud in self.clouds:
            # 移动云
            cloud['x'] += cloud['speed']
            if cloud['x'] > WIDTH + 100:
                cloud['x'] = -100
                cloud['y'] = random.randint(50, 200)
                cloud['speed'] = random.uniform(0.2, 0.5)
                cloud['size'] = random.randint(30, 60)
            
            # 绘制云
            pygame.draw.circle(WIN, (100, 100, 100), (int(cloud['x']), int(cloud['y'])), cloud['size'])
            pygame.draw.circle(WIN, (100, 100, 100), (int(cloud['x'] + cloud['size']*0.6), int(cloud['y'])), cloud['size']*0.8)
            pygame.draw.circle(WIN, (100, 100, 100), (int(cloud['x'] + cloud['size']*1.2), int(cloud['y'])), cloud['size'])
        
        # 绘制背景飞机
        for plane in self.background_planes:
            # 移动飞机
            plane['x'] += plane['speed']
            if plane['x'] > WIDTH + 100:
                plane['x'] = -100
                plane['y'] = random.randint(200, 400)
                plane['speed'] = random.uniform(1, 2)
                plane['size'] = random.randint(20, 30)
            
            # 绘制飞机（往前飞的方向）
            pygame.draw.polygon(WIN, (150, 150, 150), [
                (int(plane['x'] + plane['size']), int(plane['y'] + plane['size']/2)),
                (int(plane['x']), int(plane['y'])),
                (int(plane['x']), int(plane['y'] + plane['size'])),
                (int(plane['x'] + plane['size']), int(plane['y'] + plane['size']/2))
            ])
        
        # 绘制星星
        if self.decor_timer % 5 == 0:
            for _ in range(5):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                pygame.draw.circle(WIN, (255, 255, 255), (x, y), 1)
        
        # 更新装饰元素计时器
        self.decor_timer += 1
    
    def __init__(self):
        """
        初始化游戏属性
        """
        self.player = Player()  # 玩家对象
        self.enemies = []  # 敌人列表
        self.enemy_bullets = []  # 敌人子弹列表
        self.items = []  # 物品列表
        self.explosions = []  # 爆炸效果列表
        self.bombs = []  # 炸弹列表
        self.running = True  # 游戏运行状态
        self.clock = pygame.time.Clock()  # 游戏时钟
        self.enemy_spawn_count = 0  # 敌人生成计数器
        self.enemy_spawn_delay = 60  # 敌人生成延迟（帧）
        self.boss = None  # BOSS对象
        self.boss_defeated = False  # BOSS是否被击败
        self.level = 1  # 当前关卡
        self.max_level = 3  # 最大关卡
        self.level_start_time = pygame.time.get_ticks()  # 关卡开始时间
        # 初始化字体
        self.font = self._init_font(18)
        self.game_over = False  # 游戏结束状态
        self.show_instructions = True  # 游戏开始前显示说明界面
        self.level_enemies_spawned = False  # 关卡敌人是否已生成
        self.enemies_destroyed = 0  # 消灭的敌人数量
        self.level_message = ""  # 关卡消息
        self.level_message_timer = 0  # 关卡消息计时器
        # 双击检测
        self.space_press_count = 0  # 空格键按下次数
        self.space_last_press_time = 0  # 空格键上次按下时间
        self.double_click_time = 300  # 双击时间间隔（毫秒）
        # 鼠标右键长按检测
        self.right_mouse_pressed = False  # 鼠标右键是否被按下
        self.right_mouse_press_time = 0  # 鼠标右键按下时间
        self.long_press_time = 500  # 长按时间阈值（毫秒）
        
        # 装饰元素
        self.clouds = []  # 云列表
        self.background_planes = []  # 背景飞机列表
        self.decor_timer = 0  # 装饰元素计时器
        
        # 最高分数记录
        self.high_score = self.load_high_score()
        self.new_high_score = False  # 是否创造了新的最高分数
        
        # 升级系统
        self.level_up_score = 100  # 每100分升一级
        self.last_level_up_score = 0  # 上次升级时的分数
        
        # 屏幕震动效果
        self.screen_shake_timer = 0  # 屏幕震动计时器
        self.screen_shake_intensity = 0  # 屏幕震动强度
        
        # 连续击杀效果
        self.kill_streak = 0  # 连续击杀数
        self.kill_streak_timer = 0  # 连续击杀计时器
        self.kill_streak_timeout = 2000  # 连续击杀超时时间（毫秒）
        self.last_kill_time = 0  # 上次击杀时间
        
        # 帧率计数器
        self.fps_counter = 0
        self.fps_timer = 0
        self.current_fps = 0
        
        # 初始化云
        self._init_clouds()
        # 初始化背景飞机
        self._init_background_planes()
    
    def load_high_score(self):
        """
        加载最高分数
        """
        try:
            with open('high_score.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self, score):
        """
        保存最高分数
        """
        try:
            with open('high_score.txt', 'w') as f:
                f.write(str(score))
        except:
            pass
    
    def draw(self):
        """
        绘制游戏界面的所有元素
        """
        # 填充背景为黑色
        WIN.fill(BLACK)
        
        if self.show_instructions:
            # 绘制装饰元素
            self._draw_decorations()
            
            # 游戏说明界面
            title_text = self.font.render("Plane Game", True, WHITE)
            start_text = self.font.render("Press any key to start", True, WHITE)
            
            # Controls
            control_title = self.font.render("Controls:", True, WHITE)
            control1 = self.font.render("Move: Arrow keys", True, WHITE)
            control2 = self.font.render("Shoot: Left mouse click (auto-fire)", True, WHITE)
            control3 = self.font.render("Bomb: Right mouse click", True, WHITE)
            control4 = self.font.render("Missile: Spacebar to launch, Spacebar to detonate", True, WHITE)
            control6 = self.font.render("Weapon switch: 1(single), 2(double), 3(triple)", True, WHITE)
            control7 = self.font.render("Weapon switch: Mouse wheel up/down", True, WHITE)
            
            # Power-ups
            item_title = self.font.render("Power-ups:", True, WHITE)
            item1 = self.font.render("Yellow: Bomb (increase bomb count)", True, WHITE)
            item2 = self.font.render("Orange: Missile (increase missile count)", True, WHITE)
            item4 = self.font.render("Green: Double shot", True, WHITE)
            item5 = self.font.render("Blue: Triple shot", True, WHITE)
            item6 = self.font.render("Dark blue: Shield", True, WHITE)
            item7 = self.font.render("Red: Medkit (restore 20 health)", True, WHITE)
            
            # Gameplay
            game_title = self.font.render("Gameplay:", True, WHITE)
            game1 = self.font.render("1. Small planes appear at the start of each level", True, WHITE)
            game2 = self.font.render("2. BOSS appears after destroying all small planes", True, WHITE)
            game3 = self.font.render("3. Defeat BOSS to advance to next level", True, WHITE)
            game4 = self.font.render("4. Difficulty increases with each level", True, WHITE)
            game5 = self.font.render("5. Missiles track enemies and explode on impact", True, WHITE)
            game7 = self.font.render("7. Bombs clear all enemies on screen", True, WHITE)
            
            # Objectives
            win_title = self.font.render("Objectives:", True, WHITE)
            win1 = self.font.render("Defeat BOSS in each level, reach higher levels", True, WHITE)
            win2 = self.font.render("Collect power-ups to enhance your abilities", True, WHITE)
            win3 = self.font.render("Use bombs and missiles strategically", True, WHITE)
            
            # 绘制说明界面
            WIN.blit(title_text, (WIDTH//2 - 100, 50))
            WIN.blit(start_text, (WIDTH//2 - 120, 100))
            
            WIN.blit(control_title, (50, 150))
            WIN.blit(control1, (70, 180))
            WIN.blit(control2, (70, 210))
            WIN.blit(control3, (70, 240))
            WIN.blit(control4, (70, 270))
            WIN.blit(control6, (70, 330))
            WIN.blit(control7, (70, 360))
            
            WIN.blit(item_title, (50, 350))
            WIN.blit(item1, (70, 380))
            WIN.blit(item2, (70, 410))
            WIN.blit(item4, (70, 470))
            WIN.blit(item5, (70, 500))
            WIN.blit(item6, (70, 530))
            WIN.blit(item7, (70, 560))
            
            WIN.blit(game_title, (400, 150))
            WIN.blit(game1, (420, 180))
            WIN.blit(game2, (420, 210))
            WIN.blit(game3, (420, 240))
            WIN.blit(game4, (420, 270))
            WIN.blit(game5, (420, 300))
            WIN.blit(game7, (420, 360))
            
            WIN.blit(win_title, (400, 410))
            WIN.blit(win1, (420, 440))
            WIN.blit(win2, (420, 470))
            WIN.blit(win3, (420, 500))
        else:
            # 游戏主界面
            # 先绘制所有游戏元素到临时表面，然后应用屏幕震动
            temp_surface = pygame.Surface((WIDTH, HEIGHT))
            temp_surface.fill((0, 0, 0))
            
            # 直接绘制游戏元素，不绘制背景装饰
            
            self.player.draw(temp_surface)
            for bullet in self.player.bullets:
                bullet.draw(temp_surface)
            for missile in self.player.missiles:
                missile.draw(temp_surface)
            
            for enemy in self.enemies:
                enemy.draw(temp_surface)
            
            for bullet in self.enemy_bullets:
                bullet.draw(temp_surface)
            
            for item in self.items:
                item.draw(temp_surface)
            
            for explosion in self.explosions:
                explosion.draw(temp_surface)
            
            for bomb in self.bombs:
                bomb.draw(temp_surface)
            
            if self.boss:
                self.boss.draw(temp_surface)
            
            # 应用屏幕震动效果并绘制到主窗口
            shake_offset_x = 0
            shake_offset_y = 0
            if self.screen_shake_timer > 0:
                import random
                shake_offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
                shake_offset_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            
            # 绘制UI元素到临时表面
            score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
            health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
            bomb_text = self.font.render(f"Bombs: {self.player.bomb_count}", True, WHITE)
            missile_text = self.font.render(f"Missiles: {self.player.missile_count}", True, WHITE)
            level_text = self.font.render(f"Level: {self.level}", True, WHITE)
            
            # 计算每种子弹类型的伤害
            normal_damage = 1 * (2 ** (self.player.bullet_upgrade_count.get("normal", 0) - 1)) if self.player.bullet_upgrade_count.get("normal", 0) > 0 else 1
            double_damage = 1 * (2 ** (self.player.bullet_upgrade_count.get("double", 0) - 1)) if self.player.bullet_upgrade_count.get("double", 0) > 0 else 1
            triple_damage = 1 * (2 ** (self.player.bullet_upgrade_count.get("triple", 0) - 1)) if self.player.bullet_upgrade_count.get("triple", 0) > 0 else 1
            
            # 右下角子弹类型选择和伤害显示
            bullet_y_offset = 0
            
            # 绘制血量条背景
            max_health = 1000
            health_bar_width = 200
            health_bar_height = 15
            pygame.draw.rect(temp_surface, (50, 50, 50), (10, 10, health_bar_width, health_bar_height))
            
            # 绘制血量条
            health_ratio = min(self.player.health / max_health, 1)
            if health_ratio > 0.5:
                health_color = (0, 255, 0)
            elif health_ratio > 0.25:
                health_color = (255, 255, 0)
            else:
                health_color = (255, 0, 0)
            pygame.draw.rect(temp_surface, health_color, (10, 10, int(health_bar_width * health_ratio), health_bar_height))
            
            # 绘制血量文本
            health_text_display = self.font.render(f"Health: {self.player.health}/{max_health}", True, WHITE)
            temp_surface.blit(health_text_display, (10, 30))
            
            # 绘制分数等信息
            bottom_offset = 0
            temp_surface.blit(score_text, (10, HEIGHT - 120 + bottom_offset))
            high_score_display = self.font.render(f"High Score: {self.high_score}", True, WHITE)
            temp_surface.blit(high_score_display, (10, HEIGHT - 90 + bottom_offset))
            temp_surface.blit(bomb_text, (10, HEIGHT - 60 + bottom_offset))
            temp_surface.blit(missile_text, (10, HEIGHT - 30 + bottom_offset))
            
            # 绘制关卡在右上方
            temp_surface.blit(level_text, (WIDTH - 100, 10))
            
            # 绘制当前帧率
            fps_text = self.font.render(f"FPS: {self.current_fps}", True, WHITE)
            temp_surface.blit(fps_text, (WIDTH - 100, 30))
            
            # 绘制右下角子弹类型选择
            bullet_type_map = {"normal": "Single", "double": "Double", "triple": "Triple", "powerful": "Powerful", "five_way": "Five-Way"}
            bullet_type_en = bullet_type_map.get(self.player.bullet_type, self.player.bullet_type)
            
            bullet_select_text1 = self.font.render(f"1: Single ({normal_damage} damage)", True, WHITE if self.player.bullet_type != "normal" else YELLOW)
            temp_surface.blit(bullet_select_text1, (WIDTH - 200, HEIGHT - 100 + bullet_y_offset))
            
            if self.player.bullet_upgrade_count.get("double", 0) > 0:
                bullet_y_offset += 30
                bullet_select_text2 = self.font.render(f"2: Double ({double_damage} damage)", True, WHITE if self.player.bullet_type != "double" else YELLOW)
                temp_surface.blit(bullet_select_text2, (WIDTH - 200, HEIGHT - 100 + bullet_y_offset))
            
            if self.player.bullet_upgrade_count.get("triple", 0) > 0:
                bullet_y_offset += 30
                bullet_select_text3 = self.font.render(f"3: Triple ({triple_damage} damage)", True, WHITE if self.player.bullet_type != "triple" else YELLOW)
                temp_surface.blit(bullet_select_text3, (WIDTH - 200, HEIGHT - 100 + bullet_y_offset))
            
            if self.player.bullet_upgrade_count.get("five_way", 0) > 0:
                bullet_y_offset += 30
                five_way_damage = 1 * (2 ** (self.player.bullet_upgrade_count.get("five_way", 0) - 1)) if self.player.bullet_upgrade_count.get("five_way", 0) > 0 else 1
                bullet_select_text5 = self.font.render(f"5: Five-Way ({five_way_damage} damage)", True, WHITE if self.player.bullet_type != "five_way" else YELLOW)
                temp_surface.blit(bullet_select_text5, (WIDTH - 200, HEIGHT - 100 + bullet_y_offset))
            
            # 将临时表面绘制到主窗口
            WIN.blit(temp_surface, (shake_offset_x, shake_offset_y))
            
            # 绘制Game Over界面
            if self.game_over:
                # 检查是否创造了新的最高分数
                if self.player.score > self.high_score:
                    self.high_score = self.player.score
                    self.save_high_score(self.high_score)
                    self.new_high_score = True
                
                game_over_text = self.font.render("Game Over!", True, WHITE)
                restart_text = self.font.render("Press R to restart", True, WHITE)
                level_text = self.font.render(f"Level: {self.level}", True, WHITE)
                score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
                enemies_destroyed_text = self.font.render(f"Enemies destroyed: {self.enemies_destroyed}", True, WHITE)
                high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
                
                WIN.blit(game_over_text, (WIDTH//2 - 70, HEIGHT//2 - 120))
                WIN.blit(level_text, (WIDTH//2 - 50, HEIGHT//2 - 80))
                WIN.blit(score_text, (WIDTH//2 - 60, HEIGHT//2 - 40))
                WIN.blit(high_score_text, (WIDTH//2 - 70, HEIGHT//2))
                WIN.blit(enemies_destroyed_text, (WIDTH//2 - 80, HEIGHT//2 + 40))
                WIN.blit(restart_text, (WIDTH//2 - 100, HEIGHT//2 + 80))
                
                # 显示新纪录消息
                if self.new_high_score:
                    new_record_text = self.font.render("New High Score!", True, YELLOW)
                    WIN.blit(new_record_text, (WIDTH//2 - 80, HEIGHT//2 - 160))
            
            # 绘制关卡消息
            if self.level_message_timer > 0:
                level_message_text = self.font.render(self.level_message, True, YELLOW)
                WIN.blit(level_message_text, (WIDTH//2 - level_message_text.get_width()//2, HEIGHT//2 - 30))
            
            # 绘制连续击杀效果（不受震动影响）
            if self.kill_streak > 1:
                # 根据连续击杀数量调整字体大小
                font_size = 36 + min(self.kill_streak * 4, 50)
                kill_font = pygame.font.Font(None, font_size)
                kill_text = kill_font.render(f"{self.kill_streak} Kill Streak!", True, YELLOW)
                # 添加白色描边效果
                kill_text_outline = kill_font.render(f"{self.kill_streak} Kill Streak!", True, WHITE)
                # 绘制在屏幕中央偏上位置
                WIN.blit(kill_text_outline, (WIDTH//2 - kill_text.get_width()//2 - 2, HEIGHT//4 - 2))
                WIN.blit(kill_text_outline, (WIDTH//2 - kill_text.get_width()//2 + 2, HEIGHT//4 - 2))
                WIN.blit(kill_text_outline, (WIDTH//2 - kill_text.get_width()//2 - 2, HEIGHT//4 + 2))
                WIN.blit(kill_text_outline, (WIDTH//2 - kill_text.get_width()//2 + 2, HEIGHT//4 + 2))
                WIN.blit(kill_text, (WIDTH//2 - kill_text.get_width()//2, HEIGHT//4))
        
        pygame.display.update()
    
    def handle_events(self):
        """
        处理游戏中的所有事件，包括键盘输入、鼠标点击等
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                # 全屏切换（F11键）
                if event.key == pygame.K_F11:
                    global FULLSCREEN, WIN
                    FULLSCREEN = not FULLSCREEN
                    if FULLSCREEN:
                        WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
                    print(f"切换到{'全屏' if FULLSCREEN else '窗口'}模式")
                
                if self.show_instructions:
                    # 按任意键开始游戏
                    print("开始游戏")
                    self.show_instructions = False
                    # 游戏开始时先生成小飞机
                    for _ in range(8):
                        self.enemies.append(Enemy(self.level))
                else:
                    print(f"按键被按下 - 键码: {event.key}, 名称: {pygame.key.name(event.key)}")
                    # 打印所有按键，包括WASD
                    if event.key == pygame.K_w:
                        print("W键被按下 - 向上移动")
                    elif event.key == pygame.K_a:
                        print("A键被按下 - 向左移动")
                    elif event.key == pygame.K_s:
                        print("S键被按下 - 向下移动")
                    elif event.key == pygame.K_d:
                        print("D键被按下 - 向右移动")
                    
                    elif event.key == pygame.K_SPACE:
                        print("空格键被按下")
                        # 检查是否有导弹，如果有则直接引爆
                        if self.player.missiles:
                            print("引爆所有导弹")
                            # 遍历所有导弹并引爆
                            for missile in self.player.missiles[:]:
                                # 创建导弹爆炸范围视觉效果
                                explosion_x = missile.x + missile.width//2
                                explosion_y = missile.y + missile.height//2
                                missile_bomb = Bomb(explosion_x, explosion_y)
                                missile_bomb.max_radius = missile.explosion_radius
                                self.bombs.append(missile_bomb)
                                
                                # 对爆炸范围内的所有敌人造成伤害
                                for e in self.enemies[:]:
                                    dx = e.x + e.width//2 - explosion_x
                                    dy = e.y + e.height//2 - explosion_y
                                    distance = math.sqrt(dx*dx + dy*dy)
                                    if distance < missile.explosion_radius:
                                        e.health -= missile.explosion_damage
                                        e.hit()
                                        if e.health <= 0:
                                            self.enemies.remove(e)
                                            self.player.score += 10
                                            self.enemies_destroyed += 1
                                            self.explosions.append(Explosion(e.x + e.width//2, e.y + e.height//2, 30))
                                            if e.drop_item:
                                                # 在有boss存在时，提高医疗包的掉落率
                                                if self.boss:
                                                    item_type = random.choice(["bomb", "bullet_double", "bullet_triple", "bullet_powerful", "shield", "medkit", "medkit"])
                                                else:
                                                    # 增加子弹升级物品的掉落概率
                                                    item_type = random.choice(["bomb", "bullet_double", "bullet_double", "bullet_triple", "bullet_triple", "bullet_powerful", "shield", "medkit"])
                                                self.items.append(Item(e.x + e.width//2, e.y + e.height//2, item_type, self.level))
                                
                                # 对boss造成爆炸伤害
                                if self.boss:
                                    dx = self.boss.x + self.boss.width//2 - explosion_x
                                    dy = self.boss.y + self.boss.height//2 - explosion_y
                                    distance = math.sqrt(dx*dx + dy*dy)
                                    if distance < missile.explosion_radius:
                                        self.boss.health -= missile.explosion_damage
                                        self.boss.hit()
                                        if self.boss.health <= 0:
                                            self.explosions.append(Explosion(self.boss.x + self.boss.width//2, self.boss.y + self.boss.height//2, 60))
                                            # Boss死亡时掉落一堆物资
                                            boss_x = self.boss.x + self.boss.width//2
                                            boss_y = self.boss.y + self.boss.height//2
                                            # 掉落多种物资
                                            drop_items = ["bomb", "missile", "bullet_double", "bullet_triple", "shield", "medkit"]
                                            for i in range(8):  # 掉落8个物品
                                                item_type = random.choice(drop_items)
                                                self.items.append(Item(boss_x + random.randint(-30, 30), boss_y + random.randint(-30, 30), item_type, self.level))
                                            self.boss = None
                                            self.boss_defeated = True
                                
                                # 移除导弹并添加爆炸效果
                                self.player.missiles.remove(missile)
                                self.explosions.append(Explosion(explosion_x, explosion_y, missile.explosion_radius//2, is_missile=True))
                        else:
                            # 如果没有导弹，则发射导弹
                            print("单击空格键 - 发射导弹")
                            self.player.shoot_missile()
                    
                    # 数字键切换子弹类型
                    elif event.key == pygame.K_1:
                        print("数字键1被按下 - 切换到单发子弹")
                        self.player.upgrade_bullet("normal")  # 不增加升级次数
                    elif event.key == pygame.K_2:
                        # 只有当玩家获得了双发子弹技能时，才能切换
                        if self.player.bullet_upgrade_count.get("double", 0) > 0:
                            print("数字键2被按下 - 切换到双发子弹")
                            self.player.upgrade_bullet("double")  # 不增加升级次数
                        else:
                            print("数字键2被按下 - 尚未获得双发子弹技能")
                    elif event.key == pygame.K_3:
                        # 只有当玩家获得了三发子弹技能时，才能切换
                        if self.player.bullet_upgrade_count.get("triple", 0) > 0:
                            print("数字键3被按下 - 切换到三发子弹")
                            self.player.upgrade_bullet("triple")  # 不增加升级次数
                        else:
                            print("数字键3被按下 - 尚未获得三发子弹技能")
                    elif event.key == pygame.K_r:
                        print(f"R键被按下，游戏结束状态: {self.game_over}")
                        # 无论游戏是否结束，都允许按R键重新开始
                        print("重新开始游戏")
                        self.__init__()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.show_instructions:  # 只有在游戏主界面才响应鼠标点击
                    if event.button == 1:  # 鼠标左键
                        print("鼠标左键被按下 - 射击")
                        self.player.shoot()
                    elif event.button == 3:  # 鼠标右键
                        print("鼠标右键被按下")
                        # 记录鼠标右键按下时间
                        self.right_mouse_pressed = True
                        self.right_mouse_press_time = pygame.time.get_ticks()
            elif event.type == pygame.MOUSEBUTTONUP:
                if not self.show_instructions:  # 只有在游戏主界面才响应鼠标释放
                    if event.button == 3:  # 鼠标右键释放
                        print("鼠标右键被释放")
                        if self.right_mouse_pressed:
                            current_time = pygame.time.get_ticks()
                            press_duration = current_time - self.right_mouse_press_time
                            # 单击释放炸弹
                            print("单击鼠标右键 - 释放炸弹")
                            if self.player.use_bomb():
                                print("炸弹使用成功")
                                self.bombs.append(Bomb(self.player.x + self.player.width//2, self.player.y + self.player.height//2))
                            else:
                                print("炸弹数量不足")
                            self.right_mouse_pressed = False
            
            # 鼠标滚轮事件处理：切换武器
            elif event.type == pygame.MOUSEWHEEL:
                if not self.show_instructions:  # 只有在游戏主界面才响应鼠标滚轮
                    # 获取当前可用的武器列表
                    available_weapons = ["normal"]  # 单发子弹始终可用
                    if self.player.bullet_upgrade_count.get("double", 0) > 0:
                        available_weapons.append("double")
                    if self.player.bullet_upgrade_count.get("triple", 0) > 0:
                        available_weapons.append("triple")
                    if self.player.bullet_upgrade_count.get("five_way", 0) > 0:
                        available_weapons.append("five_way")
                    
                    if len(available_weapons) > 1:
                        # 获取当前武器的索引
                        current_index = available_weapons.index(self.player.bullet_type) if self.player.bullet_type in available_weapons else 0
                        
                        # 根据滚轮方向计算下一个武器的索引
                        if event.y > 0:  # 向上滚动，切换到上一个武器
                            print("鼠标滚轮向上滚动 - 切换到上一个武器")
                            next_index = (current_index - 1) % len(available_weapons)
                        else:  # 向下滚动，切换到下一个武器
                            print("鼠标滚轮向下滚动 - 切换到下一个武器")
                            next_index = (current_index + 1) % len(available_weapons)
                        
                        # 切换到新武器
                        new_weapon = available_weapons[next_index]
                        print(f"切换到武器: {new_weapon}")
                        self.player.upgrade_bullet(new_weapon)  # 不增加升级次数
    
    def update(self):
        """
        更新游戏中所有元素的状态
        """
        if self.show_instructions:
            return
        
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        # 检测鼠标左键状态，实现连发功能
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # 鼠标左键被按住
            self.player.shoot()
        
        self.player.update()
        
        for bullet in self.player.bullets:
            bullet.update()
        
        for missile in self.player.missiles[:]:
            missile.update(self.enemies, self.boss)
            # 如果导弹飞出屏幕，移除它
            if missile.y < -20:
                self.player.missiles.remove(missile)
        
        self.enemy_spawn_count += 1
        if self.enemy_spawn_count >= self.enemy_spawn_delay and not self.boss:
            self.enemy_spawn_count = 0
            max_enemies = min(15, 5 + self.level * 2)
            if len(self.enemies) < max_enemies:
                self.enemies.append(Enemy(self.level))
        
        for enemy in self.enemies[:]:
            bullets = enemy.update()
            enemy_removed = False
            
            # 将小飞机发射的子弹添加到敌人子弹列表
            if bullets:
                self.enemy_bullets.extend(bullets)
            
            if enemy.y > HEIGHT:
                self.enemies.remove(enemy)
                enemy_removed = True
                # 移除敌人飞机飞出屏幕时的扣血
            
            if not enemy_removed:
                for bullet in self.player.bullets[:]:
                    if (bullet.x > enemy.x and bullet.x < enemy.x + enemy.width and
                        bullet.y > enemy.y and bullet.y < enemy.y + enemy.height):
                        enemy.health -= bullet.damage
                        self.player.bullets.remove(bullet)
                        enemy.hit()
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            enemy_removed = True
                            self.player.score += enemy.score  # 使用飞机的得分属性
                            self.enemies_destroyed += 1
                            self.explosions.append(Explosion(enemy.x + enemy.width//2, enemy.y + enemy.height//2, 30))
                            
                            # 连续击杀逻辑
                            current_time = pygame.time.get_ticks()
                            if current_time - self.last_kill_time < self.kill_streak_timeout:
                                self.kill_streak += 1
                            else:
                                self.kill_streak = 1
                            self.last_kill_time = current_time
                            
                            # 升级系统：每1000分升一级
                            if self.player.score >= self.last_level_up_score + self.level_up_score:
                                self.last_level_up_score += self.level_up_score
                                self.level += 1
                                self.level_message = f"Level Up! Current Level: {self.level}"
                                self.level_message_timer = 120
                                self.screen_shake_timer = 30
                                self.screen_shake_intensity = 5
                            
                            if enemy.drop_item:
                                # 在有boss存在时，提高医疗包的掉落率
                                if self.boss:
                                    item_type = random.choice(["bomb", "missile", "bullet_double", "bullet_triple", "shield", "medkit", "medkit", "medkit"])
                                else:
                                    item_type = random.choice(["bomb", "missile", "bullet_double", "bullet_triple", "shield", "medkit"])
                                self.items.append(Item(enemy.x + enemy.width//2, enemy.y + enemy.height//2, item_type, self.level))
                            break
                
                if not enemy_removed:
                    for missile in self.player.missiles[:]:
                        if (missile.x > enemy.x and missile.x < enemy.x + enemy.width and
                            missile.y > enemy.y and missile.y < enemy.y + enemy.height):
                            # 处理导弹爆炸
                            explosion_x = enemy.x + enemy.width//2
                            explosion_y = enemy.y + enemy.height//2
                            
                            # 创建导弹爆炸范围视觉效果
                            missile_bomb = Bomb(explosion_x, explosion_y)
                            missile_bomb.max_radius = missile.explosion_radius
                            self.bombs.append(missile_bomb)
                            
                            # 对爆炸范围内的所有敌人造成伤害
                            for e in self.enemies[:]:
                                dx = e.x + e.width//2 - explosion_x
                                dy = e.y + e.height//2 - explosion_y
                                distance = math.sqrt(dx*dx + dy*dy)
                                if distance < missile.explosion_radius:
                                    e.health -= missile.explosion_damage
                                    e.hit()
                                    if e.health <= 0:
                                        self.enemies.remove(e)
                                        if e == enemy:
                                            enemy_removed = True
                                        self.player.score += e.score  # 使用飞机的得分属性
                                        self.enemies_destroyed += 1
                                        self.explosions.append(Explosion(e.x + e.width//2, e.y + e.height//2, 30))
                                        
                                        # 连续击杀逻辑
                                        current_time = pygame.time.get_ticks()
                                        if current_time - self.last_kill_time < self.kill_streak_timeout:
                                            self.kill_streak += 1
                                        else:
                                            self.kill_streak = 1
                                        self.last_kill_time = current_time
                                        
                                        # 升级系统：每100分升一级
                                        if self.player.score >= self.last_level_up_score + self.level_up_score:
                                            self.last_level_up_score += self.level_up_score
                                            self.level += 1
                                            self.level_message = f"Level Up! Current Level: {self.level}"
                                            self.level_message_timer = 120
                                            self.screen_shake_timer = 30
                                            self.screen_shake_intensity = 5
                                        
                                        if e.drop_item:
                                            # 在有boss存在时，提高医疗包的掉落率
                                            if self.boss:
                                                item_type = random.choice(["bomb", "bullet_double", "bullet_triple", "bullet_powerful", "shield", "medkit", "medkit"])
                                            else:
                                                # 增加子弹升级物品的掉落概率
                                                item_type = random.choice(["bomb", "bullet_double", "bullet_double", "bullet_triple", "bullet_triple", "bullet_powerful", "shield", "medkit"])
                                            self.items.append(Item(e.x + e.width//2, e.y + e.height//2, item_type, self.level))
                            
                            # 对boss造成爆炸伤害
                            if self.boss:
                                dx = self.boss.x + self.boss.width//2 - explosion_x
                                dy = self.boss.y + self.boss.height//2 - explosion_y
                                distance = math.sqrt(dx*dx + dy*dy)
                                if distance < missile.explosion_radius:
                                    self.boss.health -= missile.explosion_damage
                                    self.boss.hit()
                                    if self.boss.health <= 0:
                                        # 增加BOSS得分
                                        self.player.score += self.boss.score
                                        self.enemies_destroyed += 1
                                        self.explosions.append(Explosion(self.boss.x + self.boss.width//2, self.boss.y + self.boss.height//2, 60))
                                        # Boss死亡时掉落一堆物资
                                        boss_x = self.boss.x + self.boss.width//2
                                        boss_y = self.boss.y + self.boss.height//2
                                        # 掉落多种物资
                                        drop_items = ["bomb", "missile", "bullet_double", "bullet_triple", "shield", "medkit"]
                                        for i in range(8):  # 掉落8个物品
                                            item_type = random.choice(drop_items)
                                            self.items.append(Item(boss_x + random.randint(-30, 30), boss_y + random.randint(-30, 30), item_type, self.level))
                                        self.boss = None
                                        self.boss_defeated = True
                            
                            # 移除导弹并添加爆炸效果
                            self.player.missiles.remove(missile)
                            self.explosions.append(Explosion(explosion_x, explosion_y, missile.explosion_radius//2, is_missile=True))
                            break
            
            if not enemy_removed:
                if (self.player.x < enemy.x + enemy.width and self.player.x + self.player.width > enemy.x and
                    self.player.y < enemy.y + enemy.height and self.player.y + self.player.height > enemy.y):
                    if not self.player.shield:
                        self.player.health -= 20
                        if self.player.health <= 0:
                            self.game_over = True
                    self.enemies.remove(enemy)
                    self.explosions.append(Explosion(enemy.x + enemy.width//2, enemy.y + enemy.height//2, 30))
        
        if self.boss:
            if self.boss.update():
                bullets = self.boss.shoot()
                self.enemy_bullets.extend(bullets)
            
            for bullet in self.player.bullets[:]:
                if not self.boss:
                    break
                if (bullet.x > self.boss.x and bullet.x < self.boss.x + self.boss.width and
                    bullet.y > self.boss.y and bullet.y < self.boss.y + self.boss.height):
                    self.boss.health -= bullet.damage
                    self.player.bullets.remove(bullet)
                    self.boss.hit()
                    if self.boss.health <= 0:
                        self.explosions.append(Explosion(self.boss.x + self.boss.width//2, self.boss.y + self.boss.height//2, 60))
                        # Boss死亡时掉落一堆物资
                        boss_x = self.boss.x + self.boss.width//2
                        boss_y = self.boss.y + self.boss.height//2
                        # 掉落多种物资
                        drop_items = ["bomb", "missile", "bullet_double", "bullet_triple", "shield", "medkit"]
                        for i in range(8):  # 掉落8个物品
                            item_type = random.choice(drop_items)
                            self.items.append(Item(boss_x + random.randint(-30, 30), boss_y + random.randint(-30, 30), item_type, self.level))
                        self.boss = None
                        self.boss_defeated = True
            
            for missile in self.player.missiles[:]:
                if not self.boss:
                    break
                if (missile.x > self.boss.x and missile.x < self.boss.x + self.boss.width and
                    missile.y > self.boss.y and missile.y < self.boss.y + self.boss.height):
                    # 处理导弹爆炸
                    explosion_x = self.boss.x + self.boss.width//2
                    explosion_y = self.boss.y + self.boss.height//2
                    
                    # 创建导弹爆炸范围视觉效果
                    missile_bomb = Bomb(explosion_x, explosion_y)
                    missile_bomb.max_radius = missile.explosion_radius
                    self.bombs.append(missile_bomb)
                    
                    # 对爆炸范围内的所有敌人造成伤害
                    for e in self.enemies[:]:
                        dx = e.x + e.width//2 - explosion_x
                        dy = e.y + e.height//2 - explosion_y
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance < missile.explosion_radius:
                            e.health -= missile.explosion_damage
                            e.hit()
                            if e.health <= 0:
                                self.enemies.remove(e)
                                self.player.score += 10
                                self.enemies_destroyed += 1
                                self.explosions.append(Explosion(e.x + e.width//2, e.y + e.height//2, 30))
                                if e.drop_item:
                                    # 在有boss存在时，提高医疗包的掉落率
                                    if self.boss:
                                        item_type = random.choice(["bomb", "bullet_double", "bullet_triple", "bullet_powerful", "bullet_five_way", "shield", "medkit", "medkit"])
                                    else:
                                        # 增加子弹升级物品的掉落概率
                                        item_type = random.choice(["bomb", "bullet_double", "bullet_double", "bullet_triple", "bullet_triple", "bullet_powerful", "bullet_five_way", "shield", "medkit"])
                                    self.items.append(Item(e.x + e.width//2, e.y + e.height//2, item_type, self.level))
                    
                    # 对boss造成爆炸伤害
                    self.boss.health -= missile.damage
                    self.boss.hit()
                    if self.boss.health <= 0:
                        self.explosions.append(Explosion(self.boss.x + self.boss.width//2, self.boss.y + self.boss.height//2, 60))
                        self.boss = None
                        self.boss_defeated = True
                    
                    # 移除导弹并添加爆炸效果
                    self.player.missiles.remove(missile)
                    self.explosions.append(Explosion(explosion_x, explosion_y, missile.explosion_radius//2, is_missile=True))
        
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if (bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT):
                self.enemy_bullets.remove(bullet)
            else:
                if (bullet.x > self.player.x and bullet.x < self.player.x + self.player.width and
                    bullet.y > self.player.y and bullet.y < self.player.y + self.player.height):
                    if not self.player.shield:
                        self.player.health -= 10
                        if self.player.health <= 0:
                            self.game_over = True
                    self.enemy_bullets.remove(bullet)
        
        for item in self.items[:]:
            item.update()
            if item.y > HEIGHT:
                self.items.remove(item)
            else:
                if (item.x > self.player.x and item.x < self.player.x + self.player.width and
                    item.y > self.player.y and item.y < self.player.y + self.player.height):
                    if item.item_type == "bomb":
                        self.player.bomb_count += 1
                    elif item.item_type == "missile":
                        self.player.missile_count += 1
                    elif item.item_type == "bullet_double":
                        self.player.upgrade_bullet("double", is_pickup=True)
                    elif item.item_type == "bullet_triple":
                        self.player.upgrade_bullet("triple", is_pickup=True)
                    elif item.item_type == "bullet_powerful":
                        self.player.upgrade_bullet("powerful", is_pickup=True)
                    elif item.item_type == "bullet_five_way":
                        self.player.upgrade_bullet("five_way", is_pickup=True)
                    elif item.item_type == "shield":
                        self.player.activate_shield()
                    elif item.item_type == "medkit":
                        self.player.health += 20
                        if self.player.health > 1000:
                            self.player.health = 1000
                    self.items.remove(item)
        
        for explosion in self.explosions[:]:
            if explosion.update():
                self.explosions.remove(explosion)
        
        # 更新屏幕震动效果
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1
        
        # 更新连续击杀计时器
        current_time = pygame.time.get_ticks()
        if current_time - self.last_kill_time > self.kill_streak_timeout:
            self.kill_streak = 0
        
        for bomb in self.bombs[:]:
            if bomb.update():
                self.bombs.remove(bomb)
            else:
                # 炸弹清除范围内的敌人
                for enemy in self.enemies[:]:
                    dx = enemy.x + enemy.width//2 - bomb.x
                    dy = enemy.y + enemy.height//2 - bomb.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < bomb.radius:
                        self.enemies.remove(enemy)
                        self.player.score += enemy.score  # 使用飞机的得分属性
                        self.enemies_destroyed += 1
                        self.explosions.append(Explosion(enemy.x + enemy.width//2, enemy.y + enemy.height//2, 30))
                        
                        # 连续击杀逻辑
                        current_time = pygame.time.get_ticks()
                        if current_time - self.last_kill_time < self.kill_streak_timeout:
                            self.kill_streak += 1
                        else:
                            self.kill_streak = 1
                        self.last_kill_time = current_time
                        
                        # 升级系统：每1000分升一级
                        if self.player.score >= self.last_level_up_score + self.level_up_score:
                            self.last_level_up_score += self.level_up_score
                            self.level += 1
                            self.level_message = f"Level Up! Current Level: {self.level}"
                            self.level_message_timer = 120
                            self.screen_shake_timer = 30
                            self.screen_shake_intensity = 5
                        
                        if enemy.drop_item:
                            # 在有boss存在时，提高医疗包的掉落率
                            if self.boss:
                                item_type = random.choice(["bomb", "bullet_double", "bullet_triple", "bullet_powerful", "bullet_five_way", "shield", "medkit", "medkit"])
                            else:
                                # 增加子弹升级物品的掉落概率
                                item_type = random.choice(["bomb", "bullet_double", "bullet_double", "bullet_triple", "bullet_triple", "bullet_powerful", "bullet_five_way", "shield", "medkit"])
                            self.items.append(Item(enemy.x + enemy.width//2, enemy.y + enemy.height//2, item_type, self.level))
                
                # 炸弹对boss造成伤害
                if self.boss:
                    dx = self.boss.x + self.boss.width//2 - bomb.x
                    dy = self.boss.y + self.boss.height//2 - bomb.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < bomb.radius:
                        self.boss.health -= 5
                        self.boss.hit()
                        if self.boss.health <= 0:
                            # 增加BOSS得分
                            self.player.score += self.boss.score
                            self.enemies_destroyed += 1
                            self.explosions.append(Explosion(self.boss.x + self.boss.width//2, self.boss.y + self.boss.height//2, 60))
                            # Boss死亡时掉落一堆物资
                            boss_x = self.boss.x + self.boss.width//2
                            boss_y = self.boss.y + self.boss.height//2
                            # 掉落多种物资
                            drop_items = ["bomb", "missile", "bullet_double", "bullet_triple", "shield", "medkit"]
                            for i in range(8):  # 掉落8个物品
                                item_type = random.choice(drop_items)
                                self.items.append(Item(boss_x + random.randint(-30, 30), boss_y + random.randint(-30, 30), item_type, self.level))
                            self.boss = None
                            self.boss_defeated = True
        
        if not self.boss and not self.boss_defeated and len(self.enemies) == 0:
            # 所有敌人都被消灭，生成boss
            print("生成BOSS")
            self.boss = Boss(self.level)
        
        if self.boss_defeated:
            # 进入下一关
            self.level += 1
            self.boss_defeated = False
            self.level_message = f"Level {self.level}!"
            self.level_message_timer = 120  # 显示2秒
            print(f"Level {self.level}!")
            # 生成新的小飞机
            for _ in range(10):
                self.enemies.append(Enemy(self.level))
        
        if self.level_message_timer > 0:
            self.level_message_timer -= 1
    
    def run(self):
        """
        游戏的主循环
        """
        start_time = pygame.time.get_ticks()
        while self.running:
            # 控制游戏帧率为60帧/秒
            delta_time = self.clock.tick(60)
            
            # 计算帧率
            self.fps_counter += 1
            self.fps_timer += delta_time
            if self.fps_timer >= 1000:  # 每1000毫秒（1秒）更新一次
                self.current_fps = self.fps_counter
                self.fps_counter = 0
                self.fps_timer = 0
            
            if not self.game_over:
                # 处理游戏事件
                self.handle_events()
                # 更新游戏状态
                self.update()
            else:
                # 游戏结束后只处理退出事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
            
            # 绘制游戏界面
            self.draw()
        
        # 退出游戏
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()