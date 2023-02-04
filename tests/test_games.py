import random

from gts.games import GameState, adversarial


def test_adversarial():
    for State in adversarial:
        state = State()
        assert isinstance(state, State)
        assert isinstance(state.applicable_actions, list)
        assert isinstance(state.is_terminal, bool)
        assert isinstance(state.moves, int)
