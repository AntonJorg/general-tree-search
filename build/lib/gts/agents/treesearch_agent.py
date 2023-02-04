import time
from abc import ABC, abstractmethod
from collections import deque, defaultdict

from gts.tree import TreeSearchNode
from gts.games import GameState
from gts.agents.components import components


class TreeSearchAgent(ABC, *components):
    """
    The TreeSearchAgent implements the Extended General Tree Search Algorithm
    (Algorithm 9) in self.search, and also defines all component functions
    as abstract methods to be implemented in subclasses.
    """
    def __init__(self):
        self.root = None
        self.frontier = deque()

        self.start_time = None
        self.search_time = None

        self.depth = None

        self.search_info = defaultdict(float)

    def search(self, state: GameState):
        """
        Implements Extended General Tree Search (EGTS).
        """

        if state.is_terminal:
            raise ValueError("Cannot search terminal states!")

        self.search_info.clear()

        self.frontier.clear()
        self.root = TreeSearchNode(state, None, None)
        self.frontier.append(self.root)

        self.start_time = time.process_time_ns()

        while not self.should_terminate():

            node = self.select()

            leaf = self.expand(node)

            value = None
            if self.should_evaluate(leaf):
                value = self.evaluate(leaf.state)

            if self.should_backpropagate(leaf, value):
                self.backpropagate(leaf, value)

            if self.should_trim():
                self.trim()

        return self.get_best_move(), self.search_info

    def __repr__(self):
        return type(self).__name__

    @abstractmethod 
    def should_terminate(self) -> bool:
        """
        Determines when the search algorithm terminates. This should
        not happen before the search has progressed to a point where
        self.get_best_move has a valid answer, i.e. can return an
        applicable action.
        """
        pass

    @abstractmethod
    def select(self) -> TreeSearchNode:
        """
        Selects where in the search tree the search should continue.
        This can either be based on the search tree itself, or the frontier.
        """
        pass

    @abstractmethod 
    def expand(self, node: TreeSearchNode) -> TreeSearchNode:
        """
        Takes the node returned from self.select, and decides
        which child nodes to expand and add to the search 
        tree and frontier. Proactive pruning happens here,
        because is simply entails not expanding a certain action.
        """
        pass

    @abstractmethod 
    def should_evaluate(self, node: TreeSearchNode) -> bool:
        """
        Whether or not to call self.evaluate on node.
        """
        pass

    @abstractmethod 
    def evaluate(self, state: GameState) -> float:
        """
        Returns an estimate of the value of state. The estimate
        can be deterministic or stochastic, but should be a float.
        """
        pass

    @abstractmethod 
    def should_backpropagate(self, node: TreeSearchNode, value: float) -> bool:
        """
        Whether or not to backpropagate value through node. Only determines when
        to call self.backpropagate, not how far up the tree the backpropagation
        continues.
        """
        pass

    @abstractmethod 
    def backpropagate(self, node: TreeSearchNode, value: float) -> None:
        """
        Propagates the value returned from self.evaluate up through the
        search tree, starting at node. Should modify the values of nodes
        in the tree, but not the tree structure.
        """
        pass

    @abstractmethod 
    def should_trim(self) -> None:
        """
        Whether or not to trim the search tree.
        """
        pass

    @abstractmethod 
    def trim(self) -> None:
        """
        In EGTS, Trim is for retroactive pruning, and it is the only
        component function that should remove nodes from the search tree.
        """
        pass

    @abstractmethod 
    def get_best_move(self) -> int:
        """
        Using information from the search tree, the frontier, or other available sources,
        return the action that the agent should take.
        """
        pass
 

