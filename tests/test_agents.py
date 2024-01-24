from types import NoneType

from gts.agents import predefined
from gts.games import DummyState


def test_adversarial():
    state = DummyState()
    for agent in predefined:
        agent.initial_params["search_time"] = 0.001
        action, search_info = agent.search(state)

        assert not isinstance(action, NoneType)
        assert isinstance(search_info, dict)
