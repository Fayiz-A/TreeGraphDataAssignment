from typing import Optional


class InfoDisplayState:


class InfoDisplayInitState(InfoDisplayState):


class InfoDisplayRemoveSuccessState(InfoDisplayState):

    new_length: Optional[float]
    prev_length: float


class InfoDisplayErrorState(InfoDisplayState):

    error: str
