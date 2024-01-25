from py4j.java_gateway import JavaGateway


class GGPState:
    pass


ggp_server = JavaGateway().entry_point

game = ggp_server.getStateMachine("games/ticTacToe/ticTacToe.kif")

state = game.getInitialState()
for atom in state.getContents():
    print(atom)

role = game.getRole(state)
print(role)

for move in game.getLegalMoves(state, role):
    print(move)
