import random

from src.agents.treesearch_agent import TreeSearchAgent

class RandomDistributionAgent(TreeSearchAgent):
    """
    Used to select environment effects in stochastic games.
    """
    def __init__(self, *args) -> None:
        super().__init__()

    def should_terminate(self) -> bool:
        return True
    
    def select(self):
        pass

    def expand(self, node):
        pass

    def should_evaluate(self, leaf):
        pass

    def evaluate(self):
        pass

    def should_backpropagate(self, node, value):
        pass

    def backpropagate(self, node, value):
        pass

    def should_trim(self):
        pass

    def trim(self):
        pass

    def get_best_move(self) -> int:
        return random.choices(self.root.state.applicable_actions, 
            cum_weights=self.root.state.cumulative_distribution, k=1)[0]
