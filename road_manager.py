from graph import Graph
from data_loader import DataLoader
from road import Road


class RoadManager:
    graph: Graph

    def __init__(self) -> None:
        pass

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> None:
        pass

    def remove_road_and_get_path(self, road_ids: list[str], source_junction: str, target_junction: str) -> list[Road]:
        """
        Removes all roads in roads_id, and returns a list of roads which make the shortest path from
        source_junction to target_junction.

        Preconditions:
            - len(road_ids) > 0
            - source_junction is a valid junction represented by a string.
            - target_junction is a valid junction represented by a string.
        """
        for road_id in road_ids:
            self.graph.remove_road(road_id)

        return self.graph.compute_shortest_path(source_junction, target_junction)

    def check_removability(self, roads: list[Road]) -> bool:
        pass
