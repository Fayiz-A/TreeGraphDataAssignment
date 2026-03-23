"""
Unit test suite for Graph.compute_shortest_path method using network x's dijktras method
"""

import networkx as nx
from random import random

from coordinate import Coordinate
from graph import Graph, _Vertex
from math import isclose


def test_compute_shortest_path() -> None:
    # making this around 100 would make the test case very slow
    vertices_num: int = 50

    # code inspired from https://stackoverflow.com/questions/56209291/
    graph: nx.Graph = nx.complete_graph(vertices_num, nx.DiGraph())
    test_graph: Graph = Graph()

    coordinate: Coordinate = Coordinate(70.0, 70.0)

    for (start, end) in graph.edges:
        random_weight: float = 1 + (random() * 100_000)

        start_str: str = str(start)
        end_str: str = str(end)

        test_graph.add_junction(start_str)
        test_graph.add_junction(end_str)

        test_graph.add_road(start_str, end_str, random_weight, f'{start}->{end}',
                            removed=False, geometry=[coordinate, coordinate]
                            )

        graph.edges[start, end]['weight'] = random_weight

    shortest_path_matrix = dict(nx.all_pairs_dijkstra_path_length(graph))

    test_graph_vertices: dict[str, _Vertex] = test_graph.vertices

    for start_vertex in test_graph_vertices:
        for end_vertex in test_graph_vertices:
            if start_vertex != end_vertex:
                actual_shortest_path: tuple[list[_Vertex], float] =\
                    test_graph.compute_shortest_path(str(start_vertex), str(end_vertex))
                assert isclose(actual_shortest_path[1], shortest_path_matrix[int(start_vertex)][int(end_vertex)])
