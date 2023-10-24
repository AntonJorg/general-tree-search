from typing import Protocol, TypeVar

from gts.games.connectfour import ConnectFourState
from gts.games.dummy import DummyState
from gts.games.nim import NimState
from gts.games.twenty48 import Twenty48EnvironmentState, Twenty48State

ActionType = TypeVar("ActionType")

class GameState(Protocol[ActionType]):
    utility: float
    applicable_actions: list[ActionType]
    is_terminal: bool

    def result(self, action: ActionType) -> "GameState[ActionType]":
        ...

# TODO: Make into abstract base class or interface

adversarial = (DummyState, ConnectFourState, NimState)
