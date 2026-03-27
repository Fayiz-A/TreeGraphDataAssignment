"""
TODO: add docstring
"""
import doctest

from coordinate import Coordinate
from info_display import InfoDisplayState, InfoDisplayInitState
from road_manager import RoadManager
from ui_road import UIRoad
from graph import Road

import streamlit_folium
import folium


class StreamlitManager:
    """
    TODO: add docstring and representation invariants
    """
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, UIRoad]
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
            bounds=(Coordinate(43.68984603369737, -79.42711830139162),
                    Coordinate(43.64638600677007, -79.36489105224611))
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
        """
        Display anything which should be displayed using streamlit, as this method is the only method
        that gets rerun as streamlit runs the app from top down on any update.
        """
        print('displaying')
        # University of Toronto area location coordinates
        folium_map = folium.Map(location=[43.65843379478086, -79.38145637512207], zoom_start=11)

        roads: dict[str, UIRoad] = self._roads
        for road_id in roads:
            road: UIRoad = roads[road_id]

            if road.visible:
                road_data: Road = road.road
                folium.PolyLine(
                    locations=road_data.get_geometry_coordinates_tuple(),
                    tooltip=road_data.road_id,
                    color=road.colour
                ).add_to(folium_map)

        # call to render Folium map in Streamlit
        streamlit_folium.st_folium(
            folium_map,
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
