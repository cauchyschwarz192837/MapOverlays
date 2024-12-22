import matplotlib.pyplot as plt
from functools import total_ordering
import math
from enum import Enum

class IntersLoc(Enum):
    BEFORE = -1
    ON = 0
    AFTER = 1
        
@total_ordering
class Point(object):
    '''a class defining a 2D point using homogeneous coordinates
    
    Attributes:
        x  First component of homogenous coordinate,
            where x/w is corresponding Cartesian x-coordinate
        y  Second component of homogenous coordinate,
            where y/w is corresponding Cartesian y-coordinate
        w  Third component of homogenous coordinate
    '''
        
    def __init__(self, x, y, w=1):
        if w < 0:
            x = -x
            y = -y
            w = -w
        
        if (isinstance(x,int) and isinstance(y,int) and isinstance(w,int)):
            # simplify x,y,w to LCM
            g = math.gcd(math.gcd(x,y),w)
            if g > 0:
                x = x//g
                y = y//g
                w = w//g

        self._x = x
        self._y = y
        self._w = w

    @classmethod
    def from_rationals(cls,xn,xd,yn,yd):
        '''given x,y-coordinates in form integer numerators over integer denominators,
        x = xn/xd and y = yn/yd, return a Point object with integer homogeneous coordinates'''
        return cls(xn*yd, yn*xd, xd*yd)

    def __lt__(self, other):
        # return self.x() < other.x()
        cx = self._x*other._w - other._x*self._w
        cy = self._y*other._w - other._y*self._w

        if cx < 0:
            return True
        elif cx > 0:
            return False
        
        return cy < 0
    
    def __hash__(self):
        return self.p().__hash__()

    def __eq__(self, other):
        cx = self._x*other._w - other._x*self._w
        cy = self._y*other._w - other._y*self._w

        return cx == 0 and cy == 0
    
    def is_left_of(self, other):
        cx = self._x*other._w - other._x*self._w
        return cx < 0
    
    def is_right_of(self, other):
        cx = self._x*other._w - other._x*self._w
        return cx > 0
    
    def is_above(self, other):
        cy = self._y*other._w - other._y*self._w
        return cy > 0
    
    def is_below(self, other):
        cy = self._y*other._w - other._y*self._w
        return cy < 0
    
    def equal_x(self, other):
        cx = self._x*other._w - other._x*self._w
        return cx == 0
    
    def equal_y(self, other):
        cy = self._y*other._w - other._y*self._w
        return cy == 0

    def x(self):
        return self._x/self._w

    def y(self):
        return self._y/self._w

    def p(self):
        '''return point as Cartesian coordinates as floats'''
        return (self.x(), self.y())
    
    def draw(self,color='black', fig=plt, text=None):
        '''draw the point with the provided color. If text is not None, it is drawn near the point.'''
        if text is not None:
            plt.annotate(str(text), (self.x(),self.y()))

        fig.plot(self.x(), self.y(), color=color, marker="o")

    def draw_edge(self, other_point, color='black', fig=plt, arrow=True):
        '''draw an edge from this point to the provided point.
        if arrow=True then an arrowhead at the other point is drawn'''
        xs = [self.x(), other_point.x()]
        ys = [self.y(), other_point.y()]
        
        if arrow:
            fig.annotate("", xy=(other_point.x(), other_point.y()), xytext=(self.x(), self.y()), arrowprops=dict(facecolor=color, headwidth=10, headlength=10, width=0.1, linewidth=0))

        fig.plot(xs, ys, color=color, marker='o', linestyle="--")

    def translate(self, x=0, y=0):
        '''return this point translated right and up by given x and y values'''
        nx = self._x+x*self._w
        ny = self._y+y*self._w
        return Point(nx, ny, self._w)
    
    def rotate(self, rads, origin):
        '''return this point rotated "rads" radians around a circle containing this point, centered at "origin"'''
        ox = origin.x()
        oy = origin.y()
        x = self.x()
        y = self.y()
        nx = x + math.cos(rads)*(x-ox) - math.sin(rads)*(y-oy)
        ny = y + math.sin(rads)*(x-ox) + math.cos(rads)*(y-oy)
        return Point(nx,ny)
    
    def angle(self, other):
        '''return the angle between the horizontal line through this point and the ray from this point to "other",
        in radians between -pi and pi'''
        return math.atan2(other.y()-self.y(), other.x()-self.x())
    
    def __str__(self):
        return "({},{},{})::({},{})".format(self._x, self._y, self._w, self.x(), self.y())
    
    def __repl__(self):
        return str(self)

class Circle(object):
    '''a class for drawing circles, useful for visualization'''
    def __init__(self, a, b, c):
        self._a = a
        self._b = b
        self._c = c

    @classmethod
    def by_radius(cls, center, radius):
        a = center.translate(-1*radius, 0)
        b = center.translate(radius, 0)
        c = center.translate(0, radius)
        return cls(a,b,c)

    # https://math.stackexchange.com/a/3503338
    def draw(self,fig=plt):
        z1 = complex(self._a.x(), self._a.y())
        z2 = complex(self._b.x(), self._b.y())
        z3 = complex(self._c.x(), self._c.y())

        if (z1 == z2) or (z2 == z3) or (z3 == z1):
            raise ValueError(f"Duplicate points: {z1}, {z2}, {z3}")
                
        w = (z3 - z1)/(z2 - z1)
        
        # TODO: Should change 0 to a small tolerance for floating point comparisons
        if abs(w.imag) <= 0:
            raise ValueError(f"Points are collinear: {z1}, {z2}, {z3}")
            
        c = (z2 - z1)*(w - abs(w)**2)/(2j*w.imag) + z1  # Simplified denominator
        r = abs(z1 - c)
        
        circle1 = plt.Circle((c.real, c.imag), r, color='grey')
        fig.gca().add_patch(circle1)

class Segment(object):
    '''a class defining a line segment by a pair of distinct Points
    
    Attributes:
        p1      The first endpoint
        p2      The second endpoint
        top     Topmost point of p1,p2 (if tied, then leftmost)
        bottom  Bottommost point of p1,p2 (if tied, then rightmost)
        left    Leftmost point of p1,p2 (if tied, then topmost)
        right   Rightmost point of p1,p2 (if tied, then bottommost)
    '''

    def __str__(self):
        return "({},{})".format(str(self.p1), str(self.p2))
    
    def __repl__(self):
        return str(self)
    
    def __init__(self, p1, p2):
        assert(p1 != p2)

        self.p1 = p1
        self.p2 = p2
        
        self.left, self.right = p1, p2
        if p1.is_right_of(p2):
            self.left, self.right = p2, p1

        self.top, self.bottom = p1, p2
        if p1.is_below(p2):
            self.top, self.bottom = p2, p1

        if p1.equal_x(p2):
            self.left, self.right = self.top, self.bottom

        if p1.equal_y(p2):
            self.top, self.bottom = self.left, self.right

    def is_horizontal(self):
        return self.p1.equal_y(self.p2)
    
    def is_vertical(self):
        return self.p1.equal_x(self.p2)

    def __hash__(self):
        return self.p1.__hash__() + self.p2.__hash__()

    def draw(self,fig=plt, color='blue', arrow=False):
        xs = [self.p1.x(), self.p2.x()]
        ys = [self.p1.y(), self.p2.y()]
        if arrow:
            fig.annotate("", xy=(self.p2.x(), self.p2.y()), xytext=(self.p1.x(), self.p1.y()), arrowprops=dict(headwidth=7, headlength=7, width=0.1, linewidth=0.0, color=color))
        
        fig.plot(xs, ys, color=color, marker='', linestyle="-")

    def support(self):
        '''return a line supporting this segment'''
        return Line(self.p1, self.p2)
    
    def contains_segment(self, other):
        '''returns whether this segment contains the other segment'''
        if not collinear(self.p1, other.p1, self.p2) and collinear(self.p1, other.p2, self.p2):
            return False
        
        return (self.p1 == other.p1 or self.p2 == other.p1 or self.contains_interior_point(other.p1)) and (
                self.p1 == other.p2 or self.p2 == other.p2 or self.contains_interior_point(other.p2))

    def intersect_line(self, other):
        '''returns whether this segment intersects the given line'''
        p, (sloc, _) = self.generic_intersect(other)
        if sloc == IntersLoc.ON:
            return p
        else:
            return None
        
    def contains_point(self, other):
        '''returns whether this segment contains the given point'''
        return self.p1 == other or self.p2 == other or self.contains_interior_point(other)

    def contains_interior_point(self, point):
        '''returns whether this segment contains the given point in its interior'''
        return collinear_in_order(self.p1, point, self.p2)
        
    def generic_intersect(self, other):
        '''returns a point of intersection between the lines supporting this segment
        and the other provided segment, along with an InterLoc enum value specifying
        where the intersection point lies before, on, or after the respective segments,
        treating them directed from their endpoint p1 to their other endpoint p2.'''

        x1, y1 = self.p1._x, self.p1._y
        x2, y2 = self.p2._x, self.p2._y

        x3, y3 = other.p1._x, other.p1._y
        x4, y4 = other.p2._x, other.p2._y

        w1, w2  = self.p1._w, self.p2._w
        w3, w4  = other.p1._w, other.p2._w

        nw1 = w2*w3*w4
        nw2 = w1*w3*w4
        nw3 = w1*w2*w4
        nw4 = w1*w2*w3

        x1 *= nw1
        x2 *= nw2
        x3 *= nw3
        x4 *= nw4
        y1 *= nw1
        y2 *= nw2
        y3 *= nw3
        y4 *= nw4

        den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)

        if den == 0:
            return (None, (None, None))

        t_num = (x1-x3)*(y3-y4)-(y1-y3)*(x3-x4)
        u_num = -1*(x1-x2)*(y1-y3)+(y1-y2)*(x1-x3)
        
        if den < 0:
            den = -den
            t_num = -t_num
            u_num = -u_num

        t_inter = IntersLoc.BEFORE
        if 0 <= t_num <= den:
            t_inter = IntersLoc.ON
        elif t_num > den:
            t_inter = IntersLoc.AFTER
            
        u_inter = IntersLoc.BEFORE
        if 0 <= u_num <= den:
            u_inter = IntersLoc.ON
        elif u_num > den:
            u_inter = IntersLoc.AFTER
            
        x = x1*den + t_num*(x2-x1)
        y = y1*den + t_num*(y2-y1)
        w = den*w1*w2*w3*w4

        return Point(x,y,w), (t_inter, u_inter)

    def intersect(self, other):
        '''returns whether this segment intersects the given segment'''
        p, (sloc, oloc) = self.generic_intersect(other)
        if sloc == IntersLoc.ON and oloc == IntersLoc.ON:
            return p
        else:
            return None
    
