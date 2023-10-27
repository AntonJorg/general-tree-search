from typing import Any
from abc import ABC, abstractmethod

from gts.agents.treesearch_agent import TreeSearchAgent


class Component(ABC):
    def __init__(self, agent: TreeSearchAgent) -> None:
        self.agent = agent

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

