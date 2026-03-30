"""
Ontario Road Closure Analysis App
================================

This file contains code for the service class of this project RoadManager, whose job
is to facilitate between Graph Domain level (Domain term from Uncle Bob) class and
StreamlitManager boundary class.
"""
import doctest
from typing import Optional

from graph import Graph, ShortestPathResult, Road
from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState
import constants


class RoadManager:
    """
    A service class that indirectly manages the road network graph. This is a service class,
    meaning that it orchestrates and mediates between the boundary class
    (meaning class user directly interacts with) of StreamlitManager
    and entity class (meaning a low level domain (from Uncle Bob's concepts)
    class) of Graph

    Instance Attributes:
        - graph: a Graph instance that represents the Ontario road network.

    Representation Invariants:
        - self.graph represents the road network loaded from our Ontario Road Network data file
    """
    graph: Graph

    def __init__(self) -> None:
        """
        Initialize RoadManager with empty graph.

        There are no preconditions to use this constructor
        """
        self.graph = Graph()

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> bool:
        """
        Fetch and build the road network graph using data_loader, and return if the graph
        was fetched and built successfully or not.

        There are no preconditions to use this method.
        """
        result: DataLoadState = data_loader.load()

        if not isinstance(result, DataLoadSuccessState):
            return False

        graph: Graph = self.graph
        features: list = result.data['features']

        for feature in features:
            attributes: dict = feature['attributes']
            from_id: str = str(attributes['FROM_JUNCTION_ID'])
            to_id: str = str(attributes['TO_JUNCTION_ID'])
            length: float = attributes['LENGTH']
            road_id: str = str(attributes['OGF_ID'])
            direction: str = attributes['DIRECTION_OF_TRAFFIC_FLOW']
            # using tuples instead of Coordinate reduced our time for this operation about 1.4 times faster,
            # which is quite significant as we are iterating over 600_000 times
            polyline: list[tuple[float, float]] = feature['geometry']['paths'][0]

            graph.add_junction(from_id)
            graph.add_junction(to_id)

            pos_suffix: str = constants.ROAD_POSITIVE_SUFFIX
            neg_suffix: str = constants.ROAD_NEGATIVE_SUFFIX

            if direction == 'Both':
                graph.add_road(from_junction_id=from_id, to_junction_id=to_id,
                               length=length, road_id=f'{road_id}{pos_suffix}',
                               removed=False, geometry=polyline)
                graph.add_road(from_junction_id=to_id, to_junction_id=from_id,
                               length=length, road_id=f'{road_id}{neg_suffix}',
                               removed=False, geometry=polyline[::-1])
            elif direction == 'Positive':
                graph.add_road(from_junction_id=from_id, to_junction_id=to_id,
                               length=length, road_id=f'{road_id}{pos_suffix}',
                               removed=False, geometry=polyline)
            elif direction == 'Negative':
                graph.add_road(from_junction_id=to_id, to_junction_id=from_id, length=length,
                               road_id=f'{road_id}{neg_suffix}',
                               removed=False, geometry=polyline[::-1])

        return True

    def restore_removed_roads(self) -> None:
        """
        Restore all roads which were soft deleted.

        Preconditions:
            - self.graph has been initialized
        """
        self.graph.restore_removed_roads()

    def remove_road_and_get_path(
            self, road_ids: list[str], source_junction_id: str, target_junction_id: str
    ) -> Optional[ShortestPathResult]:
        """
        Remove all roads in roads_id (soft delete), and return ShortestPathResult after running
        get_shortest_path or None if the junctions get disconnected after road removal.

        Preconditions:
            - self.graph has been initialized
            - len(road_ids) > 0
            - source_junction_id in self.graph.vertices
            - target_junction_id in self.graph.vertices
            - source_junction_id != target_junction_id
        """
        for road_id in road_ids:
            self.graph.remove_road(road_id)

        return self.get_shortest_path(source_junction_id, target_junction_id)

    def get_shortest_path(self, source_junction_id: str, target_junction_id: str) -> Optional[ShortestPathResult]:
        """
        Return ShortestPathResult with all shortest paths and shortest path length if
        source_junction_id and target_junction_id are connected, otherwise return None.

        Preconditions:
            - self.graph has been initialized
            - source_junction_id in self.graph.vertices
            - target_junction_id in self.graph.vertices
            - source_junction_id != target_junction_id
        """
        return self.graph.compute_shortest_path(source_junction_id, target_junction_id)

    def check_removability(self, roads: list[str]) -> Optional[tuple[str, str]]:
        """
        Return a tuple if all roads satisfy the condition in
        self.graph.is_valid_road_selection method (see its docstring for details) or None if
        they don't. The tuple returned would have its first element as the start junction id
        and second element as end junction id, where start and end are determined from the free
        ends of the sequence of roads. See the aforementioned method for details.

        Preconditions:
            - len(roads) >= 2
        """
        return self.graph.is_valid_road_selection(roads)

    def get_roads(self) -> dict[str, Road]:
        """
        Return self.graph's roads. This is a small helper method.

        Preconditions:
            - self.graph has been initialized
        """
        return self.graph.roads


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['heapq', 'constants', 'graph', 'data_load_state', 'data_loader'],
    })
