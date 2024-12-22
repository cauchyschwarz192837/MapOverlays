from primitives import *
from dcel import DCEL, naive_overlay_intersect

if __name__=='__main__':

    verts = [
        Point(4,0),
        Point(6,1),
        Point(4,4),
        Point(3,1),
    ]

    verts2 = [
        Point(3,0),
        Point(6,1),
        Point(6,3),
        Point(3,3),
    ]

    edges = [ Segment(verts[i],verts[(i+1)%len(verts)]) for i in range(len(verts)) ]
    edges2 = [ Segment(verts2[i],verts2[(i+1)%len(verts2)]) for i in range(len(verts2)) ]

    poly1 = DCEL.from_points_segs(verts, edges)
    poly2 = DCEL.from_points_segs(verts2, edges2)

    poly1.draw()
    poly2.draw()
    inters = naive_overlay_intersect(d1,d2)
    for inter in inters:
        inter.draw()

    plt.gca().set_aspect('equal')
    plt.show()

    ol = overlay(d1,d2)

    ol.draw()
    plt.gca().set_aspect('equal')
    plt.show()