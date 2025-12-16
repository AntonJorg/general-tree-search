import sys
import argparse
from multiprocessing import Pool


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

args = parser.parse_args()


agent_dict = get_agents(args.search_time)
game_names = get_game_names()


def work_generator():
    idx = 0
    for agent1_name in agent_dict:
        for agent2_name in agent_dict:
            for game_str in game_names:
                for _ in range(args.n_games):
                    idx += 1
                    yield (idx, game_str, agent1_name, agent2_name)


def run_game(args):
    idx, game_str, agent1_name, agent2_name = args
    agents = [
        agent_dict[agent1_name](),
        agent_dict[agent2_name](),
    ]

    state = get_initial_state(game_str)

    while not state.is_terminal:
        agent = agents[state.moves % 2]

        root = agent.search(state)
        action = agent.get_solution(root)

        state = state.result(action)

    return [idx, game_str, agent1_name, agent2_name, str(state.utility)]


# game repetitions * number of games * number of agents squared
n_work_items = args.n_games * len(game_names) * len(agent_dict) * len(agent_dict)

with Pool(args.n_workers) as p:
    for result in p.imap_unordered(run_game, work_generator()):
        idx, result = result[0], result[1:]
        # output via stdout
        # collection/storage handled elsewhere
        print(
            " ".join(result),
            flush=True,
        )
        # print progress to stderr
        print(
            f"{idx / n_work_items * 100:.2f}%, ({idx}/{n_work_items})",
            file=sys.stderr,
            flush=True,
        )
