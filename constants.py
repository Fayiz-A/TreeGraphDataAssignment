"""
Ontario Road Closure Analysis App
================================

This file is for storing all constants that are used in this program.
"""

SESSION_STATE_STREAMLIT_MANAGER_KEY: str = 'streamlit_manager'

ORN_FILE_NAME = 'ontario_road_network.geojson'

MIN_ZOOM: int = 5
MAX_ZOOM: int = 19
INITIAL_ZOOM: int = 14

BIG_ENOUGH_ZOOM_THRESHOLD: int = 13
TRANSLATION_DELTA: float = 0.00002

INFINITY: int = 1_000_000_000_000

ROAD_POSITIVE_SUFFIX: str = '_pos'
ROAD_NEGATIVE_SUFFIX: str = '_neg'

SELECTED_ROAD_COLOUR: str = '#FF0000'  # red colour
SHORTEST_PATH_ROAD_COLOUR: str = '#13f207'  # green colour

ROAD_UNIDIRECTIONAL_COLOR: str = '#492201'  # brown colour
ROAD_POSITIVE_COLOR: str = '#69a2ff'  # blue colour
ROAD_NEGATIVE_COLOR: str = '#000000'  # black colour
