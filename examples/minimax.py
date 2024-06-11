from gts.agents.treesearch_agent import TreeSearchAgent
from gts.games.dummy import DummyState
from gts.components import (
    action_value,
    control,
    select,
    expand,
    evaluate,
    backpropagate,
    generic,
    frontier
)

if __name__ == "__main__":
    agent = TreeSearchAgent(
        name="MiniMax",
        should_terminate=control.when_fully_evaluated,
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

    print(agent.info())

    state = DummyState()

    action, search_info = agent.search(state)

    print("Action:", action)
    print("Search info:", search_info)
