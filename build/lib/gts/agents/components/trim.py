class Reflect:
    """
    Defines methods for implementing TreeSearchAgent.reflect.

    These methods should:
        - Take no arguments
        - Evaluate the state of the search tree and/or the frontier
        - Possibly modify the search tree and/or the frontier
        - Return nothing
    """

    def reset_tree_increment_depth(self):
        """
        
        """
        def deepest_node(node):
            if node.children:
                return max(deepest_node(c) for c in node.children)
            else:
                return node.depth

        # log before increase to reflect last completed search
        self.search_info["depth"] = min(self.depth, deepest_node(self.root))

        action = self.get_minimax_move()
        self.best_move = action
        self.depth += 1

        # reset search tree
        self.last_iter_root = self.root.copy()
        self.root.reset()
        self.frontier.append(self.root)

    def fractional_pruning(self):
        """
        
        """
        def recurse(node):
            node.children = [c for c in node.children if \
                c.count >= node.count / (node.branching_factor + self.pruning_factor)]

            for c in node.children:
                if not c.unexpanded_actions:
                    recurse(c)

        recurse(self.root)
