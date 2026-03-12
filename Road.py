from dataclasses import dataclass
from Coordinate import Coordinate
from Graph import _Vertex


@dataclass
class Road:
    from_junction: _Vertex
    to_junction: _Vertex
    length: float
    road_id: str
    removed: bool
    geometry: list[Coordinate]

