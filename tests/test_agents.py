from types import NoneType

from gts.agents import predefined
from gts.games import DummyState


def test_adversarial():
    state = DummyState()
    for agent in predefined:
        action, search_info = agent.search(state, search_time=0.01)

        assert action == 1
        assert isinstance(search_info, dict)
