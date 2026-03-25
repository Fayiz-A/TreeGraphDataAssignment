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

    def is_valid_path(self, road_ids: list[str]) -> bool:
        """
        Return true if there is a connected valid path, that is, there exists only 1 start point for the path and
        only one endpoint for the path.

        Preconditions:
            - len(road_ids) >= 0
            - all({road_id in self.roads for road_id in road_ids})

        """

        if len(road_ids) == 0:
            return False

        num_starts = set()
        num_ends = set()

        for road_id in road_ids:
            road: Road = self.roads[road_id]

            start: str = road.from_junction.junction_id
            end: str = road.to_junction.junction_id

            num_starts.add(start)
            num_ends.add(end)

        start_options: list[str] = [r for r in num_starts if r not in num_ends]
        end_options: list[str] = [r for r in num_ends if r not in num_starts]

        if len(start_options) != 1 or len(end_options) != 1:
            return False

        visited = set()
        stack: list[str] = [road_ids[0]]

        while len(stack) > 0:
            current: str = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            current_road: Road = self.roads[current]

            for other in road_ids:
                if other in visited:
                    continue

                other_road: Road = self.roads[other]

                if (current_road.to_junction == other_road.from_junction or
                        current_road.from_junction == other_road.to_junction or
                        current_road.from_junction == other_road.from_junction or
                        current_road.to_junction == other_road.to_junction):
                    stack.append(other)

        return len(visited) == len(road_ids)
