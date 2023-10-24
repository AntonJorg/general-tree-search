import typing
from gts.agents.treesearch_agent import AgentBuilder, TreeSearchAgent
from gts.games import GameState
from gts.games.dummy import DummyState
from gts.tree import TreeSearchNode

if __name__ == "__main__":
    def always(*args):
        return True

    def never(*args):
        return False

    def no_op(*args):
        pass

    def queue_select(agent: TreeSearchAgent) -> TreeSearchNode:
        return agent.frontier.pop()

    def expand_next(agent: TreeSearchAgent, node: TreeSearchNode, dfs: bool = False) -> TreeSearchNode:
        """ """
        # do not try to expand terminal states
        if node.state.is_terminal:
            return node

        action = node.unexpanded_actions.pop()
        state = node.state.result(action)

        # add node to queue for further expansion if in dfs mode
        if dfs and node.unexpanded_actions:
            agent.frontier.append(node)

        leaf = node.add_child(state, action)
        agent.frontier.append(leaf)

        # search info update
        agent.search_info["nodes_expanded"] += 1

        return leaf

    def expand_next_dfs(agent: TreeSearchAgent, node: TreeSearchNode):
        return expand_next(agent, node, dfs=True)


    def if_depth_reached(agent, node: TreeSearchNode, value: float = 0) -> bool:
        return node.depth == agent.depth or node.state.is_terminal

    def dummy_eval(agent: TreeSearchAgent, state: GameState):
        return DummyState.utilities[state.position]

    def backpropagate_minimax(self, node: TreeSearchNode, value: float) -> None:
        def bp(node):

            max_child_eval = max(c.eval for c in node.children if c.eval is not None)
            min_child_eval = min(c.eval for c in node.children if c.eval is not None)

            if node.is_max_node:
                node.alpha = max(node.alpha, max_child_eval)
            else:
                node.beta = min(node.beta, min_child_eval)

            if all(c.evaluated for c in node.children) and not node.unexpanded_actions:

                node.eval = max_child_eval if node.is_max_node else min_child_eval

                node.evaluated = True

                if node.parent is not None:
                    bp(node.parent)

        if value is None:
            # alpha beta cutoff happened
            bp(node)
        else:
            node.eval = value
            node.evaluated = True

            if node.parent is not None:
                bp(node.parent)

    from random import choice

    def get_minimax_move(self):
        utils = (c.eval for c in self.root.children)

        m = max(utils) if self.root.is_max_node else min(utils)

        # consider all moves that maximize/minimize utility
        optimal_nodes = [c for c in self.root.children if c.eval == m]

        return choice(optimal_nodes).generating_action

    def when_fully_evaluated(self):
        return self.root.eval is not None

    agent = AgentBuilder()\
        .with_should_terminate(when_fully_evaluated)\
        .with_select(queue_select)\
        .with_expand(expand_next_dfs)\
        .with_should_evaluate(if_depth_reached)\
        .with_evaluate(dummy_eval)\
        .with_should_backpropagate(if_depth_reached)\
        .with_backpropagate(backpropagate_minimax)\
        .with_should_trim(never)\
        .with_trim(no_op)\
        .with_get_best_move(get_minimax_move)\
        .build(name="MiniMax")

    print(agent)
    print(type(agent))
    print(type(agent.select))
    print(agent.select.__name__)
    print(agent.info())

    state = DummyState()

    action, info = agent.search(state)

    print(action, info)
