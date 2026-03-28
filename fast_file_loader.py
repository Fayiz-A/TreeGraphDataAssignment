import orjson
from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState, DataLoadErrorState

class FastFileLoader(DataLoader):
    """
    A DataLoader that loads road network data from a GeoJSON file.

    Instance Attributes:
        - file_name: path to a .geojson file

    Representation Invariants:
        - self.file_name must be a path to a .geojson file
    """
    file_name: str

    def __init__(self, file_name: str) -> None:
        """
        Initialize the FileLoader with a path to a geojson file.
        """
        self.file_name = file_name

    def load(self) -> DataLoadState:
        """
        Load a .geojson file, and then return instance of DataLoadErrorState
        in case of error and DataLoadSuccessState along with the data in case of successful load.

        Preconditions:
            - self.file_name points to a valid .geojson.gz file.
        """
        try:
            # code inspired from
            # https://dev.to/h4c5/json-in-data-science-projects-tips-tricks-2n1p
            with open(self.file_name, 'rb') as file:
                data = orjson.loads(file.read())
                return DataLoadSuccessState(data)
        except Exception as e:
            print(f'Exception occurred while opening a geojson file with filename {self.file_name}: {e}')
            return DataLoadErrorState(e)
