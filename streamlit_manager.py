from coordinate import Coordinate
from info_display import InfoDisplayState, InfoDisplayInitState
from road_manager import RoadManager
from ui_road import UIRoad
import constants
from graph import Road
from shapely.geometry import MultiLineString, Point


class StreamlitManager:
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, UIRoad]
    _road_average_length: float
    _info_display_state: InfoDisplayState

    def __init__(self) -> None:
        """
        Initialize StreamlitManager with the Ontario road network data and default display settings.
        """
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

        total_length: float = 0
        for key in self._roads:
            ui_road: UIRoad = self._roads[key]
            length: float = ui_road.road.length
            total_length += length

        if len(self._roads) > 0:
            self._road_average_length = total_length / len(self._roads)
        else:
            self._road_average_length = 0

    def _handle_road_removal(self) -> None:
        pass

    def _get_road_id_by_selection(self, point: Coordinate) -> UIRoad | None:
        """
        Return the UIRoad whose geometric polyline is within a threshold distance
        from the given point, or None if no visible road is close enough.

        Preconditions:
            - isinstance(point, Coordinate)
        """
        threshold: float = 0.0005  # TODO: adjust after testing
        point_shape: Point = Point(point.latitude, point.longitude)

        for ui_road in self._roads.values():
            if not ui_road.visible:
                continue

            road: Road = ui_road.road
            path: list[tuple[float, float]] = [(coordinate.latitude, coordinate.longitude)
                                               for coordinate in road.geometry]
            multiline: MultiLineString = MultiLineString([path])

            if point_shape.distance(multiline) < threshold:
                return ui_road

        return None

    def _update_visible_roads_by_bounds(self, zoom_level: int, bounds: tuple[Coordinate, Coordinate]) -> None:
        """
        Update the visible roads according to the given zoom level, the road will be invisible if all portions are
        not in the current bounds or the road length is too minor to display. If the zoom level given is equal
        to or greater than 13, all the roads should be visible that pass the aforementioned bound check.

        Preconditions:
            - 0 <= zoom_level <= constants.MAX_ZOOM
        """
        length_bound: float = (constants.MAX_ZOOM - zoom_level + 1) * self._road_average_length

        northeast_candidate: Coordinate = bounds[0]
        southwest_candidate: Coordinate = bounds[1]
        longitudes: tuple[float, float] = (northeast_candidate.longitude, southwest_candidate.longitude)
        latitudes: tuple[float, float] = (northeast_candidate.latitude, southwest_candidate.latitude)

        max_longitude: float = max(longitudes)
        min_longitude: float = min(longitudes)
        max_latitude: float = max(latitudes)
        min_latitude: float = min(latitudes)

        for ui_road in self._roads.values():
            road: Road = ui_road.road
            length: float = road.length

            # ignore how big or small a road is if the user is zoomed in enough, and thus show all roads
            # that pass the bounds check
            length_check_passed: bool = zoom_level >= constants.BIG_ENOUGH_ZOOM_THRESHOLD or length >= length_bound
            bounds_check_passed: bool = False

            if length_check_passed:
                for coord in road.geometry:
                    if (min_latitude <= coord.latitude <= max_latitude and
                            min_longitude <= coord.longitude <= max_longitude):
                        bounds_check_passed = True
                        break

            ui_road.visible = length_check_passed and bounds_check_passed

    def reset(self) -> None:
        pass

    def display(self) -> None:
        pass
