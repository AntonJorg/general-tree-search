import matplotlib.pyplot as plt
from tqdm import tqdm

from general_tree_search.games import ConnectFourState

from agents import MCTSAgent, BFMMAgent


def run_game(agent1, agent2, result_delay):
    pair = (agent1(), agent2())

    state = ConnectFourState(result_delay=result_delay)

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return state.utility


agent1 = MCTSAgent
agent2 = BFMMAgent

n_games = 25

utilities = []
delays = [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]

for result_delay in delays:
    print("Result delay:", result_delay)

    cumulative_util = 0
    for _ in tqdm(range(n_games)):
        cumulative_util += run_game(agent1, agent2, result_delay)

    avg_utility = cumulative_util / n_games

    utilities.append(avg_utility)

plt.title("MCTS performance degrades in more expensive domains")
plt.plot(delays, utilities)
plt.xscale("log")
plt.xlabel("Cost of result function")
plt.ylabel("Average utility of MCTS")
plt.show()
