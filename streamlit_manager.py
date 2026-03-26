from coordinate import Coordinate
from info_display import InfoDisplayState, InfoDisplayInitState
from road_manager import RoadManager
from ui_road import UIRoad


class StreamlitManager:
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, UIRoad]
    _info_display_state: InfoDisplayState

    def __init__(self) -> None:
        self._road_manager = RoadManager()
        self._roads = {road_id: UIRoad(road=road, visible=True, colour='blue')
                       for road_id, road in self._road_manager.graph.roads.items()}
        self._selected_roads = {}
        self._info_display_state = InfoDisplayInitState()
        self._update_visible_roads_by_bounds(
            zoom_level=14,
            bounds=(Coordinate(43.68984603369737, -79.36489105224611),
                    Coordinate(43.64638600677007, -79.42711830139162))
        )

    def _handle_road_removal(self) -> None:
        pass

    def _get_road_id_by_selection(self, point: Coordinate) -> UIRoad | None:
        pass

    def _update_visible_roads_by_bounds(self, zoom_level: int, bounds: tuple[Coordinate, Coordinate]) -> None:
        pass

    def reset(self) -> None:
        pass

    def display(self) -> None:
        pass
