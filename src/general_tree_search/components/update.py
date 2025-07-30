from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def update_sum(agent: TreeSearchAgent, node: Node, children: list[Node]) -> dict:
    return _update(agent, node, children)


def get_update_minimax(key: str):
    def update_minimax(
        agent: TreeSearchAgent, node: Node, children: list[Node]
    ) -> dict:
        if node.is_fully_expanded():
            if node.is_max_node():
                static_evaluation = max(c.values[key] for c in children)
            else:
                static_evaluation = min(c.values[key] for c in children)
        else:
            static_evaluation = node.values[key]

        return _update(agent, node, children, static_evaluation)

    return update_minimax


def _update(
    agent: TreeSearchAgent,
    node: Node,
    children: list[Node],
    static_evaluation=None,
):
    static_evaluation = (
        static_evaluation
        if static_evaluation is not None
        else node.values["static_evaluation"]
    )

    # for c in children:
    #    print(c.values)

    sum_count = sum(c.values["sum_count"] for c in children) + node.values["count"]
    sum_utility = (
        sum(c.values["sum_utility"] for c in children) + node.values["utility"]
    )

    return {
        "static_evaluation": static_evaluation,
        "avg_utility": sum_utility / sum_count,
        "utility": node.values["utility"],
        "count": node.values["count"],
        "sum_utility": sum_utility,
        "sum_count": sum_count,
    }
