import json
from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState


class FileLoader(DataLoader):
    file_name: str

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    def load(self) -> DataLoadState:
        with open(self.file_name, 'r') as f:
            data = json.load(f)
        return DataLoadSuccessState(data)
