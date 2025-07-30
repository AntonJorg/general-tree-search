from general_tree_search import AgentDefinition
from general_tree_search.games import ConnectFourState
from general_tree_search.components.choose import choose_uct
from general_tree_search.components.evaluate import simulate
from general_tree_search.components.control import timed_termination, if_fully_expanded
from general_tree_search.components.update import update_sum
from general_tree_search.components.extract_solution import most_robust_child


methods = {
    "should_terminate": timed_termination(1),
    "should_select": if_fully_expanded,
    "choose": choose_uct,
    "evaluate": simulate,
    "update": update_sum,
    "get_solution": most_robust_child,
}

MCTSAgent = AgentDefinition(**methods).to_agent_type("MCTSAgent")

agent = MCTSAgent()
print(agent)

state = ConnectFourState()

print(state)

while not state.is_terminal:
    root = agent.search(state)
    action = agent.get_solution(root)
    state = state.result(action)
    print(state)

    sim_lengths = agent.search_stats["simulation_lengths"]

    print("Number of simulations    :", root.values["sum_count"])
    print("Average simulation length:", sum(sim_lengths) / len(sim_lengths))
