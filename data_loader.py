"""
This file contains code for the abstract class DataLoader, used in a polymorphic way to load
data in other parts of the code.
"""
import doctest
from abc import ABC, abstractmethod
from data_load_state import DataLoadState


class DataLoader(ABC):
    """
    An abstract class that can be used for dependency injection (see RoadManager class' constructor and how
    StreamlitManager injects a subclass of this abstract class as a dependency). This leads to polymorphic code,
    and will make mocking for future tests very easy.
    """
    @abstractmethod
    def load(self) -> DataLoadState:
        """
        Return instance of DataLoadSuccessState with file data or DataLoadErrorState based on
        if the file opens and loads successfully or not.

        An abstract method to load any kind of data from any kind of file. This is
        extremely generic, and hence can be used in a variety of contexts. But for this project,
        it would load only a geojson file.
        """


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    # NOTE: python ta might give warning aboubt DataLoader.load not returning anything, but it is
    # an abstract method, so it is not an issue.
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['data_load_state', 'abc'],
    })
