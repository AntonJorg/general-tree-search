"""
Defines methods for implementing TreeSearchAgent.action_value.

These methods should:
    - Take no arguments
    - Return an action that is in agent.root.state.applicable_actions
    - Base its action choice on the root node, its children, or the memory dict
    - Have no side effects
"""
from math import sqrt
from random import random

from gts.tree import TreeSearchNode


def minimax_value(child: TreeSearchNode, params: dict, search_info: dict):
    if child.is_max_node:
        # parent is minimizing
        return -child.eval
    else:
        # parent is maximizing
        return child.eval


def robustness(child: TreeSearchNode, params: dict, search_info: dict):
    return child.count


def random_value(_: TreeSearchNode, params: dict, search_info: dict):
    return random() * 2 - 1


def weighted_eval_utility(child: TreeSearchNode, params: dict, search_info: dict):
    if child.is_max_node:
        # parent is minimizing
        avg_utility = 1 - child.cumulative_utility / child.count
        evaluation = 1 - child.eval
    else:
        # parent is maximizing
        avg_utility = child.cumulative_utility / child.count
        evaluation = child.eval

    q = 1 / sqrt(child.count)

    # linear interpolation between evaluation and avg_utility
    return evaluation * q + avg_utility * (1 - q)
