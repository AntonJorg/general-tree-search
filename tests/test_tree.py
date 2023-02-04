import pytest

from gts.games import adversarial
from gts.tree import TreeSearchNode


def test_node():
    state = adversarial[0]()
    node = TreeSearchNode(state, None, None)
    assert isinstance(node, TreeSearchNode)
