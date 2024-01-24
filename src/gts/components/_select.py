"""Defines methods for implementing TreeSearchAgent.select.

These methods should:
    - Be callable with no arguments
    - Base their selection on self.root or self.frontier
    - Return a TreeSearchNode
    - Have no side effects
"""
from math import log, sqrt
from random import choice

from gts.tree import TreeSearchNode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gts.agents import TreeSearchAgent


def uct_select(agent: "TreeSearchAgent", node: TreeSearchNode | None = None) -> TreeSearchNode:
    if node is None:
        node = agent.root
        assert node is not None

    if node.unexpanded_actions or node.state.is_terminal:
        return node

    def ucb(child):
        if child.is_max_node:
            exploit = (child.count - child.cumulative_utility) / child.count
        else:
            exploit = child.cumulative_utility / child.count

        explore = sqrt(2) * sqrt(log(node.count) / child.count)

        return exploit + explore

    best_child = sorted(node.children, key=ucb)[-1]

    return uct_select(agent, best_child)


def partial_expansion_uct_select(
    agent: "TreeSearchAgent", node: TreeSearchNode | None = None
) -> TreeSearchNode:
    if node is None:
        node = agent.root
        assert node is not None

    if not node.children or node.state.is_terminal:
        return node

    def ucb(child):
        if child.is_max_node:
            exploit = (child.count - child.cumulative_utility) / child.count
        else:
            exploit = child.cumulative_utility / child.count

        explore = sqrt(2) * sqrt(log(node.count) / child.count)

        return exploit + explore

    ucb_child = 0.5 + sqrt(2) * sqrt(log(node.count) / (1 + len(node.children)))

    ucbs = (ucb(c) for c in node.children)

    if node.unexpanded_actions and max(ucbs) < ucb_child:
        return node
    else:
        agent.search_info["partial_expansions"] += 1
        best_child = sorted(node.children, key=ucb)[-1]
        return partial_expansion_uct_select(agent, best_child)


def weighted_uct_select(agent: "TreeSearchAgent", node: TreeSearchNode | None = None) -> TreeSearchNode:
    if node is None:
        node = agent.root
    assert node is not None

    if node.unexpanded_actions or node.state.is_terminal:
        return node

    def weighted_uct(child: TreeSearchNode):
        if node.is_max_node:
            exploit = child.cumulative_utility / child.count
            evaluation = child.eval
        else:
            exploit = 1 - child.cumulative_utility / child.count
            evaluation = 1 - child.eval

        explore = sqrt(2) * sqrt(log(node.count) / child.count)

        q = 1 / sqrt(child.count)

        return evaluation * q + exploit * (1 - q) + explore

    best_child = sorted(node.children, key=weighted_uct)[-1]

    return weighted_uct_select(agent, best_child)


def uct_select_stochastic_environment(agent: "TreeSearchAgent", node: TreeSearchNode | None = None):
    assert node is not None

    if node.unexpanded_actions or node.state.is_terminal:
        return node

    if not node.is_max_node:
        return uct_select_stochastic_environment(agent, choice(node.children))

    c = node.cumulative_utility / node.count

    def uct(child):
        exploit = child.cumulative_utility / child.count

        explore = c * sqrt(log(node.count) / child.count)

        return exploit + explore

    best_child = sorted(node.children, key=uct)[-1]

    return uct_select_stochastic_environment(agent, best_child)


def queue_select(agent: "TreeSearchAgent"):
    return agent.frontier.pop()


def principal_variation_select(agent: "TreeSearchAgent"):
    def recurse(node: TreeSearchNode):
        if node.unexpanded_actions or not node.children:
            return node

        equal_children = [c for c in node.children if c.eval == node.eval]

        return recurse(equal_children[0])

    assert agent.root is not None
    return recurse(agent.root)

