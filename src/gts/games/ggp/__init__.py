class GGPState:
    def __init__(self, name, moves=0) -> None:
        self.name = name

        self.moves = moves

        self.applicable_actions = self._init_applicable_actions()
        self.utility = self._init_utility()
        self.is_terminal = self._init_is_terminal()

    def __repr__(self):
        return f"GGPState[{self.name}]"

    def _init_applicable_actions(self):
        pass

    def _init_utility(self):
        pass

    def _init_is_terminal(self):
        pass

    def result(self, action):
        new_pos = DummyState.results[(self.position, action)]
        return DummyState(new_pos, self.moves + 1)
