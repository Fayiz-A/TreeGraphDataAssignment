"""
This file contains code for Tree data structure adapted
for use for representing Paths from a source node
"""

from __future__ import annotations
from typing import Optional


class PathTree:
    """
    A class for representing tree data structure for paths. This tree
    represents different paths from the target node all the way to
    a source node, where source node is a leaf. This structure is upside
    down, since algorithms like Dijktras (at least the way we implemented
    it) have it easier to trace the route back.

    For our project, the tree can only represent a string, and duplicate
    strings are allowed as two different subtrees, meaning
    if tree_1.root == tree_2.root, then that does not mean that
    they are the same tree or represent the same vertex.

    Representation Invariants:
        - self.root is not None or len(self.subtrees) == 0
    """

    subtrees: list[PathTree]
    root: Optional[tuple[str, str]]

    def __init__(self, root: tuple[str, str]) -> None:
        """
        TODO: check if constructors need docstrings, preconditions etc
        """
        self.subtrees = []
        self.root = root

    def is_empty(self) -> bool:
        """
        Return whether a tree is empty or not.

        There are no preconditions to use this method
        """
        return self.root is None

    def add_subtree(self, subtree: PathTree):
        """
        Add subtree as a child of this tree

        There are no preconditions to use this method
        """

        self.subtrees.append(subtree)

    def get_values(self) -> list[tuple[str, str]]:
        """
        Get all values of this tree as a list.

        Preconditions:
            - self.root is not None
        """
        values: list[tuple[str, str]] = [self.root]
        for subtree in self.subtrees:
            values.extend(subtree.get_values())

        return values

    def print_values(self, depth: int = 0) -> None:
        """
        Print all values of this tree, with each value indented (by '-' not spaces) as per its depth in tree.

        Preconditions:
            - depth >= 0
            - self.root is not None
        """
        print(f'{'-' * depth}{self.root}')

        for subtree in self.subtrees:
            subtree.print_values(depth + 1)

    def get_all_possible_paths(self) -> list[list[tuple[str, str]]]:
        """
        Return all possible paths from the root to each leaf node.

        Preconditions:
            - self.root is not None
        """

        possible_paths: list[list[tuple[str, str]]] = []

        subtrees: list[PathTree] = self.subtrees
        root: tuple[str, str] = self.root

        if len(subtrees) == 0:
            return [[root]]
        else:
            for subtree in subtrees:
                possible_paths.extend(subtree.get_all_possible_paths())

            for possible_path in possible_paths:
                possible_path.append(root)  # this is the advantage of having our tree upside down, with root of
                # the original tree being the target junction id from dijktras if that was used.

            return possible_paths
