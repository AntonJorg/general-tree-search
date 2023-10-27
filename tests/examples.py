from gts.agents.treesearch_agent import AgentBuilder
from gts.games.dummy import DummyState
from gts.components import *


if __name__ == "__main__":

    agent = (
        AgentBuilder()
            .with_should_terminate(control.when_fully_evaluated)
            .with_select(select.queue_select)
            .with_expand(expand.expand_next_dfs)
            .with_should_evaluate(control.if_depth_reached)
            .with_evaluate(evaluate.static_evaluation)
            .with_should_backpropagate(control.if_depth_reached)
            .with_backpropagate(backpropagate.backpropagate_minimax)
            .with_should_trim(generic.never)
            .no_trim()
            .build(name="MiniMax")
    )

    print(agent.info())

    state = DummyState()

    action, search_stats = agent.search(state)

    print("Action:", action)
    print("Search stats:", search_stats)

