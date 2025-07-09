import random
import math
from database import save_record, get_top_records


class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 3
        self.damage = 15
        self.cooldown = 1
        self.last_shot = 0
        self.level = 1
        self.upgrade_cost = 50

    def upgrade(self):
        self.level += 1
        self.damage += 10
        self.range += 0.5
        self.upgrade_cost += 30
        return self.upgrade_cost

    def can_shoot(self, current_time):
        return current_time - self.last_shot >= self.cooldown

    def distance_to(self, enemy):
        return math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)


class Enemy:
    def __init__(self, wave):
        self.x = 0
        self.y = random.randint(1, 9)
        self.speed = 0.5 + wave * 0.02
        self.health = 50 + wave * 10
        self.max_health = self.health
        self.reward = 10 + wave * 2
        self.alive = True

    def move(self):
        self.x += self.speed
        return self.x < 10  # True если враг ещё на поле

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return self.reward
        return 0


class Game:
    def __init__(self):
        self.player_name = ""
        self.wave = 0
        self.score = 0
        self.money = 100
        self.lives = 10
        self.towers = []
        self.enemies = []
        self.game_time = 0
        self.game_over = False

    def start_wave(self):
        self.wave += 1
        # Создаем врагов для текущей волны
        enemy_count = 5 + self.wave * 2
        for _ in range(enemy_count):
            self.enemies.append(Enemy(self.wave))

    def place_tower(self, x, y):
        # Проверяем достаточно ли денег
        if self.money < 50:
            print("Недостаточно денег! Нужно 50 монет.")
            return False

        # Проверяем можно ли поставить башню
        if x < 1 or x > 9 or y < 1 or y > 9:
            print("Нельзя ставить башню за пределами поля!")
            return False

        for tower in self.towers:
            if tower.x == x and tower.y == y:
                print("Здесь уже есть башня!")
                return False

        # Ставим башню
        self.towers.append(Tower(x, y))
        self.money -= 50
        return True

    def upgrade_tower(self, index):
        if index < 0 or index >= len(self.towers):
            print("Неверный индекс башни!")
            return False

        tower = self.towers[index]
        if self.money < tower.upgrade_cost:
            print(f"Недостаточно денег! Нужно {tower.upgrade_cost} монет.")
            return False

        self.money -= tower.upgrade_cost
        return tower.upgrade()

    def update(self, delta_time):
        if self.game_over:
            return

        self.game_time += delta_time

        # Обновляем врагов
        for enemy in self.enemies[:]:
            if enemy.move():
                if not enemy.alive:
                    self.enemies.remove(enemy)
            else:
                # Враг дошел до конца
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True
                    print("Игра окончена! Ваша база разрушена.")
                    return

        # Стрельба башен
        for tower in self.towers:
            if tower.can_shoot(self.game_time):
                # Ищем ближайшего врага в радиусе
                target = None
                min_distance = tower.range + 1

                for enemy in self.enemies:
                    distance = tower.distance_to(enemy)
                    if distance <= tower.range and distance < min_distance:
                        target = enemy
                        min_distance = distance

                # Стреляем по врагу
                if target:
                    reward = target.take_damage(tower.damage)
                    if reward > 0:
                        self.money += reward
                        self.score += reward
                    tower.last_shot = self.game_time

        # Если волна закончилась, начинаем новую
        if not self.enemies:
            self.money += 20 + self.wave * 5
            self.score += 50
            self.start_wave()

    def draw_map(self):
        print("\n" + "=" * 30)
        print(f"Волна: {self.wave} | Жизни: {self.lives} | Деньги: {self.money} | Очки: {self.score}")
        print("=" * 30)

        # Рисуем игровое поле 10x10
        for y in range(10):
            for x in range(10):
                # Проверяем башни
                is_tower = False
                for i, tower in enumerate(self.towers):
                    if int(tower.x) == x and int(tower.y) == y:
                        print("T", end=" ")
                        is_tower = True
                        break

                if is_tower:
                    continue

                # Проверяем врагов
                is_enemy = False
                for enemy in self.enemies:
                    if int(enemy.x) == x and int(enemy.y) == y:
                        health_percent = enemy.health / enemy.max_health
                        if health_percent > 0.7:
                            print("E", end=" ")
                        elif health_percent > 0.3:
                            print("e", end=" ")
                        else:
                            print("w", end=" ")
                        is_enemy = True
                        break

                if is_enemy:
                    continue

                # Пустое пространство
                if x == 0 or x == 9 or y == 0 or y == 9:
                    print("#", end=" ")  # Граница
                else:
                    print(".", end=" ")  # Пустое поле

            print()  # Новая строка

    def show_towers(self):
        print("\nВаши башни:")
        for i, tower in enumerate(self.towers):
            print(f"{i + 1}. Позиция: ({tower.x}, {tower.y}) | Уровень: {tower.level} | "
                  f"Урон: {tower.damage} | Радиус: {tower.range:.1f} | "
                  f"Апгрейд: {tower.upgrade_cost} монет")

    def show_leaderboard(self):
        records = get_top_records()
        if not records:
            print("\nЕщё нет рекордов!")
            return

        print("\n🏆 ТОП-10 ИГРОКОВ 🏆")
        print("=" * 50)
        print(f"{'Имя':<15} {'Волна':<6} {'Очки':<10} {'Дата':<20}")
        print("-" * 50)
        for record in records:
            name, wave, score, timestamp = record
            date = timestamp.split()[0]  # Берем только дату
            print(f"{name:<15} {wave:<6} {score:<10} {date:<20}")


def main():
    game = Game()
    game.player_name = input("Введите ваше имя: ").strip() or "Игрок"

    print("\nДобро пожаловать в Tower Defence!")
    print("Цель: защитить правую сторону карты от врагов")
    print("Управление:")
    print("1. Поставить башню")
    print("2. Улучшить башню")
    print("3. Показать таблицу лидеров")
    print("4. Завершить игру")

    # Начинаем первую волну
    game.start_wave()

    # Игровой цикл
    while not game.game_over:
        game.draw_map()
        game.update(1)  # Обновляем состояние игры

        print("\nДействия:")
        print("1. Поставить башню (50 монет)")
        print("2. Улучшить башню")
        print("3. Показать таблицу лидеров")
        print("4. Пропустить ход")

        choice = input("Выберите действие: ")

        if choice == "1":
            try:
                x = int(input("Введите X координату (1-8): "))
                y = int(input("Введите Y координату (1-8): "))
                if game.place_tower(x, y):
                    print(f"Башня установлена в позиции ({x}, {y})!")
            except ValueError:
                print("Ошибка! Введите числа.")

        elif choice == "2":
            game.show_towers()
            if game.towers:
                try:
                    index = int(input("Введите номер башни для улучшения: ")) - 1
                    cost = game.upgrade_tower(index)
                    if cost:
                        print(f"Башня улучшена до уровня {game.towers[index].level}!")
                except ValueError:
                    print("Ошибка! Введите число.")
            else:
                print("У вас пока нет башен!")

        elif choice == "3":
            game.show_leaderboard()

        elif choice == "4":
            continue

        else:
            print("Неверный выбор!")

    # Сохраняем результат
    if save_record(game.player_name, game.wave, game.score):
        print("\nВаш рекорд сохранён!")
    else:
        print("\nНе удалось сохранить рекорд.")

    game.show_leaderboard()
    print("\nСпасибо за игру!")


if __name__ == "__main__":
    main()