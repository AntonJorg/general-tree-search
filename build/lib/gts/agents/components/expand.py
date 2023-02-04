from src.tree import TreeSearchNode

class Expand:
    """
    Defines methods for implementing TreeSearchAgent.expand.

    These methods should:
        - Take a TreeSearchNode
        - Return a TreeSearchNode
        - Possibly modify tree structure and frontier
        - Not modify node data unrelated to tree structure
    """

    def expand_next(self, node: TreeSearchNode, dfs: bool = False) -> TreeSearchNode:
        """
        
        """
        # do not try to expand terminal states
        if node.state.is_terminal:
            return node

        action = node.unexpanded_actions.pop()
        state = node.state.result(action)

        # add node to queue for further expansion if in dfs mode
        if dfs and node.unexpanded_actions:
            self.frontier.append(node)

        leaf = node.add_child(state, action)
        self.frontier.append(leaf)

        # search info update
        self.search_info["nodes_expanded"] += 1

        return leaf

    def expand_next_depth_limited(self, node: TreeSearchNode, dfs: bool = False) -> TreeSearchNode:
        """
        
        """
        # depth limiting
        if node.depth == self.depth:
            return node

        return self.expand_next(node, dfs)

    def expand_next_alpha_beta(self, node: TreeSearchNode) -> TreeSearchNode:
        """
        
        """
        # alpha beta pruning
        # uses strict inequalities to prevent suboptimal moves from having equal
        # utility to the optimal move
        if node.children:
            if node.is_max_node and node.children[-1].eval > node.beta or \
                not node.is_max_node and node.children[-1].eval < node.alpha:
                
                self.search_info["ab_prunes"] += 1

                node.unexpanded_actions.clear()
                return node

        return self.expand_next_depth_limited(node, dfs=True)

    def expand_next_beam(self, node: TreeSearchNode) -> TreeSearchNode:
        """
        
        """
        # beam search on root
        if node.parent is None and not node.children:
            node.unexpanded_actions = self.filter_unexpanded_actions(node)

        leaf = self.expand_next_alpha_beta(node)

        # beam search on leaf nodes
        if leaf.unexpanded_actions:
            leaf.unexpanded_actions = self.filter_unexpanded_actions(leaf)

        return leaf

    def expand_all(self, node: TreeSearchNode) -> TreeSearchNode:
        """
        
        """
        # TODO: Test if necessary
        if node.state.is_terminal:
            return node

        # search info update
        self.search_info["nodes_expanded"] += len(node.unexpanded_actions)

        while node.unexpanded_actions:
            action = node.unexpanded_actions.pop()
            state = node.state.result(action)
            leaf = node.add_child(state, action)
            self.frontier.append(leaf)

        # return last child for evaluate function
        return leaf

    def expand_all_depth_limited(self, node: TreeSearchNode) -> TreeSearchNode:
        """
        
        """
        if node.depth == self.depth:
            return node
        
        return self.expand_all(node)
