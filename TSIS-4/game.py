import pygame
import random

WIDTH, HEIGHT = 700, 700
CELL = 20


def free_cell(snake, blocked=None):
    blocked = set(blocked or [])
    while True:
        pos = (
            random.randrange(0, WIDTH, CELL),
            random.randrange(0, HEIGHT, CELL)
        )
        if pos not in snake and pos not in blocked:
            return pos


def generate_obstacles(snake, blocked=None, count=4):
    blocked = set(blocked or [])
    obstacles = []

    head_x, head_y = snake[0]

    safe_zone = set()
    for dx in (-CELL, 0, CELL):
        for dy in (-CELL, 0, CELL):
            safe_zone.add(((head_x + dx) % WIDTH, (head_y + dy) % HEIGHT))

    tries = 0
    while len(obstacles) < count and tries < 300:
        pos = free_cell(snake, blocked | set(obstacles) | safe_zone)
        obstacles.append(pos)
        tries += 1

    return obstacles


class Food:
    def __init__(self):
        self.pos = (0, 0)
        self.value = 1
        self.spawn_time = 0
        self.rect = pygame.Rect(0, 0, CELL, CELL)

    def spawn(self, snake, blocked=None):
        self.pos = free_cell(snake, blocked)
        self.value = random.choice([1, 2, 3])
        self.spawn_time = pygame.time.get_ticks()
        self.rect.topleft = self.pos

    def draw(self, screen):
        colors = {
            1: (255, 0, 0),
            2: (255, 165, 0),
            3: (255, 255, 0)
        }
        pygame.draw.rect(screen, colors[self.value], self.rect)


class Poison:
    def __init__(self):
        self.pos = (0, 0)
        self.rect = pygame.Rect(0, 0, CELL, CELL)

    def spawn(self, snake, blocked=None):
        self.pos = free_cell(snake, blocked)
        self.rect.topleft = self.pos

    def draw(self, screen):
        pygame.draw.rect(screen, (80, 0, 120), self.rect)
        pygame.draw.rect(screen, (255, 0, 255), self.rect, 2)


class PowerUp:
    def __init__(self):
        self.type = random.choice(["speed", "slow", "shield"])
        self.pos = (0, 0)
        self.spawn_time = 0
        self.rect = pygame.Rect(0, 0, CELL, CELL)

    def spawn(self, snake, blocked=None):
        self.type = random.choice(["speed", "slow", "shield"])
        self.pos = free_cell(snake, blocked)
        self.spawn_time = pygame.time.get_ticks()
        self.rect.topleft = self.pos

    def draw(self, screen):
        x, y = self.pos
        cx = x + CELL // 2
        cy = y + CELL // 2
        color = (255, 255, 255)

        if self.type == "speed":  # triangle
            points = [(cx, y), (x, y + CELL), (x + CELL, y + CELL)]
            pygame.draw.polygon(screen, color, points)

        elif self.type == "slow":  # circle
            pygame.draw.circle(screen, color, (cx, cy), CELL // 2)

        elif self.type == "shield":  # diamond
            points = [(cx, y), (x + CELL, cy), (cx, y + CELL), (x, cy)]
            pygame.draw.polygon(screen, color, points)