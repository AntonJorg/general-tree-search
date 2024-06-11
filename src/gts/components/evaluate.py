"""
Defines methods for implementing TreeSearchAgent.evaluate.

These methods should:
    - Take a GameState
    - Return an estimate of the utility of the state, as a float (or a list of floats)
    - Not have any side effects
    - Not have to be deterministic
"""
import random
from math import ceil, exp

# TODO: Remove dependency on specific games via GGP heuristics
from gts.games import *


def evaluate_utility(state: GameState, params: dict, search_info: dict):
    if state.is_terminal:
        return state.utility
    else:
        return None


def simulate(state: GameState, params: dict, search_info: dict):
    while not state.is_terminal:
        action = random.choice(state.applicable_actions)
        state = state.result(action)
    return state.utility


def simulate_many(state: GameState, params: dict, search_info: dict):
    n = params["num_simulations"]
    values = (simulate(state, params) for _ in range(n))
    return sum(values) / n


def simulate_stochastic_environment(state: GameState, params: dict, search_info: dict):
    while not state.is_terminal:
        if hasattr(state, "cumulative_distribution"):
            action = random.choices(
                state.applicable_actions,
                cum_weights=state.cumulative_distribution,
                k=1,
            )[0]
        else:
            action = random.choice(state.applicable_actions)
        state = state.result(action)
    return state.utility


def static_evaluation(state: GameState, params: dict, search_info: dict):
    match state:
        case ConnectFourState():
            return _static_eval_connectfour(state, params, search_info)
        case NimState():
            return _static_eval_nim(state, params, search_info)
        case GGPState():
            return _static_eval_ggp(state, params, search_info)
        case Twenty48State():
            return _static_eval_2048(state, params, search_info)
        case DummyState():
            return _static_eval_dummy(state, params, search_info)
        case _:
            raise ValueError(f"Unknown state type: {type(state)}")


def _static_eval_connectfour(state: ConnectFourState, params: dict, search_info: dict):
    if state.is_terminal:
        return state.utility

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
    weights = list(range(ceil(state.width / 2))) + list(
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

    return 1 / (1 + exp(-score))


def _static_eval_nim(state: NimState, params: dict, search_info: dict):
    if state.is_terminal:
        return state.utility

    result = 0
    for val in state.array:
        result ^= val

    if state.moves % 2:
        return int(not bool(result))

    return int(bool(result))


def _static_eval_ggp(state: GGPState, params: dict, search_info: dict):
    return state.utility


def _static_eval_2048(state: Twenty48State, params: dict, search_info: dict):
    return state.utility


def _static_eval_dummy(state: DummyState, params: dict, search_info: dict):
    if state.utility is None:
        return 0.0
    return state.utility


def evaluate_and_simulate(state: GameState, params: dict, search_info: dict):
    return static_evaluation(state, params, search_info), simulate(state, params, search_info)
