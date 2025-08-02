from collections import defaultdict
from general_tree_search.games import GameState


class Node[T]:
    """
    Implementation of a search tree (Definition 3).

    For clarity, the state, action, and value functions (s(n), a(n, m), and v(n))
    are implemented as simple instance variables, not separate getter functions.
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

    def is_fully_expanded(self):
        return not self.unexpanded_actions

    def is_max_node(self):
        return (self.state.moves % 2) == 0

    def to_tree_string(self, indent=0, max_indent=None):
        if max_indent is not None and indent > max_indent:
            return ""

        string = indent * "--" + str(self) + "\n"
        for c in self._children:
            string += c.to_tree_string(indent + 1, max_indent)
        return string


def parent[T](node: Node[T]) -> Node[T] | None:
    return node._parent


def children[T](node: Node[T]) -> list[Node[T]]:
    return node._children


def single_expand[T](node: Node[T]) -> Node[T]:
    if node.state.is_terminal or not node.unexpanded_actions:
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
