from gts.agents.minimax_agents import *
from gts.agents.mcts_agents import *
from gts.agents.random_agents import *
from gts.agents.maximizer_agents import *

agents = (
    IterativeDeepeningAgent,
    IterativeDeepeningAlphaBetaAgent,
    IterativeDeepeningSimulationAgent,
    BeamSearchAgent,
    BestFirstMiniMaxAgent,
    MCTSAgent,
    MCTSEvaluationAgent,
    PartialExpansionAgent,
    MiniMaxWeightedMCTSAgent,
    StaticWeightedMCTSAgent,
    MCTSTreeMiniMaxAgent,
    ProgressivePruningMCTSAgent
)
