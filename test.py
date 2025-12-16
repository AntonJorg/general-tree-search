import pyspiel
from random import choice

game = pyspiel.load_game("oware")

while True:
    i = 0
    
    state = game.new_initial_state()

    print(dir(state))
    exit()
    while not state.is_terminal():
        actions = state.legal_actions()
        state.apply_action(choice(actions))
        print(i, flush=True)
        i += 1
        if i == 999:
            break