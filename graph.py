from __future__ import annotations

from heapq import heapify, heappop, heappush
from typing import Optional

from python_ta.contracts import check_contracts

from dataclasses import dataclass
from coordinate import Coordinate
from tree import Tree


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
    def compute_shortest_path(self, source_junction_id: str, target_junction_id: str) ->\
            Optional[tuple[Tree, float]]:
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
        >>> graph.add_bidirectional_roads('A', 'B', 1, 'AB', False, coordinates)
        >>> graph.add_bidirectional_roads('A', 'D', 10, 'AD', False, coordinates)
        >>> graph.add_bidirectional_roads('B', 'C', 2, 'BC', False, coordinates)
        >>> graph.add_bidirectional_roads('B', 'D', 8, 'BD', False, coordinates)
        >>> graph.add_bidirectional_roads('E', 'D', 1, 'ED', False, coordinates)
        >>> graph.add_bidirectional_roads('D', 'C', 1, 'DC', False, coordinates)
        >>> graph.add_bidirectional_roads('A', 'E', 7, 'AE', False, coordinates)
        >>> shortest_path_result = graph.compute_shortest_path_heap('A', 'D')
        >>> (shortest_path_result[0].get_values()[::-1], shortest_path_result[1])
        (['A', 'B', 'C', 'D'], 4.0)
        """
        visited: set[str] = set()
        infinity: float = 100_000_000_000.0  # 100 million km, no road segment could be
        # that big without a junction being somewhere
        distance: dict[str, tuple[Optional[_Vertex], float]] = {}

        for vertex in self.vertices:
            if vertex == source_junction_id:
                distance[vertex] = (self.vertices[vertex], 0)
            else:
                distance[vertex] = (None, infinity)

        road_distance_list: list[tuple[float, _Vertex]] = []

        # heap related code adapted from https://docs.python.org/3/library/heapq.html
        heapify(road_distance_list)

        source_vertex: _Vertex = self.vertices[source_junction_id]

        heappush(road_distance_list, (0, source_vertex))

        while len(road_distance_list) > 0:
            least_distance_road: tuple[float, _Vertex] = heappop(road_distance_list)

            current_vertex: _Vertex = least_distance_road[1]
            current_vertex_id: str = current_vertex.junction_id

            visited.add(current_vertex_id)

            if current_vertex_id == target_junction_id:
                #  Dijktras guarantees that if mark a vertex as visited, then it has the shortest path already
                break
            else:
                neighbours: list[Road] = current_vertex.neighbours

                for road in neighbours:
                    neighbour_junction: _Vertex = road.to_junction
                    neighbour_junction_id: str = neighbour_junction.junction_id

                    # don't minimize distance for something already in visited set, it already has the shortest
                    # distance
                    if neighbour_junction_id not in visited:
                        distance_min_candidate: tuple[_Vertex, float] = distance[neighbour_junction_id]
                        potentially_less_distance: float = least_distance_road[0] + road.length * 1.0
                        # multiply by 1.0 to ensure the result is a float and not an int

                        if distance_min_candidate[1] > potentially_less_distance:

                            distance[neighbour_junction_id] = (current_vertex, potentially_less_distance)

                            heappush(road_distance_list, (distance[neighbour_junction_id][1], neighbour_junction))

        shortest_path_info: tuple[Optional[_Vertex], float] = distance[target_junction_id]
        shortest_path_node: Optional[_Vertex] = shortest_path_info[0]

        if shortest_path_node is not None:
            tree: Tree = Tree(target_junction_id)
            subtree: Optional[Tree] = None

            while shortest_path_node.junction_id != distance[shortest_path_node.junction_id][0].junction_id:
                subtree_to_add: Tree = Tree(shortest_path_node.junction_id)
                if subtree is None:
                    # we got into this loop for the first time
                    tree.add_subtree(subtree_to_add)
                else:
                    subtree.add_subtree(subtree_to_add)

                subtree = subtree_to_add

                junction_id: str = shortest_path_node.junction_id

                shortest_path_node = distance[junction_id][0]  # this gives us what vertex was the one
                # from which we marked as visited our junction_id vertex (meaning shortest path to it was found)
                # this shortest_path_node vertex is the last vertex before junction_id in one of the shortest
                # paths, which is what we currently support only for now

            if subtree is None:
                # we got into this loop for the first time
                tree.add_subtree(Tree(source_junction_id))
            else:
                subtree.add_subtree(Tree(source_junction_id))

            shortest_path_length: float = shortest_path_info[1]

            return tree, shortest_path_length
        else:
            print('target junction id is disconnected')
            return None

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
