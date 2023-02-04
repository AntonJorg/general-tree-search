from math import log, sqrt
import random

from src.agents.mcts_agents import MCTSAgent
from src.agents.minimax_agents import IterativeDeepeningAgent


class MaximizerMCTSAgent(MCTSAgent):
    """
    Changes the selection and simulation step to take into
    account chance nodes. The simulation step takes into account the
    non-uniform environment effect distribution, the selection
    step does not.
    """
    def select(self):
        return self.uct_select_stochastic_environment(self.root)

    def evaluate(self, state):
        return self.simulate_stochastic_environment(state)


class IDExpectiMaxAgent(IterativeDeepeningAgent):
    """
    Swaps out MiniMax backups for ExpextiMax backups, maximizing on
    max nodes but averaging otherwise.
    """
    def backpropagate(self, node, value):
        self.backpropagate_expectimax(node, value)
