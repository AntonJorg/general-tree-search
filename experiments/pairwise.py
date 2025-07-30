from tqdm import tqdm
from datetime import datetime
from itertools import combinations

from general_tree_search.games import ConnectFourState
from agents import agents

N_GAMES = 100
VERBOSE = True


def vprint(*args):
    if VERBOSE:
        print(*args)


def run_game(agent1, agent2):
    pair = (agent1(), agent2())

    state = ConnectFourState()

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return {
        agent1.__name__: state.utility,
        agent2.__name__: 1 - state.utility,
    }


def run_n_games(agent1, agent2, n):
    results = []
    for i in tqdm(range(n)):
        if i % 2:
            a1, a2 = agent2, agent1
        else:
            a1, a2 = agent1, agent2
        result = run_game(a1, a2)
        results.append(result)

    return {
        agent1.__name__: sum(r[agent1.__name__] for r in results),
        agent2.__name__: sum(r[agent2.__name__] for r in results),
        "n_games": N_GAMES,
    }


formatted_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
filename = f"results/{formatted_time}.txt"

with open(filename, "w"):
    pass

for agent1, agent2 in combinations(agents, 2):
    print(f"{agent1.__name__} vs. {agent2.__name__}")
    result = run_n_games(agent1, agent2, N_GAMES)
    with open(filename, "a") as f:
        f.write(f"{result}\n")
