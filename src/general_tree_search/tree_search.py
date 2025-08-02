import time
from abc import ABC, abstractmethod
from typing import Callable, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
from general_tree_search.search_tree import (
    Node,
    parent,
    children,
    single_expand,
)
from general_tree_search.games import GameState


type Value = dict

type ShouldTerminate = Callable[[TreeSearchAgent, Node], bool]
type ShouldSelect = Callable[[TreeSearchAgent, Node], bool]
type Choose = Callable[[TreeSearchAgent, list[Node]], Node]
type Evaluate = Callable[[TreeSearchAgent, GameState], Value]
type Update = Callable[[TreeSearchAgent, Node, list[Node]], Value]
type ExtractSolution = Callable[[TreeSearchAgent, Node], Any]


@dataclass
class AgentDefinition:
    """ """

    should_terminate: ShouldTerminate
    should_select: ShouldSelect
    choose: Choose
    evaluate: Evaluate
    update: Update
    get_solution: ExtractSolution

    def to_agent_type(self, name: str):
        cls = type(name, (TreeSearchAgent,), {})

        methods = asdict(self)

        # attach methods as class methods
        for method_name, func in methods.items():
            setattr(cls, method_name, func)

        # remove added methods from abstract method set
        cls.__abstractmethods__ = cls.__abstractmethods__.difference(methods.keys())

        return cls


class TreeSearchAgent(ABC):
    """ """

    def __init__(self):
        self.search_stats = defaultdict(float)

    def search(self, state: GameState, delay=0.0, plot_settings=None):
        """
        Algorithm 1.
        """
        assert not state.is_terminal, "Cannot search terminal states!"

        # initialize search tree
        root = Node(state, parent=None, generating_action=None)

        iterations = 0
        self.search_stats.clear()
        self.search_stats["start_time"] = time.process_time_ns()

        # iterate until termination condition is met
        while not self.should_terminate(root):
            iterations += 1

            if delay:
                time.sleep(delay)
                print(root.to_tree_string())

            # forward pass through the search tree
            node = self.select(root)
            # expand leaf node
            child = single_expand(node)

            # evaluate leaf node
            child.values = self.evaluate(child)
            # backpropagate through search tree
            self.backpropagate(node)

        self.search_stats["end_time"] = time.process_time_ns()
        self.search_stats["iterations"] = iterations

        # return search tree
        return root

    def select(self, node: Node) -> Node:
        """
        Algorithm 2.
        """
        while self.should_select(node) and not node.state.is_terminal:
            node = self.choose(node, children(node))

        return node

    def backpropagate(self, node: Node):
        """
        Algorithm 3.
        """
        while node is not None:
            node.values = self.update(node, children(node))
            node = parent(node)

    @abstractmethod
    def should_terminate(self):
        pass

    @abstractmethod
    def should_select(self):
        pass

    @abstractmethod
    def choose(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_solution(self):
        pass
