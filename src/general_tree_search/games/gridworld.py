from enum import Enum, IntEnum


class Direction(Enum):
    LEFT = (0, -1)
    RIGHT = (0, 1)
    UP = (-1, 0)
    DOWN = (1, 0)


class Cell(IntEnum):
    EMPTY = 0
    WALL = 1
    GOAL = 2

    def to_char(self):
        if self == 0:
            return "."
        if self == 1:
            return "#"
        return "o"


default_world = [
    [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
    [Cell.EMPTY, Cell.WALL, Cell.WALL, Cell.GOAL, Cell.EMPTY],
    [Cell.EMPTY, Cell.EMPTY, Cell.WALL, Cell.EMPTY, Cell.EMPTY],
    [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
    [Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY, Cell.EMPTY],
]

default_start_pos = (3, 0)


class GridWorldState:
    def __init__(
        self,
        player_position: tuple[int, int] = default_start_pos,
        world: list[list[Cell]] = default_world,
    ):
        self.player_position = player_position
        self.world = world
        self.is_terminal = self._check_terminal()
        self.applicable_actions = self._find_applicable_actions()
        self.utility = 1.0 if self.is_terminal else 0.0

        self.goal_positions = []
        for i in range(len(self.world)):
            for j in range(len(self.world[0])):
                if self.world[i][j] == Cell.GOAL:
                    self.goal_positions.append((i, j))

    def __repr__(self):
        rows = []
        for i, row in enumerate(self.world):
            line = ""
            for j, cell in enumerate(row):
                if (i, j) == self.player_position:
                    line += "P" + " "
                else:
                    line += cell.to_char() + " "
            rows.append(line)
        return "\n".join(rows)

    def _check_terminal(self) -> bool:
        x, y = self.player_position
        return self.world[x][y] == Cell.GOAL

    def _find_applicable_actions(self) -> list[Direction]:
        actions = []
        rows, cols = len(self.world), len(self.world[0])
        x, y = self.player_position

        for action in Direction:
            dx, dy = action.value
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and self.world[nx][ny] != Cell.WALL:
                actions.append(action)
        return actions

    def result(self, action: Direction):
        dx, dy = action.value
        x, y = self.player_position
        new_position = (x + dx, y + dy)
        return GridWorldState(new_position, self.world)
