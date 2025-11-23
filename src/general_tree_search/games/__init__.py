from general_tree_search.games.base import GameState
from general_tree_search.games.connectfour import ConnectFourState
from general_tree_search.games.dummy import DummyState
from general_tree_search.games.gridworld import GridWorldState


class PySpielState:
    def __init__(self, state, moves=0):
        self.state = state
        self.applicable_actions = state.legal_actions()
        self.is_terminal = state.is_terminal()
        self.utility = (state.rewards()[0] + 1) / 2
        self.moves = moves

    def result(self, action):
        new_state = self.state.clone()
        new_state.apply_action(action)

        return PySpielState(new_state, self.moves + 1)

    def __repr__(self):
        return repr(self.state)