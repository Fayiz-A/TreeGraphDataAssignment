"""
Ontario Road Closure Analysis App
================================

This file contains code for UIRoad class, which is a wrapper over
Road class to add attributes useful for our StreamlitManager boundary class
"""
import doctest
from dataclasses import dataclass

from graph import Road


@dataclass
class UIRoad:
    """
    A dataclass to represent a wrapper over Road with useful properties for StreamlitManager
    boundary class.

    Instance Attributes:
        - road: a road (edge) from the graph
        - visible: a flag about whether this road should be displayed on the map or not. Note: this is different
        from road.remove attribute because a road might be removed (soft deleted) but still visible, but in a
        different colour.
        - colour: the colour of this road.

    Representation Invariants:
        - self.colour is a valid colour string
        - self.road is in the graph that the map which uses this class also uses.
    """
    road: Road
    visible: bool
    colour: str


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['graph'],
    })
