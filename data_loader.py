from abc import ABC, abstractmethod
from data_load_state import DataLoadState


class DataLoader(ABC):
    @abstractmethod
    def load(self) -> DataLoadState:
        ...
