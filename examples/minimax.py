import gts.components as c
from gts.agents.treesearch_agent import AgentBuilder
from gts.games.dummy import DummyState


if __name__ == "__main__":
    agent = (
        AgentBuilder()
        .with_should_terminate(c.control.when_fully_evaluated)
        .with_select(c.select.queue_select)
        .with_expand(c.expand.expand_next_dfs)
        .with_should_evaluate(c.control.if_depth_reached, depth=3)
        .with_evaluate(c.evaluate.static_evaluation)
        .with_should_backpropagate(c.control.if_depth_reached)
        .with_backpropagate(c.backpropagate.backpropagate_minimax)
        .no_trim()
        .with_get_best_move(c.get_best_move.get_minimax_move)
        .build(name="MiniMax")
    )

    print(agent.info())

    state = DummyState()

    action, search_info = agent.search(state)

    print("Action:", action)
    print("Search info:", search_info)
