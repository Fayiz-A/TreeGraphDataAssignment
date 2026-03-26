from __future__ import annotations

import doctest
from heapq import heapify, heappop, heappush
from typing import Optional

import python_ta
from python_ta.contracts import check_contracts

from dataclasses import dataclass, field
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
        are length meters long.

    Representation Invariants:
        - self.length >= 0
        - self.length != 0 or len(self.all_shortest_paths) == 1 and len(self.all_shortest_paths[0] == 1)
        - self.length == 0 if and only if self.all_shortest_paths contains list with element origin
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
        - start_junction: the junction/vertex of where this road
        starts from
        - end_junction: the junction/vertex of where this road
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
        - shortest_paths_prev_vertex_ids: a set of vertex/junction id of
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
    shortest_paths_prev_vertex_ids: set[str]


@dataclass
class Road:
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

        >>> graph: Graph = Graph()
        >>> for i in range(65, 70):
        ...     graph.add_junction(chr(i))
        >>> coordinates: list[Coordinate] = [Coordinate(78, 100), Coordinate(79, 101)]
        >>> graph.add_bidirectional_roads('A', 'B', 4, 'AB', False, coordinates)
        >>> graph.add_bidirectional_roads('A', 'D', 5, 'AD', False, coordinates)
        >>> graph.add_bidirectional_roads('B', 'C', 4, 'BC', False, coordinates)
        >>> graph.add_bidirectional_roads('B', 'D', 1, 'BD', False, coordinates)
        >>> graph.add_bidirectional_roads('C', 'D', 3, 'CD', False, coordinates)
        >>> graph.add_bidirectional_roads('C', 'E', 1, 'CE', False, coordinates)
        >>> graph.add_bidirectional_roads('D', 'E', 4, 'DE', False, coordinates)
        >>> shortest_path_result: ShortestPathResult = graph.compute_shortest_path('A', 'E')
        >>> (sorted(shortest_path_result.all_shortest_paths, key=lambda item: ''.join(item)), shortest_path_result.length)
        ([['A', 'B', 'C', 'E'], ['A', 'B', 'D', 'C', 'E'], ['A', 'B', 'D', 'E'], ['A', 'D', 'C', 'E'], ['A', 'D', 'E']], 9.0)
        """
        #         >>> (sorted(shortest_path_result.all_shortest_paths), shortest_path_result.length) == (expected, 9.0)
        # the dijktras code for this was inspired by https://cp-algorithms.com/graph/dijkstra.html, with major
        # changes to it to make it fast, return shortest paths also and not only distance, and to make it
        # suitable for returning multiple shortest equivalent paths.
        visited: set[str] = set()
        all_shortest_paths_computed: set[str] = set()

        infinity: float = 1_000_000_000_000.0  # 1 billion km, Ontario road network
        # road length sum should not be that big
        distance: dict[str, ShortestDistanceToVertex] = {}

        for vertex in self.vertices:
            if vertex == source_junction_id:
                # distance from source_junction_id to source_junction_id
                # is always 0.0
                distance[vertex] = ShortestDistanceToVertex(
                    junction_id=vertex,
                    shortest_distance_till_now=0.0,
                    shortest_paths_prev_vertex_ids=set()
                )
            else:
                distance[vertex] = ShortestDistanceToVertex(
                    junction_id=vertex,
                    shortest_distance_till_now=infinity,
                    shortest_paths_prev_vertex_ids=set()
                )

        len_minimizer_candidate_roads: list[LenMinimizerCandidateRoad] = []

        # heap related code adapted from https://docs.python.org/3/library/heapq.html
        # we are using a min heap because it is like a priority queue with push
        # Big O time and pop Big O time as O(n) where n is the number of
        # elements inside it. See https://stackoverflow.com/a/38833175 for
        # time complexity of these heap methods
        heapify(len_minimizer_candidate_roads)

        source_vertex: _Vertex = self.vertices[source_junction_id]

        heappush(len_minimizer_candidate_roads, LenMinimizerCandidateRoad(
            length_from_source=0.0,
            start_junction=source_vertex,
            end_junction=source_vertex
        ))

        while len(len_minimizer_candidate_roads) > 0:
            # heap pop gives us the road with the least length attribute
            len_minimizer_candidate_road: LenMinimizerCandidateRoad = heappop(len_minimizer_candidate_roads)

            current_vertex: _Vertex = len_minimizer_candidate_road.end_junction
            current_vertex_id: str = current_vertex.junction_id

            if (distance[current_vertex_id].shortest_distance_till_now <
                    len_minimizer_candidate_road.length_from_source):
                # all shortest paths have been computed to current_vertex_id,
                # and any other possible path to it except these paths
                # is a path with length > distance[current_vertex_id].shortest_distance_till_now
                all_shortest_paths_computed.add(current_vertex_id)
            else:
                visited.add(current_vertex_id)
                distance[current_vertex_id].shortest_paths_prev_vertex_ids.add(
                    len_minimizer_candidate_road.start_junction.junction_id)

            if current_vertex_id == target_junction_id and target_junction_id in all_shortest_paths_computed:
                #  Our modified Dijktras guarantees that if this branch executes,
                #  then it is true that there exists no other shortest path
                #  in the graph from source_junction_id to target_junction_id apart from
                #  what we already have indirectly stored in distance list
                break
            else:
                neighbours: list[Road] = current_vertex.neighbours

                for road in neighbours:
                    # relaxation step of Dijktras algorithm
                    neighbour_junction: _Vertex = road.to_junction
                    neighbour_junction_id: str = neighbour_junction.junction_id

                    # don't minimize distance for something already in visited set, it already has the shortest
                    # distance
                    if neighbour_junction_id not in all_shortest_paths_computed:
                        shortest_dist_till_now_info: ShortestDistanceToVertex = distance[neighbour_junction_id]
                        potentially_less_distance: float = (
                                len_minimizer_candidate_road.length_from_source + road.length * 1.0)
                        # multiply by 1.0 to ensure the result is a float and not an int

                        if shortest_dist_till_now_info.shortest_distance_till_now >= potentially_less_distance:

                            shortest_dist_till_now_info.shortest_distance_till_now = potentially_less_distance

                            heappush(len_minimizer_candidate_roads, (LenMinimizerCandidateRoad(
                                length_from_source=distance[neighbour_junction_id].shortest_distance_till_now,
                                start_junction=current_vertex,
                                end_junction=neighbour_junction)
                            ))

        shortest_path_info: ShortestDistanceToVertex = distance[target_junction_id]
        shortest_path_node_list: set[str] = shortest_path_info.shortest_paths_prev_vertex_ids

        tree: PathTree = PathTree(target_junction_id)

        self._add_subtrees_from_list(
            tree=tree,
            source=source_junction_id,
            children_to_add=shortest_path_node_list,
            distance=distance
        )

        return ShortestPathResult(
            length=shortest_path_info.shortest_distance_till_now,
            all_shortest_paths=tree.get_all_possible_paths(),
        )

    def _add_subtrees_from_list(self, tree: PathTree, source: str, children_to_add: set[str],
                                distance: dict[str, ShortestDistanceToVertex]) -> None:
        """
        Mutating helper method
        TODO: continue this
        """
        for child in children_to_add:
            child_subtree: PathTree = PathTree(child)

            # we have reached our source junction
            # id if this condition is False and the
            # if branch doesn't execute. This non-execution
            # of if branch is our base case.
            if child != source:
                self._add_subtrees_from_list(
                    child_subtree,
                    source,
                    distance[child].shortest_paths_prev_vertex_ids,
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

    def check_is_neighbour(self, road_id_1: str, road_id_2: str) -> bool:
        pass


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['heapq', 'path_tree', 'coordinate'],
    })
