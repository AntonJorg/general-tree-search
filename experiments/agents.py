from general_tree_search import AgentDefinition
from general_tree_search.components.choose import (
    get_choose_uct,
    get_choose_principal_variation,
)
from general_tree_search.components.evaluate import (
    simulate,
    static_evaluation,
    get_additive_eval,
    get_setter_eval,
)
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import get_update_sum, get_update_minimax
from general_tree_search.components.extract_solution import (
    most_robust_child,
    get_minimax_child,
)


def get_agents(search_time):
    time_control = timed_termination(search_time)

    # we start out with our two well-known search algorithms:
    # MCTS and Best-First Minimax
    mcts_methods = {
        "should_terminate": time_control,
        "should_select": if_fully_expanded,
        "choose": get_choose_uct("avg_utility"),
        "evaluate": get_additive_eval(["utility", "sum_utility"], simulate),
        "update": get_update_sum("utility"),
        "get_solution": most_robust_child,
    }

    bfmm_methods = {
        "should_terminate": time_control,
        "should_select": if_fully_expanded,
        "choose": get_choose_principal_variation("static_evaluation"),
        "evaluate": get_setter_eval(["static_evaluation"], static_evaluation),
        "update": get_update_minimax("static_evaluation"),
        "get_solution": get_minimax_child("static_evaluation"),
    }

    # then all agents are either using one of the above algorithms,
    # or have only a single component function replaced
    # (additional replacements can happen for remapping purposes)
    MCTSAgent = AgentDefinition(
        **mcts_methods,
    ).to_agent_type("MCTS")

    MCTSPrincipalAgent = AgentDefinition(
        **mcts_methods | {"choose": get_choose_principal_variation("avg_utility")}
    ).to_agent_type("MC_PV")

    MCTSMinimaxAgent = AgentDefinition(
        **mcts_methods | {"update": get_update_minimax("avg_utility")},
    ).to_agent_type("MC_MM")

    MCTSEvalAgent = AgentDefinition(
        **mcts_methods
        | {
            "evaluate": get_additive_eval(["utility", "sum_utility"], static_evaluation)
        },
    ).to_agent_type("MC_EV")

    BFMMAgent = AgentDefinition(
        **bfmm_methods,
    ).to_agent_type("BFMM")

    BFMMUCTAgent = AgentDefinition(
        **bfmm_methods | {"choose": get_choose_uct("static_evaluation")},
    ).to_agent_type("BF_UCT")

    BFMMExpUtilAgent = AgentDefinition(
        **bfmm_methods
        | {
            "update": get_update_sum("utility"),
            "choose": get_choose_principal_variation("avg_utility"),
            "evaluate": get_additive_eval(
                ["utility", "sum_utility"], static_evaluation
            ),
            "get_solution": get_minimax_child("avg_utility"),
        },
    ).to_agent_type("BF_SUM")

    BFMMSimulationAgent = AgentDefinition(
        **bfmm_methods | {"evaluate": get_setter_eval(["static_evaluation"], simulate)},
    ).to_agent_type("BF_SIM")

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

    return {agent.__name__: agent for agent in agents}


if __name__ == "__main__":
    from general_tree_search.games import ConnectFourState

    state = ConnectFourState()

    agents = get_agents(1)

    for name, agent in list(agents.items())[2:]:
        print(name)
        agent = agent()
        agent.search(state, delay=1)
