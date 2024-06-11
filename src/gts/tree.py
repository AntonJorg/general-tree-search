from __future__ import annotations
from typing import Generic, TypeVar

from gts.games import GameState


T = TypeVar("T")


class TreeSearchNode(Generic[T]):
    """
    Generic doubly linked tree data structure.

    Models the Node data structure from Algorithm 7. Since python does not
    support private attributes everything is public, and respecting component
    function permissions is up to the implementation.
    """

    def __init__(
        self,
        state: GameState[T],
        parent: "TreeSearchNode[T] | None",
        generating_action: T | None,
        depth: int = 0,
        alpha=None,
        beta=None,
    ):
        # TODO: Move alg. specific parameters e.g. alpha and beta

        # data structure
        self.parent = parent
        self.children: list["TreeSearchNode[T]"] = []
        self.depth = depth

        # game related information
        self.state = state
        self.generating_action = generating_action
        # [:] equals .copy() but works for py4j.java_collections.JavaList as well
        self.unexpanded_actions = state.applicable_actions[:]
        self.branching_factor = len(self.unexpanded_actions)

        # search related information
        # TODO: Consider using a value dictionary
        self.eval = None
        self.cumulative_utility = 0.0
        self.count = 0
        self.evaluated = False
        self.alpha = -float("inf") if alpha is None else alpha
        self.beta = float("inf") if beta is None else beta
        self.is_max_node = not state.moves % 2

    def __repr__(self):
        return f"Node(action={self.generating_action}, \
utility={self.cumulative_utility}, count={self.count}, \
evaluation={self.eval}, depth={self.depth})"

    def print_tree(self, max_depth: int | None = None, depth: int = 0):
        print(depth * "--", self)
        if max_depth is None or depth < max_depth:
            for c in self.children:
                c.print_tree(max_depth, depth + 1)

    def add_child(self, state: GameState[T], generating_action: T) -> "TreeSearchNode":
        """
        Generates a new TreeSearchNode and adds it to self.children.
        """
        child = TreeSearchNode(
            state, self, generating_action, self.depth + 1, self.alpha, self.beta
        )

        self.children.append(child)

        return child

    def reset(self) -> None:
        """
        Deletes all children and resets unexpanded actions.
        """
        self.__init__(self.state, self.parent, self.generating_action, self.depth)

    def copy(self) -> "TreeSearchNode":
        node = TreeSearchNode(self.state, self.parent, self.generating_action)
        node.__dict__ = self.__dict__.copy()
        return node
