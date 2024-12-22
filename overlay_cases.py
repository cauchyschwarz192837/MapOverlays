from dcel_helpers import *
from primitives import *

def vertex_vertex(dcel, v1, inc1, v2, inc2):
    '''for an improper dcel with two incident vertices v1 and v2,
     with inc1 the list of edges to v1 and inc2 the list of halfedges incident to v2,
     merge those in inc2 to be edges of vertex v1 and remove v2 from the dcel.
     update relevant halfedge records as necessary.'''

    heads = [] # halfedges pointing to v1
    tails = [] # halfedges pointing away
    
    for inc in inc1+inc2:
        heads.append(inc.pointing_to(v1)) # v1 and v2 are equal by coordinates, so v1==v2
        tails.append(inc.pointing_from(v1))

    heads = sorted( heads, key=lambda hedge: -v1.angle(hedge.origin) ) # sorts CW around v

    # for each outgoing halfedge in clockwise order, pair it with the twin in CW order
    #   and vice versa
    for i,e in enumerate(heads):
        nxt = (i+1)%len(heads)
        e.nxt = heads[nxt].twin
        e.nxt.prv = e

    dcel.verts.remove(v2)

def edge_edge(dcel, inter, a : Edge, b : Edge):
    v = Vertex.from_point(inter)

    # for simplicity, assume the four vertices of a,b are oriented
    #   counter-clockwise as a.p1, b.p1, a.p2, b.p2; swap them if not
    if cw(a.p1, b.p1, a.p2):
        a,b = b,a

    a1, a2 = Edge(a.p1, v), Edge(v, a.p2)
    b1, b2 = Edge(b.p1, v), Edge(v, b.p2)

    a1.h1.twin = a1.h2
    a1.h2.twin = a1.h1
    a2.h1.twin = a2.h2
    a2.h2.twin = a2.h1
    b1.h1.twin = b1.h2
    b1.h2.twin = b1.h1
    b2.h1.twin = b2.h2
    b2.h2.twin = b2.h1

    a1.h1.origin = a.h1.origin
    a1.h2.origin = v
    b2.h1.origin = v
    b2.h2.origin = b.h2.origin
    a2.h1.origin = v
    a2.h2.origin = a.h2.origin
    b1.h1.origin = b.h1.origin
    b1.h2.origin = v

    #----------------------------------IN-----------------------------------

    inguys = [a1.h1, b2.h2, a2.h2, b1.h1]
    inguys_prv = [a.h1.prv, b.h2.prv, a.h2.prv, b.h1.prv]
    inguys_with_prv = list(zip(inguys, inguys_prv))

    inguys_with_prv.sort(key=lambda x: -v.angle(x[0].origin))  # index the guys

    # sorts CW around v

    # the in guys
    n = len(inguys_with_prv)
    for i, (e, prev_he) in enumerate(inguys_with_prv):
        nxt = (i + 1) % n
        e.nxt = inguys_with_prv[nxt][0].twin
        e.nxt.prv = e
        e.prv = prev_he
        prev_he.nxt = e

    '''
    for i,e in enumerate(heads):
        nxt = (i+1)%len(heads)
        e.nxt = heads[nxt].twin
        e.nxt.prv = e
    '''

    #----------------------------------IN-----------------------------------
    #----------------------------------OUT----------------------------------

    outguys = [a1.h2, b2.h1, a2.h1, b1.h2]
    outguys_nxt = [a.h2.nxt, b.h1.nxt, a.h1.nxt, b.h2.nxt]
    outguys_with_nxt = list(zip(outguys, outguys_nxt))


    outguys_with_nxt.sort(key=lambda x: -v.angle(x[0].origin))
    # sorts CW around v

    # the out guys
    for e, next_he in outguys_with_nxt:
        #nxt = (i+1)%len(outguys)
        #e.prv = outguys[nxt].twin
        #e.prv.nxt = e  # loop same as just now
        e.nxt = next_he
        next_he.prv = e
    '''
    for i,e in enumerate(heads):
        nxt = (i+1)%len(heads)
        e.nxt = heads[nxt].twin
        e.nxt.prv = e
    '''

    #----------------------------------OUT----------------------------------

    v.hedge = b2.h1 # any halfedge originating from v

    if a.p1.hedge == a.h1 or a.p1.hedge == a.h2:
        a.p1.hedge = a1.h1
    if a.p2.hedge == a.h1 or a.p2.hedge == a.h2:
        a.p2.hedge = a2.h2
    if b.p1.hedge == b.h1 or b.p2.hedge == b.h2:
        b.p1.hedge = b1.h1
    if b.p2.hedge == b.h1 or b.p2.hedge == b.h2:
        b.p2.hedge = b2.h2

    a.p1

    dcel.hedges.remove(a.h1)
    dcel.hedges.remove(a.h2)
    dcel.hedges.remove(b.h1)
    dcel.hedges.remove(b.h2)
    dcel.edges.remove(a)
    dcel.edges.remove(b)

    dcel.edges.extend([a1, a2, b1, b2])
    dcel.hedges.extend(outguys)
    dcel.hedges.extend(inguys)

    '''
    print("\nJust checking hedges-----------")
    for he in dcel.hedges:
        print(he)
    print("----------------------")
    '''
    

    dcel.verts.append(v)

    return v



















