from graph import Graph, Road
from typing import Optional

from graph import Graph, ShortestPathResult
from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState
from coordinate import Coordinate
from file_loader import FileLoader


class RoadManager:
    """
    A class that manages the road network graph. This is a service class,
    meaning that it orchestrates and mediates between the boundary class
    (meaning class user directly interacts with) of StreamlitManager
    and entity class (meaning a low level domain (from Uncle Bob's concepts
    class) of Graph

    Instance Attributes:
        - graph: a Graph instance that represents the Ontario road network.

    Representation Invariants:
        - self.graph is not None
    """
    graph: Graph

    def __init__(self) -> None:
        """
        Initialize RoadManager with the Ontario road network data.
        """
        self.graph = Graph()
        self.fetch_data_and_build_graph(FileLoader('data/ontario_road_network.geojson.gz'))
        # TODO: replace with constant from constants.py

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> None:
        """
        Fetch and build the road network graph using data_loader.

        There are no preconditions to use this function
        """
        result: DataLoadState = data_loader.load()

        if not isinstance(result, DataLoadSuccessState):
            print('Failed to load Ontario road network data.')
            return

        data: dict = result.data
        graph: Graph = self.graph

        for feature in data['features']:
            attributes: dict = feature['attributes']
            from_id: str = str(attributes['FROM_JUNCTION_ID'])
            to_id: str = str(attributes['TO_JUNCTION_ID'])
            length: float = attributes['LENGTH']
            road_id: str = str(attributes['OGF_ID'])
            direction: str = attributes['DIRECTION_OF_TRAFFIC_FLOW']
            geometry: list[Coordinate] = [Coordinate(coordinate[1], coordinate[0]) for coordinate in
                                          feature['geometry']['paths'][0]]

            graph.add_junction(from_id)
            graph.add_junction(to_id)

            if direction == 'Both':
                graph.add_road(from_junction_id=from_id, to_junction_id=to_id, length=length, road_id=f'{road_id}_pos',
                               removed=False, geometry=geometry)
                graph.add_road(from_junction_id=to_id, to_junction_id=from_id, length=length, road_id=f'{road_id}_neg',
                               removed=False, geometry=geometry[::-1])
            elif direction == 'Positive':
                graph.add_road(from_junction_id=from_id, to_junction_id=to_id, length=length, road_id=road_id,
                               removed=False, geometry=geometry)
            elif direction == 'Negative':
                graph.add_road(from_junction_id=to_id, to_junction_id=from_id, length=length, road_id=road_id,
                               removed=False, geometry=geometry[::-1])
            else:
                print(f'Unknown direction value: {direction} for road {road_id}')

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