class Line(Segment):
    '''a class representing a line, defined by two points that it contains'''
    def __init__(self, p1, p2):
        Segment.__init__(self, p1, p2)

    def draw(self,fig=plt):
        fig.axline(self.p1.p(), self.p2.p())

    def intersect(self, other):
        '''returns whether this line intersects the given line'''
        p, _ = self.generic_intersect(other)
        return p

    def intersect_segment(self, other):
        return other.intersect_line(self)

def orient(p, q, r):
    '''returns 0 if pqr are collinear, <0 if triangle pqr is CCW, >0 if triangle pqr is CW.'''
    wp = p._w
    wq = q._w
    wr = r._w
    nwp = wq*wr
    nwq = wp*wr
    nwr = wp*wq
    return (r._y*nwr - p._y*nwp)*(q._x*nwq- p._x*nwp) - (q._y*nwq - p._y*nwp)*(r._x*nwr - p._x*nwp)
    

def ccw(a,b,c):
    '''returns True if and only if the triangle a,b,c is oriented counter-clockwise'''
    return orient(a,b,c) > 0

def cw(a,b,c):
    '''returns True if and only if the triangle a,b,c is clockwise counter-clockwise'''
    return orient(a,b,c) < 0

def collinear(a,b,c):
    '''returns True if and only if two given points are equal OR all three are distinct and collinear'''
    return orient(a,b,c) == 0

def collinear_in_order(a,b,c):
    '''returns True if and only if a,b,c are distinct, collinear, and appear in that order on the line'''
    if not collinear(a,b,c):
        return False
    
    nwa = b._w*c._w
    nwb = a._w*c._w
    nwc = a._w*b._w
    
    return (a._x*nwa - b._x*nwb)*(b._x*nwb - c._x*nwc) + (a._y*nwa - b._y*nwb)*(b._y*nwb - c._y*nwc) > 0