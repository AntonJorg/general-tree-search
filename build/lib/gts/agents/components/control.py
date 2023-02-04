import time
from math import exp

from src.tree import TreeSearchNode
from src.games import ConnectFourState, NimState


class Control:
    """
    Defines methods for implementing the TreeSearchAgent methods
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

    # should_evaluate and should_backpropagate methods
    def if_depth_reached(self, node: TreeSearchNode, value: float = 0) -> bool:
        return node.depth == self.depth or node.state.is_terminal

    def if_depth_reached_or_fully_expanded(self, node: TreeSearchNode, value: float = 0) -> bool:
        return node.depth == self.depth or node.state.is_terminal or not node.unexpanded_actions

    def if_parent_fully_expanded(self, node, value=0):
        return bool(node.parent.unexpanded_actions)

    def when_terminal(self, node, value=0):
        # TODO: rename to if
        return node.state.is_terminal

    # should_terminate methods
    def timed_termination(self):
        if self.search_time is None:
            raise AttributeError("Subclass must set self.search_time to use self.timed_termination")
        
        return time.process_time_ns() - self.start_time > self.search_time * 1_000_000_000
    
    def when_fully_evaluated(self):
        return self.root.eval is not None

    def periodic(self, frequency=100):
        return not self.root.count % frequency
    
    # utility methods
    def filter_unexpanded_actions(self, node: TreeSearchNode):
        match node.state:
            case ConnectFourState():
                return self._connectfour_filter_unexpanded_actions(node)
            case NimState():
                return self._nim_filter_unexpanded_actions(node)
            case _:
                raise ValueError(f"Unknown state type: {type(state)}")    

    def _connectfour_filter_unexpanded_actions(self, node: TreeSearchNode):
        # root case
        if not node.state.piece_mask:
            middle = node.state.width // 2
            if node.state.width % 2:
                return [middle]
            else:
                return [middle - 1, middle]

        
        played_rows = [i for i in range(node.state.width) if node.state.piece_mask & 1 << (node.state.height + 1) * i]

        beam = range(max(0, min(played_rows) - 1), min(node.state.width, max(played_rows) + 2))

        beam = [action for action in beam if action in node.state.applicable_actions]

        return sorted(beam, key=lambda x: -abs(x - node.state.width//2 + .1))

    def _nim_filter_unexpanded_actions(self, node: TreeSearchNode):
        return node.unexpanded_actions
