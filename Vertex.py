from dataclasses import dataclass
from Road import Road


@dataclass
class _Vertex:
    neighbours: list[Road]
    junction_id: str
