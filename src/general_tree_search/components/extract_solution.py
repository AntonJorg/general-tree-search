import random

from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node, children


def most_robust_child(agent: TreeSearchAgent, root: Node):
    highest_count = max(c.values["sum_count"] for c in children(root))
    most_robust_child = random.choice(
        [c for c in children(root) if c.values["sum_count"] == highest_count]
    )
    return most_robust_child.generating_action


def get_minimax_child(key: str):
    def minimax_child(agent: TreeSearchAgent, root: Node):
        if root.is_max_node():
            best_val = max(c.values[key] for c in children(root))
        else:
            best_val = min(c.values[key] for c in children(root))

        best_child = random.choice(
            [c for c in children(root) if c.values[key] == best_val]
        )
        return best_child.generating_action

    return minimax_child
