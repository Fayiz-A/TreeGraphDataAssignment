from Coordinate import Coordinate
from InfoDisplay import InfoDisplayState
from RoadManager import RoadManager
from UIRoad import UIRoad


class StreamlitManager:
    _road_manager: RoadManager
    _roads: dict[str, UIRoad]
    _selected_roads: dict[str, UIRoad]
    _info_display_state: InfoDisplayState


    def __init__(self) -> None:

    def _handle_road_removal(self) -> None:

    def _get_road_id_by_selection(self, point: Coordinate) -> UIRoad | None:

    def _update_visible_roads_by_bounds(self, zoom_level: int, bounds: tuple[Coordinate, Coordinate]) -> None:

    def reset(self) -> None:

    def display(self) -> None:
