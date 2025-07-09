import math
import random

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, damage):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.damage = damage
        self.speed = 8.0
        self.active = True
        self.trail = []

        # Рассчитываем направление
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.dx = dx / dist * self.speed
            self.dy = dy / dist * self.speed
        else:
            self.dx = 0
            self.dy = 0
            self.active = False

    def update(self):
        if not self.active:
            return False

        # Добавляем текущую позицию в след
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

        # Обновляем позицию
        self.x += self.dx
        self.y += self.dy

        # Проверяем достижение цели
        dist_to_target = math.sqrt((self.x - self.target_x) ** 2 + (self.y - self.target_y) ** 2)
        return dist_to_target < 10  # Увеличили порог попадания




class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 100
        self.damage = 20
        self.cooldown = 1000
        self.last_shot = 0
        self.level = 1
        self.upgrade_cost = 50
        self.projectiles = []
        self.color = (0, 128, 255)

    def upgrade(self):
        self.level += 1
        self.damage += 20
        self.range += 20
        self.cooldown = max(300, self.cooldown - 100)
        self.upgrade_cost += 30
        return self.upgrade_cost

    def can_shoot(self, current_time):
        return current_time - self.last_shot >= self.cooldown

    def distance_to(self, enemy):
        return math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)

    def update_projectiles(self):
        hits = []
        i = 0
        while i < len(self.projectiles):
            if self.projectiles[i].update():
                # Снаряд достиг цели
                hits.append({
                    'damage': self.projectiles[i].damage,
                    'target_x': self.projectiles[i].target_x,
                    'target_y': self.projectiles[i].target_y
                })
                del self.projectiles[i]
            else:
                i += 1
        return hits


