"""
TODO: add docstring
"""
import doctest
from collections.abc import ValuesView
from copy import deepcopy
from typing import Any, Optional, cast

from streamlit import cache_data, session_state
import streamlit as st

from coordinate import Coordinate
from info_display import InfoDisplayDataLoadedState, InfoDisplayState, InfoDisplayLoadingState, \
    InvalidRoadSelectionsState, JunctionDisconnectedState, ShortestPathSuccessState
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
    _default_session_state_dict: dict[str, Any]

    def __init__(self) -> None:
        """
        Initialize StreamlitManager with the Ontario road network data and default display settings.
        """
        self._set_info_display_state(InfoDisplayLoadingState())

        with st.spinner('Loading and building graphs. This takes about 6 seconds.'):

            # this is university of toronto area along with a lot of its surroundings.
            university_bounds_zoomed_out: dict = {
                '_southWest': {'lat': 43.677742473906164, 'lng': -79.37021255493165},
                '_northEast': {'lat': 43.63427368118269, 'lng': -79.41312789916994}
            }

            self._default_session_state_dict = {
                'map_info': {
                    'last_clicked': None,
                    'last_object_clicked': None,
                    'bounds': university_bounds_zoomed_out,
                    "zoom": constants.INITIAL_ZOOM,
                }
            }

            self._set_info_display_state(InfoDisplayLoadingState())

            self._road_manager = RoadManager()

            self._set_info_display_state(InfoDisplayLoadingState())

            self._init_map_related_data()

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
            # this script uses set interval to periodically update the query params with latest bounds and zoom.
            # accessing them directly from st folium (or even trying to get their information by including
            # them in returned_objects field leads to horrible performance issues, as they force an app
            # rerun if returned that way a lot of times). We can then extract the current map zoom
            # and bounds value then from query params, that streamlit allows us to access.
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

            self._set_info_display_state(InfoDisplayDataLoadedState())

    def _get_info_display_state(self) -> InfoDisplayState:
        """
        TODO: write docstring
        Preconditions:
            - st.session_state.get('info_display_state') is not None
        """
        return st.session_state['info_display_state']

    def _set_info_display_state(self, state: InfoDisplayState) -> None:
        """
        TODO write docstring
        """
        st.session_state['info_display_state'] = state

    def _init_map_related_data(self) -> None:
        """
        TODO: add docstring.
        To clear any misconceptions, as we are using separation of concerns architecture, this
        method as a result *does not* fetch data, but only initializes data related to map
        relevant to a Boundary class such as this (boundary class means that which the user interacts
        with directly). Fetching data is RoadManager class' job.
        """
        self._roads = {}
        self._selected_roads = {}

        roads: dict[str, Road] = self._road_manager.get_roads()

        for road_id in roads:
            self._roads[road_id] = UIRoad(
                road=roads[road_id],
                visible=True,  # make every road visible, we will make the ones not in bound or too minor for
                # current zoom in another method.
                colour=self._get_apt_colour_by_road_id(road_id)
            )

    def _get_apt_colour_by_road_id(self, road_id: str) -> str:
        """
        Mutating method

        TODO: write docstring
        :return:
        """
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

        return color

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

            # shapely takes coordinates in latitude, longitude order.
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
            - constants.MIN_ZOOM <= zoom_level <= constants.MAX_ZOOM

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

        # syntax of ValuesView seen from https://stackoverflow.com/a/58013168
        all_roads: ValuesView[UIRoad] = _self._roads.values()
        delta: float = constants.LONGITUDE_TRANSLATION_DELTA

        for ui_road in all_roads:
            road: Road = ui_road.road
            length: float = road.length

            is_in_shortest_path: bool = ui_road.colour == constants.SHORTEST_PATH_ROAD_COLOUR

            # ignore how big or small a road is if the user is zoomed in enough, and thus show all roads
            # that pass the bounds check.
            length_check_passed: bool = (zoom_level >= constants.BIG_ENOUGH_ZOOM_THRESHOLD
                                         or length >= length_bound or is_in_shortest_path
                                         )
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
                             polyline_coordinate_latitude + (signed_delta * -1))
                        )

                    if (min_latitude <= polyline_coordinate_latitude <= max_latitude and
                            min_longitude <= polyline_coordinate_longitude <= max_longitude) or is_in_shortest_path:
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
            - self._roads is initialized
        """
        self._init_map_related_data()

        self._set_info_display_state(InfoDisplayDataLoadedState())
        self._road_manager.restore_removed_roads()

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
            selected_road_id: Optional[str] = self._get_road_id_by_selection(
                Coordinate(last_clicked_object['lat'], last_clicked_object['lng'])
            )

            print(f'Road selected is: {selected_road_id}')
            if selected_road_id is not None:
                selected_road = self._roads[selected_road_id]
                selected_road.colour = constants.SELECTED_ROAD_COLOUR
                road: Road = selected_road.road
                self._selected_roads[selected_road_id] = road

    def _handle_compute_shortest_path(self) -> None:
        selected_roads: dict[str, Road] = self._selected_roads

        if len(selected_roads) == 0:
            return

        info_display_state: InfoDisplayState = self._get_info_display_state()

        if isinstance(info_display_state, ShortestPathSuccessState):
            shortest_paths: list[list[tuple[str, str]]] = info_display_state.shortest_paths
            for path in shortest_paths:
                path_end_index: int = len(path) - 1
                for index in range(0, path_end_index):
                    road_id: str = path[index][1]
                    self._roads[road_id].colour = self._get_apt_colour_by_road_id(road_id)

        self._set_info_display_state(InfoDisplayLoadingState())

        road_manager: RoadManager = self._road_manager
        road_ids: list[str] = list(selected_roads.keys())
        removability_test_result: Optional[tuple[str, str]] = road_manager.check_removability(road_ids)

        if removability_test_result is not None:
            source_and_end: tuple[str, str] = removability_test_result
            source: str = source_and_end[0]
            target: str = source_and_end[1]

            prev_shortest_distance: Optional[ShortestPathResult] = road_manager.get_shortest_path(
                source_junction_id=source,
                target_junction_id=target
            )

            if prev_shortest_distance is None:
                print('Road segments were already disconnected, this should not have passed the '
                      'removability test. Still we will handle it gracefully instead of '
                      'throwing an error.')
                self._set_info_display_state(JunctionDisconnectedState())
            else:
                shortest_distance_result: Optional[ShortestPathResult] = road_manager.remove_road_and_get_path(
                    road_ids=road_ids,
                    source_junction_id=source,
                    target_junction_id=target)

                if shortest_distance_result is None:
                    self._set_info_display_state(JunctionDisconnectedState())

                all_shortest_paths: list[list[tuple[str, str]]] = shortest_distance_result.all_shortest_paths

                self._mark_road_as_in_shortest_path(
                    shortest_paths=all_shortest_paths,
                    in_shortest_path_mark=True,
                    prev_index=-1,
                    index=0
                )

                self._set_info_display_state(ShortestPathSuccessState(
                    prev_length=prev_shortest_distance.length,
                    new_length=shortest_distance_result.length,
                    shortest_paths=all_shortest_paths,
                    start_junction_location=Coordinate(self._roads[all_shortest_paths[0][0][1]].road.geometry[0][1],
                                                       self._roads[all_shortest_paths[0][0][1]].road.geometry[0][0]),
                    end_junction_location=Coordinate(self._roads[all_shortest_paths[0][-2][1]].road.geometry[-1][1],
                                                     self._roads[all_shortest_paths[0][-2][1]].road.geometry[-1][0]),
                    path_displayed_index=0
                ))
        else:
            self._set_info_display_state(InvalidRoadSelectionsState())

    def _mark_road_as_in_shortest_path(
            self, shortest_paths: list[list[tuple[str, str]]], index: int, prev_index: int,
            in_shortest_path_mark: bool,
    ) -> None:
        """
        TODO: docstring
        """
        to_display_shortest_path = shortest_paths[index]
        vertices_end_index: int = len(to_display_shortest_path) - 1

        for index in range(0, vertices_end_index):
            vertex: tuple[str, str] = to_display_shortest_path[index]

            road_id: str = vertex[1]
            road: UIRoad = self._roads[road_id]
            road.visible = in_shortest_path_mark  # TODO: remove this
            road.colour = constants.SHORTEST_PATH_ROAD_COLOUR \
                if in_shortest_path_mark else self._get_apt_colour_by_road_id(road_id)

        if prev_index != -1:
            self._mark_road_as_in_shortest_path(
                shortest_paths, index=prev_index, prev_index=-1, in_shortest_path_mark=False
            )

    def _shift_to_next_shortest_path(self) -> None:

        # cast syntax seen from https://stackoverflow.com/a/75010658
        info_display_state: ShortestPathSuccessState = cast(ShortestPathSuccessState, self._get_info_display_state())

        shortest_paths: list[list[tuple[str, str]]] = info_display_state.shortest_paths

        prev_index: int = info_display_state.path_displayed_index

        next_index: int

        if prev_index >= len(shortest_paths) - 1:
            next_index = 0
        else:
            next_index = prev_index + 1

        self._mark_road_as_in_shortest_path(
            shortest_paths, prev_index=prev_index, index=next_index, in_shortest_path_mark=True
        )

        updated_info_display_state: ShortestPathSuccessState = deepcopy(info_display_state)
        updated_info_display_state.path_displayed_index = next_index
        self._set_info_display_state(updated_info_display_state)

    def display(self) -> None:
        """
        Display anything which should be displayed using streamlit, as this method is the only method
        that gets rerun as streamlit runs the app from top down on any update.
        """
        print('\nDisplayin')
        info_display_state: InfoDisplayState = st.session_state['info_display_state']

        if isinstance(info_display_state, InfoDisplayLoadingState):
            # this is done to protect against data being accidently displayed while it is still being loaded,
            # in which case there are chances of error
            return
        elif isinstance(info_display_state, InfoDisplayDataLoadedState):

            with (st.spinner('Building Map')):

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
                    state_map_info_bounds = self._default_session_state_dict['map_info']['bounds']

                north_east_bounds: dict = state_map_info_bounds['_northEast']
                south_west_bounds: dict = state_map_info_bounds['_southWest']
                bounds: tuple[Coordinate, Coordinate] = (
                    Coordinate(north_east_bounds['lat'], north_east_bounds['lng']),
                    Coordinate(south_west_bounds['lat'], south_west_bounds['lng'])
                )

                south_west_bounds_lat: float = south_west_bounds['lat']
                south_west_bounds_lng: float = south_west_bounds['lng']
                north_east_bounds_lat: float = north_east_bounds['lat']
                north_east_bounds_lng: float = north_east_bounds['lng']

                # compute center of map from bounds, which is what location parameter takes below.
                folium_map: folium.Map = folium.Map(location=(
                    south_west_bounds_lat + ((north_east_bounds_lat - south_west_bounds_lat) / 2),
                    south_west_bounds_lng + ((north_east_bounds_lng - south_west_bounds_lng) / 2)
                ), zoom_start=zoom, max_zoom=constants.MAX_ZOOM, min_zoom=constants.MIN_ZOOM)

                self._update_visible_roads_by_bounds(zoom_level=zoom, bounds=bounds)

                roads: dict[str, UIRoad] = self._roads

                # folium.GeoJson and geojson_data syntax and format seen from
                # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson.html
                geojson_data: dict = {
                    'type': 'FeatureCollection',
                    'features': [
                        {
                            'type': 'Feature',
                            'properties': {
                                'color': roads[road_id].colour,
                                'road_id': road_id,
                                'length': f'{roads[road_id].road.length // 1.0} Meters',  # floored division
                                # to get rid of decimals, which lead to trivially longer paths (like by 0.1 meters)
                                # to not be recognized as the shortest path. Since that's
                                # how we run our shortest path algorithm by ignoring decimals to address
                                # these trivially longer paths, we will
                                # display to the user distance without decimals also. Stripping of decimals is
                                # faster here than while loading all data, since it is only for a small subset of
                                # all roads. Also, no length would become 0, since our biggest length of road is
                                # at least 1 meter.
                            },
                            'geometry': {
                                'type': 'MultiLineString',
                                'coordinates': [roads[road_id].road.geometry]
                            }
                        }
                        for road_id in roads
                        if roads[road_id].visible
                    ]
                }

                folium.GeoJson(
                    geojson_data,
                    style_function=lambda feature: {
                        'color': feature['properties']['color'],
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['road_id', 'length'],
                        aliases=['Road ID', 'Length']
                    )
                ).add_to(folium_map)

                # st.column syntax seen from https://docs.streamlit.io/develop/api-reference/layout/st.columns
                columns: list = st.columns(2)

                with columns[1]:
                    st.text(f'Roads Currently Selected: {len(self._selected_roads)}')
                    st.button('Reload Polylines', on_click=lambda: print('clicked'))
                    st.button('Compute Shortest Path', on_click=self._handle_compute_shortest_path)
                    st.button('Reset', on_click=self.reset)

                    st.text('Please note that if you zoom in too much and then perform some action, '
                            'you wil have to zoom out and press reload polylines to see polylines '
                            'after your action is done. For instance, if you zoom in to remove a polyline, '
                            'and then you click Compute Shortest Path, you might have to zoom out to see '
                            'and press Reload Polylines button to see the full shortest path. This has been '
                            'done for performance reasons, as Python is quite slow when it comes to rendering '
                            'on web, as Python is not suitable for web development and is slow enough on its own '
                            'as well.')

                    print(type(info_display_state))
                    if isinstance(info_display_state, ShortestPathSuccessState):
                        folium.Marker(
                            location=info_display_state.start_junction_location.to_tuple(),
                            tooltip='Road Segment Sequence\'s Start Junction'
                        ).add_to(folium_map)
                        folium.Marker(
                            location=info_display_state.end_junction_location.to_tuple(),
                            tooltip='Road Segment Sequence\'s End Junction'
                        ).add_to(folium_map)

                        total_shortest_paths: int = len(info_display_state.shortest_paths)
                        multiple_shortest_paths_present: bool = total_shortest_paths > 1

                        st.text('Shortest paths computed successfully.')
                        st.text(f'There {'are' if multiple_shortest_paths_present else 'is'} in total '
                                f'{total_shortest_paths} shortest '
                                f'path{'s' if multiple_shortest_paths_present else ''}.')
                        st.text(f'Displaying path number {info_display_state.path_displayed_index + 1} '
                                f'out of {total_shortest_paths} path{'s' if multiple_shortest_paths_present else ''}')
                        st.text('Previous length of shortest path before removal of road segment was '
                                f'{info_display_state.prev_length} meters.')
                        st.text('Now, after removal, the length of shortest path '
                                f'is  {info_display_state.new_length} meters.')

                        if multiple_shortest_paths_present:
                            st.button('> Show another shortest path', on_click=self._shift_to_next_shortest_path)

                    elif isinstance(info_display_state, JunctionDisconnectedState):
                        st.text('The removal of your selected road segments will cause the junction to '
                                'be disconnected')
                        st.text('Therefore, there will be no shortest path if the selected segments are closed.')
                    elif isinstance(info_display_state, InvalidRoadSelectionsState):
                        st.text('Your selection of road segments is invalid.')
                        st.text('The selected road segments considered together should have only one free start '
                                'point and only one free end point, regardless of how many of them are selected. '
                                'By free start/end point, it means that the start/end point is not the '
                                'end/start point of some other road respectively. You may want to press '
                                'reset and try again.'
                                )

                with columns[0]:
                    streamlit_folium.st_folium(
                        fig=folium_map,
                        key='map_info',
                        zoom=zoom,
                        on_change=self._handle_map_events,
                        returned_objects=['last_object_clicked'],
                    )


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['coordinate', 'info_display', 'road_manager', 'ui_road', 'graph',
                          'streamlit_folium', 'folium'],
    })
