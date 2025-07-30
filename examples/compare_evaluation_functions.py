from tqdm import tqdm

from general_tree_search import AgentDefinition
from general_tree_search.games import ConnectFourState
from general_tree_search.components.choose import get_choose_principal_variation
from general_tree_search.components.evaluate import (
    static_evaluation,
    get_static_evaluation_with_lookup,
)
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import get_update_minimax
from general_tree_search.components.extract_solution import minimax_child

N_GAMES = 50

methods = {
    "should_terminate": timed_termination(1),
    "should_select": if_fully_expanded,
    "choose": get_choose_principal_variation("static_evaluation"),
    "evaluate": static_evaluation,
    "update": get_update_minimax("static_evaluation"),
    "get_solution": minimax_child,
}

BFMMAgent = AgentDefinition(**methods).to_agent_type("BFMMAgent")

ImprovedBFMMAgent = AgentDefinition(
    **methods | {"evaluate": get_static_evaluation_with_lookup()},
).to_agent_type("ImprovedBFMMAgent")


results = {
    BFMMAgent.__name__: 0,
    ImprovedBFMMAgent.__name__: 0,
}

for i in tqdm(range(N_GAMES)):
    if i % 2:
        a2, a1 = BFMMAgent, ImprovedBFMMAgent
    else:
        a1, a2 = BFMMAgent, ImprovedBFMMAgent

    state = ConnectFourState()

    agents = [a1(), a2()]

    print(state)

    while not state.is_terminal:
        agent = agents[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)
        print(state)

    results[a1.__name__] += state.utility
    results[a2.__name__] += 1 - state.utility

for k, v in results.items():
    print(f"{k}: {v:.2f}")
