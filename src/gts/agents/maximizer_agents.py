import random
from math import log, sqrt

from gts.agents.treesearch_agent import TreeSearchAgent
from gts.agents.mcts_agents import mcts_agent
from gts.agents.minimax_agents import iterative_deepening_agent
from gts.components import (
    action_value,
    backpropagate,
    control,
    evaluate,
    expand,
    frontier,
    generic,
    select,
)


maximizer_mcts_components = mcts_agent.components()
maximizer_mcts_components.select = select.uct_select_stochastic_environment
maximizer_mcts_components.evaluate = evaluate.simulate_stochastic_environment

maximizer_mcts_agent = TreeSearchAgent(
    name="MaximizerMCTS",
    **maximizer_mcts_components.to_dict(),
)
"""
"""

iterative_deepening_expectimax_components = iterative_deepening_agent.components()
iterative_deepening_expectimax_components.backpropagate = backpropagate.backpropagate_expectimax

iterative_deepening_expectimax_agent = TreeSearchAgent(
    name="IterativeDeepeningExpectimax",
    **iterative_deepening_expectimax_components.to_dict(),
)
"""
Swaps out MiniMax backups for ExpextiMax backups, maximizing on
max nodes but averaging otherwise.
"""

