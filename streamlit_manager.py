import constants
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
        Update the visible roads according to the given zoom level, the road will be invisible if all portions are
        not in the current bounds or the road length is too minor to display. If the zoom level given is equal
        to or greater than 13, all the roads should be visible.

        Preconditions:
            - 0 <= zoom_level <= constants.MAX_ZOOM
        """
        if zoom_level >= 13:
            for ui_road in self._roads.values():
                ui_road.visible = True
            return

        length_bound: float = (constants.MAX_ZOOM - zoom_level + 1) * self.AVERAGE_LENGTH

        northeast_candidate: Coordinate = bounds[0]
        southwest_candidate: Coordinate = bounds[1]

        max_longitude: float = max(northeast_candidate.longitude, southwest_candidate.longitude)
        min_longitude: float = min(northeast_candidate.longitude, southwest_candidate.longitude)
        max_latitude: float = max(northeast_candidate.latitude, southwest_candidate.latitude)
        min_latitude: float = min(northeast_candidate.latitude, southwest_candidate.latitude)

        for ui_road in self._roads.values():
            road: Road = ui_road.road
            length: float = road.length

            length_check: bool = length >= length_bound
            bounds_check: bool = False

            if length_check:
                for coord in road.geometry:
                    if (min_latitude <= coord.latitude <= max_latitude and
                            min_longitude <= coord.longitude <= max_longitude):
                        bounds_check = True
                        break

            ui_road.visible = length_check and bounds_check

    def reset(self) -> None:
        pass

    def display(self) -> None:
        pass
