import random
import math
import numpy as np

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

    pyspiel_state = state.state
    game = pyspiel_state.get_game()
    shape = game.observation_tensor_shape()
    observation = np.array(pyspiel_state.observation_tensor()).reshape(shape)

    match game.to_string().split("(")[0]:
        case "connect_four":
            return static_evaluation_connect_four(state, observation)
        case "breakthrough":
            return static_evaluation_breakthrough(state, observation)
        case "clobber":
            return static_evaluation_clobber(state, observation)
        case "checkers":
            return static_evaluation_checkers(state, observation)
        case "lines_of_action":
            return static_evaluation_lines_of_action(state, observation)
        case "oware":
            return static_evaluation_oware(state, observation)
        case "pentago":
            return static_evaluation_pentago(state, observation)
        case "y":
            return static_evaluation_y(state, observation)
        case _:
            assert False, "Unknown game!!"


def static_evaluation_breakthrough(state, observation):
    weights_max = (np.arange(8) + 5).reshape((-1, 1))
    weights_min = (np.arange(8)[::-1] + 5).reshape((-1, 1))

    score_max = np.sum(weights_max * observation[0])
    score_min = np.sum(weights_min * observation[1])

    return 1 / (1 + np.exp(score_min - score_max))


def static_evaluation_clobber(state, observation):
    score_max = np.sum(observation[1])
    score_min = np.sum(observation[0])

    return 1 / (1 + np.exp(score_min - score_max))


def static_evaluation_checkers(state, observation):
    men_max = np.sum(observation[0])
    kings_max = np.sum(observation[1])

    kings_min = np.sum(observation[2])
    men_min = np.sum(observation[3])

    score_max = men_max + 5 * kings_max
    score_min = men_min + 5 * kings_min

    return 1 / (1 + np.exp(score_min - score_max))


def static_evaluation_lines_of_action(state, observation):
    center_max = np.sum(observation[0, 2:-2, 2:-2])
    center_min = np.sum(observation[1, 2:-2, 2:-2])

    score_max = center_max
    score_min = center_min

    return 1 / (1 + np.exp(score_min - score_max))


def static_evaluation_oware(state, observation):
    points_max = observation[12]
    points_min = observation[13]

    controlled_max = np.sum(observation[:6])
    controlled_min = np.sum(observation[6:12])

    score_max = controlled_max + 50 * points_max
    score_min = controlled_min + 50 * points_min

    return 1 / (1 + np.exp(score_min - score_max))


def static_evaluation_pentago(state, observation):
    weights = {2: 1, 3: 5, 4: 13}
    
    counts_max = count_lines(observation[1], [2, 3, 4])
    counts_min = count_lines(observation[0], [2, 3, 4])

    score_max = sum(weights[c] * counts_max[c] for c in counts_max)
    score_min = sum(weights[c] * counts_min[c] for c in counts_min)

    return 1 / (1 + np.exp(score_min - score_max))


def static_evaluation_connect_four(state, observation):
    weights = {2: 1, 3: 5}
    
    counts_max = count_lines(observation[0], [2, 3])
    counts_min = count_lines(observation[1], [2, 3])

    score_max = sum(weights[c] * counts_max[c] for c in counts_max)
    score_min = sum(weights[c] * counts_min[c] for c in counts_min)

    return 1 / (1 + np.exp(score_min - score_max))


def count_lines(board, lengths_to_count):
    H, W = board.shape
    counts = {length: 0 for length in lengths_to_count}

    def scan_line(arr):
        # Count contiguous runs of 1s in a 1D array
        if len(arr) == 0:
            return
        dif = np.diff(arr)
        idx = np.where(dif != 0)[0] + 1
        segments = np.split(arr, idx)
        for seg in segments:
            k = len(seg)
            if k in counts and np.all(seg == 1):
                counts[k] += 1

    # horizontal
    for r in range(H):
        scan_line(board[r])

    # vertical
    for c in range(W):
        scan_line(board[:, c])

    # main diagonals
    for d in range(-(H-1), W):
        diag = board.diagonal(offset=d)
        scan_line(diag)

    # anti-diagonals
    flipped = np.fliplr(board)
    for d in range(-(H-1), W):
        diag = flipped.diagonal(offset=d)
        scan_line(diag)

    return counts


def static_evaluation_y(state, observation):
    N = observation.shape[1]
    player = state.moves % 2
    board_max = observation[player]
    board_min = observation[1 - player]

    board = board_max - board_min

    for size in range(N - 1, 0, -1):
        new_board = np.zeros((size, size))
        for i in range(size):
            for j in range(size - i):
                p1 = board[i, j]
                p2 = board[i, j + 1]
                p3 = board[i + 1, j]

                new_board[i, j] = 0.5 * (p1 + p2 + p3 - p1*p2*p3)
        
        board = new_board


    return max(min((board[0, 0] + 1) * 0.5, 1), 0)
