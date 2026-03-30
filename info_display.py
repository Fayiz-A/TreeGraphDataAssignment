"""
Ontario Road Closure Analysis App
================================

This file contains the code for InfoDisplayState abstract class and its different subclasses, used
to represent state in StreamlitManager class.
"""
import doctest
from dataclasses import dataclass

from coordinate import Coordinate


class InfoDisplayState:
    """
    An abstract class to represent different states our home page can have. Using classes helps us
    pass data as per state, thus helping in encapsulation. Right now, most of these classes
    would be empty and would only be used for checking which state it is right now using isinstance,
    but there is inbuilt flexibility that if tomorrow we have to pass data around as per state, we
    can do them easily by adding attibutes to the subclasses.
    """
    def __init__(self) -> None:
        """
        This is an abstract class, so raise NotImplemented error if someone tried to instantiate this
        """
        raise NotImplementedError


@dataclass
class InfoDisplayLoadingState(InfoDisplayState):
    """
    Class to represent the state when information is being loaded/map is being built.

    Note: since streamlit does not allow business logic to continue somewhere else while its
    streamlist.spinner (loader) shows, this class would be used mainly for precautionary reasons
    (for instance preventing map rendering while data loads). Hence, during loading, keep
    the state variable in sync and update it to InfoDisplayLoadingState when loading starts.
    """


@dataclass
class InfoDisplayDataLoadedState(InfoDisplayState):
    """
    Class to represent the state when information has already been loaded and
    can be displayed to the user. While this class can be used, it has additional subclasses
    that can be used to make state related changes encapsulation more
    specific (see ShortestPathSuccessState class below for instance)
    """


@dataclass
class ShortestPathSuccessState(InfoDisplayDataLoadedState):
    """
    Class to represent the state when the result of shortest path computation is
    available. As this is a subclass of InfoDisplayDataLoadedState, it is very useful
    to display information to the side while map also remains, and does not disappear
    due to state changes.

    Instance Attributes:
        - prev_length: the length in meters (and stripped of decimals, see Graph.compute_shortest_path() method)
         of the shortest path from start_junction_location to end_junction_location before roads were removed.
        - new_length: the length of all shortest paths in meters after a sequence of road segments between
          start_junction_location and end_junction_location have been removed.
        - start_junction_location: the coordinates of start junction. Useful for placing marker there.
        - end_junction_location: the coordinates of end junction. Useful for placing marker there.
        - shortest_paths: a list of all shortest paths from start_junction_location to end_junction_location. For
          more details, see ShortestPathResult in graph.py
        - path_displayed_index: the index of the shortest path which has to be
          displayed to the user. The index is used to pick from shortest_paths list

    Representation Invariants:
        - prev_length > 0 and new_length > 0
        - len(shortest_paths) >= 1
        - path_displayed_index >= 0
    """
    prev_length: float
    new_length: float
    start_junction_location: Coordinate
    end_junction_location: Coordinate
    shortest_paths: list[list[tuple[str, str]]]
    path_displayed_index: int


@dataclass
class JunctionDisconnectedState(InfoDisplayDataLoadedState):
    """
    Class to represent the state when junction whose shortest path is being found get disconnected
    as a result of removal of roads.
    """


@dataclass
class InvalidRoadSelectionsState(InfoDisplayDataLoadedState):
    """
    Class to represent the state when the sequence of roads selected by the user is invalid. For a
    definition of invalid road selection, see Graph.check_is_valid_road_selection method.
    """


@dataclass
class InfoDisplayErrorState(InfoDisplayState):
    """
    Class to represent the state when some unexpected error happens during IO events: for now, only represents
    the error when ontario_road_network.geojson file is not able to load properly.
    """


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['coordinate'],
    })
