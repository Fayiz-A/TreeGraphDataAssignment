"""
Unit test suite for Graph.compute_shortest_path method using network x's dijktras method
"""

import networkx as nx
from random import random, randint

from coordinate import Coordinate
from graph import Graph, ShortestPathResult, _Vertex
from math import isclose

import timeit


def _generate_random_directed_weighted_complete_graphs_for_testing(vertices_num: int) -> tuple[nx.DiGraph, Graph]:
    """
    Generate and return a COMPLETE graph with vertices=vertices_num, the first element returned being an instance
    of networkx graph and the second one being an instance of Graph
    """

    # code inspired from https://stackoverflow.com/questions/56209291/
    graph: nx.DiGraph = nx.complete_graph(vertices_num, nx.DiGraph())
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

    return graph, test_graph


def test_compute_shortest_path() -> None:
    # making this around 100 would make the test case very slow, due to there being a complete graph
    # generated below, and all of its shortest paths from all possible start and end pairs being checked
    vertices_num: int = 50

    graphs: tuple[nx.DiGraph, Graph] =\
        _generate_random_directed_weighted_complete_graphs_for_testing(vertices_num)

    nx_graph: nx.DiGraph = graphs[0]
    test_graph: Graph = graphs[1]

    shortest_path_matrix = dict(nx.all_pairs_dijkstra_path(nx_graph))
    shortest_path_length_matrix = dict(nx.all_pairs_dijkstra_path_length(nx_graph))

    test_graph_vertices: dict[str, _Vertex] = test_graph.vertices

    for start_vertex in test_graph_vertices:
        for end_vertex in test_graph_vertices:
            if start_vertex != end_vertex:
                actual_shortest_path: ShortestPathResult =\
                    test_graph.compute_shortest_path(str(start_vertex), str(end_vertex))

                start_vertex_int: int = int(start_vertex)
                end_vertex_int: int = int(end_vertex)

                all_possible_paths: list[list[str]] = [[vertex_info[0]
                                                       for vertex_info in shortest_path]
                                                       for shortest_path in actual_shortest_path.all_shortest_paths]

                assert ([str(vertex) for vertex in shortest_path_matrix[start_vertex_int][end_vertex_int]] in
                        all_possible_paths)
                assert isclose(actual_shortest_path.length,
                               shortest_path_length_matrix[start_vertex_int][end_vertex_int])


def test_time_compute_shortest_path() -> None:
    graphs: tuple[nx.DiGraph, Graph] = \
        _generate_random_directed_weighted_complete_graphs_for_testing(vertices_num=1000)  # approximately
    # 500,000 edges/roads

    vertices = list(graphs[1].vertices.keys())

    # using timeit with globals like this seen from https://stackoverflow.com/a/25769110
    seconds: float = timeit.timeit(
        'graphs[1].compute_shortest_path(vertices[0], vertices[randint(0, 1000)])',
        number=10, globals={'graphs': graphs, 'vertices': vertices, 'randint': randint})  # should take at most about
    # about 40 million iterations per method call at most due to
    # 500,000 edges (considering constant factors also roughly), so in total about
    # 40 million * 10 times we call compute_shortest_path = appproximately
    # 400 million iterations at most.
    # We have about 2 million roads in our data, so compute_shortest_path would take about 200 million iterations
    # at most as it is O(ElogE) where E is the number of edges (not theta, but big O) and we are also thinking about
    # constant factors roughly speaking here. If seconds variable comes out to be under 2 seconds,
    # then compute_shortest_path method for our data would work in way less than that time.

    # note: the doctest might take more time than seconds, as it includes time for
    # _generate_random_directed_weighted_complete_graphs_for_testing method also, but
    # what matters is the time taken by
    assert seconds < 2
