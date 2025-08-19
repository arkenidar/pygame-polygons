def cross_product(o, a, b):
    """Compute the 2D cross product (signed area) of vectors OA and OB."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

EPS = 1e-9

def is_point_in_polygon(point, polygon):
    """
    Main function to test if a point is inside any polygon (convex or concave).
    Automatically selects the appropriate algorithm based on polygon convexity.
    """
    if len(polygon) < 3:
        return False
    
    # First check if polygon is convex
    if is_convex_polygon(polygon):
        return in_convex_polygon(point, polygon)
    else:
        return is_point_in_concave_polygon(point, polygon)

def is_convex_polygon(polygon):
    """Check if a polygon is convex."""
    n = len(polygon)
    if n < 3:
        return False
    
    # Determine orientation
    area = 0.0
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        area += (x1 * y2 - y1 * x2)
    
    if abs(area) <= EPS:
        is_ccw = True
    else:
        is_ccw = area > 0
    
    # Check all vertices for consistent turning
    sign = 0
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        p3 = polygon[(i + 2) % n]
        
        cross = cross_product(p1, p2, p3)
        
        if abs(cross) > EPS:
            if sign == 0:
                sign = 1 if (cross > 0) == is_ccw else -1
            else:
                current_sign = 1 if (cross > 0) == is_ccw else -1
                if current_sign != sign:
                    return False
    
    return True

def in_convex_polygon(point, polygon):
    """Half-plane test for convex polygons."""
    if len(polygon) < 3:
        return False
    
    # Determine orientation
    area = 0.0
    for i in range(len(polygon)):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % len(polygon)]
        area += (x1 * y2 - y1 * x2)
    
    if abs(area) <= EPS:
        is_ccw = True
    else:
        is_ccw = area > 0
    
    # Test point against all edges
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        s = cross_product(p1, p2, point)
        
        if is_ccw:
            if s < -EPS:
                return False
        else:
            if s > EPS:
                return False
    
    return True

def is_point_in_triangle(p, a, b, c):
    """Check if point p is inside triangle a-b-c."""
    area1 = cross_product(p, a, b)
    area2 = cross_product(p, b, c)
    area3 = cross_product(p, c, a)
    
    pos_ok = (area1 >= -EPS and area2 >= -EPS and area3 >= -EPS)
    neg_ok = (area1 <= EPS and area2 <= EPS and area3 <= EPS)
    return pos_ok or neg_ok

def find_first_concavity(polygon):
    """Find first concave vertex in polygon."""
    n = len(polygon)
    if n < 3:
        return -1
    
    # Determine orientation
    area = 0.0
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        area += (x1 * y2 - y1 * x2)
    
    if abs(area) <= EPS:
        is_ccw = True
    else:
        is_ccw = area > 0
    
    for i in range(n):
        prev = polygon[(i - 1) % n]
        curr = polygon[i]
        next_pt = polygon[(i + 1) % n]
        
        cross = cross_product(prev, curr, next_pt)
        
        if is_ccw:
            if cross < -EPS:
                return i
        else:
            if cross > EPS:
                return i
    
    return -1

def is_point_in_concave_polygon(point, polygon):
    """Concavity elimination algorithm for concave polygons."""
    current_poly = polygon.copy()
    
    while len(current_poly) >= 3:
        concavity_idx = find_first_concavity(current_poly)
        
        if concavity_idx == -1:
            return in_convex_polygon(point, current_poly)
        
        n = len(current_poly)
        prev_idx = (concavity_idx - 1) % n
        next_idx = (concavity_idx + 1) % n
        
        triangle = [
            current_poly[prev_idx],
            current_poly[concavity_idx],
            current_poly[next_idx]
        ]
        
        if is_point_in_triangle(point, triangle[0], triangle[1], triangle[2]):
            return False
        
        # Remove concave vertex
        current_poly = [pt for i, pt in enumerate(current_poly) if i != concavity_idx]
    
    return False

# Test
if __name__ == "__main__":
    # Test cases
    convex_square = [(0, 0), (5, 0), (5, 5), (0, 5)]
    concave_poly = [(0, 0), (5, 0), (5, 5), (3, 2), (0, 5)]
    
    test_points = [(2, 2), (3, 3), (6, 3), (1, 1)]
    
    print("Convex polygon test:")
    for pt in test_points:
        result = is_point_in_polygon(pt, convex_square)
        print(f"  {pt}: {'inside' if result else 'outside'}")
    
    print("\nConcave polygon test:")
    for pt in test_points:
        result = is_point_in_polygon(pt, concave_poly)
        print(f"  {pt}: {'inside' if result else 'outside'}")