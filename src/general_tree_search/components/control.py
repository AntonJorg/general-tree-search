import time

from general_tree_search.tree_search import TreeSearchAgent
from general_tree_search.search_tree import Node


def timed_termination(time_budget: float):
    def _timed_termination(agent: TreeSearchAgent, root: Node):
        return time.time() - agent.search_stats["start_time"] > time_budget

    return _timed_termination


def budget_termination(expansion_budget: float):
    def _budget_termination(agent: TreeSearchAgent, root: Node):
        return agent.search_stats["expansions"] >= expansion_budget

    return _budget_termination


def if_fully_expanded(agent: TreeSearchAgent, child: Node):
    return not child.unexpanded_actions
