from gts.games import ConnectFourState

from gts.agents.mcts_agents import mcts_agent
from gts.agents.minimax_agents import iterative_deepening_alpha_beta_agent

if __name__ == "__main__":
    agents = [mcts_agent, iterative_deepening_alpha_beta_agent]

    state = ConnectFourState()

    print("Initial state:")

    while not state.is_terminal:
        agent = agents[state.moves % 2]  # agents take turns

        print(state, "\n")
        action, search_info = agent.search(state, search_time=1.0)
        state = state.result(action)
        print(agent.name)
        print(search_info)

    print(state)
