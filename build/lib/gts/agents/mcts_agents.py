from src.agents.treesearch_agent import TreeSearchAgent


class MCTSAgent(TreeSearchAgent):
    """
    Implements Monte Carlo Tree Search as described by
    Remi Coulom, Efficient Selectivity and Backup Operators in Monte-Carlo Tree Search. 2006.
    """
    def __init__(self, search_time):
        super().__init__()
        self.search_time = search_time

    def __repr__(self):
        return super().__repr__() + f"+st={self.search_time}"

    def select(self):
        return self.uct_select()

    def expand(self, node):
        return self.expand_next(node)

    def should_evaluate(self, node):
        return True

    def evaluate(self, state):
        return self.simulate(state)

    def should_backpropagate(self, node, value):
        return True

    def backpropagate(self, node, value):
        self.backpropagate_sum(node, value)

    def should_trim(self):
        pass

    def trim(self):
        pass

    def get_best_move(self):
        return self.most_robust_child()

    def should_terminate(self):
        return self.timed_termination()


class MCTSEvaluationAgent(MCTSAgent):
    """
    Replaces the simulation step with a static evaluation
    """
    def evaluate(self, state):
        return self.static_evaluation(state)


class PartialExpansionAgent(MCTSAgent):
    """
    Adds partial expansion, allowing the search to start expanding
    children before the node itself is fully expanded.

    Emil Juul Jacobsen, Rasmus Greve, and Julian Togelius. “Monte mario: Platforming with
    MCTS”. In: Association for Computing Machinery, 2014, pp. 293–300.    
    """
    def select(self):
        return self.partial_expansion_uct_select()


class StaticWeightedMCTSAgent(MCTSAgent):
    """
    Adds static evaluation alongside simulations. UCB1 values are modified
    to include the static evaluation value.
    """
    def select(self):
        return self.weighted_uct_select()

    def evaluate(self, state):
        return self.evaluate_and_simulate(state)

    def backpropagate(self, node, value):
        self.store_eval_and_backpropagate_sum(node, value)

    def get_best_move(self):
        return self.weighted_eval_utility_move()


class MiniMaxWeightedMCTSAgent(StaticWeightedMCTSAgent):
    """
    Adds minimax backups for fully expanded nodes.
    """    
    def backpropagate(self, node, value):
        self.backpropagate_sum_and_minimax(node, value)


class MCTSTreeMiniMaxAgent(MiniMaxWeightedMCTSAgent):
    """
    Selects best move solely based on the backed up static
    evaluation values from the weighted MCTS tree.
    """
    def get_best_move(self):
        return self.get_minimax_move()


class ProgressivePruningMCTSAgent(MCTSAgent):
    """
    Periodically traverses the tree to remove unpromising nodes.
    The current method is not statistically motivated and performs
    quite poorly, but similar more thought out methods have shown promise.    
    """
    def __init__(self, search_time, pruning_factor=6):
        super().__init__(search_time)
        self.pruning_factor = pruning_factor

    def __repr__(self):
        return super().__repr__() + f"+p={self.pruning_factor}"

    def should_trim(self):
        return self.periodic()

    def trim(self):
        self.fractional_pruning()
