from graph import Graph
from data_loader import DataLoader
from data_load_state import DataLoadSuccessState
from road import Road
from coordinate import Coordinate


class RoadManager:
    _graph: Graph

    def __init__(self) -> None:
        self._graph = Graph()

    def fetch_data_and_build_graph(self, data_loader: DataLoader) -> None:
        """
        Fetches the road network data using data_loader and builds the graph.
        """
        result = data_loader.load()

        if not isinstance(result, DataLoadSuccessState):
            return

        data = result.data
        for feature in data['features']:
            attributes = feature['attributes']
            from_id = str(attributes['FROM_JUNCTION_ID'])
            to_id = str(attributes['TO_JUNCTION_ID'])
            length = attributes['LENGTH']
            road_id = str(attributes['OGF_ID'])
            direction = attributes['DIRECTION_OF_TRAFFIC_FLOW']
            geometry = [Coordinate(pt[1], pt[0]) for path in feature['geometry']['paths'] for pt in path]

            self._graph.add_junction(from_id)
            self._graph.add_junction(to_id)

            if direction == 'Both':
                self._graph.add_road(from_id, to_id, length, road_id + '_pos', False, geometry)
                self._graph.add_road(to_id, from_id, length, road_id + '_neg', False, geometry[::-1])
            elif direction == 'Positive':
                self._graph.add_road(from_id, to_id, length, road_id, False, geometry)
            elif direction == 'Negative':
                self._graph.add_road(to_id, from_id, length, road_id, False, geometry[::-1])

    def remove_road_and_get_path(self, road_id: str) -> list[Road]:
        pass

    def check_removability(self, roads: list[Road]) -> bool:
        pass
