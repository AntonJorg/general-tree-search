from math import log, sqrt
from random import choice

from gts.tree import TreeSearchNode


class Select:
    """
    Defines methods for implementing TreeSearchAgent.select.

    These methods should:
        - Be callable with no arguments
        - Base their selection on self.root or self.frontier
        - Return a TreeSearchNode
        - Have no side effects
    """

    def uct_select(self, node: TreeSearchNode = None) -> TreeSearchNode:
        if node is None:
            node = self.root

        if node.unexpanded_actions or node.state.is_terminal:
            return node

        def uct(child):
            if child.is_max_node:
                exploit = (child.count - child.cumulative_utility) / child.count
            else:
                exploit = child.cumulative_utility / child.count

            explore = sqrt(2) * sqrt(log(node.count) / child.count)

            return exploit + explore

        best_child = sorted(node.children, key=uct)[-1]

        return self.uct_select(best_child)

    def partial_expansion_uct_select(
        self, node: TreeSearchNode = None
    ) -> TreeSearchNode:
        if node is None:
            node = self.root

        if not node.children or node.state.is_terminal:
            return node

        def uct(child):
            if child.is_max_node:
                exploit = (child.count - child.cumulative_utility) / child.count
            else:
                exploit = child.cumulative_utility / child.count

            explore = sqrt(2) * sqrt(log(node.count) / child.count)

            return exploit + explore

        ucb_child = 0.5 + sqrt(2) * sqrt(log(node.count) / (1 + len(node.children)))

        ucts = (uct(c) for c in node.children)

        if node.unexpanded_actions and max(ucts) < ucb_child:
            return node
        else:
            self.search_info["partial_expansions"] += 1
            best_child = sorted(node.children, key=uct)[-1]
            return self.partial_expansion_uct_select(best_child)

    def weighted_uct_select(self, node: TreeSearchNode = None) -> TreeSearchNode:
        if node is None:
            node = self.root

        if node.unexpanded_actions or node.state.is_terminal:
            return node

        def weighted_uct(child):
            if node.is_max_node:
                exploit = child.cumulative_utility / child.count
                evaluation = child.eval
            else:
                exploit = 1 - child.cumulative_utility / child.count
                evaluation = 1 - child.eval

            explore = sqrt(2) * sqrt(log(node.count) / child.count)

            q = 1 / sqrt(child.count)

            return evaluation * q + exploit * (1 - q) + explore

        best_child = sorted(node.children, key=weighted_uct)[-1]

        return self.weighted_uct_select(best_child)

    def uct_select_stochastic_environment(self, node):
        if node.unexpanded_actions or node.state.is_terminal:
            return node

        if not node.is_max_node:
            return self.select(choice(node.children))

        c = node.cumulative_utility / node.count

        def uct(child):
            exploit = child.cumulative_utility / child.count

            explore = c * sqrt(log(node.count) / child.count)

            return exploit + explore

        best_child = sorted(node.children, key=uct)[-1]

        return self.select(best_child)

    def queue_select(self) -> TreeSearchNode:
        return self.frontier.pop()

    def principal_variation_select(self):
        def recurse(node):
            if node.unexpanded_actions or not node.children:
                return node

            equal_children = [c for c in node.children if c.eval == node.eval]

            return recurse(equal_children[0])

        return recurse(self.root)
