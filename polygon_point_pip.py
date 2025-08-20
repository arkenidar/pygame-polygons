
def cross_product(o, a, b):
    """Compute the 2D cross product (signed area) of vectors OA and OB.

    Returns a positive value when O->A->B is a counter-clockwise turn,
    negative for clockwise, and zero when collinear.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

# Small epsilon for floating-point tolerance in geometric comparisons.
# Change this value higher (e.g. 1e-8) if input coordinates are large and
# relative precision is needed.
EPS = 1e-9

def side(px, p1, p2):
    """Return the signed side value of point px relative to line p1->p2.

    The sign of the returned value indicates which side of the directed
    segment p1->p2 the point px lies on (positive/negative/zero).
    """
    # Reuse cross_product for clarity: (p2 - p1) x (px - p1)
    return cross_product(p1, p2, px)

def in_convex_polygon(point, polygon):
    """Half-plane method for testing a point inside a convex polygon.

    Works for polygons ordered clockwise or counter-clockwise. Returns True
    if the point lies inside or on the boundary of the convex polygon.
    """
    if len(polygon) < 3:
        return False

    # Determine polygon orientation via signed area
    area = 0.0
    for i in range(len(polygon)):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % len(polygon)]
        area += (x1 * y2 - y1 * x2)

    # Treat near-zero area as non-degenerate CCW for consistency
    if abs(area) <= EPS:
        is_ccw = True
    else:
        is_ccw = area > 0

    # For CCW polygon the point must be to the left (side >= 0) of every edge
    # For CW polygon the point must be to the right (side <= 0) of every edge
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        s = side(point, p1, p2)
        if is_ccw:
            # point must be left of edge: allow small negative tolerance
            if s < -EPS:
                return False
        else:
            # CW polygon: point must be right of edge
            if s > EPS:
                return False

    return True

def is_point_in_triangle(p, a, b, c):
    """Return True if point p is inside triangle a-b-c (including edges).

    Uses signed area tests to check that p is on the same side of all
    triangle edges.
    """
    # Signed areas (cross products) relative to p — reuse cross_product for clarity
    area1 = cross_product(p, a, b)
    area2 = cross_product(p, b, c)
    area3 = cross_product(p, c, a)

    # Check that all signed areas have the same sign (or are within EPS of zero)
    pos_ok = (area1 >= -EPS and area2 >= -EPS and area3 >= -EPS)
    neg_ok = (area1 <= EPS and area2 <= EPS and area3 <= EPS)
    return pos_ok or neg_ok

def find_first_concavity(polygon):
    """Find the index of the first concave vertex in the polygon.

    Returns the index of the first concave vertex, or -1 if the polygon is
    convex. The function determines polygon orientation via signed area and
    detects concave vertices accordingly.
    """
    n = len(polygon)
    if n < 3:
        return -1

    # Compute polygon signed area to determine orientation
    area = 0.0
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        area += (x1 * y2 - y1 * x2)

    # area > 0 -> counter-clockwise (CCW), area < 0 -> clockwise (CW)
    if abs(area) <= EPS:
        is_ccw = True
    else:
        is_ccw = area > 0

    for i in range(n):
        prev = polygon[(i - 1) % n]
        curr = polygon[i]
        next_pt = polygon[(i + 1) % n]

        # Compute cross = (curr - prev) x (next - curr) using helper
        cross = cross_product(prev, curr, next_pt)

        # For CCW polygon, a concave (right) turn has cross < 0
        # For CW polygon, a concave turn has cross > 0
        if is_ccw:
            if cross < -EPS:
                return i
        else:
            if cross > EPS:
                return i

    return -1  # no concave vertex found

def is_point_in_concave_polygon(point, polygon):
    """Concavity-triangle method for testing points in concave polygons.

    Repeatedly finds a concave vertex and tests whether the point lies
    within the concavity triangle; if so, the point is outside. Otherwise
    the concave vertex is removed and the process repeats until the polygon
    becomes convex, at which point the convex test is used.
    """
    current_poly = polygon.copy()

    while len(current_poly) >= 3:
        # Find first concave vertex
        concavity_idx = find_first_concavity(current_poly)

        if concavity_idx == -1:
            # Polygon became convex - use the half-plane test
            return in_convex_polygon(point, current_poly)

        # Build the concavity triangle
        n = len(current_poly)
        prev_idx = (concavity_idx - 1) % n
        next_idx = (concavity_idx + 1) % n

        triangle = [
            current_poly[prev_idx],
            current_poly[concavity_idx],
            current_poly[next_idx]
        ]

        # If the point is in the concavity triangle, it is outside
        if is_point_in_triangle(point, triangle[0], triangle[1], triangle[2]):
            return False

        # Remove the concave vertex and continue
        new_poly = []
        for i in range(len(current_poly)):
            if i != concavity_idx:
                new_poly.append(current_poly[i])

        current_poly = new_poly

    return False

if __name__ == "__main__":
    # Example concave polygon (vertices provided in either CW or CCW order)
    concave_polygon = [(0, 0), (5, 0), (5, 5), (3, 2), (0, 5)]

    # Test points
    test_points = [
        (2, 2),  # inside
        (4, 1),  # inside
        (3, 3),  # outside (in the concavity)
        (6, 3),  # outside
        (1, 1)   # inside
    ]

    for point in test_points:
        result = is_point_in_concave_polygon(point, concave_polygon)
        print(f"Point {point} is {'inside' if result else 'outside'} the polygon")


def is_point_in_polygon_ray(point, polygon, eps=1e-9):
    """Even-odd (ray-casting) test that works for simple and self-intersecting polygons.

    Returns True if point is inside or on boundary.
    """
    x, y = point
    n = len(polygon)
    if n < 3:
        return False

    inside = False
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        # Check if point is exactly on the segment (inclusive boundary)
        if min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps:
            # cross product zero -> on the line
            if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) <= eps:
                return True

        # Check if the horizontal ray intersects the edge
        intersects = ((y1 > y) != (y2 > y))
        if intersects:
            # compute x coordinate of intersection of edge with horizontal line at y
            xinters = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xinters > x:
                inside = not inside

    return inside


def trace_concavity_removal(polygon):
    """Return a list of states showing the concavity-removal process.

    Each state is a dict with keys:
      - 'polygon': list of vertices at this step (before removal)
      - 'concavity_idx': index of the concave vertex found, or -1 if convex
      - 'triangle': (optional) list of three vertices (prev, concave, next) tested

    The sequence stops when the polygon becomes convex (concavity_idx == -1)
    or fewer than 3 vertices remain.
    """
    current_poly = list(polygon)
    trace = []

    while len(current_poly) >= 3:
        state = {"polygon": list(current_poly)}
        concavity_idx = find_first_concavity(current_poly)
        state["concavity_idx"] = concavity_idx

        if concavity_idx == -1:
            trace.append(state)
            break

        n = len(current_poly)
        prev_idx = (concavity_idx - 1) % n
        next_idx = (concavity_idx + 1) % n
        triangle = [current_poly[prev_idx], current_poly[concavity_idx], current_poly[next_idx]]
        state["triangle"] = triangle
        trace.append(state)

        # remove the concave vertex and continue
        new_poly = [current_poly[i] for i in range(len(current_poly)) if i != concavity_idx]
        current_poly = new_poly

    return trace