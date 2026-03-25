"""
This file contains code for Graph class and its shortest path (modified) multi shortest path
finding Dijktras algorithm code.
"""

from __future__ import annotations

import doctest
from heapq import heapify, heappop, heappush
from typing import Optional

import python_ta
from python_ta.contracts import check_contracts

from dataclasses import dataclass
from coordinate import Coordinate
from path_tree import PathTree


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
        are self.length meters long. A shortest path here is a list
        of tuple, with first element of all tuples being a vertex id,
        the second element of all tuples (expect last one, which is just going to be an emtpy string) is the road id
        that the next vertex (next tuple's first argument) is connected to.


    Representation Invariants:
        - self.length >= 0
        - self.length != 0 or len(self.all_shortest_paths) == 1 and len(self.all_shortest_paths[0] == 1)
        - self.length == 0 if and only if self.all_shortest_paths contains list with element origin
        - len(self.all_shortest_paths) > 0
        - all(len(shortest_path) >= 2 and shortest_path[-1][1] == '' for shortest_path in self.all_shortest_paths)
    """
    length: float
    all_shortest_paths: list[list[tuple[str, str]]]


# dataclass order and field method code seen from https://stackoverflow.com/a/72330706
@check_contracts
@dataclass(order=True)
class LenMinimizerCandidateRoad:
    """
    A dataclass to represent a candidate shorter road in Dijktras algorithm.

    NOTE: This is what we were supposed to originally use, but we shifted to using a list/tuple due to reasons
    explained by the comment on variable in code below which was supposed to use this. However, this dataclass
    is not removed as it helps in reasoning about our code, documentation and representation
    invariants of the list/tuples which represents the same data as this dataclass.

    This is what gets added to a distance array which is iterated over
    in the while loop of Djiktras. The order=True attribute of this dataclass
    takes care of how priority queue/heap uses it for comparison, and hence
    it can be used in priority queues/heaps out of the box. This is ordered
    by the length_from_source instance attribute only.

    Instance Attributes:
        - length_from_source: the length of the candidate shorter road in meters *from source* to end_junction.
        - start_junction_id: the junction id of where this road
        starts from
        - end_junction_id: the junction id of where this road
        connects to (meaning where its end junction is)
        - road_id: the id of road which connects the start and end junction ids

    Representation Invariants:
        - self.length_from_source >= 0
        - self.length_from_source != 0 or self.start_junction_id == self.end_junction_id
        - self.length_from_source == 0 if and only if the self.start_junction_id is
        the origin and self.end_junction_id is the origin (typically the first road/edge added to
        Dijktras while loop variable)
        - self.start_junction_id == self.end_junction_id if and only if self.start_junction_id is origin/source vertex
        - len(self.start_junction_id.strip()) > 0
        - len(self.road_id.strip()) == 0 if and only if self.start_junction_id == self.end_junction_id
        - len(self.end_junction_id.strip()) > 0
        - both self.start_junction_id and self.end_junction_id represent valid
        junctions (vertices) present in the graph over which this
        class is being used in the graph's Dijktras algorithm
    """
    start_junction_id: str
    end_junction_id: str
    length_from_source: float
    road_id: str


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

    NOTE: This is what we were supposed to originally use, but we shifted to using a list/tuple due to reasons
    explained by the comment on variable in code below which was supposed to use this.
    However, this dataclass is not removed as it helps in reasoning about our code, documentation and
    representation invariants of the lists/tuples which represents the same data as this dataclass.

    Instance Attributes:
        - shortest_distance_till_now: the length of the shortest
        distance to vertex this is attached to from source
         found till now as per Dijktras algorithm.
        - shortest_paths_prev_vertex_ids: a set of tuple whose first element is vertex/junction id of
        the previous vertices from which the shortest distance from source
        came. This can be used to iterate back till
        the first origin after our version of Dijktras completes
        to recover the path(s). The second argument of tuple is the road id from which the vertex
        connected to self.junction_id (useful if there is more than one road from that same vertex and they
        both have the same length)
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
        self.shortest_paths_prev_vertex_ids. All those paths have the same
        length, and that length is the shortest length to the
        self.junction_id from source junction.
        - if len(self.shortest_paths_prev_vertex_ids) > 0 and self.junction_id is
        the target junction, then self.shortest_paths_prev_vertex_ids
        should contain all neighbouring junction ids that are connected
        to it and lie along all shortest paths.
        - len(self.shortest_paths_prev_vertex_ids) == 0 if and only if one
        or more of these scenarios is True:
          - Dijktras did not relax the self.junction_id this corresponds to
          - self.junction_id is the source junction itself

    """
    junction_id: str
    shortest_distance_till_now: float
    shortest_paths_prev_vertex_ids: set[tuple[str, str]]


@dataclass
class Road:
    """
    TODO: write this docstring
    """
    from_junction: _Vertex
    to_junction: _Vertex
    length: float
    road_id: str
    removed: bool
    geometry: list[Coordinate]


@dataclass
class _Vertex:
    """
    A vertex in the graph, used to represent a junction in the road network.

    Instance Attributes:
        - junction_id: a str that represents the id of the junction.
        - neighbours: a list of Roads that represents the adjacent vertices to self.vertices.

    Representation Invariants:
        - len(self.junction_id) >= 0

    """

    junction_id: str
    neighbours: list[Road]


class Graph:
    """
    A graph to represent a road network.

    Instance Attributes:
        - vertices: a mapping of a junction id to its representing vertex.
        - roads: a mapping of a road id to its Road object.

    """

    vertices: dict[str, _Vertex]
    roads: dict[str, Road]

    def __init__(self) -> None:
        """
        Initializes an empty graph (a graph with no vertices or edges).
        """
        self.vertices = {}
        self.roads = {}

    @check_contracts
    def compute_shortest_path(self, source_junction_id: str, target_junction_id: str) -> Optional[ShortestPathResult]:
        """
        Compute and return the shortest path between source junction id and target junction id and its length in
        metres. In case multiple shortest paths of same length exist, return one of them along with its length.
        In case the two vertices are disconnected, a tuple with empty list and length -1 is returned.

        This method uses Dijktras algorithm.
        TODO: Continue this.

        Preconditions:
            - source_junction_id in self.vertices and target_junction_id in self.vertices
            - source_junction_id != target_junction_id

        >>> graph: Graph = Graph()
        >>> for i in range(65, 70):
        ...     graph.add_junction(chr(i))
        >>> coordinates: list[Coordinate] = [Coordinate(78, 100), Coordinate(79, 101)]
        >>> graph.add_bidirectional_roads('A', 'B', 4, 'A->B', False, coordinates)
        >>> graph.add_bidirectional_roads('A', 'D', 5, 'A->D', False, coordinates)
        >>> graph.add_bidirectional_roads('B', 'C', 4, 'B->C', False, coordinates)
        >>> graph.add_bidirectional_roads('B', 'D', 1, 'B->D', False, coordinates)
        >>> graph.add_bidirectional_roads('C', 'D', 3, 'C->D', False, coordinates)
        >>> graph.add_bidirectional_roads('C', 'E', 1, 'C->E', False, coordinates)
        >>> graph.add_bidirectional_roads('D', 'E', 4, 'D->E', False, coordinates)
        >>> shortest_path_result: ShortestPathResult = graph.compute_shortest_path('A', 'E')
        >>> sorted(shortest_path_result.all_shortest_paths, key=lambda shortest_path:
        ... ''.join([item[0] for item in shortest_path]))
        [[('A', 'A->B'), ('B', 'B->C'), ('C', 'C->E'), ('E', '')], [('A', 'A->B'), ('B', 'B->D'), ('D', 'reverse-C->D'), ('C', 'C->E'), ('E', '')], [('A', 'A->B'), ('B', 'B->D'), ('D', 'D->E'), ('E', '')], [('A', 'A->D'), ('D', 'reverse-C->D'), ('C', 'C->E'), ('E', '')], [('A', 'A->D'), ('D', 'D->E'), ('E', '')]]
        >>> shortest_path_result.length
        9.0
        """

        # the dijktras code for this was inspired by https://cp-algorithms.com/graph/dijkstra.html, with major
        # changes to it to make it O(V + ElogE) where E is the number of edges and V the number of vertices,
        # to return shortest paths also and not only distance, and to make it
        # suitable for returning multiple shortest equivalent paths.
        visited: set[str] = set()
        all_shortest_paths_computed: set[str] = set()

        infinity: float = 1_000_000_000_000.0  # 1 billion km, Ontario road network
        # road length sum should not be that big

        # Note: we are using a list here instead of tuple, as we want to
        # be able to mutate the set and tuples are immutable
        # this list (value of dictionary) follows the same structure as our
        # ShortestDistanceToVertex dataclass, with list length always being 3, and its elements
        # corresponding to ShortestDistanceToVertex's junction_id, shortest_distance_till_now and
        # shortest_paths_prev_vertex_ids respectively, and also follow the same representation
        # invariants as that dataclass. Why didn't we use that dataclass then? That's because
        # tuples/lists are faster than dataclass, and when I used that dataclass instead of what we have now
        # the code became approximately 20 times slower. This was quite significant for our code,
        # as we are working with over million edges and about half a million vertices, and
        # code becoming 20 times slower in Dijktras algorithm meant what would run here in 1 second
        # would take 20 seconds using dataclasses.
        distance: dict[str, list[str | float | set[tuple[str, str]]]] = {}

        for vertex in self.vertices:
            if vertex == source_junction_id:
                # distance from source_junction_id to source_junction_id
                # is always 0.0
                distance[vertex] = [
                    vertex,
                    0.0,
                    set()
                ]
            else:
                distance[vertex] = [
                    vertex,
                    infinity,
                    set()
                ]

        # this tuple (each element of list) follows the same structure as our
        # LenMinimizerCandidateRoads dataclass, with tuple length always being 3, and its elements
        # corresponding to LenMinimizerCandidateRoads's length_from_junction, start_junction_id,
        # end_junction_id and road id respectively, and this tuple's corresponding arguments follow the
        # same representation invariants as that dataclass. Why didn't we use that dataclass then? For the same
        # reason we didn't use dataclass for distance.
        len_minimizer_candidate_roads: list[tuple[float, str, str, str]] = []

        # heap related code adapted from https://docs.python.org/3/library/heapq.html
        # we are using a min heap because it is like a priority queue with push
        # Big O time and pop Big O time as O(n) where n is the number of
        # elements inside it. See https://stackoverflow.com/a/38833175 for
        # time complexity of these heap methods
        heapify(len_minimizer_candidate_roads)

        source_vertex: _Vertex = self.vertices[source_junction_id]
        source_vertex_id: str = source_vertex.junction_id
        heappush(len_minimizer_candidate_roads, (
            0.0,
            source_vertex_id,
            source_vertex_id,
            ''
        ))

        while len(len_minimizer_candidate_roads) > 0:
            # heap pop gives us the road with the least length attribute
            len_minimizer_candidate_road: tuple[float, str, str, str] = heappop(len_minimizer_candidate_roads)

            current_vertex_id: str = len_minimizer_candidate_road[2]

            if (distance[current_vertex_id][1] <
                    len_minimizer_candidate_road[0]):
                # all shortest paths have been computed to current_vertex_id,
                # and any other possible path to it except these paths
                # is a path with length > distance[current_vertex_id].shortest_distance_till_now
                all_shortest_paths_computed.add(current_vertex_id)
            else:
                visited.add(current_vertex_id)
                distance[current_vertex_id][2].add(
                    (len_minimizer_candidate_road[1], len_minimizer_candidate_road[3]))

            if current_vertex_id == target_junction_id and target_junction_id in all_shortest_paths_computed:
                #  Our modified Dijktras guarantees that if this branch executes,
                #  then it is true that there exists no other shortest path
                #  in the graph from source_junction_id to target_junction_id apart from
                #  what we already have indirectly stored in distance list
                break
            else:
                neighbours: list[Road] = self.vertices[current_vertex_id].neighbours

                for road in neighbours:
                    # relaxation step of Dijktras algorithm
                    neighbour_junction: _Vertex = road.to_junction
                    neighbour_junction_id: str = neighbour_junction.junction_id

                    # don't minimize distance for something already in all_shortest_paths_computed set, it
                    # already has all possible shortest paths to it
                    if neighbour_junction_id not in all_shortest_paths_computed:
                        shortest_dist_till_now_info: list[str | float | set[str]] = distance[neighbour_junction_id]
                        potentially_less_distance: float = (
                                len_minimizer_candidate_road[0] + road.length * 1.0)
                        # multiply by 1.0 to ensure the result is a float and not an int

                        if shortest_dist_till_now_info[1] >= potentially_less_distance:

                            shortest_dist_till_now_info[1] = potentially_less_distance

                            heappush(len_minimizer_candidate_roads, (
                                potentially_less_distance,
                                current_vertex_id,
                                neighbour_junction_id,
                                road.road_id,)
                            )

        shortest_path_info: list[str | float | set[tuple[str, str]]] = distance[target_junction_id]
        shortest_path_length: float = shortest_path_info[1]

        if shortest_path_length == infinity:
            return None
        else:
            shortest_path_node_set: set[tuple[str, str]] = shortest_path_info[2]

            tree: PathTree = PathTree((target_junction_id, ''))  # target junction id does not connect to
            # further roads, check representation invariants of ShortestPathResult

            self._add_subtrees_from_list(
                tree=tree,
                source=source_junction_id,
                children_to_add=shortest_path_node_set,
                distance=distance
            )

            return ShortestPathResult(
                length=shortest_path_length,
                all_shortest_paths=tree.get_all_possible_paths(),
            )

    def _add_subtrees_from_list(self, tree: PathTree, source: str, children_to_add: set[tuple[str, str]],
                                distance: dict[str, list[str | float | set[tuple[str, str]]]]) -> None:
        """
        Given a PathTree with target junction id as its root, reconstruct all possible shortest paths from that
        to source using distance dictionary constructed from Dijktras algorithm and children_to_add.
        children_to_add consists as first tuple argument of the neighbours of tree.root junction id that lie along the
        shortest path from source to tree.root, along with the road id that those neighbours use in the
        shortest path as second tuple argument.

        This is a mutating helper recursuve method

        Preconditions:
            - source.strip() in self.vertices
            - distance is a validly constructed dictionary from Dijktras algorithm after it has been run from
            source to target. For definition of distance, see self.compute_shortest_path method where distance
            is declared.
            - children_to_add consists of all neighbours of tree.root that lie along shortest path from source to
            tree.root, along with the specific road ids that the neighbour uses to connected to tree.root
        """
        for child in children_to_add:
            child_subtree: PathTree = PathTree(child)

            # we have reached our source junction
            # id if this condition is False and the
            # if branch doesn't execute. This non-execution
            # of if branch is our base case.
            junction_id: str = child[0]
            if junction_id != source:
                self._add_subtrees_from_list(
                    child_subtree,
                    source,
                    distance[junction_id][2],
                    distance
                )
            tree.add_subtree(child_subtree)

    def remove_road(self, road_id: str) -> None:
        """
        Removes a road from the graph, and removes it from the neighbours of the vertices.
        If the road does not exist in the graph, the function does nothing

        Preconditions:
            - len(road_id) >= 0

        """
        if road_id in self.roads:
            road: Road = self.roads[road_id]
            from_vertex: _Vertex = road.from_junction
            to_vertex: _Vertex = road.to_junction

            from_vertex.neighbours.remove(road)
            to_vertex.neighbours.remove(road)
            self.roads.pop(road_id)

    def add_road(self, from_junction_id: str, to_junction_id: str, length: float, road_id: str,
                 removed: bool, geometry: list[Coordinate]) -> None:
        """
        Creates a road from from_junction_id to to_junction_id and adds it to self.road. If the road already exists,
        the function does nothing

        Preconditions:
            - from_junction_id in self.vertices
            - to_junction_id in self.vertices
            - len(geometry) > 1
            - length > 0
            - len(road_id.strip()) > 0
        """

        if road_id not in self.roads:
            junction1: _Vertex = self.vertices[from_junction_id]
            junction2: _Vertex = self.vertices[to_junction_id]
            self.roads[road_id] = Road(junction1, junction2, length, road_id,
                                       removed, geometry)

            junction1.neighbours.append(self.roads[road_id])

    def add_bidirectional_roads(self, from_junction_id: str, to_junction_id: str, length: float, road_id: str,
                                removed: bool, geometry: list[Coordinate]) -> None:
        """
        Creates a road from from_junction_id to to_junction_id and vice versa and
        adds it to self.road. If any of the road already exists, the function does nothing and adds only the
        one not existing if any.

        Preconditions:
            - from_junction_id in self.vertices
            - to_junction_id in self.vertices
            - length >= 0
            - len(road_id) >= 0
        """
        self.add_road(from_junction_id, to_junction_id, length, road_id, removed, geometry)
        self.add_road(to_junction_id, from_junction_id, length, f'reverse-{road_id}', removed, geometry)

    def add_junction(self, junction_id: str) -> None:
        """
        Maps junction_id to a new _Vertex and adds it to the mapping self.vertices. If junction_id already exists
        in self.vertices, the function does nothing.

        Preconditions:
            - len(junction_id.strip()) > 0
        """

        if junction_id not in self.vertices:
            self.vertices[junction_id] = _Vertex(junction_id, [])

    def is_valid_road_selection(self, road_ids: list[str]) -> tuple[bool, list[str]]:
        """
        Return a tuple of:
            - a bool that is true if there exists a connected valid path
            - a list of the starting junction id and the ending junction id if there is a connected valid path,
             otherwise, an empty list.

        A valid path is defined as a set of roads such that there exists only 1 start point for the path and
        only one endpoint for the path, and if there are more than one paths that are disconnected, then only
        1 path has the start and end points (the other path(s) are a cycle entirely)
        Preconditions:
            - len(road_ids) >= 0
            - all({road_id in self.roads for road_id in road_ids})

        """
        if len(road_ids) == 0:
            return False, []

        free_starts: list = []
        free_ends: list = []

        for road_id in road_ids:
            road: Road = self.roads[road_id]
            start: str = road.from_junction.junction_id
            end: str = road.to_junction.junction_id

            is_free_start: bool = True
            for other_id in road_ids:
                other: Road = self.roads[other_id]
                if other.to_junction.junction_id == start:
                    is_free_start = False
                    break

            if is_free_start:
                free_starts.append(start)

            is_free_end: bool = True
            for other_id in road_ids:
                other: Road = self.roads[other_id]
                if other.from_junction.junction_id == end:
                    is_free_end = False
                    break

            if is_free_end:
                free_ends.append(end)

        if len(set(free_starts)) != 1 or len(set(free_ends)) != 1:
            return False, []

        return True, [free_starts[0], free_ends[0]]


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['heapq', 'path_tree', 'coordinate'],
    })
