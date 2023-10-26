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
from typing import reveal_type
from gts.agents.treesearch_agent import TreeSearchAgent

# TODO: Remove dependency on specific games via GGP heuristics
from gts.games import *


def evaluate_utility(agent: TreeSearchAgent, state: GameState):
    if state.is_terminal:
        return state.utility
    else:
        return None


def simulate(agent: TreeSearchAgent, state: GameState):
    while not state.is_terminal:
        action = random.choice(state.applicable_actions)
        state = state.result(action)
    return state.utility


def simulate_many(agent: TreeSearchAgent, state: GameState):
    values = (simulate(agent, state) for _ in range(agent.num_simulations))
    return sum(values) / agent.num_simulations


def simulate_stochastic_environment(agent: TreeSearchAgent, state: GameState):
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


def static_evaluation(agent: TreeSearchAgent, state: GameState):
    match state:
        case ConnectFourState():
            return _static_eval_connectfour(agent, state)
        case NimState():
            return _static_eval_nim(agent, state)
        case Twenty48State():
            return _static_eval_2048(agent, state)
        case DummyState():
            return _static_eval_dummy(agent, state)
        case _:
            raise ValueError(f"Unknown state type: {type(state)}")


def _static_eval_connectfour(agent: TreeSearchAgent, state: ConnectFourState):
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


def _static_eval_nim(agent: TreeSearchAgent, state: NimState):
    if state.is_terminal:
        return state.utility

    result = 0
    for val in state.array:
        result ^= val

    if state.moves % 2:
        return int(not bool(result))

    return int(bool(result))


def _static_eval_2048(agent: TreeSearchAgent, state: Twenty48State):
    return state.utility


def _static_eval_dummy(agent: TreeSearchAgent, state: DummyState):
    return state.utility


def evaluate_and_simulate(agent: TreeSearchAgent, state: GameState):
    return static_evaluation(agent, state), simulate(agent, state)

