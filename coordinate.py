"""
Ontario Road Closure Analysis App
================================

This file contains code for Coordinate dataclass, used throughout the project for better representation
of coordinates which this app deals with extensively.
"""
import doctest
from dataclasses import dataclass


@dataclass
class Coordinate:
    """
    A dataclass to represent coordinate

    Instance Attributes:
        latitude: the latitude part of coordinate in decimal degrees
        longitude: the longitude part of coordinate in decimal degrees

    Representation Invariants:
        - -180 <= self.longitude <= 180
        - -90 <= self.latitude <= 90

    >>> c: Coordinate = Coordinate(-77.01, 43.0)
    """
    latitude: float
    longitude: float

    def to_tuple(self) -> tuple[float, float]:
        """
        Return a tuple of latitude and longitude in (latitude, longitude)  order.

        There are no preconditions to use this method.

        >>> c: Coordinate = Coordinate(-77.01, 43.0)
        >>> c.to_tuple()
        (-77.01, 43.0)
        """
        return self.latitude, self.longitude


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
    })
