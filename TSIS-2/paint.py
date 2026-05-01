import pygame
import sys
from datetime import datetime
from tools import flood_fill

pygame.init()

WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (0,0,0)

# добавили белый цвет
COLORS = [
    (255,255,255),(0,0,0),(255,0,0),(0,255,0),(0,0,255),
    (255,255,0),(255,165,0),(128,0,128),
    (0,255,255),(255,105,180)
]

color = BLACK

sizes = {1:2, 2:5, 3:10}
brush = sizes[2]

mode = "draw"
start_pos = None
drawing = False
last_pos = None

typing = False
text = ""
text_pos = None
font = pygame.font.Font("assets/font.ttf", 18)

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_d: mode = "draw"
            if event.key == pygame.K_l: mode = "line"
            if event.key == pygame.K_r: mode = "rect"
            if event.key == pygame.K_c: mode = "circle"
            if event.key == pygame.K_e: mode = "eraser"
            if event.key == pygame.K_f: mode = "fill"
            if event.key == pygame.K_t: mode = "text"
            if event.key == pygame.K_s: mode = "square"
            if event.key == pygame.K_g: mode = "triangle"
            if event.key == pygame.K_q: mode = "equilateral"
            if event.key == pygame.K_h: mode = "rhombus"

            # выбор цвета
            if pygame.K_0 <= event.key <= pygame.K_9:
                index = event.key - pygame.K_0
                if index < len(COLORS):
                    color = COLORS[index]

            if event.key == pygame.K_z: brush = sizes[1]
            if event.key == pygame.K_x: brush = sizes[2]
            if event.key == pygame.K_v: brush = sizes[3]

            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                name = datetime.now().strftime("paint_%H%M%S.png")
                pygame.image.save(canvas, name)

            # текст
            if typing:
                if event.key == pygame.K_RETURN:
                    img = font.render(text, True, color)
                    canvas.blit(img, text_pos)
                    typing = False
                    text = ""

                elif event.key == pygame.K_ESCAPE:
                    typing = False
                    text = ""

                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]

                else:
                    if event.unicode.isprintable():
                        text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = event.pos
            drawing = True
            last_pos = event.pos

            if mode == "fill":
                flood_fill(canvas, start_pos[0], start_pos[1], color)

            if mode == "text":
                typing = True
                text = ""
                text_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos

            if mode == "line":
                pygame.draw.line(canvas, color, start_pos, end_pos, brush)

            if mode == "rect":
                rect = pygame.Rect(start_pos[0], start_pos[1],
                                   end_pos[0]-start_pos[0],
                                   end_pos[1]-start_pos[1])
                pygame.draw.rect(canvas, color, rect, brush)

            if mode == "circle":
                r = int(((end_pos[0]-start_pos[0])**2 +
                         (end_pos[1]-start_pos[1])**2)**0.5)
                pygame.draw.circle(canvas, color, start_pos, r, brush)

            if mode == "square":
                size = max(abs(end_pos[0]-start_pos[0]),
                           abs(end_pos[1]-start_pos[1]))
                rect = pygame.Rect(start_pos[0], start_pos[1], size, size)
                pygame.draw.rect(canvas, color, rect, brush)

            if mode == "triangle":
                points = [start_pos, (end_pos[0], start_pos[1]), end_pos]
                pygame.draw.polygon(canvas, color, points, brush)

            if mode == "equilateral":
                x1,y1 = start_pos
                x2,y2 = end_pos
                w = x2 - x1
                h = abs(w) * 0.866
                points = [(x1,y1),(x2,y1),(x1+w//2, y1-h)]
                pygame.draw.polygon(canvas, color, points, brush)

            if mode == "rhombus":
                x1,y1 = start_pos
                x2,y2 = end_pos
                cx = (x1+x2)//2
                cy = (y1+y2)//2
                points = [(cx,y1),(x2,cy),(cx,y2),(x1,cy)]
                pygame.draw.polygon(canvas, color, points, brush)

    if drawing:
        pos = pygame.mouse.get_pos()

        if mode == "draw":
            pygame.draw.line(canvas, color, last_pos, pos, brush)
            last_pos = pos

        if mode == "eraser":
            pygame.draw.line(canvas, WHITE, last_pos, pos, brush)
            last_pos = pos

    screen.blit(canvas, (0,0))

    if mode == "line" and drawing:
        pygame.draw.line(screen, color, start_pos, pygame.mouse.get_pos(), 1)

    if typing:
        img = font.render(text, True, color)
        screen.blit(img, text_pos)

    # ---------- МЕНЮ (динамический фон) ----------
    menu = [
        f"Mode: {mode}",
        "D draw | L line | R rect | C circle",
        "S square | G triangle | Q equilateral | H rhombus",
        "F fill | T text | E eraser",
        "Z/X/V size | 0-9 colors",
        "Ctrl+S save"
    ]

    padding = 10
    line_height = 20
    width = 0

    # считаем ширину меню
    for line in menu:
        text_surface = font.render(line, True, BLACK)
        width = max(width, text_surface.get_width())

    box_width = width + padding*2
    box_height = len(menu)*line_height + padding*2

    pygame.draw.rect(screen, (220,220,220), (0,0,box_width,box_height))

    y = padding
    for line in menu:
        screen.blit(font.render(line, True, BLACK), (padding, y))
        y += line_height

    # палитра
    for i, col in enumerate(COLORS):
        pygame.draw.rect(screen, col, (10 + i*30, box_height + 10, 25, 25))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()