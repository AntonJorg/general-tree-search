import random

from general_tree_search.games import ConnectFourState


state = ConnectFourState()
print(state)

while not state.is_terminal:
    action = random.choice(state.applicable_actions)
    state = state.result(action)
    print(state)
