import pygame
import sys
from typing import List, Tuple
from polygon_point_pip import is_point_in_concave_polygon

WIDTH, HEIGHT = 1000, 700
BG_COLOR = (30, 30, 30)
POINT_COLOR = (255, 200, 50)
LINE_COLOR = (200, 200, 200)
FILL_COLOR = (50, 150, 220)


def draw_text(surface, text, pos, color=(220, 220, 220), font_size=18):
    font = pygame.font.SysFont(None, font_size)
    img = font.render(text, True, color)
    surface.blit(img, pos)


def draw_filled_polygon_by_sampling(surface, polygon: List[Tuple[int, int]], color: Tuple[int, int, int], sample_step: int = 1) -> None:
    """Fill a polygon by testing each point in its bounding box with a PIP test.

    This is intentionally simple and brute-force: it iterates over the integer
    coordinates inside the polygon's bounding box and sets pixels where the
    provided point-in-polygon test returns True.

    Args:
        surface: Pygame surface to draw onto.
        polygon: list of (x, y) vertex tuples.
        color: RGB color tuple.
        sample_step: step in pixels for sampling (1 = every pixel, >1 = faster/coarser).
    """
    if not polygon:
        return

    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    min_x = max(min(xs), 0)
    max_x = max(min(max(xs), surface.get_width() - 1), min_x)
    min_y = max(min(ys), 0)
    max_y = max(min(max(ys), surface.get_height() - 1), min_y)

    # Access pixel-setting once per surface for speed
    set_at = surface.set_at

    for y in range(min_y, max_y + 1, sample_step):
        for x in range(min_x, max_x + 1, sample_step):
            if is_point_in_concave_polygon((x, y), polygon):
                set_at((x, y), color)


def lighten_color(color: Tuple[int, int, int], factor: float = 0.5) -> Tuple[int, int, int]:
    """Return a lighter version of the given RGB color by blending toward white.

    factor in [0,1]: 0 => original color, 1 => white
    """
    r, g, b = color
    return (
        min(255, int(r + (255 - r) * factor)),
        min(255, int(g + (255 - g) * factor)),
        min(255, int(b + (255 - b) * factor)),
    )


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
        mouse_pos = pygame.mouse.get_pos()
        for poly in polygons:
            if len(poly) >= 3:
                # Use sampling-based fill when polygon area is small-to-medium.
                # For very large polygons this is slow; sample_step can be
                # increased to speed up the operation at the cost of quality.
                # If the mouse is inside this polygon, draw with a lighter fill.
                try:
                    inside = is_point_in_concave_polygon(mouse_pos, poly)
                except Exception:
                    inside = False

                fill_color = FILL_COLOR
                if inside:
                    fill_color = lighten_color(FILL_COLOR, factor=0.6)

                # Use pygame's native polygon fill for speed and simplicity.
                pygame.draw.polygon(screen, fill_color, poly)
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
