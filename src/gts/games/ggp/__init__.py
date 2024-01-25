import pathlib

from typing import Protocol, cast
from py4j.java_gateway import JavaGateway


class MachineState(Protocol):
    def getContents(self) -> list:
        ...


class Move(Protocol):
    ...


class Role(Protocol):
    ...


class StateMachine(Protocol):
    def getInitialState(self) -> MachineState:
        ...

    def getNextState(self, ms: MachineState, move: Move) -> MachineState:
        ...

    def getLegalMoves(self, ms: MachineState, r: Role) -> list[Move]:
        ...

    def isTerminal(self, ms: MachineState) -> bool:
        ...

    def getUtility(self, ms: MachineState) -> float:
        ...

    def getRole(self, ms: MachineState | int) -> Role:
        ...


class GGPServer(Protocol):
    def getStateMachine(self, filepath: str) -> StateMachine:
        ...


class GGPState:
    @classmethod
    def from_file(cls, filepath: pathlib.Path):
        # treat the returned JavaObject as a GGPServer object
        ggp_server = cast(GGPServer, JavaGateway().entry_point)

        state_machine = ggp_server.getStateMachine(str(filepath))
        initial_state = state_machine.getInitialState()

        name = filepath.stem

        return cls(name, state_machine, initial_state, 0)

    @classmethod
    def from_name(cls, name: str):
        # treat the returned JavaObject as a GGPServer object
        ggp_server = cast(GGPServer, JavaGateway().entry_point)

        filepath = pathlib.Path(".", "games", name, f"{name}.kif")

        state_machine = ggp_server.getStateMachine(str(filepath))
        initial_state = state_machine.getInitialState()

        return cls(name, state_machine, initial_state, 0)

    def __init__(
        self, name: str, state_machine: StateMachine, state: MachineState, moves: int
    ) -> None:
        self.name = name
        self.state_machine = state_machine
        self.state = state
        self.moves = moves

        self.role = self.state_machine.getRole(moves % 2)
        # self.role = self.state_machine.getRole(self.state)
        self.is_terminal = self.state_machine.isTerminal(self.state)
        self.applicable_actions = self._init_applicable_actions()
        self.branching_factor = len(
            self.applicable_actions
        )  # TODO: move to values dict
        self.utility = self.state_machine.getUtility(self.state)

    def __repr__(self):
        sentences = "\n".join(str(c) for c in self.state.getContents())
        return f"GGPState[{self.name}]\n{sentences}\nUtility: {self.utility}"

    def _init_applicable_actions(self):
        if self.is_terminal:
            return []
        actions = self.state_machine.getLegalMoves(self.state, self.role)
        return actions

    def result(self, action):
        return GGPState(
            self.name,
            self.state_machine,
            self.state_machine.getNextState(self.state, action),
            self.moves + 1,
        )
