"""
TODO: add docstring
"""
import doctest
from collections.abc import dict_values
from typing import Any, Optional

from streamlit import cache_data, session_state
import streamlit as st

from coordinate import Coordinate
from info_display import InfoDisplayState, InfoDisplayInitState
from road_manager import RoadManager
from ui_road import UIRoad

import streamlit_folium
import folium
import constants
from graph import Road, ShortestPathResult
from shapely.geometry import MultiLineString, Point


class StreamlitManager:
    """
    TODO: add docstring and representation invariants
    """
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, Road]
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
        self._init_map_related_data()
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

        # TODO: remove console.log
        st.html('''<script>
                    setInterval(() => {
                        if(window.frames['0'] != undefined && window.frames['0'].map != undefined) {
                            let mapObject = window.frames['0'].map
                            let zoom = mapObject.getZoom()
                            let bounds = mapObject.getBounds()

                            // url setting code seen from https://stackoverflow.com/a/41542008
                            let modifiedURL = new URL(location.href);

                            modifiedURL.searchParams.set('zoom', window.frames['0'].map.getZoom());

                            let northEast = bounds['_northEast']
                            let southWest = bounds['_southWest']
                            modifiedURL.searchParams.set('neLat', northEast['lat'],);
                            modifiedURL.searchParams.set('neLng', northEast['lng'],);
                            modifiedURL.searchParams.set('swLat', southWest['lat'],);
                            modifiedURL.searchParams.set('swLng', southWest['lng'],);

                            history.pushState(null, '', modifiedURL)
                        }
                    }, 100)
                </script>''',
                unsafe_allow_javascript=True  # this just means we trust our js code that we wrote, and are
                # not running something untrusted like from API or concatenating some input
                )

    def _init_map_related_data(self) -> None:
        """
        TODO: add docstring.
        To clear any misconceptions, as we are using separation of concerns architecture, this
        method as a result *does not* fetch data, but only initializes data related to map
        relevant to a Boundary class such as this (boundary class means that which the user interacts
        with directly). Fetching data is RoadManager class' job.
        :return:
        """
        roads: dict[str, Road] = self._road_manager.get_roads()

        for road_id in roads:
            color: str
            end_four_chars: str = road_id[-4:]  # this is guaranteed to exist, since we always append a four letter
            # suffix to our road ids when building the graph.

            if end_four_chars == constants.ROAD_POSITIVE_SUFFIX:
                color = 'blue'
            elif end_four_chars == constants.ROAD_NEGATIVE_SUFFIX:
                color = 'black'
            else:
                # it is a uni directional road
                color = 'brown'

            self._roads[road_id] = UIRoad(
                road=roads[road_id],
                visible=True,  # make every road visible, we will make the ones not in bound or too minor for
                # current zoom in another method.
                colour=color
            )

        self._selected_roads = {}

    def _get_road_id_by_selection(self, point: Coordinate) -> Optional[str]:
        """
        Return the UIRoad whose geometric polyline is within a threshold distance
        from the given point, or None if no visible road is close enough.

        Preconditions:
            -
        """
        point_shape: Point = Point(point.latitude, point.longitude)

        infinity: int = constants.INFINITY  # of course if we came here
        # because something was clicked, the click distance will be less
        # than 1 billion units.
        min_distance: float = infinity
        min_road_id: Optional[str] = None

        for ui_road in self._roads.values():
            if not ui_road.visible:
                continue

            road: Road = ui_road.road
            polyline: list[tuple[float, float]] = road.geometry
            multiline: MultiLineString = MultiLineString([[(coordinate[1], coordinate[0]) for coordinate in polyline]])

            distance_from_clicked_coordinate: float = point_shape.distance(multiline)

            if distance_from_clicked_coordinate < min_distance:
                min_distance = point_shape.distance(multiline)
                min_road_id = road.road_id

        if min_road_id is None:
            # this might happen if for some reason, our streamlit folium library messes up something,
            # thus, we just return None, as if no road was selected.
            return None
        else:
            return min_road_id

    @cache_data
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
        all_roads: dict_values[UIRoad] = _self._roads.values()
        delta: float = constants.LONGITUDE_TRANSLATION_DELTA

        for ui_road in all_roads:
            road: Road = ui_road.road
            length: float = road.length

            # ignore how big or small a road is if the user is zoomed in enough, and thus show all roads
            # that pass the bounds check
            length_check_passed: bool = zoom_level >= constants.BIG_ENOUGH_ZOOM_THRESHOLD or length >= length_bound
            bounds_check_passed: bool = False

            if length_check_passed:
                translation_factor: int = 0  # if this is 0, that means
                # don't translate, if 1 then the road needs +ve translation,
                # if -1 then negative translation

                road_id: str = road.road_id
                end_four_letters: str = road_id[-4:]  # guaranteed to exist, since we add road ids
                # with suffixes of 4 letters always

                # no need to translate single directional roads
                if end_four_letters != '_one':
                    if end_four_letters == '_pos':
                        translation_factor = 1
                    elif end_four_letters == '_neg':
                        translation_factor = -1

                signed_delta: float = (delta * translation_factor) / 2

                polyline: list[tuple[float, float]] = road.geometry

                # so we don't mutate the ones who have same polyline instance (eg the reverse of this in
                # other direction if road is biderection) don't get mutated, else it defeates the purpose of
                # translation

                # the below will be used if and only if we are translating (meaning translation_factor != 0
                polyline_copy: list[tuple[float, float]] = []

                for coord in polyline:
                    # our natural project order
                    polyline_coordinate_latitude: float = coord[1]
                    polyline_coordinate_longitude: float = coord[0]

                    if translation_factor != 0:
                        # don't do something like polyline_coordinate_longitude += as that
                        # will lead to reassignment, while we want to mutate and translate
                        # original coordinate's longitude and latitude
                        polyline_copy.append(
                            (polyline_coordinate_longitude + signed_delta,
                             polyline_coordinate_latitude + signed_delta * -1)
                        )

                    if (min_latitude <= polyline_coordinate_latitude <= max_latitude and
                            min_longitude <= polyline_coordinate_longitude <= max_longitude):
                        bounds_check_passed = True
                        # don't break, as we are also translating polylines

                if translation_factor != 0:
                    road.geometry = polyline_copy

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
        self._init_map_related_data()

        self._info_display_state = InfoDisplayInitState()
        self._road_manager.restore_removed_roads()

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

    def _handle_map_events(self) -> None:
        """
        TODO: write docstring
        """
        print('handling event')

        state_map_info: dict = self._get_state_value_by_key('map_info')
        last_clicked_object: Optional[dict] = state_map_info['last_object_clicked']
        if last_clicked_object is None:
            return
        else:
            selected_road_id: Optional[str] = (
                self._get_road_id_by_selection(Coordinate(last_clicked_object['lat'], last_clicked_object['lng'])))

            print(f'Road selected is: {selected_road_id}')
            if selected_road_id is not None:
                selected_road = self._roads[selected_road_id]
                selected_road.colour = '#FF0000'
                road: Road = selected_road.road
                self._selected_roads[selected_road_id] = road
        # zoom: int = state_map_info['zoom']
        #
        # state_map_info_bounds: dict = state_map_info['bounds']
        #
        # north_east_bounds: dict = state_map_info_bounds['_northEast']
        # south_west_bounds: dict = state_map_info_bounds['_southWest']
        # bounds: tuple[Coordinate, Coordinate] = (
        #     Coordinate(north_east_bounds['lat'], north_east_bounds['lng']),
        #     Coordinate(south_west_bounds['lat'], south_west_bounds['lng'])
        # )

    def _handle_compute_shortest_path(self) -> None:
        road_manager: RoadManager = self._road_manager
        road_ids: list[str] = list(self._selected_roads.keys())
        removability_test_result: tuple[bool, list[str]] = road_manager.check_removability(road_ids)
        if removability_test_result[0]:
            source_and_end: list[str] = removability_test_result[1]
            shortest_distance_result: Optional[ShortestPathResult] = road_manager.remove_road_and_get_path(
                road_ids=road_ids,
                source_junction_id=source_and_end[0],
                target_junction_id=source_and_end[1])
            if shortest_distance_result is None:
                print('Path is disconnected')
            else:
                print(f'Length of shortest path now {shortest_distance_result.length}')
                for shortest_path in shortest_distance_result.all_shortest_paths:
                    print(shortest_path)
                    vertices_end_index: int = len(shortest_path) - 1
                    for index in range(0, vertices_end_index):
                        vertex: tuple[str, str] = shortest_path[index]
                        road: UIRoad = self._roads[vertex[1]]
                        road.visible = True
                        road.colour = 'green'

        else:
            print('CANNOT PERFORM MODIFIED DIJKTRAS')

    def display(self) -> None:
        """
        Display anything which should be displayed using streamlit, as this method is the only method
        that gets rerun as streamlit runs the app from top down on any update.
        """
        print('\nDisplayin')
        state_map_info: dict = self._get_state_value_by_key('map_info')

        query_params = st.query_params

        current_zoom_from_map: str = query_params.get('zoom')

        zoom: int
        state_map_info_bounds: dict

        if current_zoom_from_map is not None:
            zoom = int(current_zoom_from_map)
            # 'neLat' and other query params are
            # guaranteed not to be null, as zoom and these values are set together, unless something
            # terribly goes wrong in which case it is a situation of data corruption in general.
            state_map_info_bounds = {
                '_northEast': {
                    'lat': float(query_params.get('neLat')),
                    'lng': float(query_params.get('neLng'))
                },
                '_southWest': {
                    'lat': float(query_params.get('swLat')),
                    'lng': float(query_params.get('swLng'))
                }
            }
        else:
            zoom = self._default_session_state_dict['map_info']['zoom']
            state_map_info_bounds = state_map_info['bounds']

        north_east_bounds: dict = state_map_info_bounds['_northEast']
        south_west_bounds: dict = state_map_info_bounds['_southWest']
        bounds: tuple[Coordinate, Coordinate] = (
            Coordinate(north_east_bounds['lat'], north_east_bounds['lng']),
            Coordinate(south_west_bounds['lat'], south_west_bounds['lng'])
        )

        north_east_bounds_tuple: tuple[float, float] = (
            north_east_bounds['lat'], north_east_bounds['lng']
        )
        # University of Toronto area location coordinates
        # location needs latitude and longitude coordinates, opposite to our project order,
        # but since this is just one statement, switching is easy, and hence the order in
        # north_east_bounds_tuple
        folium_map: folium.Map = folium.Map(location=(
            south_west_bounds['lat'] + ((north_east_bounds['lat'] - south_west_bounds['lat']) / 2),
            south_west_bounds['lng'] + ((north_east_bounds['lng'] - south_west_bounds['lng']) / 2)
        ), zoom_start=zoom, max_zoom=19, min_zoom=1)
        self._update_visible_roads_by_bounds(zoom_level=zoom, bounds=bounds)

        roads: dict[str, UIRoad] = self._roads
        # code adapted from https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson.html
        geojson_data: dict = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'properties': {
                        'color': roads[road_id].visible,
                        'road_id': road_id,
                        'length': f'{roads[road_id].road.length // 1.0}',  # floored division
                        # to get rid of decimals, which lead to trivially longer paths (like by 0.1 meters)
                        # to not be recognized as the shortest path. Since that's how we run our shortest path
                        # algorithm by ignoring decimals to address these trivially longer paths, we will
                        # display to the user distance without decimals also. Stripping of decimals is
                        # faster here than while loading all data, since it is only for a small subset of
                        # all roads. Also, no length would become 0, since our biggest length of road is
                        # at least 1 meter.
                    },
                    'geometry': {
                        'type': 'MultiLineString',
                        'coordinates': [[
                            (coordinate[1], coordinate[0])
                            for coordinate in roads[road_id].road.geometry
                        ]]
                    }
                }
                for road_id in roads
            ]
        }

        folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                'color': feature['properties']['color']
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['road_id', 'length']
            )
        ).add_to(folium_map)

        # geojson_data = {
        #     "type": "FeatureCollection",
        #     "features": [
        #         {
        #             "type": "Feature",
        #             "geometry": {
        #                 "type": "LineString",
        #                 "coordinates": [[lat, lon] for lat, lon in self._roads[road_id].road.geometry]
        #             },
        #             "properties": {
        #                 "color": self._roads[road_id].colour,
        #                 "road_id": road_id,
        #                 "length": self._roads[road_id].road.length // 1.0
        #             }
        #         }
        #         for road_id in self._roads
        #         if self._roads[road_id].visible
        #     ]
        # }
        #
        # folium.GeoJson(geojson_data,
        #                style_function=lambda f: {
        #                     "color": f["properties"]["color"],
        #                 },
        #                tooltip=folium.GeoJsonTooltip(
        #                    fields=["road_id", "length"],
        #                 )).add_to(folium_map)

        with st.columns(2):
            streamlit_folium.st_folium(
                fig=folium_map,
                key='map_info',
                zoom=zoom,
                on_change=self._handle_map_events,
                returned_objects=['last_object_clicked']
            )

            st.button('Reload Polylines', on_click=lambda: print('clicked'))
            st.button('Compute shortest path', on_click=self._handle_compute_shortest_path)
            st.button('Redo', on_click=self.reset)


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['coordinate', 'info_display', 'road_manager', 'ui_road', 'graph',
                          'streamlit_folium', 'folium'],
    })
