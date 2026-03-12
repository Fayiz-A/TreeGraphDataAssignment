from dataclasses import dataclass
from Vertex import _Vertex


@dataclass
class Road:
    form_junction: _Vertex
    to_junction: _Vertex
    length: float
    road_id: str
    removed: bool
