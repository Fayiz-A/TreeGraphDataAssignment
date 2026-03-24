import gzip
import geojson
from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState, DataLoadErrorState


class FileLoader(DataLoader):
    file_name: str

    def __init__(self, file_name: str) -> None:
        """
        Initialize the FileLoader with a path to a .gz file.
        """
        self.file_name = file_name

    def load(self) -> DataLoadState:
        """
        Loads and decompresses a .geojson.gz file.

        Preconditions:
            - self.file_name points to a valid .gz file containing GeoJSON.
        """
        try:
            with gzip.open(self.file_name, 'r') as f:
                data = geojson.load(f)
            return DataLoadSuccessState(data)
        except Exception as e:
            print(e)
            return DataLoadErrorState(e)
