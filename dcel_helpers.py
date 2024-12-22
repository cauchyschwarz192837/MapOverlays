import matplotlib.pyplot as plt
from primitives import *
from matplotlib.patches import Polygon

class Edge(Segment):
    '''a class representing an edge of a DCEL, as a subclass of Segment
    for arbitrary precision.
    
    Attributes:
        h1  The first Halfedge of this edge, pointing from p1 to p2
        h2  The second Halfedge of this edge, pointing from p2 to p1

    Inherited from Segment:
        p1
        p2
        top
        bottom
        left
        right
    '''

    def __init__(self, p1, p2):
        super().__init__(p1, p2)
        self.h1, self.h2 = Halfedge.from_edge(self)

    def pointing_from(self, point):
        '''given a point that is either endpoint of this edge, return the halfedge
        pointing away from that point'''
        if self.p1 == point:
            return self.h1
        elif self.p2 == point:
            return self.h2
        
        raise ValueError('given point not a vertex of this edge')
    
    def pointing_to(self, point):
        '''given a point that is either endpoint of this edge, return the halfedge
        pointing towards that point'''
        if self.p2 == point:
            return self.h1
        if self.p1 == point:
            return self.h2
        
        raise ValueError('given point not a vertex of this edge')

class Halfedge(object):
    '''a class representing one of two Halfedges corresponding to an Edge of a DCEL
    
    Attributes:
        origin  The Vertex from which this Halfedge is directed away
        edge    The Edge corresponding to this Halfedge (and its twin)
        twin    The twin of this Halfedge
        face    The incident Face to this Halfedge
        nxt     The subsequent Halfedge on this Halfedge's incident face
        prv     The preceding Halfedge on this Halfedge's incident face
        cycle   A BoundaryCycle object containing this Halfedge, corresponding
                    to the cycle of its containing face.
    '''

    def __init__(self, origin, edge, twin=None, face=None, nxt=None, prv=None, cycle=None):
        self.origin = origin
        self.edge = edge
        self.twin = twin
        self.face = face
        self.nxt = nxt
        self.prv = prv
        self.cycle = cycle
    
    def __str__(self):
        return str(self.origin) + '->' + str(self.twin.origin)
    
    def __repr__(self):
        return str(self)
    
    def contains(self, other):
        '''returns whether this Halfedge's 'contains' the other'''
        s1,t1 = self.origin, self.twin.origin
        s2,t2 = other.origin, other.twin.origin

        return ((s1 == s2 or collinear_in_order(s1, s2, t2)) and
                (t1 == t2 or collinear_in_order(s2, t2, t1)))

    @classmethod
    def from_edge(cls, edge):
        '''return a pair of Halfedges for the given Edge'''
        h1 = cls(edge.p1, edge=edge)
        h2 = cls(edge.p2, edge=edge)
        h1.twin, h2.twin = h2, h1
        return h1, h2
    
    def get_drawable(self):
        '''a helper function that returns a segment in the image
         of this Halfedge, shifted slightly left into its incident face'''
        
        tail = self.origin
        head = self.twin.origin
        rad = math.atan2(head.y()-tail.y(), head.x()-tail.x())
        r = 0.15
        shift = math.pi/10
        t1 = Point(tail.x()+r*math.cos(rad+shift), tail.y()+r*math.sin(rad+shift))
        h1 = Point(head.x()+r*math.cos(math.pi+rad-shift), head.y()+r*math.sin(math.pi+rad-shift))
        return Segment(t1,h1)
    
    def draw(self, draw_prv=False, fig=plt):
        '''draws this this Halfedge, shifted slightly left into its incident face.
        If draw_prv is True, then purple arrowed segments are drawn from this Halfedge
        to its previous Halfedge on its incident face.'''
        s = self.get_drawable()
        t1 = s.p1
        h1 = s.p2

        m1 = Point((t1.x()+h1.x())/2, (t1.y()+h1.y())/2)
        
        if draw_prv:
            prvs = self.prv.get_drawable()
            nno = prvs.p2
            no = prvs.p1
            m2 = Point((no.x()+nno.x())/2, (no.y()+nno.y())/2)
            Segment(m1,m2).draw(color='pink', arrow=True, fig=fig)

        color = 'gray'
        if self.cycle and self.cycle.is_outer:
            color = 'blue'
        elif self.cycle and not self.cycle.is_outer:
            color = 'red'

        s.draw(color=color, arrow=True, fig=fig)

class Vertex(Point):
    '''a class representing a Vertex of a DCEL, as a subclass of Point
    for arbitrary precision.
    
    Attributes:
        hedge   An incident Halfedge to this Vertex

    Inherited from Segment:
        x
        y
        z
    '''
        
    def __init__(self, x, y, w=1, hedge=None):
        super().__init__(x,y,w)
        self.hedge = hedge

    def draw(self, fig=plt):
        Circle.by_radius(self, 0.15).draw(fig=fig)

    @classmethod
    def from_point(cls, point, edge=None):
        '''return a Vertex object from a provided Point (or Vertex)'''
        return cls(point._x, point._y, point._w, edge)

class Face(object):
    '''a class representing a face of a DCEL.
    
    Attributes:
        outer           The outer cycle of this face (None if the infinite face)
        inners          A (possibly empty) list of inner cycles of this face
        overlay_data    A dict to store the faces of overlayed DCELs
                            that contain this face     
        dcel            The DCEL object of which this face belongs
    '''
    def __init__(self, outer, inners=[], dcel=None):
        self.outer = outer        
        self.inners = inners
        self.overlay_data = {}
        self.dcel = dcel

    def draw(self, fig=plt):

        # TODO: Replace with a better coloring scheme?
        bounded = list(filter(lambda x: self.overlay_data[x] != x.infinite_face, self.overlay_data.keys()))

        if len(bounded) == 0:
            color='black'
        elif len(bounded) == 1:
            color='lightblue'
        else:
            color='purple'

        if len(self.outer.hedges) > 0:
            vs = []
            for h in self.outer.hedges:
                h.draw()
                vs.append(h.get_drawable().p2.p())
                vs.append(h.nxt.get_drawable().p1.p())

            poly = Polygon(vs, facecolor=color, alpha=0.5)
            fig.gca().add_patch(poly)

class BoundaryCycle(object):
    '''a helper class representing an inner or outer cycle of a face of a DCEL.
    
    Attributes:
        hedges      The list of halfedges of this cycle
        is_outer    A boolean value denoting whether this cycle is
                        an outer cycle of its corresponding Face
        parent      The boundary cycle visible directly left of
                        this cycle's leftmost vertex
        leftmost    The leftmost Halfedge of this cycle
    '''
    def __init__(self, hedges, leftmost, is_outer):
        self.hedges = tuple(hedges)
        self.is_outer = is_outer
        self.parent = None
        self.leftmost = leftmost
        for h in hedges:
            h.cycle = self

    def __hash__(self):
        return self.hedges.__hash__()