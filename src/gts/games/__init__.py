from typing import Union

from gts.games.connectfour import ConnectFourState
from gts.games.dummy import DummyState
from gts.games.nim import NimState
from gts.games.twenty48 import Twenty48EnvironmentState, Twenty48State

# TODO: Make into abstract base class
GameState = Union[ConnectFourState, NimState, Twenty48State, Twenty48EnvironmentState, DummyState]

adversarial = (DummyState, ConnectFourState, NimState)
