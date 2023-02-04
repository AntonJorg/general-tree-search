import argparse
import json
import logging
import os
import random
from datetime import datetime
from functools import partial

from src.agents import (IDExpectiMaxAgent, MaximizerMCTSAgent,
                        RandomDistributionAgent)
from src.games import Twenty48State
from tqdm.contrib.concurrent import process_map

agent_dict = {
    agent.__name__: agent for agent in (IDExpectiMaxAgent, MaximizerMCTSAgent)
}
safe_float = (
    lambda x: round(float(x), 2)
    if "," not in x
    else round(float(x.replace(",", ".")), 2)
)

# define command line arguments
parser = argparse.ArgumentParser(
    description="Run a number of 2048 games with \
                                            the specified agent, saving the results."
)
parser.add_argument("agent", help="Which agent should play.", choices=agent_dict.keys())
parser.add_argument("iterations", help="The number of games to play.", type=int)
parser.add_argument(
    "-t",
    help="The time available to the agent for taking an action.",
    type=safe_float,
    default=1,
)

parser.add_argument(
    "-loc", help="The folder to store logs and data in.", type=str, default=""
)

# parse command line arguments
args = parser.parse_args()

# set up logging folder structure
time_string = datetime.now().strftime("%y%m%d-%H%M%S")

if args.loc:
    agent_string = f"{agent_dict[args.agent](args.t)}"
    folder = os.path.join("experiments", args.loc)
    if not os.path.isdir(folder):
        os.mkdir(folder)
    folder = os.path.join(folder, agent_string)
else:
    folder = os.path.join("logs", time_string)

os.mkdir(folder)
os.mkdir(os.path.join(folder, "games"))

print("STARTING EXPERIMENT...")
print("Configuration:")
print(args)
print("Logs will be stored in:", folder)
print("Progress:")

logging.basicConfig(
    encoding="utf-8",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)

# define function for running one game
def run_game(i, agent):
    # make sure that a given game with given agents and time will be identical
    random.seed(i)

    # log each game to separate file
    log_file = os.path.join(folder, "games", f"game_{i}.log")
    logger = logging.getLogger()
    logger.handlers = []  # remove all handlers
    fh = logging.FileHandler(log_file)
    logger.addHandler(fh)

    logger.info(f"STARTING GAME {i}")
    logger.info(f"Agent: {agent}")

    agent = agent_dict[agent](args.t)

    state = Twenty48State()
    env = RandomDistributionAgent()

    logger.info(state)

    actions = []
    search_info = {}

    while not state.is_terminal:
        action, single_search_info = agent.search(state)
        if action is None:
            state.is_terminal = True
            logger.error(f"AGENT GENERATED NoneType ACTION, DISQUALIFIED")
            break

        search_info[state.moves] = single_search_info.copy()
        state = state.result(action)
        actions.append(str(action))
        logger.info(f"Root: {agent.root}")
        logger.info("Children:")
        for c in agent.root.children:
            logger.info(c)
        logger.info(f"Agent took action {action}")
        logger.info(state)

        if state.is_terminal:
            break

        effect, _ = env.search(state)
        state = state.result(effect)
        actions.append(str(effect))

        logger.info(f"Environment effect {action}")
        logger.info(state)

    action_string = " ".join(actions)

    return i, state.utility, state.board, action_string, search_info


# insert all the constant arguments
thread_function = partial(run_game, agent=args.agent)

# run games on multiple processes
results = process_map(thread_function, range(args.iterations))


# process results
utilities = {}
games = {}
search_info = {}
boards = {}

for i, utility, board, game, game_search_info in results:
    utilities[i] = utility
    boards[i] = board
    games[i] = game
    search_info[i] = game_search_info

# save results
with open(os.path.join(folder, "data.json"), "w") as json_file:
    json.dump(
        {
            "configuration": vars(args),
            "utilities": utilities,
            "boards": boards,
            "iterations": args.iterations,
            "games": games,
            "search_info": search_info,
        },
        json_file,
    )
