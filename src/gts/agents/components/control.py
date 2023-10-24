"""Defines methods for implementing the TreeSearchAgent methods
should_terminate, should_evaluate, and should_backpropagate,
along with utility methods.

The methods intended for should_evaluate and should_backpropagate should:
    - Take a node and an optional value

The methods intended for should_terminate should:
    - Take no arguments

All the above methods should:
    - Return a boolean
    - Have no side effects

Utility methods can vary in signature as needed.
"""
# TODO: Update docstring to mention defined type signatures
import time
from math import exp
from abc import ABC, abstractmethod
from gts.agents.treesearch_agent import TreeSearchAgent

from gts.games import ConnectFourState, NimState
from gts.games.dummy import DummyState
from gts.tree import TreeSearchNode


# should_evaluate and should_backpropagate methods
def if_depth_reached(agent: TreeSearchAgent, node: TreeSearchNode, _: float = 0) -> bool:
    return node.depth == agent.depth or node.state.is_terminal

def if_depth_reached_or_fully_expanded(
    agent, node: TreeSearchNode, _: float = 0
) -> bool:
    return (
        node.depth == agent.depth
        or node.state.is_terminal
        or not node.unexpanded_actions
    )

def if_parent_fully_expanded(_: TreeSearchAgent, node: TreeSearchNode, __: float =0):
    assert node.parent is not None
    return bool(node.parent.unexpanded_actions)

def if_terminal(_: TreeSearchAgent, node: TreeSearchNode, __: float =0):
    return node.state.is_terminal

# should_terminate methods
def timed_termination(agent: TreeSearchAgent):
    assert agent.start_time is not None
    assert agent.search_time is not None
    return (
        time.process_time_ns() - agent.start_time > agent.search_time * 1_000_000_000
    )

def when_fully_evaluated(agent: TreeSearchAgent):
    assert agent.root is not None
    return agent.root.eval is not None

def periodic(agent: TreeSearchAgent, frequency=100):
    assert agent.root is not None
    return not agent.root.count % frequency

# utility methods