class Enemy:
    def __init__(self, wave, path):  # Добавлены аргументы wave и path
        self.path = path
        self.path_index = 0
        self.x, self.y = self.path[self.path_index]
        self.type = 'normal' #по умолчанию обычный враг
        # Случайный выбор типа врага
        enemy_type = random.choices(
            ['normal', 'fast', 'tank'],
            weights=[0.7, 0.2, 0.1],
            k=1
        )[0]

        if enemy_type == 'normal':
            self.speed = 1.0 + wave * 0.05
            self.health = 50 + wave * 8
            self.reward = 10 + wave * 2
            self.color = (255, 50, 50)  # Красный
        elif enemy_type == 'fast':
            self.speed = 2.0 + wave * 0.05
            self.health = 30 + wave * 5
            self.reward = 15 + wave * 3
            self.color = (50, 255, 50)  # Зеленый
        elif enemy_type == 'tank':
            self.speed = 0.7 + wave * 0.03
            self.health = 150 + wave * 15
            self.reward = 25 + wave * 5
            self.color = (100, 100, 255)  # Синий

        self.max_health = self.health
        self.alive = True
        self.hit_effect = 0
        self.type = enemy_type

    def move(self):
        if self.path_index >= len(self.path) - 1:
            return False

        target_x, target_y = self.path[self.path_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            self.path_index += 1
            return True

        if dist < self.speed:
            self.path_index += 1
            self.x, self.y = target_x, target_y
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

        return True

    def take_damage(self, damage):
        self.health -= damage
        self.hit_effect = 10
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return self.reward
        return 0



class Game:
    def __init__(self, screen_width, screen_height):
        self.player_name = ""
        self.wave = 0
        self.score = 0
        self.money = 200
        self.lives = 20
        self.towers = []
        self.enemies = []
        self.game_time = 0
        self.game_over = False
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.path = [
            (50, 50),
            (screen_width - 150, 50),
            (screen_width - 150, screen_height - 150),
            (50, screen_height - 150),
            (50, screen_height // 2),
            (screen_width - 50, screen_height // 2)
        ]

        self.base_x = screen_width - 50
        self.base_y = screen_height // 2

        self.wave_enemies = []  # Список врагов для текущей волны
        self.spawn_timer = 0  # Таймер для спавна
        self.spawn_delay = 500  # Задержка между спавном врагов (мс)
        self.enemies_per_spawn = 3  # Количество врагов за один спавн

    def start_wave(self):
        self.wave += 1

        # Рассчитываем количество обычных врагов
        base_enemies = 5
        wave_multiplier = 1.5
        enemy_count = int(base_enemies + self.wave * wave_multiplier)
        enemy_count = max(5, min(enemy_count, 50))

        # Создаем обычных врагов
        self.wave_enemies = []
        for _ in range(enemy_count):
            self.wave_enemies.append(Enemy(self.wave, self.path))

        # Каждую 5-ю волну добавляем босса В НАЧАЛО ВОЛНЫ
        if self.wave % 5 == 0:
            boss = Enemy(self.wave, self.path)

            # Усиливаем босса
            boss.health = 500 + self.wave * 50
            boss.max_health = boss.health
            boss.reward = 100 + self.wave * 20
            boss.speed = 0.5
            boss.color = (255, 215, 0)  # Золотой
            boss.type = 'boss'

            # Добавляем босса в начало списка (появится первым)
            self.wave_enemies.insert(0, boss)

        # Сбрасываем таймер спавна
        self.spawn_timer = 0
        self.spawn_delay = max(200, 1000 - self.wave * 20)
        self.enemies_per_spawn = min(5, 2 + self.wave // 3)

        # Бонус за волну
        wave_bonus = 50 + self.wave * 10
        self.money += wave_bonus
        self.score += 100

    def place_tower(self, x, y):
        if self.money < 50:
            return False, "Недостаточно денег! Нужно 50 монет."

        if x < 100 or x > self.screen_width - 100 or y < 100 or y > self.screen_height - 100:
            return False, "Ставьте башни в центре карты!"

        for tower in self.towers:
            if math.sqrt((x - tower.x) ** 2 + (y - tower.y) ** 2) < 40:
                return False, "Слишком близко к другой башне!"

        self.towers.append(Tower(x, y))
        self.money -= 50
        return True, f"Башня установлена в позиции ({int(x)}, {int(y)})!"

    def upgrade_tower(self, tower_index):
        if tower_index < 0 or tower_index >= len(self.towers):
            return False, "Неверный индекс башни!"

        tower = self.towers[tower_index]
        if self.money < tower.upgrade_cost:
            return False, f"Недостаточно денег! Нужно {tower.upgrade_cost} монет."

        self.money -= tower.upgrade_cost
        tower.upgrade()
        return True, f"Башня улучшена до уровня {tower.level}!"

    def update(self, delta_time):
        if self.game_over:
            return
         # Отладочная информация о боссе
        for enemy in self.enemies:
            if enemy.type == 'boss':
                 print(f"Босс на поле! Здоровье: {enemy.health}/{enemy.max_health}")

        self.game_time += delta_time

        # Спавн врагов из текущей волны
        if self.wave_enemies:
            self.spawn_timer += delta_time
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0

                # Спавним группу врагов
                spawn_count = min(self.enemies_per_spawn, len(self.wave_enemies))
                for _ in range(spawn_count):
                    if self.wave_enemies:
                        enemy = self.wave_enemies.pop(0)
                        self.enemies.append(enemy)

        # Перемещаем обновление врагов перед стрельбой башен
        enemies_to_remove = []
        for enemy in self.enemies:
            if not enemy.move():
                self.lives -= 1
                enemies_to_remove.append(enemy)
            else:
                if enemy.hit_effect > 0:
                    enemy.hit_effect -= 1

            if not enemy.alive:
                enemies_to_remove.append(enemy)

        # Удаляем врагов, которые достигли базы или умерли
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)

        # Проверяем конец игры
        if self.lives <= 0:
            self.game_over = True
            return

        # Стрельба башен (ПЕРЕМЕЩЕНА ПОСЛЕ ОБНОВЛЕНИЯ ВРАГОВ)
        for tower in self.towers:
            if tower.can_shoot(self.game_time):
                target = None
                min_distance = tower.range + 1

                for enemy in self.enemies:
                    distance = tower.distance_to(enemy)
                    if distance <= tower.range and distance < min_distance:
                        target = enemy
                        min_distance = distance

                if target:
                    tower.projectiles.append(
                        Projectile(tower.x, tower.y, target.x, target.y, tower.damage)
                    )
                    tower.last_shot = self.game_time

        # Обновляем снаряды и наносим урон
        for tower in self.towers:
            hits = tower.update_projectiles()
            for hit in hits:
                damage = hit['damage']
                hit_x = hit['target_x']
                hit_y = hit['target_y']

                # Ищем всех врагов в радиусе 50 пикселей
                hit_enemies = []
                for enemy in self.enemies:
                    dist = math.sqrt((hit_x - enemy.x) ** 2 + (hit_y - enemy.y) ** 2)
                    if dist < 50:
                        hit_enemies.append(enemy)

                # Наносим урон всем найденным врагам
                for enemy in hit_enemies:
                    if enemy.alive:
                        reward = enemy.take_damage(damage)
                        if reward > 0:
                            self.money += reward
                            self.score += reward

        # Если волна закончилась (все враги созданы и все побеждены)
        if not self.wave_enemies and not self.enemies:
            self.start_wave()