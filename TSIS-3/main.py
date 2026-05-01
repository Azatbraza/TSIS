import pygame
import sys
import random

def get_username():
    name = ""
    font = pygame.font.SysFont(None, 50)

    while True:
        screen.fill((0,0,0))

        text1 = font.render("ENTER USERNAME", True, (255,255,255))
        text2 = font.render(name if name else "Player", True, (0,255,0))
        text3 = font.render("ENTER - START", True, (200,200,200))

        screen.blit(text1, (WIDTH//2 - 200, 250))
        screen.blit(text2, (WIDTH//2 - 120, 320))
        screen.blit(text3, (WIDTH//2 - 140, 400))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return name if name else "Player"

                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    if e.unicode.isprintable():
                        name += e.unicode

from racer import Player, Enemy, Oil, PowerUp, Coin
from ui import draw_text, main_menu, leaderboard_screen, settings_screen
from persistence import load_settings, save_settings, load_scores, save_score

pygame.init()
pygame.mixer.init()

# Размер окна
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer TSIS3")
clock = pygame.time.Clock()

# Границы дороги
ROAD_LEFT = 100
ROAD_RIGHT = WIDTH - 100

# ---------- ЗАГРУЗКА КАРТИНОК ----------
def load_image(path, size, fallback_color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except:
        # Если картинки нет, рисуем запасной прямоугольник
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf

def load_background(path, size):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.smoothscale(img, size)
    except:
        # Запасной фон, если road.png не найден
        surf = pygame.Surface(size)
        surf.fill((65, 65, 65))

        pygame.draw.rect(surf, (90, 90, 90), (ROAD_LEFT, 0, WIDTH - 2 * ROAD_LEFT, HEIGHT))
        pygame.draw.rect(surf, (255, 255, 255), (ROAD_LEFT, 0, 6, HEIGHT))
        pygame.draw.rect(surf, (255, 255, 255), (ROAD_RIGHT - 6, 0, 6, HEIGHT))

        for y in range(0, HEIGHT, 60):
            pygame.draw.rect(surf, (230, 230, 230), (WIDTH // 2 - 5, y, 10, 30))

        return surf

background = load_background("assets/road.png", (WIDTH, HEIGHT))

# Выбор картинки машины по цвету
def get_player_image(color_name):
    file_map = {
        "yellow": "player.png",
        "green": "player_green.png",
        "white": "player_white.png"
    }
    filename = file_map.get(color_name, "player.png")
    return load_image(f"assets/{filename}", (220, 250), (255, 255, 255))

# Вражеская машина, масло и power-ups
enemy_img = load_image("assets/enemy.png", (220, 250), (255, 60, 60))
oil_img = load_image("assets/oil.png", (150, 100), (30, 30, 30))

power_images = {
    "nitro": load_image("assets/nitro.png", (80, 80), (0, 120, 255)),
    "shield": load_image("assets/shield.png", (80, 80), (0, 220, 0)),
    "repair": load_image("assets/repair.png", (80, 80), (255, 160, 0)),
}

# ---------- ЗВУКИ ----------
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None

crash_sound = load_sound("assets/crash.wav")
coin_sound = load_sound("assets/coin.wav")
nitro_sound = load_sound("assets/nitro.wav")
shield_sound = load_sound("assets/shield.wav")
repair_sound = load_sound("assets/repair.wav")

settings = load_settings()


# Функция выбора координаты спавна
def pick_spawn_x(occupied_xs, player_x, recent_xs=None, min_gap=240, recent_gap=300):
    left = ROAD_LEFT + 70
    right = ROAD_RIGHT - 70
    recent_xs = recent_xs or []

    for _ in range(40):
        x = random.randint(left, right)

        # Не спавним слишком близко к игроку
        if abs(x - player_x) < 220:
            continue

        # Не спавним рядом с уже существующими объектами
        if any(abs(x - ox) < min_gap for ox in occupied_xs):
            continue

        # Не спавним почти в тех же местах, что и недавно
        if any(abs(x - rx) < recent_gap for rx in recent_xs[-5:]):
            continue

        return x

    return random.randint(left, right)


def run_game():
    # Загружаем машину нужного цвета
    player_img = get_player_image(settings.get("car_color", "yellow"))
    player = Player(player_img)

    enemies = []
    oils = []
    powers = []
    coins_list = []

    # Базовая скорость зависит от сложности
    base_speed = 3 if settings["difficulty"] == "normal" else 5

    distance = 0.0
    coins_value = 0
    hp = 100

    nitro_until = 0
    power_bonus = 0

    # Здесь храним последние позиции врагов,
    # чтобы они не появлялись почти в одной точке
    recent_enemy_xs = []

    running = True
    while running:
        clock.tick(60)
        now = pygame.time.get_ticks()

        # Проверяем, действует ли нитро
        nitro_active = now < nitro_until
        player.set_nitro(nitro_active)

        # Чем дальше едем, тем быстрее движется мир
        world_speed_bonus = int(distance // 1200)
        speed_bonus = world_speed_bonus + (3 if nitro_active else 0)

        # Дистанция растёт не слишком быстро
        distance += 0.20 + (0.05 if nitro_active else 0.0)

        # Итоговый счёт
        score = int(distance) + coins_value * 4 + power_bonus

        screen.blit(background, (0, 0))

        # ---------- СОБЫТИЯ ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ---------- ИГРОК ----------
        player.update()

        # ---------- СЛОЖНОСТЬ ----------
        if settings["difficulty"] == "hard":
            enemy_chance = 0.010 + min(distance / 40000.0, 0.012)
        else:
            enemy_chance = 0.006 + min(distance / 50000.0, 0.010)

        oil_chance = 0.006 + min(distance / 70000.0, 0.004)
        coin_chance = 0.012
        power_chance = 0.003

        # По мере роста дистанции можно держать больше объектов на экране
        enemy_limit = min(3 + int(distance // 1200), 8)
        oil_limit = min(2 + int(distance // 2500), 5)
        coin_limit = 5
        power_limit = 2

        # Все текущие координаты, чтобы новые объекты не появлялись рядом
        occupied_xs = (
            [e.rect.centerx for e in enemies] +
            [o.rect.centerx for o in oils] +
            [c.rect.centerx for c in coins_list] +
            [p.rect.centerx for p in powers]
        )

        # ---------- СПАВН ----------
        if len(enemies) < enemy_limit and random.random() < enemy_chance:
            x = pick_spawn_x(occupied_xs, player.rect.centerx, recent_enemy_xs, 260, 320)
            enemies.append(Enemy(enemy_img, base_speed, x))
            recent_enemy_xs.append(x)
            recent_enemy_xs = recent_enemy_xs[-5:]

        if len(oils) < oil_limit and random.random() < oil_chance:
            x = pick_spawn_x(occupied_xs, player.rect.centerx, recent_enemy_xs, 240, 300)
            oils.append(Oil(oil_img, base_speed, x))

        if len(coins_list) < coin_limit and random.random() < coin_chance:
            x = pick_spawn_x(occupied_xs, player.rect.centerx, recent_enemy_xs, 220, 280)
            coins_list.append(Coin(base_speed, x))

        if len(powers) < power_limit and random.random() < power_chance:
            x = pick_spawn_x(occupied_xs, player.rect.centerx, recent_enemy_xs, 260, 320)
            powers.append(PowerUp(power_images, base_speed, x))

        # ---------- ОБНОВЛЕНИЕ ----------
        for en in enemies[:]:
            en.update(speed_bonus)
            if en.rect.top > HEIGHT + 250:
                enemies.remove(en)

        for o in oils[:]:
            o.update(speed_bonus)
            if o.rect.top > HEIGHT + 200:
                oils.remove(o)

        for c in coins_list[:]:
            c.update(speed_bonus)
            if c.rect.top > HEIGHT + 200:
                coins_list.remove(c)

        for p in powers[:]:
            p.update(speed_bonus)
            if p.rect.top > HEIGHT + 200:
                powers.remove(p)

        # ---------- СТОЛКНОВЕНИЕ С ВРАГАМИ ----------
        for en in enemies[:]:
            if player.hitbox.colliderect(en.hitbox):
                enemies.remove(en)

                # Щит защищает от одного удара
                if player.shield_hits > 0:
                    player.shield_hits = 0
                else:
                    hp -= 50

                if hp <= 0:
                    if settings["sound"] and crash_sound:
                        crash_sound.play()
                    return score, int(distance), coins_value

        # ---------- МАСЛО ----------
        for o in oils:
            if player.hitbox.colliderect(o.rect):
                # Машина начинает вилять 3-4 секунды
                if player.wobble_until < now:
                    player.start_wobble(random.randint(3000, 4000))

        # ---------- МОНЕТЫ ----------
        for c in coins_list[:]:
            if player.hitbox.colliderect(c.rect):
                coins_value += c.value
                power_bonus += c.value * 2

                if settings["sound"] and coin_sound:
                    coin_sound.play()

                coins_list.remove(c)

        # ---------- POWER-UPS ----------
        for p in powers[:]:
            if player.hitbox.colliderect(p.rect):
                if p.type == "shield":
                    player.shield_hits = 1
                    power_bonus += 15
                    if settings["sound"] and shield_sound:
                        shield_sound.play()

                elif p.type == "nitro":
                    nitro_until = now + 4500
                    power_bonus += 20
                    if settings["sound"] and nitro_sound:
                        nitro_sound.play()

                elif p.type == "repair":
                    hp = min(100, hp + 50)
                    power_bonus += 10
                    if settings["sound"] and repair_sound:
                        repair_sound.play()

                powers.remove(p)

        # ---------- ОТРИСОВКА ----------
        screen.blit(player.image, player.rect)

        for en in enemies:
            screen.blit(en.image, en.rect)

        for o in oils:
            screen.blit(o.image, o.rect)

        for c in coins_list:
            screen.blit(c.image, c.rect)

        for p in powers:
            screen.blit(p.image, p.rect)

        # ---------- HUD ----------
        draw_text(screen, f"Score: {score}", 28, 120, 35)
        draw_text(screen, f"Distance: {int(distance)}", 28, 400, 35)
        draw_text(screen, f"HP: {hp}", 28, 620, 35)
        draw_text(screen, f"Coins: {coins_value}", 28, 840, 35)

        pygame.draw.rect(screen, (120, 0, 0), (900, 20, 250, 22))
        pygame.draw.rect(screen, (0, 200, 0), (900, 20, 250 * hp // 100, 22))

        if player.shield_hits > 0:
            draw_text(screen, "SHIELD", 28, 1020, 60, (0, 200, 0))

        if nitro_active:
            left = max(0, (nitro_until - now) // 1000)
            draw_text(screen, f"NITRO: {left}s", 28, 1020, 100, (0, 120, 255))

        pygame.display.update()


while True:
    choice = main_menu(screen)

    if choice == "play":
        username = get_username()
        score, dist, coins_value = run_game()
        save_score(username, score, dist)


    
    elif choice == "leaderboard":
        leaderboard_screen(screen, load_scores())

    elif choice == "settings":
        settings = settings_screen(screen, settings)
        save_settings(settings)

    elif choice == "quit":
        pygame.quit()
        sys.exit()