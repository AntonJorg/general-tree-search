import math
import matplotlib.pyplot as plt

from tqdm import tqdm

from general_tree_search.games import ConnectFourState
from agents import agents, MCTSAgent


def run_game(agent1, agent2):
    pair = (agent1(), agent2())

    state = ConnectFourState()

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return state.utility


def ucb1(N):
    def _ucb1(agent):
        return agent["utility"] / agent["count"] + math.sqrt(
            2 * math.log(N) / agent["count"]
        )

    return _ucb1


agent_dict = {
    agent.__name__: {
        "agent": agent,
        "count": 1,
        "utility": 1,
    }
    for agent in agents
}

counts = {name: [] for name in agent_dict.keys()}

N_ITERS = 500

for i in tqdm(range(N_ITERS)):
    agent = max(agent_dict.values(), key=ucb1(i + 1))

    result = run_game(agent["agent"], MCTSAgent)

    agent["utility"] += result
    agent["count"] += 1

    for name in agent_dict.keys():
        counts[name].append(agent_dict[name]["count"])


for key, values in counts.items():
    plt.plot(values, label=key)

plt.xlabel("Index")
plt.ylabel("Game count")
plt.title("UCB1 Search over agent space")
plt.legend()
plt.show()
