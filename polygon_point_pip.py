
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
    def _orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def _on_segment(a, b, p):
        return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])

    def segments_intersect(a1, a2, b1, b2):
        o1 = _orient(a1, a2, b1)
        o2 = _orient(a1, a2, b2)
        o3 = _orient(b1, b2, a1)
        o4 = _orient(b1, b2, a2)

        # Check special cases: collinear and on-segment
        if abs(o1) <= EPS and _on_segment(a1, a2, b1):
            return True
        if abs(o2) <= EPS and _on_segment(a1, a2, b2):
            return True
        if abs(o3) <= EPS and _on_segment(b1, b2, a1):
            return True
        if abs(o4) <= EPS and _on_segment(b1, b2, a2):
            return True

        if (o1 > 0 and o2 < 0 or o1 < 0 and o2 > 0) and (o3 > 0 and o4 < 0 or o3 < 0 and o4 > 0):
            return True

        return False

    def polygon_self_intersections(poly):
        n = len(poly)
        if n < 4:
            return []
        intersections = []
        for i in range(n):
            a1 = poly[i]
            a2 = poly[(i + 1) % n]
            for j in range(i + 1, n):
                # skip adjacent edges
                if j == i:
                    continue
                if j == (i + 1) % n or i == (j + 1) % n:
                    continue
                b1 = poly[j]
                b2 = poly[(j + 1) % n]
                if segments_intersect(a1, a2, b1, b2):
                    intersections.append((i, j))
        return intersections

    def is_vertex_concave(idx, poly, is_ccw):
        n = len(poly)
        prev = poly[(idx - 1) % n]
        curr = poly[idx]
        nxt = poly[(idx + 1) % n]
        cross = cross_product(prev, curr, nxt)
        if is_ccw:
            return cross < -EPS
        else:
            return cross > EPS

    # restart loop with safer removal strategy
    while len(current_poly) >= 3:
        state = {"polygon": list(current_poly)}

        # compute orientation
        area = 0.0
        for i in range(len(current_poly)):
            x1, y1 = current_poly[i]
            x2, y2 = current_poly[(i + 1) % len(current_poly)]
            area += (x1 * y2 - y1 * x2)
        is_ccw = True if abs(area) <= EPS else (area > 0)

        # collect concave vertex indices
        concave_indices = [i for i in range(len(current_poly)) if is_vertex_concave(i, current_poly, is_ccw)]

        if not concave_indices:
            state["concavity_idx"] = -1
            trace.append(state)
            break

        # try removing a concave vertex that does not create self-intersections
        removed = False
        for concavity_idx in concave_indices:
            n = len(current_poly)
            prev_idx = (concavity_idx - 1) % n
            next_idx = (concavity_idx + 1) % n
            triangle = [current_poly[prev_idx], current_poly[concavity_idx], current_poly[next_idx]]
            state_try = {"polygon": list(current_poly), "concavity_idx": concavity_idx, "triangle": triangle}

            # form new polygon with this vertex removed
            new_poly = [current_poly[i] for i in range(len(current_poly)) if i != concavity_idx]
            # if removal causes no self-intersection, accept it
            if not polygon_self_intersections(new_poly):
                trace.append(state_try)
                current_poly = new_poly
                removed = True
                break
            else:
                # record that this attempted removal would self-intersect (skipped)
                state_try["skipped"] = True
                trace.append(state_try)

        if not removed:
            # cannot safely remove any concave vertex without creating self-intersection
            break

    return trace


def trace_by_ear_clipping(polygon):
    """Produce a trace of ear removals for a simple polygon.

    Each step is a dict: {'polygon': current_polygon, 'removed_idx': idx, 'triangle': [prev,curr,next]}
    The routine assumes the input polygon is simple (non-self-intersecting). If the polygon
    is not simple, the function will attempt to proceed but may return an incomplete trace.
    This is intended as an offline analysis helper to validate and visualize safe removals.
    """
    from math import fabs

    def _orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def _on_segment(a, b, p):
        return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])

    def segments_intersect(a1, a2, b1, b2):
        o1 = _orient(a1, a2, b1)
        o2 = _orient(a1, a2, b2)
        o3 = _orient(b1, b2, a1)
        o4 = _orient(b1, b2, a2)

        if abs(o1) <= EPS and _on_segment(a1, a2, b1):
            return True
        if abs(o2) <= EPS and _on_segment(a1, a2, b2):
            return True
        if abs(o3) <= EPS and _on_segment(b1, b2, a1):
            return True
        if abs(o4) <= EPS and _on_segment(b1, b2, a2):
            return True

        if (o1 > 0 and o2 < 0 or o1 < 0 and o2 > 0) and (o3 > 0 and o4 < 0 or o3 < 0 and o4 > 0):
            return True

        return False

    def polygon_has_self_intersections(poly):
        n = len(poly)
        if n < 4:
            return False
        for i in range(n):
            a1 = poly[i]
            a2 = poly[(i + 1) % n]
            for j in range(i + 1, n):
                # skip adjacent edges
                if j == i:
                    continue
                if j == (i + 1) % n or i == (j + 1) % n:
                    continue
                b1 = poly[j]
                b2 = poly[(j + 1) % n]
                if segments_intersect(a1, a2, b1, b2):
                    return True
        return False

    poly = list(polygon)
    trace = []
    # defensive: collapse exact duplicate consecutive vertices
    def _cleanup(p):
        out = []
        for v in p:
            if not out or out[-1] != v:
                out.append(v)
        # also remove last if equal to first
        if len(out) > 1 and out[0] == out[-1]:
            out.pop()
        return out

    poly = _cleanup(poly)

    # quick reject if polygon too small
    if len(poly) < 3:
        return trace

    # main loop
    max_iters = len(poly) * 2 + 10
    iters = 0
    while len(poly) > 3 and iters < max_iters:
        iters += 1
        n = len(poly)
        # compute orientation
        area = 0.0
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            area += (x1 * y2 - y1 * x2)
        is_ccw = True if abs(area) <= EPS else (area > 0)

        ear_found = False
        for i in range(n):
            prev = poly[(i - 1) % n]
            curr = poly[i]
            nxt = poly[(i + 1) % n]
            # convexity test
            cross = _orient(prev, curr, nxt)
            if is_ccw:
                if cross <= EPS:
                    continue
            else:
                if cross >= -EPS:
                    continue

            # check no other vertex inside triangle prev-curr-next
            contains_other = False
            for j in range(n):
                if j in ((i - 1) % n, i, (i + 1) % n):
                    continue
                p = poly[j]
                if is_point_in_triangle(p, prev, curr, nxt):
                    contains_other = True
                    break
            if contains_other:
                continue

            # this is an ear: record and remove curr
            state = {"polygon": list(poly), "removed_idx": i, "triangle": [prev, curr, nxt]}
            trace.append(state)
            del poly[i]
            ear_found = True
            break

        if not ear_found:
            # could be numeric/degenerate; stop early
            break

    # append final triangle state if available
    if len(poly) == 3:
        trace.append({"polygon": list(poly), "removed_idx": -1, "triangle": [poly[0], poly[1], poly[2]]})

    return trace