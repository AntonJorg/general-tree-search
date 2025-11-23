import logging
from multiprocessing import Pool

import pyspiel

from agents import get_agents
from general_tree_search.games import PySpielState


game_configs = {
    "breakthrough": {
        "columns": 8,
        "rows": 8,
    },
    "checkers": {
        "columns": 8,
        "rows": 8,
    },
    "clobber": {
        "columns": 8,
        "rows": 8,
    },
    "connect_four": {
        "columns": 7,
        "rows": 6,
        "x_in_row": 4,
    },
    "lines_of_action": {},
    "oware": {
        "num_houses_per_player": 6,
        "num_seeds_per_house": 4,
    },
    "pentago": {
        "ansi_color_output": True,
    },
    "y": {
        "ansi_color_output": True,
        "board_size": 13,
    },
}

agent_dict = get_agents(0.01)

N_GAMES = 2
N_WORKERS = 8

work_items = []

def work_generator():
    for agent1_name in agent_dict:
        for agent2_name in agent_dict:
            for game_str, params in game_configs.items():
                for _ in range(N_GAMES):
                    yield (game_str, params, agent1_name, agent2_name)

def run_game(args):
    game_str, params, agent1_name, agent2_name = args
    agents = [
        agent_dict[agent1_name](), 
        agent_dict[agent2_name](),
    ]

    game = pyspiel.load_game(game_str, params)
    state = PySpielState(game.new_initial_state())

    while not state.is_terminal:
        agent = agents[state.moves % 2]

        root = agent.search(state)
        action = agent.get_solution(root)
        
        state = state.result(action)

    return [
        game_str,
        agent1_name,
        agent2_name,
        str(state.utility)
    ]


with Pool(N_WORKERS) as p:
    for result in (p.imap_unordered(run_game, work_generator())):
        # output via stdout
        # collection/storage handled elsewhere
        print(" ".join(result))