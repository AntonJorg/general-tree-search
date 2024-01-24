from py4j.java_gateway import JavaGateway


game = JavaGateway().entry_point

game.loadGDL("games/ticTacToe/ticTacToe.kif")

state = game.getInitialState()
for atom in state.getContents():
    print(atom)

role = game.getRole(state)
print(role)

for move in game.getLegalMoves(state, role):
    print(move)
