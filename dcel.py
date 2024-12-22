import matplotlib.pyplot as plt
from primitives import *
from dcel_datasets import *
from overlay_cases import *
from dcel_helpers import *
    
class DCEL(object):
    '''representation of a planar subdivision as a doubly-connected edge list (DCEL),
    represented by halfedges, vertices, and face records (see dcel_helpers.py for their implementations).
    NOTE: We also explicitly include edge records, which must also be updated during the overlay method.'''

    VERIFY=False

    '''a class defining a DCEL
    
    Attributes:
        edges           The list of Edges in this DCEL
        hedges          The list of Halfedges in this DCEL
        verts           The list of Vertex objects in this DCEL
        faces           The list of Faces in this DCEL
        infinite_face   The infinite face of this DCEL
    '''

    def __init__(self, edges, hedges, verts, faces=None):
        self.edges = edges
        self.hedges = hedges
        self.verts = verts
        self.faces = faces
        self.infinite_face = None

    def draw(self, fig=plt):
        if self.faces is not None:
            for f in self.faces:
                f.draw(fig=fig)

        for v in self.verts:
            v.draw(fig=fig)
        
        for he in self.hedges:
            he.draw(fig=fig)

    def copy(self):
        '''returns a copy of this DCEL by reconstructing it from its underlying vertex coordinates and segments'''
        npoints = [ Point(v._x, v._y, v._w) for v in self.verts ]
        nsegs = [ Segment(e.p1, e.p2) for e in self.edges ]
        dcel = self.from_points_segs(npoints, nsegs)
        return dcel
    
    def verify(self, verify_edges=True, verify_hedges=True, verify_vertices=True):
        '''a helper method for debugging purposes'''
        if verify_edges:
            for e in self.edges:
                if e.h1 not in self.hedges:
                    raise ValueError(str(e.h1) + ' not in hedges')
                
                if e.h2 not in self.hedges:
                    raise ValueError(str(e.h2) + ' not in hedges')
            
        if verify_hedges:
            for h in self.hedges:
                if h.edge not in self.edges:
                    raise ValueError(str(e) + ' not in edges')
                
                if h.prv is None:
                    raise ValueError(str(h) + ' has no prev')
                elif h.prv not in self.hedges:
                    raise ValueError(str(h.prv) + ' is prev and not in hedges')
                
                if h.nxt is None:
                    raise ValueError(str(h) + ' has no next')
                elif h.nxt not in self.hedges:
                    raise ValueError(str(h.prv) + ' is next and not in hedges')

            for h in self.hedges:
                if h.nxt.prv != h:
                    raise ValueError(str(h) + ' is not next.prev')
                if h.prv.nxt != h:
                    raise ValueError(str(h) + ' is not prev.next')
        
        if verify_vertices:
            for v in self.verts:
                if v.hedge is None or v.hedge not in self.hedges:
                    raise ValueError(str(v.hedge) + ' is halfedge at vertex ' + str(v) + ' and not in hedges')
            
            for h in self.hedges:
                if h.origin not in self.verts:
                    raise ValueError(str(h.origin) + ' is vertex of halfedge ' + str(h) + ' and not in verts')
            
            for e in self.edges:
                if e.p1 not in self.verts:
                    raise ValueError(str(e.p1) + ' is vertex of edge ' + str(e) + ' and not in verts')
                if e.p2 not in self.verts:
                    raise ValueError(str(e.p2) + ' is vertex of edge ' + str(e) + ' and not in verts')
            
    def annotate_faces(self, other):
        '''identify face of "other" dcel that contains each face of this dcel.
        assumes self is obtained as overlay of "other" with one or more other dcels.
        NOTE: This takes time linear in the number of original halfedges since we do
        not implement the sweep-line to make this more efficient.'''

        for face in self.faces:
            if face == self.infinite_face:
                face.overlay_data[other] = other.infinite_face
                continue
            
            leftmost = face.outer.leftmost

            # infer original hedge that defines the leftmost
            adj = []
            for hedge in other.hedges:

                # if an original hedge supports leftmost
                if hedge.contains(leftmost):
                    face.overlay_data[other] = hedge.cycle.face
                    break

                # leftmost emanates left from the interior hedge
                if (collinear_in_order(hedge.origin, leftmost.origin, hedge.twin.origin) and
                    cw(hedge.origin, leftmost.twin.origin, hedge.twin.origin)):

                    face.overlay_data[other] = hedge.cycle.face
                    break

                # hedge has the same origin, keep it as adjacent for later checks
                if hedge.origin == leftmost.origin:
                    adj.append(hedge)

            # if succeeded at finding face above, we are done
            if other in face.overlay_data:
                continue

            # if we found adjacent hedges, pick next in CW order
            if len(adj) > 0:
                # get next in CW order from adjacent in adj
                v = leftmost.origin
                adj.append(leftmost)
                cw_hedges = sorted(adj, key=lambda z: -v.angle(z.twin.origin)) # sort in CW order
                idx = cw_hedges.index(leftmost)
                hedge = cw_hedges[(idx+1)%len(adj)]
                face.overlay_data[other] = hedge.cycle.face
                continue

            # this hedge is disjoint from any original edges, so find the rightmost visible to left
            #   of leftmost.)

            visible_edge, visible_inter = self.get_rightmost_visible_edge(leftmost, other.edges)
        
            if visible_inter is None:
                face.overlay_data[other] = other.infinite_face
            else:
                h1 = visible_edge.h1
                h2 = visible_edge.h2

                # swap h1,h2 so that h1.origin is not directly horizontal from leftmost
                if visible_inter == h1.origin:
                    h1, h2 = h2, h1

                # if clockwise, h1 lies right of the leftward ray, so leftmost is left of h1
                if cw(leftmost.origin, visible_inter, h1.origin):
                    f = h1.cycle.face
                # if ccw, h1 lies left of the leftward ray, so leftmost is right of h1
                elif ccw(leftmost.origin, visible_inter, h1.origin):
                    f = h2.cycle.face
                else:
                    ValueError('impossible case finding visible halfedge')

                face.overlay_data[other] = f
            
    def get_rightmost_visible_edge(self, leftmost, edge_set):
        '''given the leftmost halfedge of a boundary cycle and the edges of a DCEL, return
        the visible edge and the point on that edge that is closest on the left to the origin
         of the given halfedge.'''

        line = Line(leftmost.origin, leftmost.origin.translate(-1,0))
        inters = [ (e.intersect_line(line),e) for e in edge_set ]
    
        visible_edge = None
        visible_inter = None
        for inter,e in inters:

            if inter is None:
                continue

            elif (leftmost.origin == e.p1 or leftmost.origin == e.p2):
                continue
            
            elif (not e.is_horizontal()) and inter < leftmost.origin:

                if visible_edge is None:
                    visible_edge, visible_inter = e,inter
                    continue
                
                if visible_inter < inter:
                    visible_edge, visible_inter = e,inter

        return visible_edge, visible_inter
    
    def get_leftmost_by_origin(self, a, b):
        '''given two halfedges, return the one whose origin is left, picking the higher
        of the two if both origins have same x-coordinate.'''
        ao = a.origin
        bo = b.origin
        if (bo.is_left_of(ao) or (bo.equal_x(ao) and bo.is_above(ao))):
            return b
        else:
            return a

    def set_faces(self):
        '''computes all faces and assigns each halfedge its incident face.'''
        edges = self.edges
        hedges = self.hedges

        marked = set()
        infinite_face_outer = BoundaryCycle([], None, is_outer=True)
        cycles = [infinite_face_outer]
        

        # iterate through all halfedges, marking them with the cycle that contains them
        for e in hedges:
            if e in marked:
                continue

            first = e
            fedges = []

            leftmost = first
            curr = first

            # traverse the cycle and find the halfedge with leftmost origin vertex
            while (curr not in marked):

                leftmost = self.get_leftmost_by_origin(leftmost, curr)
                
                marked.add(curr)
                fedges.append(curr)
                curr = curr.nxt


            # detect outer cycles as those oriented clockwise
            is_outer = ccw(leftmost.prv.origin, leftmost.origin, leftmost.nxt.origin)

            cycle = BoundaryCycle(fedges, leftmost, is_outer)
            cycles.append(cycle)

            cycle.visible_hedge = None

            # for each inner cycle, find the rightmost visible halfedge from its leftmost vertex
            if not is_outer:

                visible_edge, visible_inter = self.get_rightmost_visible_edge(leftmost, edges)

                if visible_inter is None:
                    cycle.parent = None
                else:
                    h1 = visible_edge.h1
                    h2 = visible_edge.h2

                    # swap h1,h2 so that h1.origin is not directly horizontal from leftmost
                    if visible_inter == h1.origin:
                        h1,h2 = h2,h1
                    
                    # if clockwise, h1 lies right of the leftward ray, so leftmost is left of h1
                    if cw(leftmost.origin, visible_inter, h1.origin):
                        cycle.visible_hedge = h1
                    # if ccw, h1 lies left of the leftward ray, so leftmost is right of h1
                    elif ccw(leftmost.origin, visible_inter, h1.origin):
                        cycle.visible_hedge = h2
                    else:
                        raise ValueError('impossible case finding visible halfedge')
        

        cycle_pairs = { c : [] for c in cycles if c.is_outer }
        
        # assign each cycle the cycle containing its visible halfedge
        for cycle in cycles:
            if not cycle.is_outer:
                if cycle.visible_hedge is None:
                    cycle.parent = infinite_face_outer
                else:
                    cycle.parent = cycle.visible_hedge.cycle


        for cycle in cycles:
            if cycle.is_outer:
                continue

            # for each inner cycle, iterate through parent pointers
            #   to find its outer cycle

            curr = cycle
            while not curr.is_outer:
                curr = curr.parent
            
            cycle_pairs[curr].append(cycle)
        
        faces = []
        
        for outer in cycle_pairs.keys():
            # create Face objects with outer cycles and all inner cycles paired
            inners = cycle_pairs[outer]
            face = Face(outer, inners, dcel=self)
            faces.append(face)

            if outer == infinite_face_outer:
                self.infinite_face = face

        for face in faces:
            # for convenience, add cross-pointers from hedges and cycles to their faces
            if face.outer is not None:
                face.outer.face = face
                for e in face.outer.hedges:
                    e.face = face

            for inner in face.inners:
                inner.face = face
                for e in inner.hedges:
                    e.face = face
        
        self.faces = faces

    @classmethod
    def from_points_segs(cls, points, segs):
        
        p2v = {}
        adj = {}
        edges = []
        hedges = []
        verts = []

        # for every point, make a Vertex
        for p in points:
            v = Vertex.from_point(p)
            verts.append(v)
            p2v[p] = v
            adj[v] = []
        
        # for each segment, make an Edge and its Halfedges with corresponding Vertex as endpoints
        for seg in segs:
            v1 = p2v[seg.p1]
            v2 = p2v[seg.p2]
            
            e = Edge(v1,v2)
            edges.append(e)
            adj[v1].append(e.h1)
            adj[v2].append(e.h2)

            hedges.append(e.h1)
            hedges.append(e.h2)

        # for each outgoing halfedge from Vertex v, set their prv and nxt pointers
        for v in verts:
            cw_hedges = sorted(adj[v], key=lambda z: -v.angle(z.twin.origin)) # sort in CW order
            deg = len(cw_hedges)
            for i in range(deg):
                cur = cw_hedges[i]
                nxt = cw_hedges[(i+1)%deg]

                cur.twin.nxt = nxt
                nxt.prv = cur.twin
            
            adj[v] = cw_hedges
            v.hedge = adj[v][0]

        dcel = cls(edges, hedges, verts)
        
        dcel.set_faces()
        dcel.annotate_faces(dcel)
        dcel.verify()

        return dcel
    
