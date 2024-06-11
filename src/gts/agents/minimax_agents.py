from gts.agents.treesearch_agent import TreeSearchAgent
from gts.agents.wrappers import IterativeDeepeningWrapper

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


minimax_agent = TreeSearchAgent(
    name="MiniMax",
    should_terminate=control.when_fully_evaluated,
    use_frontier=generic.always,
    frontier=frontier.FrontierLIFO,
    select=select.queue_select,
    expand=expand.expand_all_depth_limited,
    evaluate=evaluate.static_evaluation,
    should_backpropagate=control.if_depth_reached,
    backpropagate=backpropagate.backpropagate_minimax,
    action_value=action_value.minimax_value,
)
"""TODO"""


alpha_beta_components = minimax_agent.components()
alpha_beta_components.should_backpropagate = control.if_depth_reached_or_fully_expanded
alpha_beta_components.expand = expand.expand_next_alpha_beta

alpha_beta_agent = TreeSearchAgent(
    name="AlphaBeta",
    **alpha_beta_components.to_dict(),
)
"""TODO"""


def iterative_deepening(agent: TreeSearchAgent, state, params):
    depth = 1
    best_move = None
    while not control.timed_termination(agent, state, params):
        params["depth_limit"] = depth
        best_move = agent.search(state, **params)
        depth += 1

    return best_move


iterative_deepening_agent = IterativeDeepeningWrapper(minimax_agent)
"""Adds iterative deepening to MiniMax."""

iterative_deepening_alpha_beta_agent = IterativeDeepeningWrapper(alpha_beta_agent)
"""Combines iterative deepening and alpha beta pruning."""

minimax_simulation_components = minimax_agent.components()
minimax_simulation_components.evaluate = evaluate.simulate_many
minimax_simulation_components.params["num_simulations"] = 10

minimax_simulation_agent = TreeSearchAgent(
    name="MiniMaxSimulation",
    **minimax_simulation_components.to_dict(),
)
"""TODO"""

iterative_deepening_simulation_agent = IterativeDeepeningWrapper(minimax_simulation_agent)
"""Combines iterative deepening and simulation-based evaluation."""


beam_search_components = minimax_agent.components()
beam_search_components.expand = expand.expand_next_beam

beam_search_agent = TreeSearchAgent(
    name="BeamSearch",
    **beam_search_components.to_dict(),
)
"""TODO"""


best_first_minimax_components = minimax_agent.components()
best_first_minimax_components.select = select.principal_variation_select
best_first_minimax_components.expand = expand.expand_next
best_first_minimax_components.should_evaluate = generic.always
best_first_minimax_components.should_backpropagate = generic.always
best_first_minimax_components.should_terminate = control.timed_termination

best_first_minimax_agent = TreeSearchAgent(
    name="BestFirstMiniMax",
    **best_first_minimax_components.to_dict(),

)
"""
Expands all children of the node at the end of the principal variation,
then backs up new minimax values.

Richard E Korf and David Maxwell Chickering in Artificial Intelligence:
Best-first minimax search. 1996, pp. 299–337.
"""
