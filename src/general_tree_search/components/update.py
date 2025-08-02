from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def get_update_sum(key: str):
    def update_sum(agent: TreeSearchAgent, node: Node, children: list[Node]) -> dict:
        values = node.values.copy()
        values["sum_count"] += 1

        values["sum_utility"] = (
            sum(c.values["sum_utility"] for c in children) + node.values[key]
        )

        values["avg_utility"] = values["sum_utility"] / values["sum_count"]

        return values

    return update_sum


def get_update_minimax(key: str):
    def update_minimax(
        agent: TreeSearchAgent, node: Node, children: list[Node]
    ) -> dict:
        values = node.values.copy()
        if node.is_fully_expanded() and children:
            if node.is_max_node():
                static_evaluation = max(c.values[key] for c in children)
            else:
                static_evaluation = min(c.values[key] for c in children)
        else:
            static_evaluation = values[key]

        values["sum_count"] += 1
        values["avg_utility"] = values["sum_utility"] / values["sum_count"]

        values[key] = static_evaluation

        return values

    return update_minimax
