from math import sqrt

from src.tree import TreeSearchNode

class Backpropagate:
    """
    Defines methods for implementing TreeSearchAgent.backpropagate.

    These methods should:
        - Take a TreeSearchNode and a float (or a list of floats)
        - Not return anything
        - Only propagate up through the tree, i.e. from node to parent
        - Not change the structure of the tree
    """

    def backpropagate_sum(self, node: TreeSearchNode, value: float) -> None:    
        node.cumulative_utility += value
        node.count += 1
    
        if node.parent is not None:
            self.backpropagate_sum(node.parent, value)

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

    def backpropagate_expectimax(self, node, value):
        def bp(n):
            if n is None or len(n.unexpanded_actions) != 0 or any(c.eval is None for c in n.children):
                return

            if n.is_max_node:
                n.eval = max(c.eval for c in n.children)
            else:
                n.eval = sum(c.eval * w for c, w in zip(n.children, n.state.distribution[::-1])) / sum(n.state.distribution)

            if n.parent is not None:
                bp(n.parent)
           
        node.eval = value
        bp(node.parent)

    def backpropagate_sum_and_minimax(self, node, value):
        evaluation, simulation_result = value

        self.backpropagate_sum(node, simulation_result)

        def bp(node):
            child_evals = (c.eval for c in node.children)
            pre_update_eval = node.eval
            if node.is_max_node:
                node.eval = max(child_evals)
            else:
                node.eval = min(child_evals)
            
            # ancestor values will not change if current value did not
            if node.parent is not None and pre_update_eval != node.eval:
                bp(node.parent)

        node.eval = evaluation

        bp(node.parent)
    
    def store_eval_and_backpropagate_sum(self, node, value):
        evaluation, simulation_result = value

        node.eval = evaluation

        self.backpropagate_sum(node, simulation_result)
