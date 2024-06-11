"""
Defines methods for implementing TreeSearchAgent.trim.

These methods should:
    - Take no arguments
    - Evaluate the state of the search tree and/or the frontier
    - Possibly modify the search tree and/or the frontier
    - Return nothing
"""
from gts.components.action_value import get_minimax_move
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gts.agents import TreeSearchAgent


def reset_tree_increment_depth(agent: "TreeSearchAgent"):
    """ """

    def deepest_node(node):
        if node.children:
            return max(deepest_node(c) for c in node.children)
        else:
            return node.depth

    assert agent.root is not None

    # log before increase to reflect last completed search
    agent.search_info["depth"] = min(agent.params["depth"], deepest_node(agent.root))

    action = get_minimax_move(agent)
    agent.params["best_move"] = action
    agent.params["depth"] += 1

    # reset search tree
    agent.params["last_iter_root"] = agent.root.copy()
    agent.root.reset()

    agent.frontier.clear()
    agent.frontier.append(agent.root)


def fractional_pruning(agent: "TreeSearchAgent"):
    """ """

    def recurse(node):
        node.children = [
            c
            for c in node.children
            if c.count
            >= node.count / (node.branching_factor + agent.params["pruning_factor"])
        ]

        for c in node.children:
            if not c.unexpanded_actions:
                recurse(c)

    recurse(agent.root)
