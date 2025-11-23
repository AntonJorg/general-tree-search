from general_tree_search import AgentDefinition
from general_tree_search.games import ConnectFourState
from general_tree_search.components.choose import get_choose_principal_variation
from general_tree_search.components.evaluate import get_setter_eval, static_evaluation
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import get_update_minimax
from general_tree_search.components.extract_solution import get_minimax_child


methods = {
    "should_terminate": timed_termination(1),
    "should_select": if_fully_expanded,
    "choose": get_choose_principal_variation("static_evaluation"),
    "evaluate": get_setter_eval(["static_evaluation"], static_evaluation),
    "update": get_update_minimax("static_evaluation"),
    "get_solution": get_minimax_child("static_evaluation"),
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
