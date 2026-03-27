import gzip
import geojson
from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState, DataLoadErrorState


class FileLoader(DataLoader):
    """
    A DataLoader that loads road network data from a compressed GeoJSON file.

    Instance Attributes:
        - file_name: path to a .geojson.gz file

    Representation Invariants:
        - self.file_name must be a path to a .geojson.gz file
    """
    file_name: str

    def __init__(self, file_name: str) -> None:
        """
        Initialize the FileLoader with a path to a geojson.gz file.
        """
        self.file_name = file_name

    def load(self) -> DataLoadState:
        """
        Load and decompress a .geojson.gz file, and then return instance of DataLoadErrorState
        in case of error and DataLoadSuccessState along with the data in case of successful load.

        Preconditions:
            - self.file_name points to a valid .geojson.gz file.
        """
        try:
            # code inspired from https://www.tutorialspoint.com/python/gzip_module.htm and
            # https://pypi.org/project/geojson/
            with gzip.open(self.file_name, 'r') as f:
                data = geojson.load(f)
            return DataLoadSuccessState(data)
        except Exception as e:
            print(f'Exception occurred while opening a geojson file with filename {self.file_name}: {e}')
            return DataLoadErrorState(e)
