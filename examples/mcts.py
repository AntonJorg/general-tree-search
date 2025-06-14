import random
import raylibpy as rl

from general_tree_search import AgentDefinition
from general_tree_search.games import ConnectFourState, DummyState
from general_tree_search.search_tree import Node
from general_tree_search.tree_search import PlotSettings
from general_tree_search.components.choose import choose_uct
from general_tree_search.components.evaluate import simulate
from general_tree_search.components.control import budget_termination
from general_tree_search.components.generic import always, never, noop
from general_tree_search.components.update import update_sum


def should_select(agent, node: Node):
    return node.is_fully_expanded() and not node.state.is_terminal


def actionvalue(agent, child: Node):
    return child.values["sum_count"]


methods = {
    "update": update_sum,
    "choose": choose_uct,
    "evaluate": simulate,
    "should_select": should_select,
    "should_terminate": budget_termination(1000),
    "actionvalue": actionvalue,
}

MCTSAgent = AgentDefinition(**methods).to_agent_type("MCTSAgent")

agent = MCTSAgent()
print(agent)

state = ConnectFourState()
print(state)

ps = PlotSettings(
    height=1200,
    width=1600,
    delay=0.1,
    iters_per_render=1,
    get_utility=lambda vals: vals["sum_utility"] / vals["sum_count"],
    get_width=lambda vals: vals["sum_count"] ** 2,
)

while not state.is_terminal:
    action = agent.search(state, delay=0.05, plot_settings=ps)
    state = state.result(action)
    print(state)

    sim_lengths = agent.search_stats["simulation_lengths"]

    print("Average simulation length:", sum(sim_lengths) / len(sim_lengths))
