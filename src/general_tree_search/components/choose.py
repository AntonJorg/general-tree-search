import math
from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def choose_uct(agent: TreeSearchAgent, node: Node, children: list[Node]):
    N = sum(c.values["count"] for c in children) + 1

    def ucb1(c: Node):
        if node.is_max_node():
            exploit = c.values["sum_utility"] / c.values["sum_count"]
        else:
            exploit = (c.values["sum_count"] - c.values["sum_utility"]) / c.values[
                "sum_count"
            ]

        explore = math.sqrt(2 * math.log(N) / c.values["sum_count"])

        return exploit + explore

    return max(children, key=ucb1)


def choose_principal_variation(
    agent: TreeSearchAgent, node: Node, children: list[Node]
):
    if node.is_max_node():
        return max(children, key=lambda c: c.values["minimax"])
    else:
        return min(children, key=lambda c: c.values["minimax"])
