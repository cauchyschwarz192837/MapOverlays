# modified dynamic AVL tree from https://www.geeksforgeeks.org/deletion-in-an-avl-tree/
from primitives import *
from avl import AVLTree
from event_queue import *
from sweep_line_comparator import *
import time
import random
from sweep_line_datasets import *

class SweepLine(AVLTree):
    '''an implementation of a balanced binary search tree, namely an AVL tree,
    using a custom comparator to sort segments on a moving horizontal sweep-line
    by their points of intersection.'''

    DRAW=False

    def __init__(self):
        super().__init__(SweepLineComparator())
        self.queue = EventQueue()

    def swap(self, left, right):
        '''swaps the positions of two segments, left and right, within the tree.
        requires that, according to the current position of the sweep-line,
        the right segment is the right neighbor of the given left segment.'''
        assert(self.right_neighbor(left) == right)

        node_left = self._search(self.root, left)
        node_right = self._search(self.root, right)
        
        assert(node_left is not None and node_right is not None)

        node_left.key, node_right.key = node_right.key, node_left.key


    def handle_insert(self, seg : Segment):

        # TODO: Order and place the following two lines appropriately within the method.
        #  The latter sets the sweep-line position to the y-coordinate of this point.
        #  Any tree operations after this line will compare segments by their intersection
        #  with this new position of the line, so place this line appropriately within the method.
        #
        #  super().insert(seg), self.comparator.set_last(seg.top)

        self.comparator.set_last(seg.top)
        super().insert(seg) # sorted by x-coordinate of intersection with sweep line (from sweep_line_comparator.py)

        left_neighbor = self.left_neighbor(seg)
        right_neighbor = self.right_neighbor(seg)

        new_evts = []

        if left_neighbor:
            intersection_point = seg.intersect(left_neighbor) # just using predefined function
            if intersection_point:
                toAdd = Event(EventKind.INTER, intersection_point, (left_neighbor, seg))
                self.queue.push(toAdd) # has an EventQueue data member
                new_evts.append(toAdd)

        if right_neighbor:
            intersection_point = seg.intersect(right_neighbor)
            if intersection_point:
                toAdd2 = Event(EventKind.INTER, intersection_point, (seg, right_neighbor))
                self.queue.push(toAdd2)
                new_evts.append(toAdd2)

        return new_evts

    def handle_delete(self, seg : Segment):
        
        # TODO: Order and place the following two lines appropriately within the method,
        #  which set the sweep-line position to the y-coordinate of this point.
        #  Any tree operations after this line will compare segments by their intersection
        #  with this new position of the line, so place this line appropriately within the method.
        #
        #  super().delete(seg), self.comparator.set_last(seg.bottom)

        self.comparator.set_last(seg.bottom)

        left_neighbor = self.left_neighbor(seg)
        right_neighbor = self.right_neighbor(seg)

        new_evts = []
        
        super().delete(seg)

        if left_neighbor and right_neighbor:
            intersection_point = left_neighbor.intersect(right_neighbor)
            if intersection_point:
                toAdd = Event(EventKind.INTER, intersection_point, (left_neighbor, right_neighbor))
                self.queue.push(toAdd)
                new_evts.append(toAdd)
    
        return new_evts

    def handle_intersection(self, point, left : Segment, right : Segment):
        '''handle and process an intersection-type event, where 
            point is the intersection point, "left" is the intersecting segment to the left above the sweep-line (and right below it),
            and "right" is the intersecting segment to the right above the sweep-line (and left below it):

        - swap the intersecting segments in the tree,
        - update the sweep-line's position, and
        - return any new intersections as events to process in the future.'''        

        new_evts = []

        # (1) Swap the positions of the given segments within this (self) tree
        self.swap(left, right)

        # (2) Set the sweep-line position to the y-coordinate of this point.
        self.comparator.set_last(point)

        # TODO: (3) Compute any new intersection events to new_evts.
        # Note that the order of the intersecting segments matters in the Event object;
        #   the one which is left above the sweep-line should come first in the tuple, e.g.,
        #   Event(Event.Kind, inter_point, (left_seg, right_seg))

        left_neighbor = self.left_neighbor(right)
        right_neighbor = self.right_neighbor(left)

        if left_neighbor:
            intersection_point = left_neighbor.intersect(right)
            if intersection_point:
                toAdd = Event(EventKind.INTER, intersection_point, (left_neighbor, right))
                self.queue.push(toAdd)
                new_evts.append(toAdd)

        if right_neighbor:
            intersection_point = right_neighbor.intersect(left)
            if intersection_point:
                toAdd = Event(EventKind.INTER, intersection_point, (left, right_neighbor))
                self.queue.push(toAdd)
                new_evts.append(toAdd)

        return new_evts

    def find_intersections(self, segs):
        '''compute all pairwise segment intersections between the segments in "segs",
        assuming:
            - no two segments have endpoints with the same y-coordinate,
            - no three segments intersect, and
            - no two segments intersect at their endpoints.
        As a consequence, all events (see event_queue.py) have different y-coordinates.
        '''
        inters = []

        # initialize queue with insertion and deletion events
        for seg in segs:
            self.queue.push(Event(EventKind.INSERT, seg.top, (seg,)))
            self.queue.push(Event(EventKind.DELETE, seg.bottom, (seg,)))
        
        # while the queue is non-empty, pop the next (lower) event
        while (self.queue.size() > 0):

            evt = self.queue.pop()

            """
            if self.DRAW:
                for s in segs:
                    s.draw(color='grey')

                segs_on_line = self.in_order()
                for s in segs_on_line:
                    s.draw(color='black')

                self.comparator.draw()

                evt.point.draw()
            """

            match evt.kind:
                case EventKind.INSERT:                    
                    assert(len(evt.involved) == 1)
                    seg = evt.involved[0]
                    new_evts = self.handle_insert(seg)
                    
                    if self.DRAW:
                        seg.draw(color='red')

                case EventKind.DELETE:
                    assert(len(evt.involved) == 1)
                    seg = evt.involved[0]
                    new_evts = self.handle_delete(seg)

                    if self.DRAW:
                        seg.draw(color='red')
                    
                case EventKind.INTER:              # check order!       
                    inters.append(evt.point) # store the intersection to be reported
                    assert(len(evt.involved) == 2)
                    left, right = evt.involved
                    new_evts = self.handle_intersection(evt.point, left, right)
                    
                    if self.DRAW:
                        left.draw(color='red')
                        right.draw(color='pink')

            # add all, if any, new events to the queue
            for e in new_evts:
                self.queue.push(e)

            if self.DRAW:
                plt.show()
        
        return inters

def naive_seg_inter(segs):
    inters = []
    for i in range(len(segs)-1):
        for j in range(i+1,len(segs)):
            s1 = segs[i]
            s2 = segs[j]

            inter = s1.intersect(s2)
            if inter is not None:
                inters.append(inter)

    return inters


if __name__ == "__main__":

    random.seed(290)

    tree = SweepLine()

    n = 8

    segs = generate_random_segments(n)
    # segs = generate_tall_verticals(n)
    # segs = generate_short_verticals(n)
    
    start = time.time()
    soln = naive_seg_inter(segs)
    print('naive time: ', time.time()-start)

    start = time.time()
    inters = tree.find_intersections(segs)
    print(len(inters))
    print('sens. time: ', time.time()-start)
    
    print(set(inters) == set(soln))
