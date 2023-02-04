from types import NoneType

from gts.agents import agents
from gts.games import DummyState


def test_adversarial():
    for Agent in agents:
        state = DummyState()
        agent = Agent(search_time=0.05)

        action, search_info = agent.search(state)

        assert not isinstance(action, NoneType)
        assert isinstance(search_info, dict)
