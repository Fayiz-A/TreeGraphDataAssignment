from coordinate import Coordinate
from info_display import InfoDisplayState
from road import Road
from road_manager import RoadManager
from ui_road import UIRoad


class StreamlitManager:
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, UIRoad]
    AVERAGE_LENGTH: float
    MAX_ZOOM: int = 19
    _info_display_state: InfoDisplayState

    def __init__(self) -> None:

        total_length: float = 0
        for key in self._roads:
            ui_road: UIRoad = self._roads[key]
            length: float = ui_road.road.length
            total_length += length

        if len(self._roads) > 0:
            self.AVERAGE_LENGTH = total_length / len(self._roads)
        else:
            self.AVERAGE_LENGTH = 0

    def _handle_road_removal(self) -> None:
        pass

    def _get_road_id_by_selection(self, point: Coordinate) -> UIRoad | None:
        pass

    def _update_visible_roads_by_bounds(self, zoom_level: int, bounds: tuple[Coordinate, Coordinate]) -> None:
        """
        Updates the map zoom level to the given zoom level and updates the visible roads. If the zoom level
        will be updated to 0, all the roads should be visible.

        Preconditions:
            - 0 <= zoom_level <= 19
        """
        if zoom_level == 0:
            for ui_road in self._roads.values():
                ui_road.visible = True
            return

        length_bound: float = (self.MAX_ZOOM - zoom_level + 1) * self.AVERAGE_LENGTH

        max_longitude: float = max(bounds[0].longitude, bounds[1].longitude)
        min_longitude: float = min(bounds[0].longitude, bounds[1].longitude)
        max_latitude: float = max(bounds[0].latitude, bounds[1].latitude)
        min_latitude: float = min(bounds[0].latitude, bounds[1].latitude)

        for ui_road in self._roads.values():
            road: Road = ui_road.road
            length: float = road.length

            length_check: bool = length <= length_bound
            bounds_check: bool = True

            for coord in road.geometry:
                if not (min_latitude <= coord.latitude <= max_latitude and
                        min_longitude <= coord.longitude <= max_longitude):
                    bounds_check = False
                    break

            ui_road.visible = length_check and bounds_check

    def reset(self) -> None:
        pass

    def display(self) -> None:
        pass
