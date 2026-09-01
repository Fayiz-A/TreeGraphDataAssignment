"""
Ontario Road Closure Analysis App
================================

This file contains the code for Boundary class Streamlit Manager. It is the file which
user interacts with directly.
"""

import doctest
from collections.abc import ValuesView
from copy import deepcopy
from typing import Any, Optional, cast

from streamlit import cache_data, session_state
import streamlit as st
import streamlit_folium
import folium
from shapely.geometry import MultiLineString, Point

from compressed_geo_json_file_loader import CompressedGeoJsonFileLoader
from coordinate import Coordinate
from info_display import InfoDisplayDataLoadedState, InfoDisplayErrorState, InfoDisplayState, InfoDisplayLoadingState, \
    InvalidRoadSelectionsState, JunctionDisconnectedState, ShortestPathSuccessState
from road_manager import RoadManager
from ui_road import UIRoad
import constants
from graph import Road, ShortestPathResult


class StreamlitManager:
    """
    The boundary class of this project which the user interacts with. Its job is not to
    perform any business logic like fetching data or building graphs. Its job is only and only
    to deal with UI related logic.

    There are no public attributes to this class, as the only interaction permitted to this class
    is by user interaction or for trivial bootstrapping code like in main.py that cannot be
    written in class due to framework limitations.
    """
    # Private instance attributes:
    #   - _road_manager: instance of service class (the one which handles business logic and mediates
    #     between Graph and this class).
    #   - _roads: a mapping between road id and UIRoad
    #   - _selected_roads: a mapping between road id and roads which are currently selected by user
    #   - _road_average_length: average length of roads in our data set, useful for our UI related
    #     display logic.
    #   - _default_session_state_dict: a default fallback dictionary in case Streamlit's session state does
    #     not have the required values.
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, Road]
    _road_average_length: float
    _default_session_state_dict: dict[str, Any]

    def __init__(self) -> None:
        """
        Initialize StreamlitManager with the Ontario road network data and default display settings, and
        add code to run Javascript to update query params with latest map bounds and zoom informations
        periodically.
        """
        self._set_info_display_state(InfoDisplayLoadingState())

        # note: spinners should best be in display method, but streamlit forces us to use
        # spinner/loading indicator here with the business logic happening in context manager.

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
            data_fetched: bool = self._road_manager.fetch_data_and_build_graph(CompressedGeoJsonFileLoader(
                constants.ORN_FILE_NAME)
            )

            self._set_info_display_state(InfoDisplayLoadingState())

            if data_fetched:
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
            else:
                # problem opening data
                self._set_info_display_state(InfoDisplayErrorState())

    def _get_info_display_state(self) -> InfoDisplayState:
        """
        Return info_display_state from streamlit's session state. This is a small helper method

        Preconditions:
            - st.session_state.get('info_display_state') is not None
        """
        return st.session_state['info_display_state']

    def _set_info_display_state(self, state: InfoDisplayState) -> None:
        """
        Set info_display_state in streamlit's session state. This is a small helper method.

        There are no preconditions to use this method.
        """
        st.session_state['info_display_state'] = state

    def _init_map_related_data(self) -> None:
        """
        Initialize map related data, in particular empty selected roads, get roads from
         road manager and mark every road as visible

        To clear any misconceptions, as we are using separation of concerns architecture, this
        method as a result *does not* fetch data, but only initializes data related to map
        relevant to a Boundary class such as this class (boundary class means that which the user interacts
        with directly). Fetching data is RoadManager class' job.

        There are no preconditions to use this method.
        """
        self._roads = {}
        self._selected_roads = {}

        roads: dict[str, Road] = self._road_manager.get_roads()  # this does *not* result in file calls. This is
        # just a getter method called.

        for road_id in roads:
            self._roads[road_id] = UIRoad(
                road=roads[road_id],
                visible=True,  # make every road visible, we will make the ones not in bound or too minor for
                # current zoom invisible in another method.
                colour=self._get_apt_colour_by_road_id(road_id)
            )

    def _get_apt_colour_by_road_id(self, road_id: str) -> str:
        """
        Return colour as per road id as per the following legend:
            - positive road: blue
            - negative road: black
            - unidirectional road: brown

        Preconditions:
            - len(road_id) > 4
        """
        color: str
        end_four_chars: str = road_id[-4:]  # this is guaranteed to exist, since we always append a four letter
        # suffix to our road ids when building the graph.

        if end_four_chars == constants.ROAD_POSITIVE_SUFFIX:
            color = constants.ROAD_POSITIVE_COLOR
        elif end_four_chars == constants.ROAD_NEGATIVE_SUFFIX:
            color = constants.ROAD_NEGATIVE_COLOR
        else:
            # fallback colour
            color = constants.ROAD_UNIDIRECTIONAL_COLOR

        return color

    def _get_road_id_by_selection(self, point: Coordinate) -> Optional[str]:
        """
        Return the road id whose geometric polyline is the closest to
        point coordinate, or None if no visible road is close enough. This method
        should only be called if a click is detected on a line, and we want to figure
        out which line it is, and it should not be used to detect if a line was clicked upon
        or not.

        The None return is just for extreme rare edge cases: don't rely
        on this returning None to figure out if a line was clicked upon or not.

        Preconditions:
            - A line was clicked upon in the folium map
        """
        point_shape: Point = Point(point.latitude, point.longitude)

        infinity: int = constants.INFINITY  # of course if we came here
        # because something was clicked, the click distance will be less
        # than 1 trillion units.
        min_distance: float = infinity
        min_road_id: Optional[str] = None

        for ui_road in self._roads.values():
            if not ui_road.visible:
                continue

            road: Road = ui_road.road
            polyline: list[tuple[float, float]] = road.geometry

            # shapely takes coordinates in latitude, longitude order.
            multiline: MultiLineString = MultiLineString([[(coordinate[1], coordinate[0]) for coordinate in polyline]])

            dist_from_clicked_coordinate: float = point_shape.distance(multiline)

            if dist_from_clicked_coordinate < min_distance:
                min_distance = point_shape.distance(multiline)
                min_road_id = road.road_id

        if min_road_id is None:
            # this might happen if for some reason, our streamlit folium library messes up something,
            # thus, we just return None instead of throwing errors, as if no road was selected.
            return None
        else:
            return min_road_id

    @cache_data
    def _compute_visible_roads_cached(_self, zoom_level: int, bounds: tuple[Coordinate, Coordinate]) -> None:
        """
        Make roads visible and invisible according to the given zoom level and bounds. The road will be invisible
        if all portions are not in the current bounds or the road length is too minor to display. If
        the zoom level given is equal to or greater than 13, all the roads that pass the aforementioned bound
        check would be visible.

        NOTE: This is a cached version of _compute_visible_roads. Use this where possible. This means it does not
        do anything if zoom_level or bounds don't change as compared to previous invoking of this method.

        self is written as _self as Streamlit's @cache_data decorator ignores any argument having an underscore,
        and this is important otherwise Streamlit will try to compute a hash of self, which would lead to errors.

        Preconditions:
            - constants.MIN_ZOOM <= zoom_level <= constants.MAX_ZOOM
            - bounds' first coordinate represents northeast coordinates and the other one represents
            southwest coordinates of a map's bounds
        """
        _self._compute_visible_roads(zoom_level=zoom_level, bounds=bounds)

    def _compute_visible_roads(self, zoom_level: int, bounds: tuple[Coordinate, Coordinate]) -> None:
        """
        Make roads visible and invisible according to the given zoom level and bounds. The road will be invisible
        if all portions are not in the current bounds or the road length is too minor to display. If
        the zoom level given is equal to or greater than 13, all the roads that pass the aforementioned bound
        check would be visible.

        NOTE: this is not cached, and hence will update roads on every call (and this is an expensive method).
        Don't call this except if no other option is available. Instead, always try to
        use self._compute_visible_roads_cached.

        Preconditions:
            - constants.MIN_ZOOM <= zoom_level <= constants.MAX_ZOOM
            - bounds' first coordinate represents northeast coordinates and the other one represents
            southwest coordinates of a map's bounds
        """

        length_bound: float = (constants.MAX_ZOOM - zoom_level + 1) * self._road_average_length * 0.75

        northeast_candidate: Coordinate = bounds[0]
        southwest_candidate: Coordinate = bounds[1]
        longitudes: tuple[float, float] = (northeast_candidate.longitude, southwest_candidate.longitude)
        latitudes: tuple[float, float] = (northeast_candidate.latitude, southwest_candidate.latitude)

        max_longitude: float = max(longitudes)
        min_longitude: float = min(longitudes)
        max_latitude: float = max(latitudes)
        min_latitude: float = min(latitudes)

        # syntax of ValuesView seen from https://stackoverflow.com/a/58013168
        all_roads: ValuesView[UIRoad] = self._roads.values()
        delta: float = constants.TRANSLATION_DELTA

        for ui_road in all_roads:
            road: Road = ui_road.road
            length: float = road.length

            is_in_shortest_path: bool = ui_road.colour == constants.SHORTEST_PATH_ROAD_COLOUR

            # ignore how big or small a road is if the user is zoomed in enough, and thus show all roads
            # that pass the bounds check.
            length_check_passed: bool = (zoom_level >= constants.BIG_ENOUGH_ZOOM_THRESHOLD
                                         or length >= length_bound or is_in_shortest_path)
            bounds_check_passed: bool = False

            if length_check_passed:
                translation_factor: int = 0  # if this is 0, that means
                # don't translate, if 1 then the road needs +ve translation,
                # if -1 then negative translation

                end_four_letters: str = road.road_id[-4:]  # guaranteed to exist, since we add road ids
                # with suffixes of 4 letters always

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

                    if (min_latitude <= polyline_coordinate_latitude <= max_latitude
                       and min_longitude <= polyline_coordinate_longitude <= max_longitude) or is_in_shortest_path:

                        bounds_check_passed = True
                        # don't break, as we are also translating polylines

                if translation_factor != 0:
                    road.geometry = polyline_copy

            ui_road.visible = length_check_passed and bounds_check_passed

    def reset(self) -> None:
        """
        Reset StreamlitManager to its initial state by clearing selected roads,
        restoring deleted roads, restoring all roads to their original colour and
        recomputing visible roads by force. This method also sets info display state to
        InfoDisplayDataLoadedState(), so any shortest path related information would get removed
        from screen.

        Preconditions:
            - self._roads is initialized
            - self._default_session_state_dict.get('map_info') is not None
        """
        self._init_map_related_data()

        self._set_info_display_state(InfoDisplayDataLoadedState())
        self._road_manager.restore_removed_roads()

        zoom_and_bounds: tuple[int, tuple[Coordinate, Coordinate]] = self._get_current_zoom_and_bounds()
        # use non cached version since the cached one won't update if bounds or zoom don't change,
        # which they haven't
        self._compute_visible_roads(zoom_level=zoom_and_bounds[0], bounds=zoom_and_bounds[1])

    def _get_state_value_by_key(self, key: str) -> Any:
        """
        Return Streamlit session state's current value of key field, or from
        self._default_session_state_dict if key is not currently in session state.

        Preconditions:
            - key in self._default_session_state_dict
        """
        current_value_in_state: Any = session_state.get(key)

        if current_value_in_state is None:
            # this might happen if the key has yet not been inserted into session state
            return self._default_session_state_dict[key]
        else:
            return current_value_in_state

    def _handle_map_events(self) -> None:
        """
        Handle any events that happen to the map, primarily when a polyline is clicked.
        This is a callback method.

        Preconditions:
            - self._default_session_state_dict.get('map_info') is not None
        """

        state_map_info: dict = self._get_state_value_by_key('map_info')
        last_clicked_object: Optional[dict] = state_map_info['last_object_clicked']
        if last_clicked_object is None:
            return
        else:
            selected_road_id: Optional[str] = self._get_road_id_by_selection(
                Coordinate(last_clicked_object['lat'], last_clicked_object['lng'])
            )

            if selected_road_id is not None:
                selected_road: UIRoad = self._roads[selected_road_id]
                selected_road.colour = constants.SELECTED_ROAD_COLOUR
                road: Road = selected_road.road
                self._selected_roads[selected_road_id] = road

    def _handle_compute_shortest_path(self) -> None:
        """
        Handle pressing of Compute Shortest Path button by checking if
        shortest path can be computed with current selection of Roads, and if yes
        then computing it and in both cases changing state as required.
        This is a callback method.

        Preconditions:
            - self._road_manager has been initialized
            - self._selected_roads has been initialized
        """
        selected_roads: dict[str, Road] = self._selected_roads

        if len(selected_roads) == 0:
            st.toast('Please select at least a road to compute shortest path between start and end points of '
                     'the road segment/segments.', duration='long')
            return

        info_display_state: InfoDisplayState = self._get_info_display_state()

        self._set_info_display_state(InfoDisplayLoadingState())

        if isinstance(info_display_state, ShortestPathSuccessState):
            # this happens if let's say previous shortest path algorithm had coloured some roads.

            shortest_paths: list[list[tuple[str, str]]] = info_display_state.shortest_paths
            for path in shortest_paths:
                path_end_index: int = len(path) - 1
                for index in range(0, path_end_index):
                    road_id: str = path[index][1]
                    self._roads[road_id].colour = self._get_apt_colour_by_road_id(road_id)

        road_manager: RoadManager = self._road_manager
        road_ids: list[str] = list(selected_roads.keys())
        removability_test_result: Optional[tuple[str, str]] = road_manager.check_removability(road_ids)

        if removability_test_result is not None:
            source_road_id: str = removability_test_result[0]
            target_road_id: str = removability_test_result[1]

            road_manager.restore_removed_roads()  # prevent previously deleted roads from affecting us now.
            prev_shortest_distance: Optional[ShortestPathResult] = road_manager.get_shortest_path(
                source_junction_id=source_road_id,
                target_junction_id=target_road_id
            )

            if prev_shortest_distance is None:
                # Road segments were already disconnected this means. This should not have passed the
                # removability test. Still we will handle it gracefully instead of
                # throwing an error.

                self._set_info_display_state(JunctionDisconnectedState())
            else:
                shortest_distance_result: Optional[ShortestPathResult] = road_manager.remove_road_and_get_path(
                    road_ids=road_ids,
                    source_junction_id=source_road_id,
                    target_junction_id=target_road_id)

                if shortest_distance_result is None:
                    self._set_info_display_state(JunctionDisconnectedState())
                else:
                    all_shortest_paths: list[list[tuple[str, str]]] = shortest_distance_result.all_shortest_paths

                    self._mark_road_as_in_shortest_path(
                        shortest_paths=all_shortest_paths,
                        in_shortest_path_mark=True,
                        prev_index=-1,
                        index=0
                    )

                    first_shortest_path: list[tuple[str, str]] = all_shortest_paths[0]

                    start_road: UIRoad = self._roads[first_shortest_path[0][1]]  # first_shortest_path[0]
                    # is guaranteed to exist, as every shortest path needs to have a beginning. Refer to
                    # ShortestPathResult.all_shortest_paths for more details. The first element of tuple then is
                    # the first road id of this shortest path.

                    start_road_geometry_first: tuple[float, float] = start_road.road.geometry[0]  # guaranteed to
                    # exist: each road has to have at least two elements in geometry to form a polyline/road

                    end_road: UIRoad = self._roads[first_shortest_path[-2][1]]  # take second last, since last one
                    # does not have a road, as it doesn't have a vertex. Refer to
                    # ShortestPathResult.all_shortest_paths for more details. This is guaranteed to exist,
                    # since every shortest path needs to have at least two vertices and hence 2 elements in
                    # first_shortest_path. After that, the first element from tuple is the road id of the last
                    # road id in shortest path.
                    end_road_geometry_last: tuple[float, float] = end_road.road.geometry[-1]  # guaranteed to
                    # exist: each road has to have at least two elements in geometry to form a polyline/road

                    self._set_info_display_state(ShortestPathSuccessState(
                        prev_length=prev_shortest_distance.length,
                        new_length=shortest_distance_result.length,
                        shortest_paths=all_shortest_paths,
                        # 1st element is longitude, 2nd element is latitude, following our project and
                        # file ontario_road_network.geojson data's natural order
                        start_junction_location=Coordinate(start_road_geometry_first[1],
                                                           start_road_geometry_first[0]),
                        end_junction_location=Coordinate(end_road_geometry_last[1],
                                                         end_road_geometry_last[0]),
                        path_displayed_index=0
                    ))
        else:
            self._set_info_display_state(InvalidRoadSelectionsState())

    def _mark_road_as_in_shortest_path(
            self, shortest_paths: list[list[tuple[str, str]]], index: int, prev_index: int,
            in_shortest_path_mark: bool,
    ) -> None:
        """
        Mark all roads that occur in shortest_paths current index as in_shortest_path_mark value.
        If prev_index is not -1, then mark all roads in shortest_paths from prev_index as
        invisible (useful to display new shortest path while disappearing the previous one).

        - prev_index != index
        - -1 <= prev_index < len(shortest_paths)
        - 0 <= prev_index < len(shortest_paths)
        - shortest_paths is a valid list of shortest path created after running Graph.compute_shortest_path()
        """
        to_display_shortest_path = shortest_paths[index]
        vertices_end_index: int = len(to_display_shortest_path) - 1

        for vertex_index in range(0, vertices_end_index):
            vertex: tuple[str, str] = to_display_shortest_path[vertex_index]

            road_id: str = vertex[1]
            road: UIRoad = self._roads[road_id]
            road.visible = in_shortest_path_mark
            road.colour = constants.SHORTEST_PATH_ROAD_COLOUR \
                if in_shortest_path_mark else self._get_apt_colour_by_road_id(road_id)

        if prev_index != -1:
            self._mark_road_as_in_shortest_path(
                shortest_paths, index=prev_index, prev_index=-1, in_shortest_path_mark=False
            )

    def _shift_to_next_shortest_path(self) -> None:
        """
        Shift to next shortest path present in our info display state which is instance of ShortestPathSuccessState.
        This also changes info display state to a newer version of ShortestPathSuccessState, with updated
        index.

        Preconditions:
            - isinstance(ShortestPathSuccessState, self._get_info_display_state())
        """
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

        # prevent mutation at distance.
        updated_info_display_state: ShortestPathSuccessState = deepcopy(info_display_state)
        updated_info_display_state.path_displayed_index = next_index
        self._set_info_display_state(updated_info_display_state)

    def _get_current_zoom_and_bounds(self) -> tuple[int, tuple[Coordinate, Coordinate]]:
        """
        Return current zoom and map bounds either from query parameters (updated from javascript) or
        from default values if they still have not been assigned.

        Preconditions:
            - self._default_session_state_dict.get('map_info') is not None

        Postconditions:
            - first element of tuple is zoom, second element of tuple is a tuple of Coordinates with first
            one as north east coordinates and seconds one as south west coordinates
        """
        query_params = st.query_params  # we don't write type annotations for this, as its type is a private
        # variable in streamlit libraries code.

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
            map_info: dict = self._default_session_state_dict['map_info']
            zoom = map_info['zoom']
            state_map_info_bounds = map_info['bounds']

        north_east_bounds: dict = state_map_info_bounds['_northEast']
        south_west_bounds: dict = state_map_info_bounds['_southWest']
        bounds: tuple[Coordinate, Coordinate] = (
            Coordinate(north_east_bounds['lat'], north_east_bounds['lng']),
            Coordinate(south_west_bounds['lat'], south_west_bounds['lng'])
        )
        return zoom, bounds

    def display(self) -> None:
        """
        Display anything which should be displayed using streamlit, as this method is the only method
        that gets rerun as streamlit runs the app from top down on any update.

        There are no preconditions to run this method, apart from info_display_state being in correct
        state as required by what should be displayed at that time.
        """
        info_display_state: InfoDisplayState = self._get_info_display_state()

        if isinstance(info_display_state, InfoDisplayLoadingState):
            # this is done to protect against data being accidently displayed while it is still being loaded,
            # in which case there are chances of error
            return
        elif isinstance(info_display_state, InfoDisplayErrorState):
            st.error('Error occurred while loading road network data from file. '
                     f'Ensure that the file {constants.ORN_FILE_NAME} is on the correct path.')
        elif isinstance(info_display_state, InfoDisplayDataLoadedState):

            with st.spinner('Building Map'):

                st.badge('Positive roads go south to north or west to east', color='blue')
                st.badge('Negative roads go north to south or east to west', color='gray')
                st.badge('Blue roads are positive roads and black roads are negative roads')
                st.badge('Red roads are removed roads', color='red')
                st.badge('Green roads are the ones that represent the shortest path when asked.', color='green')

                zoom_and_bounds: tuple[int, tuple[Coordinate, Coordinate]] = self._get_current_zoom_and_bounds()
                zoom: int = zoom_and_bounds[0]
                bounds: tuple[Coordinate, Coordinate] = zoom_and_bounds[1]

                # this is from _get_current_zoom_and_bounds return post condition
                north_east_bounds = bounds[0]
                south_west_bounds = bounds[1]

                south_west_bounds_lat: float = south_west_bounds.latitude
                south_west_bounds_lng: float = south_west_bounds.longitude

                # compute center of map from bounds, which is what location parameter takes below.
                folium_map: folium.Map = folium.Map(location=(
                    south_west_bounds_lat + ((north_east_bounds.latitude - south_west_bounds_lat) / 2),
                    south_west_bounds_lng + ((north_east_bounds.longitude - south_west_bounds_lng) / 2)
                ), zoom_start=zoom, max_zoom=constants.MAX_ZOOM, min_zoom=constants.MIN_ZOOM)

                self._compute_visible_roads_cached(zoom_level=zoom, bounds=bounds)

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
                columns: list = st.columns([0.7, 0.3])  # 70 % and 30 % space allotted
                # for map and buttons/text on screen

                with columns[1]:
                    st.text(f'Roads Currently Selected: {len(self._selected_roads)}')
                    st.button('Reload Polylines')  # the display method will run automatically
                    st.button('Compute Shortest Path', on_click=self._handle_compute_shortest_path)
                    st.button('Reset', on_click=self.reset)

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
                        many_shortest_paths_present: bool = total_shortest_paths > 1
                        path_word_as_per_number: str = f'path{'s' if many_shortest_paths_present else ''}'

                        st.text('Shortest paths computed successfully.')
                        st.text(f'There {'are' if many_shortest_paths_present else 'is'} in total '
                                f'{total_shortest_paths} shortest '
                                f'{path_word_as_per_number}.')
                        st.text(f'Displaying path number {info_display_state.path_displayed_index + 1} '
                                f'out of {total_shortest_paths} {path_word_as_per_number}')
                        st.text('Previous length of shortest path before removal of road segment was '
                                f'{info_display_state.prev_length} meters.')
                        st.text('Now, after removal, the length of shortest path '
                                f'is  {info_display_state.new_length} meters.')

                        if many_shortest_paths_present:
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

                    st.text('Please note that if you zoom in too much and then perform some action, '
                            'you wil have to zoom out and press reload polylines to see polylines '
                            'after your action is done. For instance, if you zoom in to remove a polyline, '
                            'and then you click Compute Shortest Path, and then you zoom out, '
                            'to see shortest paths, you might have to press Reload Polylines button '
                            'to see all other roads to get a full context. This lazy rendering of '
                            'polylines as per zoom has been done for performance reasons, as Python is '
                            'quite slow on its own.')

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
        'max-nested-blocks': 4,
        'extra-imports': ['coordinate', 'info_display', 'road_manager', 'ui_road', 'graph',
                          'streamlit_folium', 'folium', 'streamlit', 'shapely.geometry', 'collections.abc',
                          'constants', 'copy', 'fast_geo_json_file_loader'],
    })
