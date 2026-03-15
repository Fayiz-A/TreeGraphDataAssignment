from Graph import Graph
from DataLoader import DataLoader
from Road import Road


class RoadManager:
    _graph: Graph

    def __init__(self) -> None:

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> None:

    def remove_road_and_get_path(self, road_id: str) -> list[Road]:

    def check_removability(self, roads: list[Road]) -> bool:
