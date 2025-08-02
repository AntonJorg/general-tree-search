import os
import numpy as np

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from datetime import datetime
from itertools import combinations, repeat

from general_tree_search.games import ConnectFourState
from agents import get_agents

SEARCH_TIME = 0.5
N_PAIRWISE_GAMES = 100
N_SEARCH_GAMES = 250

agents = get_agents(SEARCH_TIME)

# base, expensive_result, tall_board
EXPERIMENT = "base"

WORKER_COUNT = os.cpu_count() // 2 + 2


def get_initial_state():
    if EXPERIMENT == "base":
        return ConnectFourState()
    if EXPERIMENT == "expensive_result":
        return ConnectFourState(result_delay=1e-3)
    if EXPERIMENT == "tall_board":
        raise ValueError("TODO")
    raise ValueError(f"Option {EXPERIMENT=} not supported")


def run_game(args):
    agent1_key, agent2_key, game_idx = args

    if game_idx % 2:
        agent1_key, agent2_key = agent2_key, agent1_key

    agent1, agent2 = agents[agent1_key], agents[agent2_key]

    pair = (agent1(), agent2())

    state = get_initial_state()

    expansions = []
    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return {
        agent1_key: state.utility,
        agent2_key: 1 - state.utility,
    }


formatted_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
filename = f"results/raw/{EXPERIMENT}-{formatted_time}.txt"

# create experiment file
with open(filename, "w") as f:
    experiment_parameters = {
        "n_pairwise_games": N_PAIRWISE_GAMES,
        "n_search_games": N_SEARCH_GAMES,
        "search_time": SEARCH_TIME,
        "n_agents": len(agents),
        "experiment_type": EXPERIMENT,
    }
    f.write(f"{experiment_parameters}\n")

print("Running pairwise matches...")
for agent1_key, agent2_key in combinations(agents.keys(), 2):
    print(f"{agent1_key} vs. {agent2_key}")

    iterator = zip(
        repeat(agent1_key, N_PAIRWISE_GAMES),
        repeat(agent2_key, N_PAIRWISE_GAMES),
        range(N_PAIRWISE_GAMES),
    )

    results = process_map(
        run_game,
        iterator,
        total=N_PAIRWISE_GAMES,
        max_workers=WORKER_COUNT,
    )

    aggregated = {
        agent1_key: sum(r[agent1_key] for r in results),
        agent2_key: sum(r[agent2_key] for r in results),
    }

    with open(filename, "a") as f:
        f.write(f"{aggregated}\n")


def run_game_sync(agent1, agent2):
    pair = (agent1(), agent2())
    state = get_initial_state()

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return state.utility


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


def hierarchical_ucb(
    max_utils,
    max_counts,
    min_utils,
    min_counts,
    total_matches,
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


counts_over_time = np.zeros((n_max, N_SEARCH_GAMES))

agent_names = list(agents.keys())

print("Running hierarchical UCB search in agent space...")
for i in tqdm(range(N_SEARCH_GAMES)):
    total_matches = i + 1
    max_idx, min_idx = hierarchical_ucb(
        max_utils, max_counts, min_utils, min_counts, total_matches
    )

    max_name = agent_names[max_idx]
    min_name = agent_names[min_idx]

    result = run_game_sync(max_agents[max_name], min_agents[min_name])

    # Update max agent stats
    max_utils[max_idx] += result
    max_counts[max_idx] += 1

    # Update min agent stats (from perspective of max agent)
    min_utils[max_idx, min_idx] += result
    min_counts[max_idx, min_idx] += 1

    counts_over_time[:, i] = max_counts

with open(filename, "a") as f:
    for agent, counts in zip(agent_names, counts_over_time):
        d = {agent: ", ".join(str(c) for c in counts)}
        f.write(f"{d}\n")

print("Experiment complete!")
print(f"Result saved at: {filename}")
