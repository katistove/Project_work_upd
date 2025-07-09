import pygame
import sys
import math
from database import save_record, get_top_records
from game_logic import Game, Tower, Enemy, Projectile

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Настройки окна
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defence")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
BACKGROUND = (30, 30, 50)
LIGHT_BLUE = (100, 200, 255)

# Шрифты
font_small = pygame.font.SysFont(None, 28)
font_medium = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 48)


# Кнопка
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)

        text_surf = font_medium.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# Текстовое поле
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLUE
        self.text = text
        self.txt_surface = font_medium.render(text, True, WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = LIGHT_BLUE if self.active else BLUE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font_medium.render(self.text, True, WHITE)
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)


# Инициализация игры
game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

# Создание кнопок
tower_button = Button(20, 20, 200, 50, "Поставить башню (50$)", BLUE, (30, 100, 200))
upgrade_button = Button(20, 90, 200, 50, "Улучшить башню", GREEN, (30, 180, 30))
menu_button = Button(20, 160, 200, 50, "Главное меню", GRAY, (80, 80, 80))


# Главное меню
def main_menu():
    # Кнопки меню
    start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 60, "Начать игру", BLUE, (30, 100, 200))
    records_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 60, "Рекорды", GREEN, (30, 180, 30))
    quit_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 160, 200, 60, "Выход", RED, (180, 30, 30))

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if start_button.is_clicked(mouse_pos, event):
                return "name_input"

            if records_button.is_clicked(mouse_pos, event):
                return "records"

            if quit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()

        # Отрисовка меню
        screen.fill(BACKGROUND)

        # Заголовок
        title = font_large.render("TOWER DEFENCE", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Кнопки
        start_button.check_hover(mouse_pos)
        records_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        start_button.draw(screen)
        records_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.flip()


# Экран ввода имени
def name_input_screen():
    input_box = InputBox(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50)
    start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 50, "Начать игру", BLUE,
                          (30, 100, 200))

    name = ""

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            result = input_box.handle_event(event)
            if result:
                name = result

            if start_button.is_clicked(mouse_pos, event):
                return name or "Игрок"

        # Отрисовка
        screen.fill(BACKGROUND)

        # Заголовок
        title = font_large.render("ВВЕДИТЕ ВАШЕ ИМЯ", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Поле ввода
        input_box.draw(screen)
        start_button.check_hover(mouse_pos)
        start_button.draw(screen)

        pygame.display.flip()


# Экран рекордов
def show_records():
    records = get_top_records()

    back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Назад", GRAY, (80, 80, 80))

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if back_button.is_clicked(mouse_pos, event):
                return

        # Отрисовка
        screen.fill(BACKGROUND)

        # Заголовок
        title = font_large.render("ТАБЛИЦА РЕКОРДОВ", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Заголовки таблицы
        pygame.draw.rect(screen, (70, 70, 100), (50, 120, SCREEN_WIDTH - 100, 40))
        texts = ["Игрок", "Волна", "Очки", "Дата"]
        for i, text in enumerate(texts):
            x = 100 + i * 220
            header = font_medium.render(text, True, WHITE)
            screen.blit(header, (x, 130))

        # Список рекордов
        if not records:
            no_records = font_medium.render("Пока нет рекордов!", True, WHITE)
            screen.blit(no_records, (SCREEN_WIDTH // 2 - no_records.get_width() // 2, 200))
        else:
            for i, record in enumerate(records[:10]):
                name, wave, score, timestamp = record
                date = timestamp.split()[0]

                y = 180 + i * 40
                bg_color = (50, 50, 80) if i % 2 == 0 else (60, 60, 90)
                pygame.draw.rect(screen, bg_color, (50, y, SCREEN_WIDTH - 100, 35))

                # Данные
                screen.blit(font_small.render(name, True, WHITE), (100, y + 10))
                screen.blit(font_small.render(str(wave), True, WHITE), (320, y + 10))
                screen.blit(font_small.render(str(score), True, WHITE), (540, y + 10))
                screen.blit(font_small.render(date, True, WHITE), (760, y + 10))

        # Кнопка назад
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)

        pygame.display.flip()



def game_screen(player_name):
    global game

    # Сброс игры
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.player_name = player_name
    game.start_wave()

    selected_tower = None
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks()

    # Сообщения интерфейса
    message = ""
    message_timer = 0
    placing_mode = False

    def show_message(text, duration=2000):
        nonlocal message, message_timer
        message = text
        message_timer = duration

    while True:
        try:
            mouse_pos = pygame.mouse.get_pos()
            current_time = pygame.time.get_ticks()
            delta_time = current_time - last_time
            last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if tower_button.rect.collidepoint(mouse_pos):
                            if game.money >= 50:
                                placing_mode = True
                                show_message("Режим установки: кликните на карте")
                            else:
                                show_message("Недостаточно денег! Нужно 50 монет")
                        elif upgrade_button.rect.collidepoint(mouse_pos) and selected_tower is not None:
                            success, msg = game.upgrade_tower(selected_tower)
                            show_message(msg)
                        elif menu_button.rect.collidepoint(mouse_pos):
                            if not game.game_over:
                                save_record(game.player_name, game.wave, game.score)
                            return
                        else:
                            if placing_mode:
                                success, msg = game.place_tower(mouse_pos[0], mouse_pos[1])
                                show_message(msg)
                                placing_mode = False
                            else:
                                selected_tower = None
                                for i, tower in enumerate(game.towers):
                                    distance = math.sqrt((tower.x - mouse_pos[0]) ** 2 + (tower.y - mouse_pos[1]) ** 2)
                                    if distance < 30:
                                        selected_tower = i
                                        break

            if not game.game_over:
                game.update(delta_time)

            if message_timer > 0:
                message_timer -= delta_time
                if message_timer <= 0:
                    message = ""

            screen.fill(BACKGROUND)

            # Рисуем путь
            for i in range(len(game.path) - 1):
                pygame.draw.line(screen, GRAY, game.path[i], game.path[i + 1], 30)

            # Рисуем базу
            pygame.draw.circle(screen, GREEN, (game.base_x, game.base_y), 30)
            pygame.draw.circle(screen, BLACK, (game.base_x, game.base_y), 30, 2)

            # Рисуем врагов
            for enemy in game.enemies:
                if enemy.hit_effect > 0:
                    pygame.draw.circle(screen, (255, 100, 100), (int(enemy.x), int(enemy.y)), 18)

                pygame.draw.circle(screen, enemy.color, (int(enemy.x), int(enemy.y)), 15)
                pygame.draw.circle(screen, BLACK, (int(enemy.x), int(enemy.y)), 15, 2)

                # ПОЛОСКА ЗДОРОВЬЯ (ИСПРАВЛЕННЫЙ РАСЧЕТ)
                health_percent = max(0, enemy.health / enemy.max_health)
                health_width = int(30 * health_percent)  # Явное преобразование в int

                # Фон полоски (красный)
                pygame.draw.rect(screen, RED, (enemy.x - 15, enemy.y - 30, 30, 7))

                # Зеленая часть (текущее здоровье)
                health_color = GREEN
                if enemy.hit_effect > 0:
                    health_color = YELLOW
                pygame.draw.rect(screen, health_color, (enemy.x - 15, enemy.y - 30, health_width, 7))

                # Контур
                pygame.draw.rect(screen, BLACK, (enemy.x - 15, enemy.y - 30, 30, 7), 1)

                # Текст здоровья
                health_text = font_small.render(f"{int(enemy.health)}/{int(enemy.max_health)}", True, WHITE)
                screen.blit(health_text, (enemy.x - health_text.get_width() // 2, enemy.y - 45))

                # Особый рендеринг для босса
                if hasattr(enemy, 'type') and enemy.type == 'boss':
                    # Больший размер
                    pygame.draw.circle(screen, enemy.color, (int(enemy.x), int(enemy.y)), 25)
                    pygame.draw.circle(screen, BLACK, (int(enemy.x), int(enemy.y)), 25, 2)

                    # Коронка над боссом
                    crown_points = [
                        (enemy.x - 20, enemy.y - 30),
                        (enemy.x, enemy.y - 50),
                        (enemy.x + 20, enemy.y - 30),
                        (enemy.x + 15, enemy.y - 40),
                        (enemy.x, enemy.y - 55),
                        (enemy.x - 15, enemy.y - 40)
                    ]
                    pygame.draw.polygon(screen, (255, 215, 0), crown_points)
                    pygame.draw.polygon(screen, BLACK, crown_points, 2)

                    # Текст "BOSS"
                    boss_text = font_small.render("BOSS", True, BLACK)
                    screen.blit(boss_text, (enemy.x - boss_text.get_width() // 2, enemy.y - 70))
            # Рисуем снаряды
            for tower in game.towers:
                for projectile in tower.projectiles:
                    pygame.draw.circle(screen, YELLOW, (int(projectile.x), int(projectile.y)), 5)
                    pygame.draw.circle(screen, ORANGE, (int(projectile.x), int(projectile.y)), 3)

                    if len(projectile.trail) > 1:
                        for i in range(1, len(projectile.trail)):
                            prev_pos = projectile.trail[i - 1]
                            curr_pos = projectile.trail[i]
                            pygame.draw.line(screen, (255, 255, 0), prev_pos, curr_pos, 2)

            # Рисуем башни
            for i, tower in enumerate(game.towers):
                color = YELLOW if i == selected_tower else BLUE
                pygame.draw.circle(screen, color, (int(tower.x), int(tower.y)), 20)
                pygame.draw.circle(screen, BLACK, (int(tower.x), int(tower.y)), 20, 2)

                level_text = font_small.render(f"{tower.level}", True, WHITE)
                damage_text = font_small.render(f"{tower.damage}", True, (255, 200, 0))
                screen.blit(level_text, (tower.x - 5, tower.y - 8))
                screen.blit(damage_text, (tower.x - 10, tower.y + 10))

                if i == selected_tower:
                    pygame.draw.circle(screen, (100, 100, 100, 100), (int(tower.x), int(tower.y)), tower.range, 1)

            # Панель информации
            pygame.draw.rect(screen, (40, 40, 70), (0, 0, SCREEN_WIDTH, 220))
            pygame.draw.line(screen, WHITE, (0, 220), (SCREEN_WIDTH, 220), 2)

            stats = [
                f"Игрок: {game.player_name}",
                f"Волна: {game.wave}",
                f"Жизни: {game.lives}",
                f"Деньги: {game.money}$",
                f"Очки: {game.score}"
            ]

            for i, stat in enumerate(stats):
                text = font_medium.render(stat, True, WHITE)
                screen.blit(text, (SCREEN_WIDTH - 250, 30 + i * 35))

            # Кнопки
            tower_button.check_hover(mouse_pos)
            upgrade_button.check_hover(mouse_pos)
            menu_button.check_hover(mouse_pos)

            tower_button.draw(screen)
            upgrade_button.draw(screen)
            menu_button.draw(screen)

            if message:
                msg_surface = font_medium.render(message, True, YELLOW)
                screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, 250))

            if placing_mode:
                pygame.draw.circle(screen, (200, 200, 200, 150), mouse_pos, 20, 2)
                pygame.draw.circle(screen, (100, 100, 255, 100), mouse_pos, 100, 1)

                placing_text = font_small.render("Кликните для установки башни", True, YELLOW)
                screen.blit(placing_text, (mouse_pos[0] + 30, mouse_pos[1] - 20))

            if game.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                game_over = font_large.render("ИГРА ОКОНЧЕНА!", True, RED)
                screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

                score_text = font_medium.render(f"Ваш результат: Волна {game.wave}, Очки {game.score}", True, WHITE)
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

                save_record(game.player_name, game.wave, game.score)

                continue_text = font_small.render("Нажмите 'Главное меню' для выхода", True, YELLOW)
                screen.blit(continue_text,
                            (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

            pygame.display.flip()
            clock.tick(60)

        except Exception as e:
            print(f"Ошибка: {e}")
            pygame.quit()
            sys.exit()

# Основной игровой цикл
def main():
    current_screen = "menu"
    player_name = ""

    while True:
        if current_screen == "menu":
            current_screen = main_menu()
        elif current_screen == "name_input":
            player_name = name_input_screen()
            current_screen = "game"
        elif current_screen == "game":
            game_screen(player_name)
            current_screen = "menu"
        elif current_screen == "records":
            show_records()
            current_screen = "menu"


if __name__ == "__main__":
    main()