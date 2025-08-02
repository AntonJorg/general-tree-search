import random
import math

from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def get_additive_eval(keys: list[str], evaluate: callable):
    def additive_eval(agent: TreeSearchAgent, node: Node):
        value = {
            "static_evaluation": None,
            "utility": node.values["utility"],
            "sum_utility": node.values["sum_utility"],
            "sum_count": node.values["sum_count"] + 1,
        }

        evaluation = evaluate(node.state)

        for key in keys:
            value[key] += evaluation

        value["avg_utility"] = value["sum_utility"] / value["sum_count"]

        return value

    return additive_eval


def get_setter_eval(keys: list[str], evaluate: callable):
    def setter_eval(agent: TreeSearchAgent, node: Node):
        value = {
            "static_evaluation": None,
            "utility": node.values["utility"],
            "sum_utility": node.values["sum_utility"],
            "sum_count": node.values["sum_count"] + 1,
        }

        evaluation = evaluate(node.state)

        for key in keys:
            value[key] = evaluation

        value["avg_utility"] = value["sum_utility"] / value["sum_count"]

        return value

    return setter_eval


def simulate(state):
    while not state.is_terminal:
        action = random.choice(state.applicable_actions)
        state = state.result(action)

    return state.utility


def static_evaluation(state):
    if state.is_terminal:
        return state.utility

    if state.moves % 2:
        other_pieces = state.player_mask
        current_pieces = state.player_mask ^ state.piece_mask
    else:
        current_pieces = state.player_mask
        other_pieces = state.player_mask ^ state.piece_mask

    possible = state._possible()
    other_wins = state._winning_positions(other_pieces)
    forced = other_wins & possible
    if forced & (forced - 1):
        return 0

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

    return 1 / (1 + math.exp(-score))
