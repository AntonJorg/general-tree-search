import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from general_tree_search.games import ConnectFourState
from agents import agents


def run_game(agent1, agent2):
    pair = (agent1(), agent2())
    state = ConnectFourState()

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return (
        state.utility
    )  # 1 if agent1 wins, 0 if agent2 wins (assuming standard utility)


def hierarchical_ucb(
    max_utils, max_counts, min_utils, min_counts, total_matches, c=2.0
):
    """
    Selects (max_agent_idx, min_agent_idx) using a hierarchical UCB approach.
    """
    # UCB for max agents
    max_avg = max_utils / max_counts
    max_ucb = max_avg + np.sqrt(2 * np.log(total_matches) / max_counts)
    max_idx = np.argmax(max_ucb)

    # UCB for min agents (we want to minimize utility of the selected max agent)
    min_avg = min_utils[max_idx] / min_counts[max_idx]
    min_ucb = (1 - min_avg) + np.sqrt(
        2 * np.log(np.sum(min_counts[max_idx])) / min_counts[max_idx]
    )
    min_idx = np.argmax(min_ucb)

    return max_idx, min_idx


# Prepare agents
max_agents = agents  # Max player candidates
min_agents = agents  # Min player candidates (can also be different set)
n_max = len(max_agents)
n_min = len(min_agents)

# Track utilities and counts
max_utils = np.ones(n_max)  # Start with 1 to avoid division by zero
max_counts = np.ones(n_max)

min_utils = np.ones((n_max, n_min))
min_counts = np.ones((n_max, n_min))

N_ITERS = 200
counts_over_time = np.zeros((n_max, N_ITERS))

for i in tqdm(range(N_ITERS)):
    total_matches = i + 1
    max_idx, min_idx = hierarchical_ucb(
        max_utils, max_counts, min_utils, min_counts, total_matches
    )

    result = run_game(max_agents[max_idx], min_agents[min_idx])

    # Update max agent stats
    max_utils[max_idx] += result
    max_counts[max_idx] += 1

    # Update min agent stats (from perspective of max agent)
    min_utils[max_idx, min_idx] += result
    min_counts[max_idx, min_idx] += 1

    counts_over_time[:, i] = max_counts

# Plot how many games each max agent played
for idx, name in enumerate([a.__name__ for a in max_agents]):
    plt.plot(counts_over_time[idx], label=name)

plt.xlabel("Iteration")
plt.ylabel("Game count")
plt.title("Hierarchical UCB Search over agent space")
plt.legend()
plt.show()
