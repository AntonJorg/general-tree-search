from typing import Union

from games.connectfour import ConnectFourState
from games.nim import NimState
from games.twenty48 import Twenty48EnvironmentState, Twenty48State

GameState = Union[ConnectFourState, NimState, Twenty48State, Twenty48EnvironmentState]

states = (
    ConnectFourState,
    NimState
)
