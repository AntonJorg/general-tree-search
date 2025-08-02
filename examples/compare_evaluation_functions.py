from tqdm import tqdm

from general_tree_search import AgentDefinition
from general_tree_search.games import ConnectFourState
from general_tree_search.components.choose import (
    get_choose_principal_variation,
    get_choose_uct,
)
from general_tree_search.components.evaluate import (
    static_evaluation,
    get_static_evaluation_with_lookup,
    static_evaluation_improved,
)
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import get_update_minimax
from general_tree_search.components.extract_solution import minimax_child


N_GAMES = 10

methods = {
    "should_terminate": timed_termination(0.5),
    "should_select": if_fully_expanded,
    "choose": get_choose_uct("static_evaluation"),
    "evaluate": static_evaluation,
    "update": get_update_minimax("static_evaluation"),
    "get_solution": minimax_child,
}

BFMMAgent = AgentDefinition(**methods).to_agent_type("BFMMAgent")

ImprovedBFMMAgent = AgentDefinition(
    **methods | {"evaluate": static_evaluation_improved},
).to_agent_type("ImprovedBFMMAgent")


results = {
    BFMMAgent.__name__: 0,
    ImprovedBFMMAgent.__name__: 0,
}

for i in tqdm(range(N_GAMES)):
    a1, a2 = BFMMAgent, ImprovedBFMMAgent

    state = ConnectFourState()

    agents = [a1(), a2()]

    while not state.is_terminal:
        agent = agents[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    results[a1.__name__] += state.utility
    results[a2.__name__] += 1 - state.utility

for k, v in results.items():
    print(f"{k}: {v:.2f}")
