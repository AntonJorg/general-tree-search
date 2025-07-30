from general_tree_search import AgentDefinition
from general_tree_search.games import ConnectFourState
from general_tree_search.components.choose import choose_principal_variation
from general_tree_search.components.evaluate import static_evaluation
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import get_update_minimax
from general_tree_search.components.extract_solution import minimax_child


methods = {
    "should_terminate": timed_termination(1),
    "should_select": if_fully_expanded,
    "choose": choose_principal_variation,
    "evaluate": static_evaluation,
    "update": get_update_minimax("static_evaluation"),
    "get_solution": minimax_child,
}

BFMMAgent = AgentDefinition(**methods).to_agent_type("BFMMAgent")

agent = BFMMAgent()
print(agent)

state = ConnectFourState()
print(state)

while not state.is_terminal:
    root = agent.search(state)
    action = agent.get_solution(root)
    state = state.result(action)
    print(state)
