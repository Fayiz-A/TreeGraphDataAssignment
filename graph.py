from dataclasses import dataclass
from coordinate import Coordinate
from road import Road


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

    def compute_shortest_path(self, source_junction_id: str, target_junction_id: str) -> list[Road]:
        pass

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
