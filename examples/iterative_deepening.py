import time

from gts.agents.treesearch_agent import TreeSearchAgent
from gts.agents.wrappers import IterativeDeepeningWrapper
from gts.games.connectfour import ConnectFourState
from gts.components import (
    action_value,
    control,
    expand,
    evaluate,
    backpropagate,
    generic,
    frontier
)

if __name__ == "__main__":

    agent = TreeSearchAgent(
        name="MiniMax",
        should_terminate=control.when_fully_evaluated_or_timed_termination,
        use_frontier=generic.always,
        frontier=frontier.FrontierLIFO,
        select=generic.no_op,
        expand=expand.expand_all_depth_limited,
        evaluate=evaluate.static_evaluation,
        should_backpropagate=control.if_depth_reached,
        backpropagate=backpropagate.backpropagate_minimax,
        action_value=action_value.minimax_value,
        params={
            "depth_limit": 5,
        }
    )

    agent = IterativeDeepeningWrapper(agent)

    print(agent.info())

    state = ConnectFourState()

    # search_time can also be supplied as agent parameter
    action, search_stats = agent.search(state, search_time=1)

    print("Action:", action)
    print("Search stats:", search_stats)
