# Map Overlays Implementation

Project for CS 290: Computational Geometry. This project implements key subroutines for an $O((n+k) \log n)$-time segment intersection algorithm and an algorithm to compute the overlay of two planar subdivisions, represented as doubly-connected edge lists (DCELs).

## Figures

### Segment Intersections

![](./figs/seg_inter_all.png)

All intersections for $n=12$ segments, generated with `generate_random_segments(12)`.

![](./figs/seg_inter_del.png)

A deletion event: The segment being deleted is red, the left neighbor to the event point is orange, and the right neighbor to the event point is green.

![](./figs/seg_inter_inter.png)

An intersection event: The intersecting segments are red/pink. The left neighbor to the intersection is orange, and the right neighbor to the intersection is green.

### Map Overlay

![](./figs/edge_edge.png)
![](./figs/edge_edge2.png)

The before/after of overlaying the DCELs from `edge_edge_test()` in `dcel_datasets.py`. Halfedges are red on inner cycles, and blue on outer cycles. In the overlay, the purple face is contained in a bounding face of each of the original DCELs.

![](./figs/vertex_edge.png)
![](./figs/vertex_edge2.png)

The before/after of overlaying the DCELs from `vert_edge_test()` in `dcel_datasets.py`. Halfedges are red on inner cycles, and blue on outer cycles. Halfedges are red on inner cycles, and blue on outer cycles. In the overlay, the purple face is contained in a bounding face of each of the original DCELs. Note the `Halfedge`s on the (single) inner cycle of the bounded face in the overlay, which have been updated accordingly.

![](./figs/vertex_vertex.png)
![](./figs/vertex_vertex2.png)

The before/after of overlaying the DCELs from `vert_vert_test()` in `dcel_datasets.py`. The purple arrows point from `Halfedge`s to their previous on the same face. In the overlay, the purple face is contained in a bounding face of each of the original DCELs. Note the `Halfedge`s on the (single) inner cycle of the bounded face in the overlay, which have been updated accordingly.
