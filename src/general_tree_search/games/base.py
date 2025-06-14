from abc import ABC, abstractmethod
from typing import Protocol, Hashable

class GameState[T: Hashable](Protocol):
    utility: float
    applicable_actions: list[T]
    is_terminal: bool

    @abstractmethod
    def result(self, action: T) -> "GameState[T]":
        ...

