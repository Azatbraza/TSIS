import pygame, sys
from pygame.locals import *
import random, time

# Инициализация
pygame.init()

# Константы
FPS = 60
FramePerSec = pygame.time.Clock()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Цвета
BLACK = (0, 0, 0); WHITE = (255, 255, 255)
RED = (255, 0, 0); GREEN = (0, 255, 0)
GOLD = (255, 215, 0); SILVER = (192, 192, 192); CYAN = (0, 255, 255)

# Глобальные параметры
SPEED = 5
BASE_SPEED = 5
SCORE = 0
COIN_SCORE = 0
N_LIMIT = 10 

# Нитро переменные
nitro_active = False
nitro_start_time = 0
NITRO_DURATION = 3

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer - Final Version")

# Функция для загрузки картинок БЕЗ сплющивания
def load_smart_img(path, target_width):
    try:
        img = pygame.image.load(path).convert_alpha()
        # Вычисляем высоту на основе пропорций оригинала
        ratio = target_width / img.get_width()
        target_height = int(img.get_height() * ratio)
        return pygame.transform.smoothscale(img, (target_width, target_height))
    except:
        # Если файл не найден, создаем цветной блок
        surf = pygame.Surface((target_width, target_width * 2))
        surf.fill((random.randint(0,255), 0, 0))
        return surf

# Загрузка ресурсов
IMG_PLAYER = load_smart_img("tools/Player.png", 50)
IMG_ENEMY = load_smart_img("tools/Enemy.png", 50)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = IMG_ENEMY
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, SCREEN_WIDTH-50), -100)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > SCREEN_HEIGHT):
            SCORE += 1
            self.rect.top = -100
            self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -100)

class Coin(pygame.sprite.Sprite):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy 
        self.weight = 1
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        # Разные веса монет (Задание 1.1)
        if random.randint(1, 10) > 8:
            self.weight = 5
            color = GOLD
        else:
            self.weight = 1
            color = SILVER
        
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, color, (15, 15), 15)
        pygame.draw.circle(self.image, BLACK, (15, 15), 15, 2) # Обводка
        
        while True:
            self.rect.center = (random.randint(30, SCREEN_WIDTH - 30), -50)
            if not self.rect.colliderect(self.enemy.rect):
                break

    def move(self):
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > SCREEN_HEIGHT):
            self.spawn()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = IMG_PLAYER
        self.rect = self.image.get_rect()
        self.rect.center = (200, 520)
       
    def move(self):
        pressed = pygame.key.get_pressed()
        step = 10 if nitro_active else 5
        if self.rect.left > 0 and pressed[K_LEFT]: self.rect.move_ip(-step, 0)
        if self.rect.right < SCREEN_WIDTH and pressed[K_RIGHT]: self.rect.move_ip(step, 0)

# Объекты
E1 = Enemy(); P1 = Player(); C1 = Coin(E1)
all_sprites = pygame.sprite.Group([P1, E1, C1])
enemies = pygame.sprite.Group([E1])
coins = pygame.sprite.Group([C1])

font = pygame.font.SysFont("Verdana", 20)
last_threshold = 0

# Игровой цикл
while True:
    now = time.time()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit(); sys.exit()
        
        # Нитро (Задание NFS)
        if event.type == KEYDOWN:
            if event.key == K_n and not nitro_active:
                nitro_active = True
                nitro_start_time = now
                BASE_SPEED = SPEED
                SPEED += 6

    # Сброс Нитро через 3 секунды
    if nitro_active and (now - nitro_start_time > NITRO_DURATION):
        nitro_active = False
        SPEED = BASE_SPEED

    DISPLAYSURF.fill(WHITE)
    
    # Полоска прогресса до ускорения (Задание 1.2)
    progress = (COIN_SCORE % N_LIMIT) / N_LIMIT
    pygame.draw.rect(DISPLAYSURF, SILVER, (0, 0, SCREEN_WIDTH, 10))
    pygame.draw.rect(DISPLAYSURF, GREEN, (0, 0, SCREEN_WIDTH * progress, 10))

    # Полоска Нитро
    if nitro_active:
        n_prog = (NITRO_DURATION - (now - nitro_start_time)) / NITRO_DURATION
        pygame.draw.rect(DISPLAYSURF, CYAN, (0, 10, SCREEN_WIDTH * n_prog, 5))

    # Статистика
    DISPLAYSURF.blit(font.render(f"Coins: {COIN_SCORE}", True, BLACK), (SCREEN_WIDTH - 120, 15))
    DISPLAYSURF.blit(font.render(f"Speed: {round(SPEED, 1)}", True, BLACK), (10, 15))

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Сбор монет
    if pygame.sprite.spritecollideany(P1, coins):
        COIN_SCORE += C1.weight
        # Автоматическое ускорение (Задание 1.2)
        if COIN_SCORE // N_LIMIT > last_threshold:
            if nitro_active: BASE_SPEED += 1
            else: SPEED += 1
            last_threshold = COIN_SCORE // N_LIMIT
        C1.spawn()

    # Столкновение с врагом
    if pygame.sprite.spritecollideany(P1, enemies):
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(pygame.font.SysFont("Verdana", 60).render("GAME OVER", True, BLACK), (30, 250))
        pygame.display.update()
        time.sleep(2)
        pygame.quit(); sys.exit()
        
    pygame.display.update()
    FramePerSec.tick(FPS)