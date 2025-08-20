import pygame
import sys
import threading
from typing import List, Tuple
from polygon_point_pip import is_point_in_concave_polygon, is_point_in_polygon_ray, trace_concavity_removal

WIDTH, HEIGHT = 1000, 700
BG_COLOR = (30, 30, 30)
POINT_COLOR = (255, 200, 50)
LINE_COLOR = (200, 200, 200)
FILL_COLOR = (50, 150, 220)

# Default polygon (will be added as the first polygon on every app start)
DEFAULT_POLYGON_STR = (
    "334,262;210,352;302,406;640,403;602,273;464,294;420,363;490,356;"
    "427,380;362,372;304,351;324,325;335,325;393,312;406,276;388,270;"
    "372,282;337,297"
)


def parse_polygon_from_string(s: str):
    """Parse a semicolon-separated list of x,y pairs into a list of tuples."""
    pts = []
    for part in s.split(";"):
        part = part.strip()
        if not part:
            continue
        try:
            x_str, y_str = part.split(",")
            pts.append((int(x_str), int(y_str)))
        except Exception:
            continue
    return pts


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
    # ensure default test polygon is present first
    default_poly = parse_polygon_from_string(DEFAULT_POLYGON_STR)
    if default_poly:
        polygons.append(default_poly)
    current: List[Tuple[int, int]] = []

    running = True
    debug_trace_mode = False
    trace_steps = []
    trace_index = 0
    # runtime toggle: when True, use the research PIP for the first/default polygon only
    use_research_pip_for_default = False
    trace_thread = None
    trace_computing = False
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
                elif event.key == pygame.K_d:
                    # toggle debug trace mode for the first/default polygon
                    debug_trace_mode = not debug_trace_mode
                    trace_steps = []
                    trace_index = 0
                    # if enabling, compute trace in background to avoid freeze
                    if debug_trace_mode and polygons:
                        def _compute_trace(poly):
                            nonlocal trace_steps, trace_computing, trace_thread
                            try:
                                trace_computing = True
                                trace_steps = trace_concavity_removal(poly)
                            finally:
                                trace_computing = False
                                trace_thread = None

                        trace_thread = threading.Thread(target=_compute_trace, args=(polygons[0],), daemon=True)
                        trace_thread.start()
                elif event.key == pygame.K_LEFT:
                    if debug_trace_mode and trace_steps:
                        trace_index = max(0, trace_index - 1)
                elif event.key == pygame.K_RIGHT:
                    if debug_trace_mode and trace_steps:
                        trace_index = min(len(trace_steps) - 1, trace_index + 1)
                elif event.key == pygame.K_s:
                    try:
                        with open("polygons.txt", "w") as f:
                            for poly in polygons:
                                f.write(";".join(f"{x},{y}" for x, y in poly) + "\n")
                        print("Saved polygons to polygons.txt")
                    except Exception as e:
                        print("Failed to save:", e)
                elif event.key == pygame.K_r:
                    # toggle using the research PIP routine for testing the default polygon
                    use_research_pip_for_default = not use_research_pip_for_default

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
                # Use the ray-casting test which handles self-intersections
                # For the first polygon, optionally use the research PIP routine
                try:
                    if use_research_pip_for_default and polygons.index(poly) == 0:
                        inside = is_point_in_concave_polygon(mouse_pos, poly)
                    else:
                        inside = is_point_in_polygon_ray(mouse_pos, poly)
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
        draw_text(screen, "D: toggle PIP trace mode   LEFT/RIGHT: step trace   R: toggle research PIP for default", (12, 60))
        draw_text(screen, f"Research PIP for default: {'ON' if use_research_pip_for_default else 'OFF'}", (12, 84))
        if debug_trace_mode:
            if trace_computing:
                draw_text(screen, "Computing PIP trace...", (12, 108), color=(255, 180, 0))
            elif trace_steps:
                # draw the current traced polygon and triangle highlight
                step = trace_steps[trace_index]
                traced_poly = step.get("polygon", [])
                if len(traced_poly) >= 3:
                    pygame.draw.polygon(screen, (80, 80, 120), traced_poly)
                    pygame.draw.polygon(screen, (180, 180, 220), traced_poly, width=2)
                tri = step.get("triangle")
                if tri:
                    # highlight triangle in red-ish
                    pygame.draw.polygon(screen, (200, 80, 80), tri)
                    for v in tri:
                        pygame.draw.circle(screen, (255, 120, 120), v, 5)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
