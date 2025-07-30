import random
import math
import pickle

from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def get_static_evaluation_with_lookup():
    with open("data/lookup.pkl", "rb") as f:
        lookup = pickle.load(f)

    def static_evaluation_with_lookup(agent: TreeSearchAgent, node: Node):
        s = node.state
        if (util := lookup.get((s.piece_mask, s.player_mask))) is not None:
            return _evaluate(agent, node, static_evaluation=util)
        return static_evaluation(agent, node)

    return static_evaluation_with_lookup


def static_evaluation(agent: TreeSearchAgent, node: Node):
    state = node.state

    if state.is_terminal:
        return _evaluate(agent, node, static_evaluation=state.utility)

    if state.moves % 2:
        other_pieces = state.player_mask
        current_pieces = state.player_mask ^ state.piece_mask
    else:
        current_pieces = state.player_mask
        other_pieces = state.player_mask ^ state.piece_mask

    shifts = [state.height + 1, 1, state.height, state.height + 2]

    # count 2 connected
    current_two = 0
    other_two = 0
    for shift in shifts:
        current_two += (current_pieces & current_pieces >> shift).bit_count()
        other_two += (other_pieces & other_pieces >> shift).bit_count()

    # count three connected
    current_three = 0
    other_three = 0
    for shift in shifts:
        m = current_pieces & current_pieces >> shift
        current_three += (m & m >> shift).bit_count()
        m = other_pieces & other_pieces >> shift
        other_three += (m & m >> shift).bit_count()

    col_mask = 2 ** (state.height) - 1
    weights = list(range(math.ceil(state.width / 2))) + list(
        reversed(range(state.width // 2))
    )
    weights = (w + 1 for w in weights)

    current_position = 0
    other_position = 0
    for i, weight in enumerate(weights):
        current_position += (
            current_pieces & col_mask << i * (state.height + 1)
        ).bit_count() * weight
        other_position += (
            other_pieces & col_mask << i * (state.height + 1)
        ).bit_count() * weight

    score = (
        (current_position - other_position) * 0.01
        + (current_two - other_two) * 0.1
        + current_three
        - other_three
    )

    static_evaluation = 1 / (1 + math.exp(-score))

    return _evaluate(agent, node, static_evaluation=static_evaluation)


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

    return _evaluate(agent, node, rollout=state.utility)


def _evaluate(
    agent: TreeSearchAgent,
    node: Node,
    rollout=None,
    static_evaluation=None,
):
    rollout = rollout if rollout is not None else 0
    static_evaluation = (
        static_evaluation
        if static_evaluation is not None
        else node.values["static_evaluation"]
    )

    sum_utility = node.values["sum_utility"] + rollout
    sum_count = node.values["sum_count"] + 1

    return {
        "static_evaluation": static_evaluation,
        "avg_utility": sum_utility / sum_count,
        "utility": node.values["utility"] + rollout,
        "count": node.values["count"] + 1,
        "sum_utility": sum_utility,
        "sum_count": sum_count,
    }
