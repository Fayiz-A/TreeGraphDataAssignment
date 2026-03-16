from typing import Optional


class InfoDisplayState:
    pass


class InfoDisplayInitState(InfoDisplayState):
    pass


class InfoDisplayRemoveSuccessState(InfoDisplayState):
    new_length: Optional[float]
    prev_length: float


class InfoDisplayErrorState(InfoDisplayState):
    error: str
