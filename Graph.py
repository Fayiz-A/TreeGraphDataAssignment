from dataclasses import dataclass
from Coordinate import Coordinate
from Road import Road


@dataclass
class _Vertex:
    neighbours: list[Road]
    junction_id: str


class Graph:
    vertices: dict[str, _Vertex]
    roads: dict[str, Road]

    def __init__(self) -> None:

    def compute_shortest_path(self, source_junction_id, target_junction_id) -> list[Road]:

    def remove_road(self, road_id: str) -> None:

    def add_road(self, from_junction_id: str, to_junction_id: str, length: float, road_id: str,
                 removed: bool, geometry: list[Coordinate]) -> None:

    def add_junction(self, junction_id: str) -> None:

    def check_is_neighbour(self, road_id_1: str, road_id_2: str) -> bool:
