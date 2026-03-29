from dataclasses import dataclass


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


@dataclass(slots=True, frozen=True)
class ShortestPathSuccessState(InfoDisplayDataLoadedState):
    prev_length: float
    new_length: float
    shortest_paths: list[list[tuple[str, str]]]


class JunctionDisconnectedState(InfoDisplayDataLoadedState):
    pass


class InvalidRoadSelectionsState(InfoDisplayDataLoadedState):
    pass


class InfoDisplayErrorState(InfoDisplayState):
    error: str
