from gts.agents.treesearch_agent import TreeSearchAgent
from gts.components import (
    action_value,
    control,
    select,
    expand,
    evaluate,
    backpropagate,
    generic,
    frontier
)


mcts_agent = TreeSearchAgent(
    name="MCTS",
    should_terminate=control.timed_termination,
    use_frontier=generic.never,
    frontier=frontier.FrontierNone,
    select=select.uct_select,
    expand=expand.expand_next,
    evaluate=evaluate.simulate,
    should_backpropagate=generic.always,
    backpropagate=backpropagate.backpropagate_sum,
    action_value=action_value.robustness,
)
"""
Implements Monte Carlo Tree Search as described by Remi Coulom, Efficient
Selectivity and Backup Operators in Monte-Carlo Tree Search. 2006.
"""

mcts_evaluation_components = mcts_agent.components()
mcts_evaluation_components.evaluate = evaluate.static_evaluation

mcts_evaluation_agent = TreeSearchAgent(
    "MCTSEvaluation",
    **mcts_evaluation_components.to_dict(),
)
"""
Replaces the simulation step with a static evaluation
"""

partial_expansion_components = mcts_agent.components()
partial_expansion_components.select = select.partial_expansion_uct_select

partial_expansion_agent = TreeSearchAgent(
    "PartialExpansion",
    **partial_expansion_components.to_dict(),
)
"""
Adds partial expansion, allowing the search to start expanding
children before the node itself is fully expanded.

Emil Juul Jacobsen, Rasmus Greve, and Julian Togelius. “Monte mario: Platforming with
MCTS”. In: Association for Computing Machinery, 2014, pp. 293–300.
"""

static_weighted_mcts_components = mcts_agent.components()
static_weighted_mcts_components.select = select.weighted_uct_select
static_weighted_mcts_components.evaluate = evaluate.evaluate_and_simulate
static_weighted_mcts_components.backpropagate = backpropagate.store_eval_and_backpropagate_sum
static_weighted_mcts_components.get_best_move = action_value.weighted_eval_utility

static_weighted_mcts_agent = TreeSearchAgent(
    "StaticWeightedMCTS",
    **static_weighted_mcts_components.to_dict(),
)
"""
Adds static evaluation alongside simulations. UCB1 values are modified
to include the static evaluation value.
"""

minimax_weighted_mcts_components = mcts_agent.components()
minimax_weighted_mcts_components.backpropagate = backpropagate.backpropagate_sum_and_minimax

minimax_weighted_mcts_agent = TreeSearchAgent(
    "MinimaxWeightedMCTS",
    **minimax_weighted_mcts_components.to_dict(),
)
"""
Adds minimax backups for fully expanded nodes.
"""

mcts_tree_minimax_components = minimax_weighted_mcts_components
mcts_tree_minimax_components.get_best_move = action_value.minimax_value

mcts_tree_minimax_agent = TreeSearchAgent(
    "MCTSTreeMinimax",
    **mcts_tree_minimax_components.to_dict(),
)
"""
Selects best move solely based on the backed up static
evaluation values from the weighted MCTS tree.
"""
