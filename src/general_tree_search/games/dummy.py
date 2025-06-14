class DummyState:
    actions = {0: [0, 1], 1: [0, 1], 2: [0], 3: [], 4: [], 5: [0, 1], 6: []}
    results = {
        (0, 0): 1,
        (0, 1): 2,
        (1, 0): 3,
        (1, 1): 4,
        (2, 0): 5,
        (5, 0): 6,
        (5, 1): 4,
    }
    utilities = {0: None, 1: None, 2: None, 3: 1, 4: -1, 5: None, 6: 0}

    def __init__(self, position=0, moves=0) -> None:
        self.position = position

        self.applicable_actions = DummyState.actions[position]
        self.utility = DummyState.utilities[position]

        self.is_terminal = not (self.utility is None and self.applicable_actions)

        self.moves = moves

    def __repr__(self):
        return f"DummyState[{self.position}]"

    def result(self, action):
        new_pos = DummyState.results[(self.position, action)]
        return DummyState(new_pos, self.moves + 1)
