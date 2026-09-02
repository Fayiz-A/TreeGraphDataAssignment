"""
Ontario Road Closure Analysis App
================================

This file contains a concrete implementation of DataLoader abstract class to load geojson files efficiently.
"""
import doctest

import orjson
import streamlit

from data_loader import DataLoader
from data_load_state import DataLoadState, DataLoadSuccessState, DataLoadErrorState


class CompressedGeoJsonFileLoader(DataLoader):
    """
    A DataLoader that loads road network data from a GeoJSON file using orjson (meaning it loads
    them a lot faster than geojson or json libraries do).

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

    @streamlit.cache_resource
    def load(_self) -> DataLoadState:
        """
        Load a .geojson file, and then return instance of DataLoadErrorState
        in case of error or DataLoadSuccessState along with the file data in case of successful load.

        Preconditions:
            - self.file_name points to a valid .geojson file.
        """
        try:
            # code inspired from
            # https://dev.to/h4c5/json-in-data-science-projects-tips-tricks-2n1p
            with open(_self.file_name, 'rb') as file:
                data = orjson.loads(file.read())
                return DataLoadSuccessState(data)
        except Exception as e:
            # this print would not be removed, so there is more context to troubleshoot in case error happens
            # even in production.
            print(f'Exception occurred while opening a geojson file with filename {_self.file_name}: {e}')
            return DataLoadErrorState(e)


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    # note: python ta shows that using Exception clause is too broad as it leads to undetected errors,
    # but that won't happen with us, as we are logging the error and even returning it wrapped in an
    # object (DataLoadErrorState) back to the one who called the load method.
    # second note: python_ta catches a false positive that orjson.loads does not exist. This is not true, and
    # it does exist.

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'allowed-io': ['FastGeoJsonFileLoader.load'],
        'extra-imports': ['orjson', 'data_load_state', 'data_loader'],
    })
