import random
from math import log, sqrt

from gts.agents.mcts_agents import mcts_agent
from gts.agents.minimax_agents import iterative_deepening_agent
from gts.components import *


maximizer_mcts_agent = (
   mcts_agent.to_builder()
       .with_select(select.uct_select_stochastic_environment)
       .with_evaluate(evaluate.simulate_stochastic_environment)
       .build("MaximizerMCTSAgent")
)


"""
Swaps out MiniMax backups for ExpextiMax backups, maximizing on
max nodes but averaging otherwise.
"""
iterative_deepening_expectimax_agent = (
    iterative_deepening_agent.to_builder()
        .with_backpropagate(backpropagate.backpropagate_expectimax)
        .build("IterativeDeepeningExpectiMaxAgent")
)

