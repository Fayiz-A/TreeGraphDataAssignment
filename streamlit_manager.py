"""
TODO: add docstring
"""
import doctest

from coordinate import Coordinate
from info_display import InfoDisplayState
from road import Road
from road_manager import RoadManager
from ui_road import UIRoad

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
        pass

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
        # University of Toronto area location coordinates
        folium_map = folium.Map(location=[43.65843379478086, -79.38145637512207], zoom_start=11)

        roads: dict[str, UIRoad] = self._roads
        for road_id in roads:
            road: UIRoad = roads[road_id]

            if road.visible:
                road_data: Road = road.road
                folium.PolyLine(
                    locations=road_data.geometry,
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
        'extra-imports': ['coordinate', 'info_display', 'road_manager', 'ui_road', 'streamlit_folium', 'folium'],
    })
