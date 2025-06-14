import random
from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def static_evaluation(agent: TreeSearchAgent, node: Node):
    v = random.random()
    return {
        "evaluation": v,
        "minimax": v,
        "count": 1,
        "sum_count": 1,
    }


def simulate(agent: TreeSearchAgent, node: Node):
    state = node.state
    n = 0
    while not state.is_terminal:
        action = random.choice(state.applicable_actions)
        state = state.result(action)
        n += 1

    if not agent.search_stats["simulation_lengths"]:
        agent.search_stats["simulation_lengths"] = []
    agent.search_stats["simulation_lengths"].append(n)

    return {
        "utility": state.utility,
        "count": 1,
        "sum_utility": state.utility,
        "sum_count": 1,
    }
