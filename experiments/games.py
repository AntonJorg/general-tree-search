import pyspiel
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


def get_game_names():
    return list(game_configs.keys())


def get_initial_state(game_str):
    game = pyspiel.load_game(game_str, game_configs[game_str])
    return PySpielState(game.new_initial_state())
