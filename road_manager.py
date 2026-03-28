from typing import Optional

from graph import Graph, ShortestPathResult
from data_loader import DataLoader
from road import Road


class RoadManager:
    graph: Graph

    def __init__(self) -> None:
        pass

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> None:
        pass

    def remove_road_and_get_path(
            self, road_ids: list[str], source_junction_id: str, target_junction_id: str
    ) -> Optional[ShortestPathResult]:
        """
        Remove all roads in roads_id, and return a list of roads which make the shortest path from
        source_junction_id to target_junction_id.

        Preconditions:
            - len(road_ids) > 0
            - source_junction_id in self.graph.vertices
            - target_junction_id in self.graph.vertices
            - source_junction_id != target_junction_id
        """
        for road_id in road_ids:
            self.graph.remove_road(road_id)

        return self.graph.compute_shortest_path(source_junction_id, target_junction_id)

    def check_removability(self, roads: list[Road]) -> bool:
        pass
