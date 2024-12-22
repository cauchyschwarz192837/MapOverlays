import random
from itertools import islice
from primitives import Point, Segment

def sample_integer_points(n,xoffset=0,yoffset=0,sparsity=5):
    '''returns a set of points with distinct integer coordinates,
    as a result no two points lie on the same horizontal or vertical lines.'''
    xs = list(range(sparsity*n))
    ys = list(range(sparsity*n))
    random.shuffle(xs)
    random.shuffle(ys)
    return [Point(x+xoffset*sparsity,y+yoffset*sparsity) for x,y in islice(zip(xs,ys), n)]

def generate_random_segments(n):
    '''returns a set of n segments as paired randomly-sampled endpoints'''
    pts = sample_integer_points(2*n)
    segs = [ Segment(p1,p2) for p1,p2 in zip(pts[:n],pts[n:]) ]
    return segs

def generate_tall_verticals(n):
    '''returns a set of n disjoint vertical segments that intersect the x-axis'''
    return [
        Segment(Point(i,i),Point(i,-i)) for i in range(1,n+1)
    ]

def generate_short_verticals(n):
    '''returns a set of n disjoint vertical segments with disjoint y-intervals'''
    return [
        Segment(Point(i,i),Point(2*i+1,2*i+1,2)) for i in range(n)
    ]