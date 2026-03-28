"""
TODO: add docstring
"""
import doctest
import pprint
from typing import Any

from streamlit import cache_data, cache_resource, session_state

from coordinate import Coordinate
from info_display import InfoDisplayState, InfoDisplayInitState
from road_manager import RoadManager
from ui_road import UIRoad

import streamlit_folium
import folium
import constants
from graph import Road
from shapely.geometry import MultiLineString, Point


class StreamlitManager:
    """
    TODO: add docstring and representation invariants
    """
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, UIRoad]
    _road_average_length: float
    _info_display_state: InfoDisplayState
    _default_session_state_dict: dict[str, Any]

    def __init__(self) -> None:
        """
        Initialize StreamlitManager with the Ontario road network data and default display settings.
        """
        self._default_session_state_dict = {
            'map_info': {
                "last_clicked": None,
                "last_object_clicked": None,
                "last_object_clicked_tooltip": None,
                "last_object_clicked_popup": None,
                "all_drawings": None,
                "last_active_drawing": None,
                "bounds": {
                    "_southWest": {"lat": 43.64638600677007, "lng": -79.42711830139162},
                    "_northEast": {"lat": 43.68984603369737, "lng": -79.36489105224611}
                },
                "zoom": 13,
                "last_circle_radius": None,
                "last_circle_polygon": None,
                "center": {"lat": 43.66638600677007, "lng": -79.49711830139162},
                "selected_layers": []
            }
        }

        self._road_manager = RoadManager()
        self._roads = {road_id: UIRoad(road=road, visible=True, colour='blue')
                       for road_id, road in self._road_manager.graph.roads.items()}
        self._selected_roads = {}
        self._info_display_state = InfoDisplayInitState()

        total_length: float = 0
        for key in self._roads:
            ui_road: UIRoad = self._roads[key]
            length: float = ui_road.road.length
            total_length += length

        if len(self._roads) > 0:
            self._road_average_length = total_length / len(self._roads)
        else:
            self._road_average_length = 0

        self._update_visible_roads_by_bounds(
            zoom_level=13,
            bounds=(Coordinate(43.68984603369737, -79.36489105224611),
                    Coordinate(43.64638600677007, -79.42711830139162))
        )

        self._update_state('map', self._build_folium_map((Coordinate(43.68984603369737, -79.36489105224611),
                    Coordinate(43.64638600677007, -79.42711830139162)), 13))

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

    def _update_visible_roads_by_bounds(_self, zoom_level: int, bounds: tuple[Coordinate, Coordinate]) -> None:
        """
        Update the visible roads according to the given zoom level, the road will be invisible if all portions are
        not in the current bounds or the road length is too minor to display. If the zoom level given is equal
        to or greater than 13, all the roads should be visible that pass the aforementioned bound check.

        Preconditions:
            - 0 <= zoom_level <= constants.MAX_ZOOM

        TODO: explain why _self not self; and why bounds and zoom not used
        """
        length_bound: float = (constants.MAX_ZOOM - zoom_level + 1) * _self._road_average_length

        northeast_candidate: Coordinate = bounds[0]
        southwest_candidate: Coordinate = bounds[1]
        longitudes: tuple[float, float] = (northeast_candidate.longitude, southwest_candidate.longitude)
        latitudes: tuple[float, float] = (northeast_candidate.latitude, southwest_candidate.latitude)

        max_longitude: float = max(longitudes)
        min_longitude: float = min(longitudes)
        max_latitude: float = max(latitudes)
        min_latitude: float = min(latitudes)

        total: int = 0
        for ui_road in _self._roads.values():
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
            if ui_road.visible:
                total += 1

        print(f'Total visible roads now: {total} as per bounds {bounds}')

    def reset(self) -> None:
        """
        Reset StreamlitManager to its initial state by clearing selections,
        rebuilding the roads, and restoring the default display settings.

        Preconditions:
            - self._roads and self._selected_roads are initialized
        """
        self._selected_roads.clear()

        self._roads = {road_id: UIRoad(road=road, visible=True, colour='blue')
                       for road_id, road in self._road_manager.graph.roads.items()}

        self._info_display_state = InfoDisplayInitState()

        self._update_visible_roads_by_bounds(
            zoom_level=14,
            bounds=(Coordinate(43.68984603369737, -79.36489105224611),
                    Coordinate(43.64638600677007, -79.42711830139162))
        )

    def _update_state(self, key: str, value: Any) -> None:
        """
        TODO: write docstring
        """
        current_value_in_state: Any = session_state.get(key)

        if current_value_in_state is None or current_value_in_state != value:
            print(f'Updating state variable {key}')
            session_state[key] = value

    def _get_state_value_by_key(self, key: str) -> Any:
        """
        TODO: write docstring
        Preconditions:
            - key in self._default_session_state_dict
        """
        current_value_in_state: Any = session_state.get(key)

        if current_value_in_state is None:
            # this might happen if the key has yet not been inserted into session state
            print('Returning default')
            return self._default_session_state_dict[key]
        else:
            print('Returning current value')
            return current_value_in_state

    def _build_folium_map(_self, bounds: tuple[Coordinate, Coordinate], zoom: int) -> folium.Map:
        """
        explain why _self not self; and why bounds and zoom not used
        TODO: write docstring
        """
        print('Building folium map')

        north_east_bounds: Coordinate = bounds[0]
        north_east_bounds_formatted: tuple[float, float] = (
            north_east_bounds.latitude, north_east_bounds.longitude
        )
        # University of Toronto area location coordinates
        folium_map: folium.Map = folium.Map(location=north_east_bounds_formatted, zoom_start=zoom)

        # roads: dict[str, UIRoad] = _self._roads
        # for road_id in roads:
        #     road: UIRoad = roads[road_id]
        #
        #     if road.visible:
        #         road_data: Road = road.road
        #         folium.PolyLine(
        #             locations=road_data.get_geometry_coordinates_tuple(),
        #             tooltip=road_data.road_id,
        #             color=road.colour
        #         ).add_to(folium_map)

        return folium_map

    @cache_resource
    def add_polylines(_self, _folium_map: folium.Map, bounds: tuple[Coordinate, Coordinate], zoom: int) -> folium.Map:
        print(f'Adding polylines as per {bounds}')
        roads: dict[str, UIRoad] = _self._roads
        for road_id in roads:
            road: UIRoad = roads[road_id]

            if road.visible:
                road_data: Road = road.road
                folium.PolyLine(
                    locations=road_data.get_geometry_coordinates_tuple(),
                    tooltip=road_data.road_id,
                    color=road.colour
                ).add_to(_folium_map)

        return _folium_map

    def _handle_map_events(self) -> None:
        """
        TODO: write docstring
        """
        print('handling event')
        state_map_info: dict = self._get_state_value_by_key('map_info')

        zoom: int = state_map_info['zoom']

        state_map_info_bounds: dict = state_map_info['bounds']

        north_east_bounds: dict = state_map_info_bounds['_northEast']
        south_west_bounds: dict = state_map_info_bounds['_southWest']
        bounds: tuple[Coordinate, Coordinate] = (
            Coordinate(north_east_bounds['lat'], north_east_bounds['lng']),
            Coordinate(south_west_bounds['lat'], south_west_bounds['lng'])
        )

        self._update_visible_roads_by_bounds(bounds=bounds, zoom_level=zoom)

    def display(self) -> None:
        """
        Display anything which should be displayed using streamlit, as this method is the only method
        that gets rerun as streamlit runs the app from top down on any update.
        """
        print('Displaying')
        state_map_info: dict = self._get_state_value_by_key('map_info')

        zoom: int = state_map_info['zoom']

        state_map_info_bounds: dict = state_map_info['bounds']
        center: dict = state_map_info['center']

        north_east_bounds: dict = state_map_info_bounds['_northEast']
        south_west_bounds: dict = state_map_info_bounds['_southWest']
        bounds: tuple[Coordinate, Coordinate] = (
            Coordinate(north_east_bounds['lat'], north_east_bounds['lng']),
            Coordinate(south_west_bounds['lat'], south_west_bounds['lng'])
        )

        folium_map: folium.Map = self._get_state_value_by_key('map')
        folium_map = self.add_polylines(folium_map, bounds=bounds, zoom=zoom)
        # call to render Folium map in Streamlit
        streamlit_folium.st_folium(
            fig=folium_map,
            key='map_info',
            on_change=self._handle_map_events,
            center=(center['lat'], center['lng'])
        )
        pprint.pprint(f'Folium map bounds: {session_state['map_info']['bounds'] if session_state.get(['map_info']) is not None else 'NULL'}')


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['coordinate', 'info_display', 'road_manager', 'ui_road', 'graph',
                          'streamlit_folium', 'folium'],
    })
