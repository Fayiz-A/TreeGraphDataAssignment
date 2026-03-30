"""
Ontario Road Closure Analysis App
================================
"""

from dataclasses import dataclass

from coordinate import Coordinate


class InfoDisplayState:
    """
    An abstract class to represent different states our home page can have. Using classes helps us
    pass data as per state, thus helping in encapsulation. Right now, most of these classes
    would be empty and would only be used for checking which state it is right now using isinstance,
    but there is inbuilt flexibility that if tomorrow we have to pass data around as per state, we
    can do them easily by adding attibutes to the subclasses
    """
    def __init__(self):
        """
        This is an abstract class, so raise NotImplemented error if someone tried to instantiate this
        """
        raise NotImplementedError


class InfoDisplayLoadingState(InfoDisplayState):
    """

    TODO: continue this
    """


class InfoDisplayDataLoadedState(InfoDisplayState):
    """
    TODO: continue this
    """


@dataclass
class ShortestPathSuccessState(InfoDisplayDataLoadedState):
    prev_length: float
    new_length: float
    start_junction_location: Coordinate
    end_junction_location: Coordinate
    shortest_paths: list[list[tuple[str, str]]]
    path_displayed_index: int


class JunctionDisconnectedState(InfoDisplayDataLoadedState):
    pass


class InvalidRoadSelectionsState(InfoDisplayDataLoadedState):
    pass


class InfoDisplayErrorState(InfoDisplayState):
    pass
