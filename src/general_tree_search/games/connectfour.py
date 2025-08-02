import time


class ConnectFourState:
    """
    Represents the Connect 4 board as two binary numbers; the piece mask
    and the player mask. Each bit in the numbers correspond to a field on
    the board as such:

    .  .  .  .  .  .  .
    5 12 19 26 33 40 47
    4 11 18 25 32 39 46
    3 10 17 24 31 38 45
    2  9 16 23 30 37 44
    1  8 15 22 29 36 43
    0  7 14 21 28 35 42

    Bitboard representation for a 7x6 board. The bits marked by dots
    are left blank to prevent a four in a row from the top of one row
    to the bottom of the next.

    The piece mask describes which fields contain a piece, and the
    player mask describes which of those pieces belong to the current
    player.

    Though the move count could be inferred from the piece mask,
    this state also keeps a separate move count.
    """

    type Action = int

    BOTTOM_MASK = 0b0000001_0000001_0000001_0000001_0000001_0000001_0000001
    BOARD_MASK = 0b0111111_0111111_0111111_0111111_0111111_0111111_0111111

    def __init__(
        self,
        piece_mask=0,
        player_mask=0,
        moves=0,
        action_sequence="",
        result_delay=0,
    ):
        self.width = 7
        self.height = 6

        self.piece_mask = piece_mask
        self.player_mask = player_mask

        self.moves = moves
        self.action_sequence = action_sequence

        self.result_delay = result_delay

        self.applicable_actions = self._init_applicable_actions()
        self.utility = self._init_utility()
        self.is_terminal = self._init_is_terminal()

    def __repr__(self):
        board = "Board:\n"
        for i in range(self.height - 1, -1, -1):
            for j in range(self.width):
                idx = i + j * (self.height + 1)
                if self.piece_mask & 1 << idx:
                    if self.player_mask & 1 << idx:
                        if self.moves % 2:
                            board += "2 "
                        else:
                            board += "1 "
                    else:
                        if self.moves % 2:
                            board += "1 "
                        else:
                            board += "2 "
                else:
                    board += ". "
            board += "\n"
        board += f"Applicable actions: {self.applicable_actions}\n"
        board += f"Piece mask : {self.piece_mask:0{(self.height + 1) * self.width}b}\n"
        board += f"Player mask: {self.player_mask:0{(self.height + 1) * self.width}b}\n"
        board += f"Moves made : {str(self.moves)}\n"
        board += f"Move string: {self.action_sequence}\n"
        board += f"Winner     : {None if self.utility == 0.5 else (1 if self.utility else 2)}"
        return board

    def _init_applicable_actions(self) -> list[Action]:
        """
        The set A(s).

        Returns the actions that are applicable in the current
        state, ie. the actions corresponding to non-full columns.
        Sorted from the middle out, examples:

        Unsorted:          Return value
        [0, 1, 2, 3, 4] -> [0, 4, 1, 3, 2]
        [0, 1, 2, 3]    -> [0, 3, 1, 2]
        """
        a = self.height - 1
        b = self.height + 1
        moves = (i for i in range(self.width) if not self.piece_mask & (1 << a + i * b))
        return sorted(moves, key=lambda x: -abs(x - self.width // 2 + 0.1))

    def _init_utility(self) -> float:
        """
        The utility function U: S_T -> V. Note that the utility is always given
        from the Max players perspective.

        Returns the utility of terminal states according to the
        following cases:

            Max win: 1.0
            Min win: 0.0
            Draw   : 0.5

        Even though the utility function is theoretically
        only defined on terminal states, this implementation does not
        check if that is the case, but will return 0.5 for
        non-terminal states, as there is no winner.
        """
        # the winner can only be the previous player to move
        pieces = self.player_mask ^ self.piece_mask
        utility_of_win = self.moves % 2

        # size of bit shift needed to check consecutive pieces in
        # the vertical, horizontal, diagonal, and anti-diagonal direction
        shifts = [self.height + 1, 1, self.height, self.height + 2]

        for shift in shifts:
            m = pieces & pieces >> shift
            if m & m >> 2 * shift > 0:
                return utility_of_win

        # if no win is detected
        return 0.5

    def _init_is_terminal(self) -> bool:
        """
        Whether s is a member of S_T.

        Return True in terminal states, false otherwise.
        A state is terminal if there is a winner, or there are no applicable actions.
        """
        return not self.applicable_actions or self.utility != 0.5

    def _possible(self):
        """Mask of possible locations for stones dropped at next move."""
        return (self.piece_mask + self.BOTTOM_MASK) & self.BOARD_MASK

    def _winning_positions(self, position) -> int:
        H = self.height

        r = (position << 1) & (position << 2) & (position << 3)

        p = (position << (H + 1)) & (position << 2 * (H + 1))
        r |= p & (position << 3 * (H + 1))
        r |= p & (position >> (H + 1))
        p >>= 3 * (H + 1)
        r |= p & (position << (H + 1))
        r |= p & (position >> 3 * (H + 1))

        p = (position << H) & (position << 2 * H)
        r |= p & (position << 3 * H)
        r |= p & (position >> H)
        p >>= 3 * H
        r |= p & (position << H)
        r |= p & (position >> 3 * H)

        p = (position << (H + 2)) & (position << 2 * (H + 2))
        r |= p & (position << 3 * (H + 2))
        r |= p & (position >> (H + 2))
        p >>= 3 * (H + 2)
        r |= p & (position << (H + 2))
        r |= p & (position >> 3 * (H + 2))

        return r & (self.BOARD_MASK ^ self.piece_mask)

    def result(self, action: Action) -> "ConnectFourState":
        """
        The result function $\gamma: S \times A \to S$

        Includes the option of inducing an artificial delay, to simulate
        more computationally expensive domains.

        To introduce the delay, pass `result_delay` when constructing the initial state.
        """
        player_mask = self.player_mask ^ self.piece_mask
        piece_mask = self.piece_mask | self.piece_mask + (
            1 << action * (self.height + 1)
        )

        if self.result_delay:
            time.sleep(self.result_delay)

        return ConnectFourState(
            piece_mask,
            player_mask,
            self.moves + 1,
            self.action_sequence + str(action),
            self.result_delay,
        )

    def apply_many(self, action_string: str) -> "ConnectFourState":
        """
        Applies the result function for each action in action_string.
        Useful for generating positions.
        """
        state = self
        for char in action_string:
            if state.is_terminal:
                raise ValueError("Cannot advance from terminal state")
            if int(char) not in state.applicable_actions:
                raise ValueError("Invalid action")
            state = state.result(int(char))
        return state
