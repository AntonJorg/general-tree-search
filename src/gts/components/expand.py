"""Defines methods for implementing TreeSearchAgent.expand.

These methods should:
    - Take a TreeSearchNode
    - Return a TreeSearchNode
    - Possibly modify tree structure and frontier
    - Not modify node data unrelated to tree structure
"""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from gts.agents import TreeSearchAgent

from gts.components.frontier import Frontier
from gts.games.connectfour import ConnectFourState
from gts.tree import TreeSearchNode

FrontierPushType = Callable[[Frontier, TreeSearchNode], None]

def expand_next(
    node: TreeSearchNode, push_to_frontier: FrontierPushType, params: dict, search_info: dict, dfs: bool = False
) -> TreeSearchNode:
    """ """
    # do not try to expand terminal states
    if node.state.is_terminal:
        return node

    action = node.unexpanded_actions.pop()
    state = node.state.result(action)

    # add node to queue for further expansion if in dfs mode
    if dfs and node.unexpanded_actions:
        push_to_frontier(node)

    leaf = node.add_child(state, action)
    push_to_frontier(leaf)

    # search info update
    search_info["nodes_expanded"] += 1

    return leaf


def expand_next_dfs(node: TreeSearchNode, push_to_frontier: FrontierPushType, params: dict, search_info: dict,) -> TreeSearchNode:
    return expand_next(agent, node, dfs=True)


def expand_next_depth_limited(
    node: TreeSearchNode, push_to_frontier: FrontierPushType, params: dict, search_info: dict, dfs: bool = False
) -> TreeSearchNode:
    """ """
    # depth limiting
    if node.depth == params["depth_limit"]:
        return node

    return expand_next(node, push_to_frontier, params, search_info, dfs)


def expand_next_alpha_beta(
    node: TreeSearchNode, push_to_frontier: FrontierPushType, params: dict, search_info: dict,
) -> TreeSearchNode:
    """ """
    # alpha beta pruning
    # uses strict inequalities to prevent suboptimal moves from having equal
    # utility to the optimal move
    if node.children:
        if (
            node.is_max_node
            and node.children[-1].eval > node.beta
            or not node.is_max_node
            and node.children[-1].eval < node.alpha
        ):
            search_info["ab_prunes"] += 1

            node.unexpanded_actions = []  # .clear() not possible for py4j compatibility
            return node

    return expand_next_depth_limited(node, push_to_frontier, params, search_info, dfs=True)


def expand_next_beam(node: TreeSearchNode, push_to_frontier: FrontierPushType, params: dict, search_info: dict,) -> TreeSearchNode:
    """ """
    # beam search on root
    if node.parent is None and not node.children:
        node.unexpanded_actions = filter_unexpanded_actions(agent, node)

    leaf = expand_next_alpha_beta(agent, node)

    # beam search on leaf nodes
    if leaf.unexpanded_actions:
        leaf.unexpanded_actions = filter_unexpanded_actions(agent, leaf)

    return leaf


# TODO: this function should be supplied in the builder, and is not necessarily
# component
def filter_unexpanded_actions(agent: "TreeSearchAgent", node: TreeSearchNode):
    match node.state:
        case ConnectFourState():
            return _connectfour_filter_unexpanded_actions(agent, node)
        case _:
            return node.unexpanded_actions


def _connectfour_filter_unexpanded_actions(
    agent: "TreeSearchAgent", node: TreeSearchNode[ConnectFourState]
):
    # root case
    if not node.state.piece_mask:
        middle = node.state.width // 2
        if node.state.width % 2:
            return [middle]
        else:
            return [middle - 1, middle]

    played_rows = [
        i
        for i in range(node.state.width)
        if node.state.piece_mask & 1 << (node.state.height + 1) * i
    ]

    beam = range(
        max(0, min(played_rows) - 1), min(node.state.width, max(played_rows) + 2)
    )

    beam = [action for action in beam if action in node.state.applicable_actions]

    return sorted(beam, key=lambda x: -abs(x - node.state.width // 2 + 0.1))


def expand_all(node: TreeSearchNode, push_to_frontier: FrontierPushType, params: dict, search_info: dict,) -> TreeSearchNode:
    """ """
    # TODO: Test if necessary
    if node.state.is_terminal:
        return node

    # search info update
    search_info["nodes_expanded"] += len(node.unexpanded_actions)

    leaf = None
    while node.unexpanded_actions:
        action = node.unexpanded_actions.pop()
        state = node.state.result(action)
        leaf = node.add_child(state, action)
        push_to_frontier(leaf)

    assert leaf is not None
    # return last child for evaluate function
    return leaf


def expand_all_depth_limited(
    node: TreeSearchNode, push_to_frontier: FrontierPushType, params: dict, search_info: dict,
) -> TreeSearchNode:
    """ """
    if node.depth == params["depth_limit"]:
        return node

    return expand_all(node, push_to_frontier, params, search_info)
