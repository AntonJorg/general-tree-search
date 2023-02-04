from __future__ import annotations
from typing import List, Tuple
import matplotlib.pyplot as plt


class NimState:
    """

    """

    def __init__(self, width=10, array=None, moves=0, action_sequence=""):
        self.width = width

        self.array = list(range(1, width + 1)) if array is None else array

        self.moves = moves
        self.action_sequence = action_sequence

        self.applicable_actions = self._init_applicable_actions()
        self.utility = self._init_utility()
        self.is_terminal = self._init_is_terminal()

    def __repr__(self):
        board = "Board:\n"
        for i in self.array:
            if i:
                board += "I " * i + "\n"
            else:
                board += "-\n" 
            
        board += f"Applicable actions: {self.applicable_actions}\n"
        board += f"Array      : {self.array}\n"
        board += f"Moves made : {str(self.moves)}\n"
        board += f"Move string: {self.action_sequence}\n"
        board += f"Winner     : {None if self.utility == 0.5 else (1 if self.utility else 2)}"
        return board

    def _init_applicable_actions(self) -> List[Tuple[int, int]]:
        """
        The set A(s).

        Returns the actions that are applicable in the current
        state.
        """
        actions = []
        for i, size in enumerate(self.array):
            for j in range(size):
                actions.append((i, j + 1))
        return actions

    def _init_utility(self) -> int:
        """
        The utility function U: S^o -> R.

        Returns the utility of terminal states according to the
        following cases:

            Player 1 win: 1.0
            Player 2 win: 0.0
            Draw        : Not possible

        Even though the utility function is theoretically
        only defined on terminal states, this implementation does not
        check if that is the case, but will return 0.5 for
        non-terminal states, as there is no winner.
        """
        if not any(self.array):
            return self.moves % 2

        # if no win is detected
        return 0.5

    def _init_is_terminal(self) -> bool:
        """
        Whether s is a member of S^o

        Return True in terminal states, false otherwise.
        A state is terminal if there is a winner, or there are no applicable actions.
        """
        return self.utility != 0.5


    def result(self, action: Tuple[int, int]) -> NimState:
        """
        The result function R: S x A -> S
        """
        idx, a = action

        array = [val - a if i == idx else val for i, val in enumerate(self.array)]

        return NimState(self.width, array, self.moves + 1, self.action_sequence + f"{idx},{a} ")


    def apply_many(self, action_string: str) -> NimState:
        """
        Applies the result function for each action in action_string.
        Useful for generating positions.
        """
        for char in action_string.split(" "):
            action = tuple(int(c) for c in char.split(","))
            state = self.result(action)
        return state
