import numpy as np

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from datetime import datetime
from itertools import combinations, repeat

from general_tree_search.games import ConnectFourState
from agents import get_agents

SEARCH_TIME = 0.25
N_PAIRWISE_GAMES = 6

agents = get_agents(SEARCH_TIME)

# base, expensive_result, tall_board
EXPERIMENT = "base"


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

    agent1, agent2 = agents[agent1_key], agents[agent2_key]
    if game_idx % 2 == 0:
        pair = (agent1(), agent2())
    else:
        pair = (agent2(), agent1())

    state = get_initial_state()

    gamestr = str(state)
    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)
        gamestr += "\n" + str(state)

    return {agent1_key: state.utility, agent2_key: 1 - state.utility, "game": gamestr}


iterator = zip(
    repeat("MCTS", N_PAIRWISE_GAMES),
    repeat("BFMM", N_PAIRWISE_GAMES),
    range(N_PAIRWISE_GAMES),
)

results = process_map(run_game, iterator, total=N_PAIRWISE_GAMES, max_workers=6)

for r in results:
    print(r["game"])
    del r["game"]

for r in results:
    print(r)


def run_game_sync(agent1, agent2):
    pair = (agent1(), agent2())
    state = get_initial_state()

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return state.utility


for _ in range(N_PAIRWISE_GAMES):
    print(run_game_sync(agents["MCTS"], agents["BFMM"]))
