import argparse
import json
import logging
import os
import random
from datetime import datetime
from functools import partial

from src.agents import agents
from src.games import states
from tqdm.contrib.concurrent import process_map

agent_dict = {agent.__name__: agent for agent in agents}
state_dict = {state.__name__.replace("State", ""): state for state in states}

safe_float = (
    lambda x: round(float(x), 2)
    if "," not in x
    else round(float(x.replace(",", ".")), 2)
)

# define command line arguments
parser = argparse.ArgumentParser(
    description="Run a number of Connect Four games for \
                                            two agents, saving the results."
)
parser.add_argument("game", help="What game to play.", choices=state_dict.keys())
parser.add_argument(
    "agent0", help="The first agent to make a move.", choices=agent_dict.keys()
)
parser.add_argument(
    "agent1", help="The second agent to make a move.", choices=agent_dict.keys()
)
parser.add_argument("iterations", help="The number of games to play.", type=int)
parser.add_argument(
    "-t",
    help="The time available to the agents for taking an action.",
    type=safe_float,
    default=1,
)

parser.add_argument(
    "-loc", help="The folder to store logs and data in.", type=str, default=""
)

parser.add_argument(
    "-arg2agent0", help="Additional argument for Agent 0", type=safe_float, default=None
)

parser.add_argument(
    "-arg2agent1", help="Additional argument for Agent 1", type=safe_float, default=None
)

parser.add_argument(
    "-swap", help="Whether to swap seats every round.", action="store_true"
)


# parse command line arguments
args = parser.parse_args()


agent0_args = (args.t,) if args.arg2agent0 is None else (args.t, args.arg2agent0)
agent1_args = (args.t,) if args.arg2agent1 is None else (args.t, args.arg2agent1)


# set up logging folder structure
time_string = datetime.now().strftime("%y%m%d-%H%M%S")

if args.loc:
    agent_string = f"{agent_dict[args.agent0](*agent0_args)}vs{agent_dict[args.agent1](*agent1_args)}"
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
def run_game(i, agent0, agent1, agent0_args, agent1_args, swap):
    # make sure that a given game with given agents and time will be identical
    random.seed(i)

    if swap and i % 2:
        agent0, agent1 = agent1, agent0
        agent0_args, agent1_args = agent1_args, agent0_args

    # log each game to separate file
    log_file = os.path.join(folder, "games", f"game_{i}.log")
    logger = logging.getLogger()
    logger.handlers = []  # remove all handlers
    fh = logging.FileHandler(log_file)
    logger.addHandler(fh)

    logger.info(f"STARTING GAME {i}")
    logger.info(f"Agent 0: {agent0}")
    logger.info(f"Agent 1: {agent1}")

    agents = [agent_dict[agent0](*agent0_args), agent_dict[agent1](*agent1_args)]

    state = state_dict[args.game]()

    logger.info(state)

    actions = []
    search_info = {}

    while not state.is_terminal:
        agent_idx = state.moves % 2
        agent = agents[agent_idx]
        action, single_search_info = agent.search(state)
        if action is None:
            state.is_terminal = True
            state.utility = state.moves % 2
            logger.error(f"AGENT {agent_idx} GENERATED NoneType ACTION, DISQUALIFIED")
            break
        search_info[state.moves] = single_search_info.copy()
        state = state.result(action)
        actions.append(str(action))
        logger.info(f"Root: {agent.root}")
        logger.info("Children:")
        for c in agent.root.children:
            logger.info(c)
        logger.info(f"Agent {agent_idx} took action {action}")
        logger.info(state)

    action_string = "".join(actions)

    util = 1 - state.utility if swap and i % 2 else state.utility

    return i, util, action_string, search_info


# insert all the constant arguments
thread_function = partial(
    run_game,
    agent0=args.agent0,
    agent1=args.agent1,
    agent0_args=agent0_args,
    agent1_args=agent1_args,
    swap=args.swap,
)

# run games on multiple processes
results = process_map(thread_function, range(args.iterations))


# process results
agent0_wins = 0
agent1_wins = 0
draws = 0
games = {}
search_info = {}

for i, utility, game, game_search_info in results:
    if utility == 1:
        agent0_wins += 1
    elif utility == 0:
        agent1_wins += 1
    else:
        draws += 1

    games[i] = game
    search_info[i] = game_search_info

# save results
with open(os.path.join(folder, "data.json"), "w") as json_file:
    json.dump(
        {
            "configuration": vars(args),
            "agent0_wins": agent0_wins,
            "agent1_wins": agent1_wins,
            "draws": draws,
            "iterations": args.iterations,
            "games": games,
            "search_info": search_info,
        },
        json_file,
    )