def vertex_edge(dcel, v, incident_edges, e : Edge):
    '''for an improper dcel with an edge e that crosses vertex v with incident edges
    "incident_edges", modify dcel so that e is split into two edges incident to v:
        - replace e with new edges and corresponding halfedges incident to v,
        - update all relevant attributes of both new and existing vertices/halfedges, and
        - remove all the old edges and halfedges from the dcel'''

    e1, e2 = Edge(e.p1, v), Edge(v, e.p2) # split into two edges, with pair halfedges each

    # collect all halfedges pointing to the vertex v (incoming halfedges)
    incoming = []
    for inc_edge in incident_edges:
        halfedge = inc_edge.pointing_to(v)
        incoming.append(halfedge)
    incoming.append(e1.h1)
    incoming.append(e2.h2) # added the two extra guys

    # incoming sorted in clockwise order around v
    incoming.sort(key=lambda he: -v.angle(he.origin))

    n = len(incoming)
    for i in range(n):
        curr_halfedge = incoming[i]
        next_he = incoming[(i+1)%n]
        curr_halfedge.nxt = next_he.twin
        curr_halfedge.nxt.prv = curr_halfedge

    e2.h1.nxt = e.h1.nxt
    e.h1.nxt.prv = e2.h1

    e2.h2.prv = e.h2.prv
    e.h2.prv.nxt = e2.h2

    e1.h1.prv = e.h1.prv
    e.h1.prv.nxt = e1.h1

    e1.h2.nxt = e.h2.nxt
    e.h2.nxt.prv = e1.h2

    '''
    for i,e in enumerate(heads):
        nxt = (i+1)%len(heads)
        e.nxt = heads[nxt].twin
        e.nxt.prv = e
    '''

    dcel.edges.extend([e1, e2])
    dcel.hedges.extend([e1.h1, e1.h2, e2.h1, e2.h2])


    v.hedge = e1.h2  # any halfedge originating from v

    if e.p1.hedge == e.h1 or e.p1.hedge == e.h2:
        e.p1.hedge = e1.h1
    if e.p2.hedge == e.h1 or e.p2.hedge == e.h2:
        e.p2.hedge = e2.h2

    dcel.edges.remove(e)
    dcel.hedges.remove(e.h1)
    dcel.hedges.remove(e.h2)

    for vertex in [v, e.p1, e.p2]:
        if vertex.hedge not in dcel.hedges:
            vertex.hedge = next((he for he in dcel.hedges if he.origin == vertex), None)
