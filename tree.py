"""
This file contains code for Tree data structure
"""

from __future__ import annotations
from typing import Optional


class Tree:
    """
    A class for representing tree data structure. For our project, the tree can only represent a string, and
    duplicate strings are allowed as two different subtrees, meaning if tree_1.root == tree_2.root, then
    that does not mean that they are the same tree.

    Representation Invariants:
        - leaves >= 0
        - self.root is not None or len(self.subtrees) == 0
    """

    subtrees: list[Tree]
    root: Optional[str]
    leaves: int

    def __init__(self, root: str) -> None:
        """
        TODO: check if constructors need docstrings, preconditions etc
        """
        self.subtrees = []
        self.root = root
        self.leaves = 1

    def is_empty(self) -> bool:
        """
        Return whether a tree is empty or not.

        There are no preconditions to use this method
        """
        return self.root is None

    def is_leaf(self) -> bool:
        """Return if this tree is a leaf or not. A tree is a leaf if and only if it does not have
        any subtrees

        There are no preconditions to use this method
        """
        return len(self.subtrees) == 0

    def add_subtree(self, subtree: Tree):
        """
        Add subtree as a child of this tree

        There are no preconditions to use this method
        """
        if not self.is_leaf():
            self.leaves += 1

        self.subtrees.append(subtree)

    def get_values(self) -> list[str]:
        values: list[str] = [self.root]
        for subtree in self.subtrees:
            values.extend(subtree.get_values())

        return values

    def print_values(self, depth: int = 0) -> None:
        print(f'{'-' * depth}{self.root}')

        for subtree in self.subtrees:
            subtree.print_values(depth + 1)
