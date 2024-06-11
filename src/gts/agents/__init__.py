from gts.agents.minimax_agents import (
    iterative_deepening_agent,
    iterative_deepening_alpha_beta_agent,
    iterative_deepening_simulation_agent,
    beam_search_agent,
    best_first_minimax_agent,
)
from gts.agents.mcts_agents import (
    mcts_agent,
    mcts_evaluation_agent,
    partial_expansion_agent,
    static_weighted_mcts_agent,
    minimax_weighted_mcts_agent,
    mcts_tree_minimax_agent,
)
from gts.agents.maximizer_agents import (
    maximizer_mcts_agent,
    iterative_deepening_expectimax_agent,
)

predefined = (
    iterative_deepening_agent,
    iterative_deepening_alpha_beta_agent,
    iterative_deepening_simulation_agent,
    beam_search_agent,
    best_first_minimax_agent,
    mcts_agent,
    mcts_evaluation_agent,
    partial_expansion_agent,
    static_weighted_mcts_agent,
    minimax_weighted_mcts_agent,
    mcts_tree_minimax_agent,
)

