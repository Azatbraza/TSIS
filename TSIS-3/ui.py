import pygame


# Функция для вывода текста на экран
def draw_text(screen, text, size, x, y, color=(0, 0, 0), center=True):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    rect = img.get_rect()

    # Можно рисовать по центру или от левого верхнего угла
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(img, rect)


# Главное меню
def main_menu(screen):
    while True:
        screen.fill((235, 235, 235))

        # Заголовок и кнопки
        draw_text(screen, "RACER", 64, 600, 140)
        draw_text(screen, "1 - Play", 34, 600, 300)
        draw_text(screen, "2 - Leaderboard", 34, 600, 360)
        draw_text(screen, "3 - Settings", 34, 600, 420)
        draw_text(screen, "Esc - Quit", 28, 600, 500)

        pygame.display.update()

        # Обработка нажатий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "play"
                if event.key == pygame.K_2:
                    return "leaderboard"
                if event.key == pygame.K_3:
                    return "settings"
                if event.key == pygame.K_ESCAPE:
                    return "quit"


# Экран таблицы рекордов
def leaderboard_screen(screen, scores):
    while True:
        screen.fill((255, 255, 255))

        draw_text(screen, "Leaderboard", 48, 600, 90)

        y = 180

        # Если есть записи — выводим топ 10
        if scores:
            for i, s in enumerate(scores[:10]):
                line = f"{i+1}. {s['name']}  Score: {s['score']}  Dist: {s['distance']}"
                draw_text(screen, line, 26, 600, y)
                y += 42
        else:
            draw_text(screen, "No scores yet", 28, 600, 240)

        draw_text(screen, "Esc - Back", 22, 600, 850)

        pygame.display.update()

        # Выход назад
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


# Экран настроек
def settings_screen(screen, settings):
    # Доступные цвета машины
    colors = ["yellow", "green", "white"]

    while True:
        screen.fill((240, 240, 240))

        draw_text(screen, "Settings", 48, 600, 90)

        # Текущие настройки
        draw_text(screen, f"Sound: {'ON' if settings['sound'] else 'OFF'}", 30, 600, 260)
        draw_text(screen, f"Difficulty: {settings['difficulty']}", 30, 600, 330)
        draw_text(screen, f"Car color: {settings.get('car_color', 'yellow')}", 30, 600, 400)

        # Подсказки управления
        draw_text(screen, "S - sound", 22, 600, 520)
        draw_text(screen, "D - difficulty", 22, 600, 560)
        draw_text(screen, "C - car color", 22, 600, 600)
        draw_text(screen, "Esc - back", 22, 600, 850)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings

            if event.type == pygame.KEYDOWN:

                # Включение/выключение звука
                if event.key == pygame.K_s:
                    settings["sound"] = not settings["sound"]

                # Смена сложности
                if event.key == pygame.K_d:
                    if settings["difficulty"] == "normal":
                        settings["difficulty"] = "hard"
                    else:
                        settings["difficulty"] = "normal"

                # Смена цвета машины
                if event.key == pygame.K_c:
                    current = settings.get("car_color", "yellow")
                    idx = colors.index(current) if current in colors else 0
                    settings["car_color"] = colors[(idx + 1) % len(colors)]

                # Выход назад
                if event.key == pygame.K_ESCAPE:
                    return settings