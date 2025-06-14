import math

from general_tree_search import AgentDefinition
from general_tree_search.games import GridWorldState
from general_tree_search.search_tree import Node, get_children
from general_tree_search.components.control import budget_termination


def should_select(agent, node: Node):
    return node.is_fully_expanded() and not node.state.is_terminal


def actionvalue(agent, node: Node):
    children = get_children(node)
    return min(children, key=lambda c: c.values["best_f"])


def choose(agent, node, children):
    return min(children, key=lambda c: c.values["best_f"])


def evaluate(agent, node):
    state = node.state
    pi, pj = state.player_position

    euclideans = []
    for i, j in state.goal_positions:
        euclideans.append(math.sqrt((pi - i) ** 2 + (pj - j) ** 2))
    heuristic = min(euclideans)

    cost = node.depth

    return {
        "cost": cost,
        "utility": state.utility,
        "heuristic": heuristic,
        "best_f": cost + heuristic,
    }


def update(agent, node, children):
    utility = max(c.values["utility"] for c in children)
    best_f = min(c.values["best_f"] for c in children)
    best_f = min(node.values["best_f"], best_f)
    heuristic = node.values["heuristic"]
    cost = node.values["cost"]
    return {
        "cost": cost,
        "utility": utility,
        "heuristic": heuristic,
        "best_f": best_f,
    }


methods = {
    "update": update,
    "choose": choose,
    "evaluate": evaluate,
    "should_select": should_select,
    "should_terminate": budget_termination(1000),
    "actionvalue": actionvalue,
}

BFSAgent = AgentDefinition(**methods).to_agent_type("BFSAgent")

agent = BFSAgent()
print(agent)

state = GridWorldState()
print(state)

node = agent.search(state)

print(node.to_tree_string(max_indent=9))

print(state.player_position)

while not state.is_terminal:
    node = agent.actionvalue(node)
    action = node.generating_action
    print(action)
    state = state.result(action)
    print(state)
