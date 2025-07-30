import math
from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def get_choose_uct(utility_estimate: str):
    def choose_uct(agent: TreeSearchAgent, node: Node, children: list[Node]):
        N = node.values["sum_count"]

        is_max_node = node.is_max_node()

        def ucb1(c: Node):
            exploit = c.values[utility_estimate]

            assert 0 <= exploit <= 1, "Invalid avg. utility!"

            if not is_max_node:
                exploit = 1 - exploit

            explore = math.sqrt(2 * math.log(N) / c.values["sum_count"])

            return exploit + explore

        return max(children, key=ucb1)

    return choose_uct


def get_choose_principal_variation(utility_estimate: str):
    def choose_principal_variation(
        agent: TreeSearchAgent, node: Node, children: list[Node]
    ):
        if node.is_max_node():
            return max(children, key=lambda c: c.values[utility_estimate])
        else:
            return min(children, key=lambda c: c.values[utility_estimate])

    return choose_principal_variation
