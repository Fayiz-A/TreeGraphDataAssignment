"""
This file contains code related to 3 dataclasses that
should be used in our modified version of Dijktras
algorithm to make the code readable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from python_ta.contracts import check_contracts

from graph import _Vertex


@check_contracts
@dataclass
class ShortestPathResult:
    """
    A dataclass to represent what a shortest path algorithm
    to find *all* shortest paths from one source to another source
    would return. In case the target vertex is disconected, do *not* use
    this class, and rather return something like None from the method/function
    which uses this.

    Instance Attributes:
        - length: the length of the shortest path in meters. There
        exists no other shorter path than this length in the graph
        over which the algorithm was run.
        - all_shortest_paths: a collection of all shortest
        paths from source vertex to target vertex which have
        are length meters long.

    Representation Invariants:
        - length >= 0
        - length != 0 or len(all_shortest_paths) == 1 and len(all_shortest_paths[0] == 1)
        - length == 0 if and only if all_shortest_paths contains list with element origin
    """
    length: float
    all_shortest_paths: list[list[str]]


# dataclass order and field method code seen from https://stackoverflow.com/a/72330706
@check_contracts
@dataclass(order=True)
class LenMinimizerCandidateRoad:
    """
    A dataclass to represent a candidate shorter road in Dijktras algorithm.

    This is what gets added to a distance array which is iterated over
    in the while loop of Djiktras. The order=True attribute of this dataclass
    takes care of how priority queue/heap uses it for comparison, and hence
    it can be used in priority queues/heaps out of the box. This is ordered
    by the length_from_source instance attribute only.

    Instance Attributes:
        - length_from_source: the length of the candidate shorter road in meters *from source* to end_junction.
        - start_junction_id: the junction/vertex id of where this road
        starts from
        - end_junction_id: the junction/vertex id of where this road
        connects to (meaning where its end junction is)

    Representation Invariants:
        - self.length_from_source >= 0
        - self.length_from_source != 0 or self.start_junction.junction_id == self.end_junction.junction_id
        - self.length_from_source == 0 if and only if the self.start_junction.junction_id is
        the origin and end_junction.junction_id is the
        origin (typically the first road/edge added to
        Dijktras while loop variable)
        - len(self.start_junction_id.strip()) > 0
        - len(self.end_junction_id.strip()) > 0
        - both start_junction and end_junction are valid
        junctions (vertices) present in the graph over which this
        class is being used in the graph's Dijktras algorithm
    """
    start_junction: _Vertex = field(compare=False)
    end_junction: _Vertex = field(compare=False)
    length_from_source: float


@check_contracts
@dataclass
class ShortestDistanceToVertex:
    """
    A dataclass to represent the shortest distance till now/eventually
    to the vertex this is attached to in the dictionary that uses it.
    To be used in Dijktras algorithm to represent shortest distances
    till now and then eventually the final shortest distance if the
    junction id this is attached to is our target one (or lies in path
    of even one of the possible shortest path to target junction id)

    Instance Attributes:
        - shortest_distance_till_now: the length of the shortest
        distance to vertex this is attached to from source
         found till now as per Dijktras algorithm.
        - shortest_paths_prev_vertex_ids: a list of vertex/junction id of
        the previous vertices from which the shortest distance from source
        came. This can be used to iterate back till
        the first origin after our version of Dijktras completes
        to recover the path(s).
        - junction_id: the junction_id this represents shortest path to
        from source junction

    Representation Invariants:
        - self.shortest_distance_till_now == infinity if and only
        if the Dijktras algorithm has not yet performed relaxations
        on the junction to which this is attached to or if the
        junction is disconnected, where infinity is a very large
        number that would never be reached even if all edges
        of the road are summed up twice (twice to
        be on a safer side). Ensure not to make it so big the
        Python cannot handle it simply.
        - self.shortest_distance_till_now >= 0
        - self.shortest_distance_till_now == 0 if and only if this
        represents route to the source itself
        - if len(self.shortest_paths_prev_vertex_ids) > 0, then all paths are
        tracable back to source and can be traced using
        self.shortest_paths_prev_vertex_ids, and those paths have the same
        length, and that length is the shortest length to the
        self.junction_id from source junction.
        - if len(self.shortest_paths_prev_vertex_ids) > 0 and self.junction_id is
        the target junction, then self.shortest_paths_prev_vertex_ids
        should contain all neighbouring junction ids that are connected
        to it and lie along the shortest path.
        - len(self.shortest_paths_prev_vertex_ids) == 0 if and only if one
        or more of these scenarios is True:
          - Dijktras did not relax the self.junction_id this corresponds to
          - self.junction_id is the source junction itself

    """
    junction_id: str
    shortest_distance_till_now: float
    shortest_paths_prev_vertex_ids: list[str]