def naive_overlay_intersect(dcel1, dcel2):
    inters = set()
    for e1 in dcel1.edges:
        for e2 in dcel2.edges:

            inter = e1.intersect(e2)
            if inter is not None:
                inters.add(inter)

    return inters

def overlay(dcel1, dcel2, compute_faces=False):
    '''returns a DCEL which is the overlay of dcel1 and dcel2
    NOTE: for simplicity, this implementation does not use the sweep-line technique
    and has much higher asymptotic runtime.'''
    odcel1, odcel2 = dcel1, dcel2

    dcel1 = dcel1.copy()
    dcel2 = dcel2.copy()

    # find all intersections; ideally use line-sweep for large inputs
    inters = naive_overlay_intersect(dcel1, dcel2)

    # combine copies of given dcels into a single one
    verts = dcel1.verts + dcel2.verts
    edges = dcel1.edges + dcel2.edges
    hedges = dcel1.hedges + dcel2.hedges

    ol_dcel = DCEL(edges, hedges, verts)

    for h in hedges:
        h.face = None

    # process each intersection between the given dcels
    for inter in inters:
        # get all segments containing inter
        crossing_edges = list(filter(lambda e: e.contains_interior_point(inter), ol_dcel.edges))
        incident_edges =  list(filter(lambda e: e.p1 == inter or e.p2 == inter, ol_dcel.edges))

        if ol_dcel.VERIFY:
            ol_dcel.verify()
        
        # two edges intersect
        if len(incident_edges) == 0:   
            assert(len(crossing_edges) == 2)
            a,b = crossing_edges[:2]
            edge_edge(ol_dcel, inter, a, b)

        # an edge crosses a vertex
        elif len(crossing_edges) == 1:
            e = crossing_edges[0]
            idx = verts.index(inter)
            v = verts[idx]
            vertex_edge(ol_dcel, v, incident_edges, e)

        # two vertices coincide
        else:
            assert(len(crossing_edges) == 0)
            coinciding = [ v for v in verts if v == inter ]
            assert(len(coinciding) == 2)
            v1, v2 = coinciding[:2]
            inc1, inc2 = [], []
            for e in incident_edges:
                if e.p1 == v1 or e.p2 == v1:
                    inc1.append(e)
                else:
                    inc2.append(e)

            vertex_vertex(ol_dcel, v1, inc1, v2, inc2)

    if compute_faces:
        ol_dcel.set_faces()
        ol_dcel.annotate_faces(odcel1)
        ol_dcel.annotate_faces(odcel2)

    return ol_dcel

if __name__=='__main__':

    verts = [
            Point(4,0),
            Point(6,1),
            Point(6,5),
            Point(4,5),
            Point(3,1),
        ]

    verts2 = [
        Point(3,0),
        Point(5,0),
        Point(6,1),
        Point(7,4),
        Point(6,5),
        Point(5,4),
        Point(3,7),
        Point(4,1),
        Point(3,2)
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]
    edges2 = [ Segment(verts2[i],verts2[(i+1)%len(verts2)]) for i in range(len(verts2)) ]

    poly1 = DCEL.from_points_segs(verts, edges)
    poly2 = DCEL.from_points_segs(verts2, edges2)

    #poly1.draw()
    poly2.draw()

    plt.gca().set_aspect('equal')
    plt.show()

    #ol = overlay(poly1,poly2, compute_faces=True)

    #ol.draw()
    #plt.gca().set_aspect('equal')
    #plt.show()