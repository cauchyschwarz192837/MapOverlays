from primitives import *
from dcel import DCEL

def edge_edge_test():
    '''a pair of DCELs with two edge-edge intersections'''
    verts = [
        Point(4,0),
        Point(6,1),
        Point(4,4),
        Point(3,1),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly1 = DCEL.from_points_segs(verts,edges)

    verts = [
        Point(2,2),
        Point(8,3),
        Point(6,6),
        Point(4,5),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly2 = DCEL.from_points_segs(verts,edges)

    return poly1, poly2 

def vert_vert_test():
    '''a pair of dcels with coinciding vertices'''
    verts = [
        Point(0,0),
        Point(4,0),
        Point(2,4),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly1 = DCEL.from_points_segs(verts,edges)

    verts = [
        Point(2,4),
        Point(0,6),
        Point(4,6),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly2 = DCEL.from_points_segs(verts,edges)

    return poly1, poly2   

def vert_vert_test2():
    '''a pair of dcels with coinciding vertices and other intersections'''
    verts = [
        Point(0,0),
        Point(4,0),
        Point(2,4),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly1 = DCEL.from_points_segs(verts,edges)

    verts = [
        Point(2,4),
        Point(0,3),
        Point(4,1,2),
        Point(4,2),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]
    edges.append(Segment(verts[1], verts[3]))

    poly2 = DCEL.from_points_segs(verts,edges)

    return poly1, poly2 

def vert_edge_test():
    '''a pair of dcels with an edge crossing a vertex of the other'''
    verts = [
        Point(1,0),
        Point(1,2),
        Point(0,1),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly1 = DCEL.from_points_segs(verts,edges)

    verts = [
        Point(2,1),
        Point(0,3),
        Point(2,4),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly2 = DCEL.from_points_segs(verts,edges)

    return poly1, poly2   

def vert_edge_test2():
    '''a pair of dcels with vertex-vertex and vertex-edge intersections'''
    verts = [
        Point(0,0),
        Point(4,0),
        Point(2,4),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly1 = DCEL.from_points_segs(verts,edges)

    verts = [
        Point(2,1),
        Point(2,6),
        Point(0,3),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    poly2 = DCEL.from_points_segs(verts,edges)

    return poly1, poly2

def disconnected_test():
    '''a pair of dcels, one of which is connected, whose overlay has vertex-vertex
    and vertex-edge events'''
    verts1 = []
    segs1 = []
    for i in range(3):
        for j in range(3):
            verts1.append(Point(i,j))
            if i < 2:
                segs1.append(Segment(Point(i,j), Point(i+1,j)))
            if j < 2:
                segs1.append(Segment(Point(i,j), Point(i,j+1)))

    verts2 = [
        Point(0,0),
        Point(1,1),
        Point(2,2),
        Point(-1,3),
        Point(3,-1),
        Point(10,0),
        Point(12,0),
        Point(11,1),
    ]
    segs2 = [
        Segment(verts2[1],verts2[0]),
        Segment(verts2[1],verts2[2]),
        Segment(verts2[1],verts2[3]),
        Segment(verts2[1],verts2[4]),

        Segment(verts2[0],verts2[4]),
        Segment(verts2[4],verts2[2]),
        Segment(verts2[2],verts2[3]),
        Segment(verts2[3],verts2[0]),

        Segment(verts2[-1],verts2[-2]),
        Segment(verts2[-2],verts2[-3]),
        Segment(verts2[-3],verts2[-1]),
    ]


    dcel1 = DCEL.from_points_segs(verts1,segs1)
    dcel2 = DCEL.from_points_segs(verts2,segs2)
    
    return dcel1, dcel2  

def grid_lines_test():
    '''a pair of disconnected DCELs, each 3 rectangles, which compose
    a grid-like shape when overlayed'''
    n = 3
    m = 3
    rowpts = []
    rowedges = []
    colpts = []
    coledges = []

    for i in range(n):
        colpts.extend([
            Point(1+2*i,0),Point(2+2*i,0),
            Point(2+2*i,2*n+1),Point(1+2*i,2*n+1)
        ])
        coledges.extend([
            Segment(colpts[-1],colpts[-2]),
            Segment(colpts[-2],colpts[-3]),
            Segment(colpts[-3],colpts[-4]),
            Segment(colpts[-4],colpts[-1]),
        ])

    for i in range(m):
        rowpts.extend([
            Point(0,1+2*i),Point(0,2+2*i),
            Point(2*n+1,2+2*i),Point(2*n+1,1+2*i)
        ])
        rowedges.extend([
            Segment(rowpts[-1],rowpts[-2]),
            Segment(rowpts[-2],rowpts[-3]),
            Segment(rowpts[-3],rowpts[-4]),
            Segment(rowpts[-4],rowpts[-1]),
        ])

    rowdcel = DCEL.from_points_segs(rowpts, rowedges)
    coldcel = DCEL.from_points_segs(colpts, coledges)

    return rowdcel, coldcel                     

def poly_with_holes():
    '''a single connected DCEL with two holes'''
    cycles = [
        [
            Point(2,2),
            Point(4,4),
            Point(3,5),
        ],
        [
            Point(6,6),
            Point(8,8),
            Point(7,9),
        ],
        [
            Point(0,0),
            Point(9,1),
            Point(10,10),
            Point(1,9),
        ]
    ]

    verts = []
    edges = []
    for h in cycles:
        verts.extend(h)
        edges.extend([ Segment(h[i],h[(i+1)%len(h)]) for i in range(len(h)) ])

    return verts, edges

def star():
    '''a single DCEL with only one face'''
    verts = [
        Point(1,1),
        Point(0,1),
        Point(2,1),
        Point(1,0),
        Point(1,2),
    ]

    edges = [ Segment(verts[0], verts[i]) for i in range(1,len(verts)) ]

    return DCEL.from_points_segs(verts, edges)

def simple_graph():
    '''an example connected DCEL'''
    verts = [
        Point(0,0),
        Point(0,2),
        Point(2,2),
        Point(2,0),
        Point(3,3),
        Point(2,4),
    ]

    edges = [
        Segment(verts[0], verts[1]),
        Segment(verts[0], verts[3]),
        Segment(verts[1], verts[2]),
        Segment(verts[2], verts[3]),
        Segment(verts[2], verts[4]),
        Segment(verts[2], verts[5]),
        Segment(verts[4], verts[5]),
    ]

    return verts, edges

def rectangle(x1,y1,x2,y2):
    '''a single DCEL representing an axis-aligned rectangle with bottom-left
    vertex (x1,y1) and top-right vertex (x2,y2)'''
    verts = [
        Point(x1,y1),Point(x1,y2),
        Point(x2,y2),Point(x2,y1),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]

    dcel = DCEL.from_points_segs(verts, edges)
    return dcel
