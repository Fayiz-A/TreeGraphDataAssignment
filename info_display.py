from dataclasses import dataclass

from coordinate import Coordinate


class InfoDisplayState:
    def __init__(self):
        """
        This is an abstract class, so raise unimplemented error if someone tried to instantiate this
        """
        pass
        # raise NotImplementedError


class InfoDisplayLoadingState(InfoDisplayState):
    """
    Immutable
    TODO: continue this
    """
    # message: str


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
    error: str
