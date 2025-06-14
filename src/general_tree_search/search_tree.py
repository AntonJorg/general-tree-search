import itertools
from collections import defaultdict
from general_tree_search.games import GameState


class Node[T]:
    """
    From article:

    A search tree of a state transition
    system Σ = (S, A, γ, s0) is a tuple T = (N, E, V, s, a, v)
    where (N, E) is a finite, rooted tree with root n0, V is a set
    of values, s : N → S maps nodes to states, a : E → A
    maps edges to actions, and v : N → V is a partial map
    from nodes to values. We refer to s(n) as the state of n, a(e)
    as the action of e, and v(n) as the value of n. We require
    that s(n0) = s0, and that for all (n1, n2) ∈ E, s(n2) =
    γ(s(n1), a(n1, n2)).
    """

    def __init__(
        self,
        state: GameState[T],
        parent: "Node[T] | None",
        generating_action: T | None,
        depth: int = 0,
        keys: list[str] | None = None,
    ):
        self._parent = parent
        self._children: list[Node[T]] = []
        self.depth = depth

        self.state = state
        self.generating_action = generating_action
        self.unexpanded_actions = self.state.applicable_actions.copy()

        self.values: dict[str] = defaultdict(float)

    def __repr__(self):
        return f"Node[{self.values}]"

    def __hash__(self):
        return self.id

    def is_fully_expanded(self):
        return not self.unexpanded_actions

    def is_max_node(self):
        return (self.depth % 2) == 0

    def to_tree_string(self, indent=0, max_indent=None):
        if max_indent is not None and indent > max_indent:
            return ""

        string = indent * "--" + str(self) + "\n"
        for c in self._children:
            string += c.to_tree_string(indent + 1, max_indent)
        return string


def get_parent[T](node: Node[T]) -> Node[T] | None:
    return node._parent


def get_children[T](node: Node[T]) -> list[Node[T]]:
    return node._children


def set_values[T](node: Node[T], values: dict[str]) -> None:
    node.values = values


def expand_one[T](node: Node[T]) -> Node[T]:
    if not node.unexpanded_actions:
        return node
    action = node.unexpanded_actions.pop()
    state = node.state.result(action)
    child = Node(
        state=state,
        parent=node,
        generating_action=action,
        depth=node.depth + 1,
    )
    node._children.append(child)
    return child
