from graph import Graph, Road
from data_loader import DataLoader


class RoadManager:
    _graph: Graph

    def __init__(self) -> None:
        pass

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> None:
        pass

    def remove_road_and_get_path(self, road_id: str) -> list[Road]:
        pass

    def check_removability(self, roads: list[Road]) -> bool:
        pass
