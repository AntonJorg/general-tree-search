"""
Defines methods for implementing TreeSearchAgent.get_best_move.

These methods should:
    - Take no arguments
    - Return an action that is in agent.root.state.applicable_actions
    - Base its action choice on the search tree or information that TreeSearchAgent.reflect has stored
    - Have no side effects
"""
from math import sqrt
from random import choice

from gts.agents.treesearch_agent import TreeSearchAgent


def get_minimax_move(agent: TreeSearchAgent):
    utils = (c.eval for c in agent.root.children)

    m = max(utils) if agent.root.is_max_node else min(utils)

    # consider all moves that maximize/minimize utility
    optimal_nodes = [c for c in agent.root.children if c.eval == m]

    return choice(optimal_nodes).generating_action


def most_robust_child(agent: TreeSearchAgent):
    return sorted(agent.root.children, key=lambda c: c.count)[-1].generating_action


def random_move(agent: TreeSearchAgent):
    return choice(agent.root.state.applicable_actions)


def get_stored_best_move(agent: TreeSearchAgent):
    return agent.best_move


def weighted_eval_utility_move(agent: TreeSearchAgent):
    def weight(child):
        if agent.root.is_max_node:
            exploit = child.cumulative_utility / child.count
            evaluation = child.eval
        else:
            exploit = 1 - child.cumulative_utility / child.count
            evaluation = 1 - child.eval

        q = 1 / sqrt(child.count)

        return evaluation * q + exploit * (1 - q)

    return sorted(agent.root.children, key=weight)[-1].generating_action

