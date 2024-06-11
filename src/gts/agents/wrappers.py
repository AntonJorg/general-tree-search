import time

from typing import TypeVar

from gts.agents.treesearch_agent import TreeSearchAgent
from gts.components import control
from gts.games import GameState

T = TypeVar("T")

class IterativeDeepeningWrapper:
    def __init__(self, agent: TreeSearchAgent):
        self.agent = agent

    def search(self, state: GameState[T], **params) -> tuple[T, dict]:
        depth = 1
        action = None
        params["start_time"] = time.process_time_ns()
        while not control.timed_termination(None, params, {}):
            # TODO: fix without using try/except
            try:
                action, search_info = self.agent.search(state, depth_limit=depth, **params)
            except TypeError:
                # this happens when trying to maximize a set of unevaluated children
                # which means time is up
                pass
            depth += 1

        # TODO: Merge search_info from all depths

        return action, search_info
        
    def components(self):
        return self.agent.components()
    
    def info(self):
        return self.agent.info()