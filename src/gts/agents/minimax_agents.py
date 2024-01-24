from gts.agents.treesearch_agent import TreeSearchAgent

from gts.agents.treesearch_agent import AgentBuilder
from gts.components import *


minimax_agent = (
    AgentBuilder()
    .with_should_terminate(control.when_fully_evaluated)
    .with_select(select.queue_select)
    .with_expand(expand.expand_all_depth_limited)
    .with_should_evaluate(control.if_depth_reached)
    .with_evaluate(evaluate.static_evaluation)
    .with_should_backpropagate(control.if_depth_reached)
    .with_backpropagate(backpropagate.backpropagate_minimax)
    .with_get_best_move(get_best_move.get_minimax_move)
    .no_trim()
    .build(name="MiniMax")
)
"""TODO"""


_alpha_beta_builder = (
    AgentBuilder()
    .with_should_backpropagate(control.if_depth_reached_or_fully_expanded)
    .with_expand(expand.expand_next_alpha_beta)
)


alpha_beta_agent = (
    minimax_agent.to_builder().merge(_alpha_beta_builder).build(name="AlphaBeta")
)
"""TODO"""


_iterative_deepening_builder = (
    AgentBuilder()
    .with_should_terminate(control.timed_termination)
    .with_should_trim(control.when_fully_evaluated)
    .with_trim(trim.reset_tree_increment_depth)
    .with_get_best_move(get_best_move.get_stored_best_move)
    .add_params(depth=1, best_move=None)
)


iterative_deepening_agent = (
    minimax_agent.to_builder()
    .merge(_iterative_deepening_builder)
    .build("IterativeDeepening")
)
"""Adds iterative deepening to MiniMax."""


iterative_deepening_alpha_beta_agent = (
    iterative_deepening_agent.to_builder()
    .merge(_alpha_beta_builder)
    .build("IterativeDeepeningAlphaBeta")
)
"""Combines iterative deepening and alpha beta pruning."""


iterative_deepening_simulation_agent = (
    iterative_deepening_agent.to_builder()
    .with_evaluate(evaluate.simulate_many)
    .add_params(num_simulations=10)
    .build("IterativeDeepeningSimulation")
)
"""TODO"""

beam_search_agent = (
    iterative_deepening_alpha_beta_agent.to_builder()
    .with_expand(expand.expand_next_beam)
    .build("BeamSearch")
)
"""TODO"""


_best_first_minimax_builder = (
    AgentBuilder()
    .with_select(select.principal_variation_select)
    .with_expand(expand.expand_next)
    .with_should_evaluate(generic.always)
    .with_should_backpropagate(generic.always)
    .with_should_terminate(control.timed_termination)
)

best_first_minimax_agent = (
    minimax_agent.to_builder()
    .merge(_best_first_minimax_builder)
    .build("BestFirstMiniMax")
)
"""
Expands all children of the node at the end of the principal variation,
then backs up new minimax values.

Richard E Korf and David Maxwell Chickering in Artificial Intelligence:
Best-first minimax search. 1996, pp. 299–337.
"""
