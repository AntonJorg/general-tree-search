from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def update_sum(agent: TreeSearchAgent, node: Node, children: list[Node]) -> dict:
    count = sum(c.values["sum_count"] for c in children) + node.values["count"]
    utility = sum(c.values["sum_utility"] for c in children) + node.values["utility"]

    return {
        "count": node.values["count"],
        "utility": node.values["utility"],
        "sum_count": count,
        "sum_utility": utility,
    }


def update_minimax(agent: TreeSearchAgent, node: Node, children: list[Node]) -> dict:
    count = sum(c.values["sum_count"] for c in children) + node.values["count"]
    if node.unexpanded_actions:
        return {
            "minimax": node.values["minimax"],
            "evaluation": node.values["evaluation"],
            "sum_count": count,
            "count": node.values["count"],
        }

    if node.is_max_node():
        minimax = max(c.values["minimax"] for c in children)
    else:
        minimax = min(c.values["minimax"] for c in children)

    return {
        "minimax": minimax,
        "evaluation": node.values["evaluation"],
        "sum_count": count,
        "count": node.values["count"],
    }
