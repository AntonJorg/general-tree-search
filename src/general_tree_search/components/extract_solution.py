from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def most_robust_child(agent: TreeSearchAgent, root: Node):
    most_robust_child = max(root._children, key=lambda c: c.values["sum_count"])
    return most_robust_child.generating_action


def minimax_child(agent: TreeSearchAgent, root: Node):
    if root.is_max_node():
        best_child = max(root._children, key=lambda c: c.values["static_evaluation"])
    else:
        best_child = min(root._children, key=lambda c: c.values["static_evaluation"])
    return best_child.generating_action
