import random
from functools import reduce
from itertools import accumulate, chain, islice, repeat


class Twenty48State:
    """
    States in the game 2048 where the player has control. The board is modeled
    as a tuple of tuples, with the log2 value of tiles stored at their respective
    locations. 0 is an empty tile. Rules are as in the original 2048 game,
    which can be found at https://github.com/gabrielecirulli/2048.
    """

    def __init__(
        self, board=None, moves=0, score_penalty=0, action_sequence=""
    ) -> None:

        self.board = board or self._init_empty_board()

        self.utility = (
            sum(
                sum((el - 1) * 2**el if not el == 0 else 0 for el in row)
                for row in self.board
            )
            - score_penalty
        )

        self.successors = {
            "U": self._up(),
            "D": self._down(),
            "L": self._left(),
            "R": self._right(),
        }

        self.applicable_actions = self._init_applicable_actions()

        self.is_terminal = not self.applicable_actions

        self.score_penalty = score_penalty

        self.moves = moves
        self.action_sequence = action_sequence

    def __repr__(self) -> str:
        cell_padding = 8
        board = ""
        for row in self.board:
            board += ("-" * (((cell_padding + 1) * 4) + 1)) + "\n"
            board += "|"
            for tile in row:
                if tile == 0:
                    board += (" " * cell_padding) + "|"
                else:
                    board += (
                        "{: ^{padding}}".format(2**tile, padding=cell_padding) + "|"
                    )
            board += "\n"
        board += "-" * (((cell_padding + 1) * 4) + 1) + "\n"
        board += f"\nApplicable actions: {self.applicable_actions}\n"
        board += f"Moves made : {str(self.moves)}\n"
        board += f"Move string: {self.action_sequence}\n"
        board += f"Score      : {self.utility}\n"
        board += f"Is terminal: {self.is_terminal}"
        return board

    @staticmethod
    def _shift(rows):
        rows = ((el for el in row if el != 0) for row in rows)
        rows = (islice(chain(row, repeat(0)), 4) for row in rows)
        return rows

    @staticmethod
    def _transpose(rows):
        return zip(*rows)

    @staticmethod
    def _reverse(rows):
        return (tuple(row)[::-1] for row in rows)

    @staticmethod
    def _rows_to_tuple(rows):
        return tuple(tuple(row) for row in rows)

    def _compress(self, rows):
        rows = (reduce(self._comp_accum, row, tuple()) for row in rows)
        rows = ((el for el in row if el is not None) for row in rows)
        rows = (islice(chain(row, repeat(0)), 4) for row in rows)
        return rows

    @staticmethod
    def _comp_accum(a, b):
        if len(a) > 0 and a[-1] == b and b != 0:
            return a[:-1] + (b + 1, None)  # Stop chain merging
        else:
            return a + (b,)

    def _left(self):
        board = self._shift(self.board)
        return self._rows_to_tuple(self._compress(board))

    def _right(self):
        board = self._reverse(self.board)
        board = self._shift(board)
        board = self._compress(board)
        return self._rows_to_tuple(self._reverse(board))

    def _up(self):
        board = self._transpose(self.board)
        board = self._shift(board)
        board = self._compress(board)
        return self._rows_to_tuple(self._transpose(board))

    def _down(self):
        board = self._transpose(self.board)
        board = self._reverse(board)
        board = self._shift(board)
        board = self._compress(board)
        board = self._reverse(board)
        return self._rows_to_tuple(self._transpose(board))

    def _board_to_list(self):
        return list(list(row) for row in self.board)

    def _is_board_full(self):
        for row in self.board:
            for tile in row:
                if tile == 0:
                    return False
        return True

    def result(self, action):
        """
        The result function R: S x A -> S
        """
        board = self.successors.get(action)
        if board is None:
            raise ValueError("Unknown action:", action)

        return Twenty48EnvironmentState(
            board,
            self.moves + 1,
            self.score_penalty,
            self.action_sequence + f"{action} ",
        )

    def _init_empty_board(self):
        board_positions = [(j, i) for i in range(4) for j in range(4)]

        positions = random.sample(board_positions, k=2)
        values = random.choices((1, 2), weights=[9, 1], k=2)

        chosen = {(j, i): val for (j, i), val in zip(positions, values)}
        board = tuple(
            tuple(chosen.get((j, i)) or 0 for i in range(4)) for j in range(4)
        )

        return board

    def _init_applicable_actions(self):
        """
        The set A(s).
        """
        valid = []
        for a, board in self.successors.items():
            if board != self.board:
                valid.append(a)

        return valid


class Twenty48EnvironmentState(Twenty48State):
    """
    Separates the environment effects (spawning additional tiles) from the
    player controls.
    """

    def __init__(
        self, board=None, moves=-1, score_penalty=0, action_sequence=""
    ) -> None:

        self.board = board or tuple(tuple(0 for _ in range(4)) for _ in range(4))

        self.applicable_actions = self._init_applicable_actions()

        # no need to normalize, random.choices does that automatically
        self.distribution = [
            9 if val == 1 else 1 for _, _, val in self.applicable_actions
        ]
        self.cumulative_distribution = list(accumulate(self.distribution))

        self.score_penalty = score_penalty
        self.utility = (
            sum(
                sum((el - 1) * 2**el if not el == 0 else 0 for el in row)
                for row in self.board
            )
            - score_penalty
        )

        self.is_terminal = self._is_board_full()

        self.moves = moves
        self.action_sequence = action_sequence

    def result(self, action):
        y, x, val = action
        board = tuple(
            tuple(val if i == x and j == y else self.board[j][i] for i in range(4))
            for j in range(4)
        )

        sp = 4 if val == 2 else 0

        return Twenty48State(
            board,
            self.moves + 1,
            self.score_penalty + sp,
            self.action_sequence + f"{x}{y}{val} ",
        )

    def _init_applicable_actions(self):
        actions = [
            (j, i, val)
            for val in (1, 2)
            for i in range(4)
            for j in range(4)
            if self.board[j][i] == 0
        ]

        return actions
