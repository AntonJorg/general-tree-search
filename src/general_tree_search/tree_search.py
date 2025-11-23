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
    """
    Helper class for creating agent classes at runtime. Note that it takes 6 functions,
    instead of the 5 from the article. This is because we include `get_solution`
    here, which is not part of the 5 component functions, and only used after
    the GTS algorithm has completed.
    """

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
    """
    Game playing agent implementing the General Tree Search (GTS) algorithm.
    """

    def __init__(self):
        self.search_stats = defaultdict(float)

    def search(self, state: GameState, delay=0.0, plot_settings=None):
        """
        Algorithm 1: General Tree Search (GTS)
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
                start = time.process_time()
                while time.process_time() - start < delay:
                    pass
                print(root.to_tree_string())

            # forward pass through the search tree (alg. 2)
            node = self.select(root)
            # expand leaf node
            child = single_expand(node)

            # evaluate leaf node
            child.values = self.evaluate(child)
            # backpropagate through search tree (alg. 3)
            self.backpropagate(node)

        self.search_stats["end_time"] = time.process_time_ns()
        self.search_stats["iterations"] = iterations

        # return search tree
        return root

    def select(self, node: Node) -> Node:
        """
        Algorithm 2: Selection step
        """
        while self.should_select(node) and not node.state.is_terminal:
            node = self.choose(node, children(node))

        return node

    def backpropagate(self, node: Node):
        """
        Algorithm 3: Backpropagation step
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
