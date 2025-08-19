import pygame
import sys
from typing import List, Tuple

WIDTH, HEIGHT = 1000, 700
BG_COLOR = (30, 30, 30)
POINT_COLOR = (255, 200, 50)
LINE_COLOR = (200, 200, 200)
FILL_COLOR = (50, 150, 220)


def draw_text(surface, text, pos, color=(220, 220, 220), font_size=18):
    font = pygame.font.SysFont(None, font_size)
    img = font.render(text, True, color)
    surface.blit(img, pos)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Polygon Drawer - left click to add, right click or Enter to close")
    clock = pygame.time.Clock()

    polygons: List[List[Tuple[int, int]]] = []
    current: List[Tuple[int, int]] = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click -> add vertex
                    current.append(event.pos)
                elif event.button == 3:  # right click -> close polygon if possible
                    if len(current) >= 3:
                        polygons.append(list(current))
                    current.clear()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if len(current) >= 3:
                        polygons.append(list(current))
                    current.clear()
                elif event.key == pygame.K_BACKSPACE:
                    if current:
                        current.pop()
                elif event.key == pygame.K_c:
                    polygons.clear()
                    current.clear()
                elif event.key == pygame.K_s:
                    try:
                        with open("polygons.txt", "w") as f:
                            for poly in polygons:
                                f.write(";".join(f"{x},{y}" for x, y in poly) + "\n")
                        print("Saved polygons to polygons.txt")
                    except Exception as e:
                        print("Failed to save:", e)

        # draw
        screen.fill(BG_COLOR)

        # draw filled polygons
        for poly in polygons:
            if len(poly) >= 3:
                pygame.draw.polygon(screen, FILL_COLOR, poly)
                pygame.draw.polygon(screen, LINE_COLOR, poly, width=2)

        # current polygon: lines and points
        if current:
            if len(current) >= 2:
                pygame.draw.lines(screen, LINE_COLOR, False, current, 2)
            for v in current:
                pygame.draw.circle(screen, POINT_COLOR, v, 4)

        # helper text
        draw_text(screen, "Left click: add vertex   Right click or Enter: close polygon   Backspace: undo   C: clear   S: save", (12, 12))
        draw_text(screen, f"Polygons: {len(polygons)}   Current vertices: {len(current)}", (12, 36))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
