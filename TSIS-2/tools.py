import pygame
from collections import deque

# функция заливки области (ведро)
def flood_fill(surface, x, y, new_color):

    target_color = surface.get_at((x, y))

    if target_color == new_color:
        return

    width, height = surface.get_size()

    queue = deque()
    queue.append((x, y))

    while queue:
        px, py = queue.popleft()

        if surface.get_at((px, py)) == target_color:
            surface.set_at((px, py), new_color)

            if px > 0:
                queue.append((px - 1, py))
            if px < width - 1:
                queue.append((px + 1, py))
            if py > 0:
                queue.append((px, py - 1))
            if py < height - 1:
                queue.append((px, py + 1))