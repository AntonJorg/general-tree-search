from general_tree_search import AgentDefinition
from general_tree_search.components.choose import (
    get_choose_uct,
    get_choose_principal_variation,
)
from general_tree_search.components.evaluate import (
    simulate,
    static_evaluation,
    get_static_evaluation_with_lookup,
)
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import update_sum, get_update_minimax
from general_tree_search.components.extract_solution import (
    most_robust_child,
    minimax_child,
)

time_control = timed_termination(0.1)

# we start out with our two well-known search algorithms; MCTS and Best-First Minimax
mcts_methods = {
    "should_terminate": time_control,
    "should_select": if_fully_expanded,
    "choose": get_choose_uct("avg_utility"),
    "evaluate": simulate,
    "update": update_sum,
    "get_solution": most_robust_child,
}

bfmm_methods = {
    "should_terminate": time_control,
    "should_select": if_fully_expanded,
    "choose": get_choose_principal_variation("static_evaluation"),
    "evaluate": get_static_evaluation_with_lookup(),
    "update": get_update_minimax("static_evaluation"),
    "get_solution": minimax_child,
}

# then all agents are either using one of the above algorithms,
# or have only a single component function replaced
# (additional replacements can happen for remapping purposes)
MCTSAgent = AgentDefinition(
    **mcts_methods,
).to_agent_type("MCTSAgent")

MCTSPrincipalAgent = AgentDefinition(
    **mcts_methods | {"choose": get_choose_principal_variation("avg_utility")}
).to_agent_type("MCTSPrincipalAgent")

MCTSMinimaxAgent = AgentDefinition(
    **mcts_methods | {"update": get_update_minimax("avg_utility")},
).to_agent_type("MCTSMinimaxAgent")

MCTSEvalAgent = AgentDefinition(
    **mcts_methods
    | {"evaluate": static_evaluation, "choose": get_choose_uct("static_evaluation")},
).to_agent_type("MCTSEvalAgent")

BFMMAgent = AgentDefinition(
    **bfmm_methods,
).to_agent_type("BFMMAgent")

BFMMUCTAgent = AgentDefinition(
    **bfmm_methods | {"choose": get_choose_uct("static_evaluation")},
).to_agent_type("BFMMUCTAgent")

BFMMExpUtilAgent = AgentDefinition(
    **bfmm_methods | {"update": update_sum},
).to_agent_type("BFMMExpUtilAgent")

BFMMSimulationAgent = AgentDefinition(
    **bfmm_methods | {"evaluate": simulate},
).to_agent_type("BFMMSimulationAgent")

agents = [
    MCTSAgent,
    MCTSPrincipalAgent,
    MCTSMinimaxAgent,
    MCTSEvalAgent,
    BFMMAgent,
    BFMMUCTAgent,
    BFMMExpUtilAgent,
    BFMMSimulationAgent,
]
