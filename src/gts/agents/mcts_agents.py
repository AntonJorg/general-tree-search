from gts.agents.treesearch_agent import AgentBuilder
from gts.components import *


mcts_agent = (
    AgentBuilder()
    .with_should_terminate(control.timed_termination)
    .with_select(select.uct_select)
    .with_expand(expand.expand_next)
    .with_should_evaluate(generic.always)
    .with_evaluate(evaluate.simulate)
    .with_should_backpropagate(generic.always)
    .with_backpropagate(backpropagate.backpropagate_sum)
    .no_trim()
    .with_get_best_move(get_best_move.most_robust_child)
    .build("MCTS")
)
"""
Implements Monte Carlo Tree Search as described by Remi Coulom, Efficient
Selectivity and Backup Operators in Monte-Carlo Tree Search. 2006.
"""

mcts_evaluation_agent = (
    mcts_agent.to_builder()
    .with_evaluate(evaluate.static_evaluation)
    .build("MCTSEvaluation")
)
"""
Replaces the simulation step with a static evaluation
"""

partial_expansion_agent = (
    mcts_agent.to_builder()
    .with_select(select.partial_expansion_uct_select)
    .build("PartialExpansion")
)
"""
Adds partial expansion, allowing the search to start expanding
children before the node itself is fully expanded.

Emil Juul Jacobsen, Rasmus Greve, and Julian Togelius. “Monte mario: Platforming with
MCTS”. In: Association for Computing Machinery, 2014, pp. 293–300.
"""

static_weighted_mcts_agent = (
    mcts_agent.to_builder()
    .with_select(select.weighted_uct_select)
    .with_evaluate(evaluate.evaluate_and_simulate)
    .with_backpropagate(backpropagate.store_eval_and_backpropagate_sum)
    .with_get_best_move(get_best_move.weighted_eval_utility_move)
    .build("StaticWeightedMCTS")
)
"""
Adds static evaluation alongside simulations. UCB1 values are modified
to include the static evaluation value.
"""

minimax_weighted_mcts_agent = (
    static_weighted_mcts_agent.to_builder()
    .with_backpropagate(backpropagate.backpropagate_sum_and_minimax)
    .build("MiniMaxWeightedMCTS")
)
"""
Adds minimax backups for fully expanded nodes.
"""

mcts_tree_minimax_agent = (
    minimax_weighted_mcts_agent.to_builder()
    .with_get_best_move(get_best_move.get_minimax_move)
    .build("MCTSTreeMiniMax")
)
"""
Selects best move solely based on the backed up static
evaluation values from the weighted MCTS tree.
"""

progressive_pruning_mcts_agent = (
    mcts_agent.to_builder()
    .with_should_trim(control.periodic)
    .with_trim(trim.fractional_pruning)
    .add_params(pruning_factor=6)
    .build("ProgressivePruning")
)
"""
Periodically traverses the tree to remove unpromising nodes.
The current method is not statistically motivated and performs
quite poorly, but similar more thought out methods have shown promise.
"""
