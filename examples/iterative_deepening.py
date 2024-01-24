import gts.components as c
from gts.agents.treesearch_agent import AgentBuilder
from gts.games.connectfour import ConnectFourState


if __name__ == "__main__":
    agent = (
        AgentBuilder()
        .with_should_terminate(c.control.timed_termination)
        .with_select(c.select.queue_select)
        .with_expand(c.expand.expand_next_dfs)
        .with_should_evaluate(c.control.if_depth_reached, depth=1)
        .with_evaluate(c.evaluate.static_evaluation)
        .with_should_backpropagate(c.control.if_depth_reached)
        .with_backpropagate(c.backpropagate.backpropagate_minimax)
        .with_should_trim(c.control.when_fully_evaluated)
        .with_trim(c.trim.reset_tree_increment_depth)
        .with_get_best_move(c.get_best_move.get_minimax_move)
        .build(name="IterativeDeepening")
    )

    print(agent.info())

    state = ConnectFourState()

    # search_time can also be supplied as agent parameter
    action, search_stats = agent.search(state, search_time=1)

    print("Action:", action)
    print("Search stats:", search_stats)
