import time

from fast_file_loader import FastFileLoader
from typing import Optional

from graph import Graph, ShortestPathResult, Road
from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState


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
        self.fetch_data_and_build_graph(FastFileLoader('data/ontario_road_network.geojson'))
        # TODO: replace with constant from constants.py

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> None:
        """
        Fetch and build the road network graph using data_loader.

        There are no preconditions to use this function
        """
        start_time_all: float = time.perf_counter()

        print('Starting data load')
        load_time_start: float = time.perf_counter()

        result: DataLoadState = data_loader.load()

        if not isinstance(result, DataLoadSuccessState):
            print('Failed to load Ontario road network data.')
            return

        print(f'Data loaded in {time.perf_counter() - load_time_start}')

        start_time: float = time.perf_counter()

        data: dict = result.data
        graph: Graph = self.graph
        features: list = data['features']
        coordinates_length: int = 0

        time_delta_2: float = 0
        time_delta_3: float = 0
        time_delta_4: float = 0
        time_delta_5: float = 0

        for feature in features:
            time_start_4: float = time.perf_counter()
            attributes: dict = feature['attributes']
            from_id: str = str(attributes['FROM_JUNCTION_ID'])
            to_id: str = str(attributes['TO_JUNCTION_ID'])
            length: float = attributes['LENGTH']
            road_id: str = str(attributes['OGF_ID'])
            direction: str = attributes['DIRECTION_OF_TRAFFIC_FLOW']
            # using tuples instead of Coordinate reduced our time for this operation about 1.4 times faster,
            # which is quite significant as we are iterating over 600_000 times
            polyline: list[tuple[float, float]] = feature['geometry']['paths'][0]

            time_start_5: float = time.perf_counter()
            geometry: list[tuple[float, float]] = polyline

            coordinates_length += len(polyline)
            time_delta_5 += (time.perf_counter() - time_start_5)

            time_delta_4 += (time.perf_counter() - time_start_4)
            time_start_2: float = time.perf_counter()

            graph.add_junction(from_id)
            graph.add_junction(to_id)

            time_delta_2 += (time.perf_counter() - time_start_2)

            time_start_3: float = time.perf_counter()

            if direction == 'Both':
                graph.add_road(from_junction_id=from_id, to_junction_id=to_id, length=length, road_id=f'{road_id}_pos',
                               removed=False, geometry=geometry)
                graph.add_road(from_junction_id=to_id, to_junction_id=from_id, length=length, road_id=f'{road_id}_neg',
                               removed=False, geometry=geometry[::-1])
            elif direction == 'Positive':
                graph.add_road(from_junction_id=from_id, to_junction_id=to_id, length=length, road_id=f'{road_id}_one',
                               removed=False, geometry=geometry)
            elif direction == 'Negative':
                # TODO: check if geometry reveral is fine or not
                graph.add_road(from_junction_id=to_id, to_junction_id=from_id, length=length, road_id=f'{road_id}_one',
                               removed=False, geometry=geometry[::-1])
            else:
                print(f'Unknown direction value: {direction} for road {road_id}')

            time_delta_3 += (time.perf_counter() - time_start_3)

        end_time: float = time.perf_counter()

        print(f'Whole of graph built in {end_time-start_time} seconds overall. add_junction method took {time_delta_2} seconds, and add_road method took {time_delta_3} seconds. The attribute extraction took {time_delta_4} seconds.')
        print(f'The whole fetch_data_and_build_graph method took {time.perf_counter() - start_time_all}')
        print(f'The geometry loop took {time_delta_5} seconds, and we had {coordinates_length} coordinates in total')

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

    def check_removability(self, roads: list[str]) -> tuple[bool, list[str]]:
        return self.graph.is_valid_road_selection(roads)
