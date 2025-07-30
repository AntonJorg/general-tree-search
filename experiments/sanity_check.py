from agents import agents

from general_tree_search.games import ConnectFourState


def run_game(agent1, agent2):
    pair = (agent1(), agent2())

    state = ConnectFourState()
    print(state)

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)
        print(state)

    return state.utility


for agent in agents:
    print("Now testing", agent.__name__)
    run_game(agent, agent)
