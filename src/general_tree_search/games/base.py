from abc import abstractmethod
from typing import Protocol, Hashable


class GameState[T: Hashable](Protocol):
    """
    Protocol for objects representing game states (Definition 5).
    """

    utility: float
    applicable_actions: list[T]
    is_terminal: bool

    @abstractmethod
    def result(self, action: T) -> "GameState[T]": ...
