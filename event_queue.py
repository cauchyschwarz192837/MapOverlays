from functools import total_ordering
from primitives import *
import heapq
from enum import Enum

class EventKind(Enum):
    '''a simple enum class to denote types of events'''
    INSERT = 1
    INTER = 2
    DELETE = 3

@total_ordering
class Event(object):
    '''a class to record information about segment-intersect events, which correspond to
        - starting to intersect a segment from above,
        - stopping intersecting a segment from above,
        - an intersection of two distinct segments.
        
        events are ordered in chronological order, as the sweep-line is parallel to the y-axis
        and moves downwards through segments.
        '''
    def __hash__(self):
        return self.point.__hash__()

    def __init__(self, kind, point, involved):
        self.kind = kind
        self.point = point
        self.involved = involved

    def __lt__(self, other):
        # order first in decreasing y-coordinate, breaking ties by x-coordinate
        cx = self.point._x*other.point._w - other.point._x*self.point._w
        cy = self.point._y*other.point._w - other.point._y*self.point._w

        if cy > 0:
            return True
        elif cy < 0:
            return False
        
        return cx < 0
    
    def __eq__(self, other):
        # return true if and only if event points are the same
        cx = self.point._x*other.point._w - other.point._x*self.point._w
        cy = self.point._y*other.point._w - other.point._y*self.point._w

        return cx == 0 and cy == 0
    
class EventQueue(object):
    '''implementation of a priority queue for segment-intersection events'''

    def __init__(self, evts=[]):
        self.q = list(evts)
        self.all_evts = { e:e for e in evts }
        self.last_evt = None
        heapq.heapify(self.q)

    def pop(self):
        '''return next event in priority queue'''
        
        if len(self.q) == 0:
            raise ValueError('event queue empty, cannot pop')
        
        evt = heapq.heappop(self.q)

        if self.last_evt:
            assert(self.last_evt < evt)

        self.last_evt = evt
        return evt
    
    def push(self, evt):
        '''add the provided event to the priority queue,
        ignoring it if it has been seen before.
        assumes no distinct events occur with the same y-coordinate.'''
        if evt in self.all_evts:
            e = self.all_evts[evt]
            if e.kind == evt.kind and set(e.involved) == set(evt.involved):
                # found same event again, skip adding it.
                # this may be an already-processed intersection event
                return
            else:
                # found shared endpoint of different involved segments
                raise ValueError('coinciding events are unsupported')
        
        # new unseen event, add to queue
        heapq.heappush(self.q, evt)
        self.all_evts[evt] = evt

    def size(self):
        return len(self.q)