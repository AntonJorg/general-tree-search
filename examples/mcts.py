import pyspiel

from general_tree_search import AgentDefinition
from general_tree_search.games import PySpielState
from general_tree_search.components.choose import get_choose_uct
from general_tree_search.components.evaluate import simulate, get_additive_eval
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import get_update_sum
from general_tree_search.components.extract_solution import most_robust_child


methods = {
    "should_terminate": timed_termination(1.0),
    "should_select": if_fully_expanded,
    "choose": get_choose_uct("avg_utility"),
    "evaluate": get_additive_eval(["utility", "sum_utility"], simulate),
    "update": get_update_sum("utility"),
    "get_solution": most_robust_child,
}

MCTSAgent = AgentDefinition(**methods).to_agent_type("MCTSAgent")

agent = MCTSAgent()
print(agent)

game = pyspiel.load_game("oware")

while True:
    state = PySpielState(game.new_initial_state())

    print(state)

    while not state.is_terminal:
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)
        print(state)
