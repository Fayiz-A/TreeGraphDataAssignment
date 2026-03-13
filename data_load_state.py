from abc import ABC
from typing import Any


class DataLoadState(ABC):
    ...


class DataLoadSuccessState(DataLoadState):
    data: Any

    def __init__(self, data: Any) -> None:
        self.data = data


class DataLoadErrorState(DataLoadState):
    error: Any

    def __init__(self, error: Any) -> None:
        self.error = error
