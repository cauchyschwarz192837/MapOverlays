from primitives import Line, cw, ccw
import matplotlib.pyplot as plt

class SweepLineComparator(object):
    '''A custom comparator for use by the provided AVL tree (in `avl.py`),
    that maintains the position of a horizontal sweep-line to order intersected segments
    by their points of intersection with the sweep-line.
    
    Attributes:
        last        The last point at which the sweep-line stopped to process
                        an event. Its y-coordinate defines the position of the
                        line attribute
        y           The y-coordinate of the sweep-line as floating-point (for efficiency)
        line        A horizontal Line object through self.y
    '''

    EPS = 0.01 # a parameter used to determine when to rely on arbitrary-precision math

    def __init__(self, last=None):
        self.last = last
        self.y = None if last is None else last.y()
        self.line = None if last is None else Line(last, last.translate(1,0)) # arbitrary shift in x-dir

    def set_last(self, last):
        '''sets the sweep-line to the y-coordinate of the provided point,
        which is assumed to be the most-recently processed event'''
        self.y = None if last is None else last.y()
        self.line = None if last is None else Line(last, last.translate(1,0)) # arbitrary shift in x-dir

    def get_exact_intersect(self, a):
        '''computes the x-coordinate of the intersection of the given segment and
        the sweep-line, using arbitrary-precision arithmetic'''
        return a.intersect_line(self.line)
    
    def get_fast_intersect(self, a):
        '''computes the x-coordinate of the intersection of the given segment and
        the sweep-line, with (potentially inaccurate) floating-point arithmetic'''
        yi = self.y
        x1,y1 = a.p1.p()
        x2,y2 = a.p2.p()

        if abs(x1-x2) < self.EPS:
            # near-vertical
            return x1
        
        dx = x2-x1
        dy = y2-y1

        m = dy/dx
        b1 = y1-m*x1
        xi = (yi-b1)/m

        return xi

    def compare(self, a, b):
        '''compares the x-coordinates of the intersections of the lines
        supporting a and b with the horizontal sweep-line y=self.y'''

        if a == b:
            return 0

        fa = self.get_fast_intersect(a)
        fb = self.get_fast_intersect(b)

        if abs(fa-fb) > self.EPS:
            return (fa > fb) - (fa < fb)

        ia = self.get_exact_intersect(a)
        ib = self.get_exact_intersect(b)

        assert(ia is not None and ib is not None)
 
        if ia == ib:
            # if they have same intersection with the current sweep-line,
            #   put a before b if a's intersection on lower sweep-lines is left of b's
            return cw(ia, a.bottom, b.bottom) - ccw(ia, a.bottom, b.bottom)
    
        return (ia > ib) - (ia < ib)
    
    def draw(self, fig=plt):
        if self.line:
            self.line.draw(fig=fig)