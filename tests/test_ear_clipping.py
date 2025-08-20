import pytest
from polygon_point_pip import trace_by_ear_clipping, is_point_in_triangle

# A helper polygon_self_intersections isn't exported; recreate a simple
# intersection check here for tests.

def segments_intersect(a1, a2, b1, b2):
    def orient(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    def on_seg(a,b,p):
        return min(a[0],b[0]) <= p[0] <= max(a[0],b[0]) and min(a[1],b[1]) <= p[1] <= max(a[1],b[1])
    o1 = orient(a1,a2,b1)
    o2 = orient(a1,a2,b2)
    o3 = orient(b1,b2,a1)
    o4 = orient(b1,b2,a2)
    if abs(o1) < 1e-9 and on_seg(a1,a2,b1):
        return True
    if abs(o2) < 1e-9 and on_seg(a1,a2,b2):
        return True
    if abs(o3) < 1e-9 and on_seg(b1,b2,a1):
        return True
    if abs(o4) < 1e-9 and on_seg(b1,b2,a2):
        return True
    return (o1>0 and o2<0 or o1<0 and o2>0) and (o3>0 and o4<0 or o3<0 and o4>0)


def poly_has_self_intersections(poly):
    n = len(poly)
    if n < 4:
        return False
    for i in range(n):
        a1 = poly[i]
        a2 = poly[(i+1)%n]
        for j in range(i+1, n):
            if j == i:
                continue
            if j == (i+1)%n or i == (j+1)%n:
                continue
            b1 = poly[j]
            b2 = poly[(j+1)%n]
            if segments_intersect(a1,a2,b1,b2):
                return True
    return False


def test_simple_convex_polygon():
    poly = [(0,0),(4,0),(4,3),(0,3)]
    trace = trace_by_ear_clipping(poly)
    # every intermediate polygon must be simple
    for step in trace:
        assert not poly_has_self_intersections(step['polygon'])


def test_simple_concave_polygon():
    poly = [(0,0),(5,0),(5,5),(3,2),(0,5)]
    trace = trace_by_ear_clipping(poly)
    for step in trace:
        assert not poly_has_self_intersections(step['polygon'])


def test_default_problematic_polygon():
    s = "334,262;210,352;302,406;640,403;602,273;464,294;420,363;490,356;427,380;362,372;304,351;324,325;335,325;393,312;406,276;388,270;372,282;337,297"
    poly = [(int(x),int(y)) for part in s.split(';') for x,y in [part.split(',')]]
    trace = trace_by_ear_clipping(poly)
    for step in trace:
        assert not poly_has_self_intersections(step['polygon'])
