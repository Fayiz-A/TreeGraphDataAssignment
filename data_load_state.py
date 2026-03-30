"""
Ontario Road Closure Analysis App
================================

This file contains the code for an abstract class DataLoadState and its subclasses that represent
various states that data loading might lead to.
"""
import doctest
from dataclasses import dataclass
from abc import ABC
from typing import Any


class DataLoadState(ABC):
    """
    An abstract class to represent a parent class for all different types of data load states that might
    occur when data gets loaded (successfully or unsuccessfully).
    """


@dataclass
class DataLoadSuccessState(DataLoadState):
    """
    A dataclass to represent the state when a file gets loaded successfully.

    Instance Attributes:
        - data: the data read from the file

    There are no representation invariants for this class.
    """
    data: Any


@dataclass
class DataLoadErrorState(DataLoadState):
    """
    A dataclass to represent the state when a file does *not* load successfully.

    Instance Attributes:
        - error: the error encountered due to which file was not able to get loaded/read

    There are no representation invariants for this class.
    """
    error: Any


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['abc'],
    })
