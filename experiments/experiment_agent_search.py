import argparse
from multiprocessing import Pool

import numpy as np

from agents import get_agents
from games import get_game_names, get_initial_state


parser = argparse.ArgumentParser()
parser.add_argument(
    "-t",
    "--search-time",
    type=float,
    default=1.0,
    help="Search time per agent (seconds)",
)
parser.add_argument(
    "-g",
    "--n-games",
    type=int,
    default=1,
    help="Number of games per agent pair",
)
parser.add_argument(
    "-w",
    "--n-workers",
    type=int,
    default=1,
    help="Number of worker processes",
)
parser.add_argument(
    "-c",
    "--continue_from",
    type=str,
    default=None,
    help="Output file to continue from",
)


args = parser.parse_args()

agent_dict = get_agents(args.search_time)
game_names = get_game_names()

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

def run_game_sync(agent1, agent2, game_str):
    pair = (agent1(), agent2())
    state = get_initial_state(game_str)

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return state.utility


def search_game(game_str):
    # Prepare agents
    max_agents = agent_dict  # Max player candidates
    min_agents = agent_dict  # Min player candidates (can also be different set)
    n_max = len(max_agents)
    n_min = len(min_agents)

    # Track utilities and counts
    max_utils = np.ones(n_max)  # Start with 1 to avoid division by zero
    max_counts = np.ones(n_max)

    min_utils = np.ones((n_max, n_min))
    min_counts = np.ones((n_max, n_min))


    counts_over_time = np.zeros((n_max, args.n_games))

    agent_names = list(agent_dict.keys())

    out_lines = []

    for i in range(args.n_games):
        total_matches = i + 1
        max_idx, min_idx = hierarchical_ucb(
            max_utils, max_counts, min_utils, min_counts, total_matches
        )

        max_name = agent_names[max_idx]
        min_name = agent_names[min_idx]

        result = run_game_sync(max_agents[max_name], min_agents[min_name], game_str)

        # Update max agent stats
        max_utils[max_idx] += result
        max_counts[max_idx] += 1

        # Update min agent stats (from perspective of max agent)
        min_utils[max_idx, min_idx] += result
        min_counts[max_idx, min_idx] += 1

        counts_over_time[:, i] = max_counts

        out_lines.append(f"{game_str} {max_name} {min_name} {result}")

    return out_lines

with Pool(args.n_workers) as p:
    for result in p.imap_unordered(search_game, game_names):
        # output via stdout
        # collection/storage handled elsewhere
        print(
            "\n".join(result),
            flush=True,
        )
        # print progress to stderr
        #print(
        #    f"{idx / n_work_items * 100:.2f}%, ({idx}/{n_work_items})",
        #    file=sys.stderr,
        #    flush=True,
        #)
