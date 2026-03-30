"""
This file contains code for Graph class and its shortest path (modified) multi shortest path
finding Dijktras algorithm code.
It also contains 2 classes: LenMinimizerCandidateRoad and ShortestDistanceToVertex that
are used to document how our tuples/lists should behave and should not behave, but these classes
were not used to improve performance (read NOTE in both these classes' docstrings)

Finally, it contains code for ShortestPathResult, which is the dataclass used to give shortest
path finding methods results in.
"""

from __future__ import annotations

from dataclasses import dataclass
import doctest
from heapq import heapify, heappop, heappush
from typing import Optional

from python_ta.contracts import check_contracts

import constants
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
        are self.length meters long (ignoring decimals). A shortest path here is a list
        of tuple, with first element of all tuples being a vertex id, while
        the second element of all tuples (except last one, which is just going to be an emtpy string)
        being the road id of Road that the next vertex (next tuple's first argument) is
        connected to using from current vertex.


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


# the slot trick for Road and _Vertex class was taken from
# https://towardsdatascience.com/should-you-use-slots-how-slots-affect-your-class-when-and-how-to-use-ab3f118abc71/
# this makes our dataclass faster
@dataclass(slots=True)
class Road:
    """
    A representation of a weighted directed edge between two vertices/junctions.

    Instance Attributes:
        - from_junction: the vertex from which this road originates
        - to_junction: the vertex to which this road goes
        - length: the length/weight of this road in meters
        - road_id: the id of this edge/road. This should have a _neg if road is negative, _pos if road is positive (
        positive roads run west to east or south to north, while negative roads run east to west or north to south)
        - removed: represents if the road is soft deleted or not
        - geometry: polyline of this road which gives it its shape, where each coordinate of polyline is represented
         by a tuple whose *first element is longitude* and *second element is latitude* (this is opposite from
         normal order, but this is how our data is stored in file, and reversing it during load
         leads to huge performance issues, as there are millions of them)

    Representation Invariants:
        - self.length > 0
        - len(self.road_id.strip()) > 0
        - self.road_id[-4:] == '_neg' or self.road_id[-4:] == '_pos'
        - both self.from_junction and self.to_junction represent valid Vertices in our graph
        - len(self.geometry) >= 2
    """
    from_junction: Vertex
    to_junction: Vertex
    length: float
    road_id: str
    removed: bool
    geometry: list[tuple[float, float]]


@dataclass(slots=True)
class Vertex:
    """
    A vertex in the graph, used to represent a junction in the road network.

    Instance Attributes:
        - junction_id: a str that represents the id of the junction.
        - neighbours: a list of Roads that represents the adjacent vertices.

    Representation Invariants:
        - len(self.junction_id.strip()) > 0
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

    vertices: dict[str, Vertex]
    roads: dict[str, Road]

    def __init__(self) -> None:
        """
        Initializes an empty graph (a graph with no vertices or edges).
        """
        self.vertices = {}
        self.roads = {}

    @check_contracts
    def compute_shortest_path(
            self, source_junction_id: str, target_junction_id: str
    ) -> Optional[ShortestPathResult]:
        """
        Compute and return the shortest paths between source junction id and target junction id and its length in
        metres. In case multiple shortest paths of same length exist, return all of them.
        In case the two vertices are disconnected, None is returned. See ShortestPathResult docstring
        for understanding what exactly the response of ShortestPathResult is composed of.

        A note on triviality and shortest path:
        Shortest path is any path with the shortest possible length from source_junction_id to
        target_junction_id, but we compare lengths by stripping the number of all its decimals. This
        helps ignore trivial differences in two paths (like two paths differing by just 0.1 m, so one of
        them counts as shortest while the other doesn't: this ignoring of decimals prevents this triviality
        from stopping the latter path as also being counted as a shortest path).

        This method uses a modified version of Dijktras algorithm to make it work for
        multiple shortest paths.

        Breaking up a doctest result which is too big for one line inspired by https://stackoverflow.com/a/13395612
        NOTE: Pycharm might highlight item loop variable in doctest as an unresolved reference, this is a false
        positive by Pycharm. So ignore it, and the doctest works fine.

        Preconditions:
            - source_junction_id in self.vertices and target_junction_id in self.vertices
            - source_junction_id != target_junction_id

        >>> graph: Graph = Graph()
        >>> for i in range(65, 70):
        ...     graph.add_junction(chr(i))
        >>> coordinates: list[tuple[float, float]] = [(78, 100), (79, 101)]
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
        [[('A', 'A->B_pos'), ('B', 'B->C_pos'), ('C', 'C->E_pos'), ('E', '')], [('A', 'A->B_pos'), ('B', 'B->D_pos'), \
('D', 'C->D_neg'), ('C', 'C->E_pos'), ('E', '')], [('A', 'A->B_pos'), ('B', 'B->D_pos'), ('D', 'D->E_pos'), \
('E', '')], [('A', 'A->D_pos'), ('D', 'C->D_neg'), ('C', 'C->E_pos'), ('E', '')], [('A', 'A->D_pos'), \
('D', 'D->E_pos'), ('E', '')]]
        >>> shortest_path_result.length
        9.0
        """

        # the dijktras code for this was inspired by https://cp-algorithms.com/graph/dijkstra.html, with major
        # changes to it to make it O(V + ElogE) where E is the number of edges and V the number of vertices,
        # to return shortest paths also and not only distance, and to make it
        # suitable for returning multiple shortest equivalent paths.
        visited: set[str] = set()
        all_shortest_paths_computed: set[str] = set()

        infinity: float = constants.INFINITY  # 1 billion km, Ontario road network
        # road length sum should and will not be that big

        # Note: we are using a list here instead of tuple, as we want to
        # be able to mutate the set and tuples are immutable.
        # This list (value of dictionary) follows the same structure as our
        # ShortestDistanceToVertex dataclass, with list length always being 3, and its elements
        # corresponding to ShortestDistanceToVertex's junction_id, shortest_distance_till_now and
        # shortest_paths_prev_vertex_ids respectively, and also follow the same representation
        # invariants as that dataclass. Why didn't we use that dataclass then? That's because
        # tuples/lists are faster than dataclass, and when I used that dataclass instead of what we have now
        # the code became approximately 20 times slower. This was quite significant for our code,
        # as we are working with over million edges and about half a million vertices, and
        # code becoming 20 times slower in Dijktras algorithm meant what would run here in 0.5 seconds
        # would take 10 seconds using dataclasses.
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
        # LenMinimizerCandidateRoads dataclass, with tuple length always being 4, and its elements
        # corresponding to LenMinimizerCandidateRoads's length_from_junction, start_junction_id,
        # end_junction_id and road id respectively, and this tuple's corresponding arguments follow the
        # same representation invariants as that dataclass. Why didn't we use that dataclass then? For the same
        # reason we didn't use dataclass for distance.
        len_minimizer_candidate_roads: list[tuple[float, str, str, str]] = []

        # heap related code adapted from https://docs.python.org/3/library/heapq.html
        # we are using a min heap because it is like a priority queue with push
        # Big O time and pop Big O time as O(log n) where n is the number of
        # elements inside it. See https://stackoverflow.com/a/38833175 for
        # time complexity of these heap methods
        heapify(len_minimizer_candidate_roads)

        source_vertex: Vertex = self.vertices[source_junction_id]
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

            if distance[current_vertex_id][1] < len_minimizer_candidate_road[0]:
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
                self._minimize_dist_to_neighbours(
                    all_shortest_paths_computed=all_shortest_paths_computed,
                    distance=distance,
                    len_minimizer_candidate_road=len_minimizer_candidate_road,
                    len_minimizer_candidate_roads=len_minimizer_candidate_roads,
                    current_vertex_id=current_vertex_id
                )

        return self._interpret_dijktras_results(
            source_junction_id=source_junction_id,
            target_junction_id=target_junction_id,
            distance=distance,
            infinity=infinity
        )

    def _minimize_dist_to_neighbours(self, all_shortest_paths_computed: set[str],
                                     distance: dict[str, list[str | float | set[tuple[str, str]]]],
                                     len_minimizer_candidate_roads: list[tuple[float, str, str, str]],
                                     len_minimizer_candidate_road: tuple[float, str, str, str],
                                     current_vertex_id: str) -> None:
        """
        Perform edge relaxation step of Dijktras for each road current_vertex_id is connected to, if
        it has not been soft deleted. This means that if the distance from current_vertex_id to the
        vertex id the road in consideration connects to can be minimized if current road is taken as
        compared to value in distance dictionary, then register this in distance dictionary at appropriate
        place and add the road to len_minimizer_candidate_roads heap (mutation). len_minimizer_candidate_road
        is the road that connects to current_vertex_id and is one of the neighbouring roads which minimized
        the distance the most among current_vertex_id's neighbours. Also, all_shortest_paths_computed
        is a set for whom all equal shortest paths have been found, so it would be used to make this
        method skip edge relaxation to vertices to whom already all shortest paths have been computed.

        For understanding how to declare complex parameters like distance and len_minimizer_candidate_roads and
        len_minimizer_candidate_road, check out these variable's descriptions in self.compute_shortest_path method.

        This is a mutating helper method.

        Preconditions:
            - current_vertex_id in self.vertices
            - the values in distance, len_minimizer_candidate_roads and len_minimizer_candidate_road follow
            the same format as described in self.compute_shortest_path where these variables were declared.
        """
        neighbours: list[Road] = self.vertices[current_vertex_id].neighbours

        for road in neighbours:
            if road.removed:
                # if road is soft deleted, don't add it as a potential minimizing candidate
                continue
            else:
                # relaxation step of Dijktras algorithm
                neighbour_junction: Vertex = road.to_junction
                neighbour_junction_id: str = neighbour_junction.junction_id

                # don't minimize distance for something already in all_shortest_paths_computed set, it
                # already has all possible shortest paths to it
                if neighbour_junction_id in all_shortest_paths_computed:
                    continue

                shortest_dist_till_now_info: list[str | float | set[str]] = distance[neighbour_junction_id]
                potentially_less_distance: float = len_minimizer_candidate_road[0] + road.length // 1.0
                # divide by 1.0 to ensure the result is a float and not an int and to strip decimals.

                if shortest_dist_till_now_info[1] >= potentially_less_distance:
                    shortest_dist_till_now_info[1] = potentially_less_distance

                    heappush(len_minimizer_candidate_roads, (
                        potentially_less_distance,
                        current_vertex_id,
                        neighbour_junction_id,
                        road.road_id,)
                    )

    def _interpret_dijktras_results(
            self,
            source_junction_id: str,
            target_junction_id: str,
            distance: dict[str, list[str | float | set[tuple[str, str]]]],
            infinity: float,
    ) -> Optional[ShortestPathResult]:
        """
        Return ShortestPathResult if source_junction_id and target_junction_id are not disconnected, otherwise
        return None. Use distance, which has been built due to Dijktras algorithm, and infinity which was
        what Dijktras algorithm used as its infinity value to achieve this.

        To understand more about what ShortestPathResult, see ShortestPathResult class' docstring.

        Preconditions:
            - source_junction_id in self.vertices
            - target_junction_id in self.vertices
            - the values in distance, as described in self.compute_shortest_path where this variable was declared.
            - Dijktras has been successfully run and has populated distance dictionary correctly.
            - infinity > 0
        """
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
            - source in self.vertices
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
        Soft remove a road from the graph by marking its remove attribute as removed
        If the road does not exist in the graph, the function does nothing

        Preconditions:
            - len(road_id) >= 0

        """
        if road_id in self.roads:
            road: Road = self.roads[road_id]
            road.removed = True

    def restore_removed_roads(self) -> None:
        """
        Restore all roads which were soft deleted.

        Preconditions:
            - self.roads has been initialized
        """
        roads: dict[str, Road] = self.roads
        for road_id in roads:
            roads[road_id].removed = False

    def add_road(self, from_junction_id: str, to_junction_id: str, length: float, road_id: str,
                 removed: bool, geometry: list[tuple[float, float]]) -> None:
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
            junction1: Vertex = self.vertices[from_junction_id]
            junction2: Vertex = self.vertices[to_junction_id]
            self.roads[road_id] = Road(junction1, junction2, length, road_id,
                                       removed, geometry)

            junction1.neighbours.append(self.roads[road_id])

    def add_bidirectional_roads(self, from_junction_id: str, to_junction_id: str, length: float, road_id: str,
                                removed: bool, geometry: list[tuple[float, float]]) -> None:
        """
        Create a road from from_junction_id to to_junction_id and vice versa and
        add it to self.roads. If any of the roads already exists, the method does nothing and adds only the
        one not existing if any.

        Preconditions:
            - from_junction_id in self.vertices
            - to_junction_id in self.vertices
            - length >= 0
            - len(road_id.strip()) >= 0
        """
        self.add_road(
            from_junction_id, to_junction_id, length,
            f'{road_id}{constants.ROAD_POSITIVE_SUFFIX}', removed, geometry)
        self.add_road(
            to_junction_id, from_junction_id, length,
            f'{road_id}{constants.ROAD_NEGATIVE_SUFFIX}', removed, geometry)

    def add_junction(self, junction_id: str) -> None:
        """
        Map junction_id to a new _Vertex and add it to the mapping self.vertices. If junction_id already exists
        in self.vertices, the method does nothing.

        Preconditions:
            - len(junction_id.strip()) > 0
        """

        if junction_id not in self.vertices:
            self.vertices[junction_id] = Vertex(junction_id, [])

    def is_valid_road_selection(self, road_ids: list[str]) -> Optional[tuple[str, str]]:
        """
        Return a tuple of the starting junction id and the ending junction id if there is a connected valid path,
        otherwise return None.

        A valid path is defined as a set of roads such that there exists only 1 start point for the path and
        only one endpoint for the path, and if there are more than one paths that are disconnected, then only
        1 path has the start and end points (the other path(s) are a cycle entirely)

        Preconditions:
            - len(road_ids) >= 0
            - all({road_id in self.roads for road_id in road_ids})

        """
        if len(road_ids) == 0:
            return None

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
            return None

        return free_starts[0], free_ends[0]


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['path_tree', 'constants', 'heapq'],
    })
