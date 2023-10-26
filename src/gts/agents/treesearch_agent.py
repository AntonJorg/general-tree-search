import time
from collections import defaultdict, deque
from typing import Callable, Generic, TypeVar
from dataclasses import dataclass, fields, asdict

from gts.games import GameState
from gts.tree import TreeSearchNode


T = TypeVar('T')

ShouldTerminateType = Callable[
    ["TreeSearchAgent"],
    bool
]

SelectType = Callable[
    ["TreeSearchAgent"],
    TreeSearchNode
]

ExpandType = Callable[
    ["TreeSearchAgent", TreeSearchNode],
    TreeSearchNode
]

ShouldEvaluateType = Callable[
    ["TreeSearchAgent", TreeSearchNode],
    bool
]

EvaluateType = Callable[
    ["TreeSearchAgent", GameState[T]],
    float
]

ShouldBackpropagateType = (
    Callable[
        ["TreeSearchAgent", TreeSearchNode],
        bool
    ] |
    Callable[
        ["TreeSearchAgent", TreeSearchNode, float],
        bool
    ]
)

BackpropagateType = (
    Callable[
        ["TreeSearchAgent", TreeSearchNode],
        None
    ] |
    Callable[
        ["TreeSearchAgent", TreeSearchNode, float],
        None
    ]
)

ShouldTrimType = Callable[
    ["TreeSearchAgent"],
    bool
]

TrimType = Callable[
    ["TreeSearchAgent"],
    None
]

GetBestMoveType = Callable[
    ["TreeSearchAgent"],
    T
]


@dataclass
class ComponentFunctions(Generic[T]):
    should_terminate: ShouldTerminateType
    select: SelectType
    expand: ExpandType
    should_evaluate: ShouldEvaluateType
    evaluate: EvaluateType[T]
    should_backpropagate: ShouldBackpropagateType
    backpropagate: BackpropagateType
    should_trim: ShouldTrimType
    trim: TrimType
    get_best_move: GetBestMoveType[T]


@dataclass
class AgentBuilder:
    should_terminate: ShouldTerminateType | None = None
    select: SelectType | None = None
    expand: ExpandType | None = None
    should_evaluate: ShouldEvaluateType | None = None
    evaluate: EvaluateType | None = None
    should_backpropagate: ShouldBackpropagateType | None = None
    backpropagate: BackpropagateType | None = None
    should_trim: ShouldTrimType | None = None
    trim: TrimType | None = None
    get_best_move: GetBestMoveType | None = None

    def merge(self, other: "AgentBuilder"):
        d1, d2 = asdict(self), asdict(other)
        return AgentBuilder(
            **{k: (d1[k] if d2[k] is None else d2[k]) for k in d1.keys()}
        )

    def with_should_terminate(self, func: ShouldTerminateType):
        self.should_terminate = func
        return self

    def with_select(self, func: SelectType):
        self.select = func
        return self

    def with_expand(self, func: ExpandType):
        self.expand = func
        return self

    def with_should_evaluate(self, func: ShouldEvaluateType):
        self.should_evaluate = func
        return self

    def with_evaluate(self, func: EvaluateType):
        self.evaluate = func
        return self

    def with_should_backpropagate(self, func: ShouldBackpropagateType):
        self.should_backpropagate = func
        return self

    def with_backpropagate(self, func: BackpropagateType):
        self.backpropagate = func
        return self

    def with_should_trim(self, func: ShouldTrimType):
        self.should_trim = func
        return self

    def with_trim(self, func: TrimType):
        self.trim = func
        return self

    def with_get_best_move(self, func: GetBestMoveType):
        self.get_best_move = func
        return self

    def build(self, name: str):
        if not self.all_defined():
            raise ValueError("All functions must be specified!")
        cf = ComponentFunctions(**asdict(self))
        return TreeSearchAgent(name, cf)

    def all_defined(self):
        return all(v is not None for _, v in asdict(self).items())


class TreeSearchAgent:
    """
    Agent implements the Extended General Tree Search Algorithm
    (Algorithm 9) in self.search, and also defines all component functions
    as abstract methods to be implemented in subclasses.
    """

    def __init__(self, name: str, cf: ComponentFunctions):
        self.name = name

        self.component_functions = cf

        # unpack manually to enable type hinting
        self.should_terminate = cf.should_terminate
        self.select = cf.select
        self.expand = cf.expand
        self.should_evaluate = cf.should_evaluate
        self.evaluate = cf.evaluate
        self.should_backpropagate = cf.should_backpropagate
        self.backpropagate = cf.backpropagate
        self.should_trim = cf.should_trim
        self.trim = cf.trim
        self.get_best_move = cf.get_best_move

        self.root = None
        self.frontier: deque[TreeSearchNode] = deque()

        self.start_time: int | None = None
        self.search_time: float | None = None

        self.depth = None

        # Additional info for calls to self.search
        self.search_info = defaultdict(float)

    def __repr__(self):
        return f"Agent[{self.name}]"

    def search(self, state: GameState[T]) -> tuple[T, dict]:
        """
        Implements Extended General Tree Search (EGTS).
        """

        if state.is_terminal:
            raise ValueError("Cannot search terminal states!")

        self.search_info.clear()

        self.frontier.clear()
        self.root = TreeSearchNode(state, None, None)
        self.frontier.append(self.root)

        # use process_time_ns for accuracy when parallelizing
        self.start_time = time.process_time_ns()

        while not self.should_terminate(self):

            node = self.select(self)

            leaf = self.expand(self, node)

            value = None
            if self.should_evaluate(self, leaf):
                value = self.evaluate(self, leaf.state)

            if value is not None and self.should_backpropagate(self, leaf, value):
                self.backpropagate(self, leaf, value)

            if self.should_trim(self):
                self.trim(self)

        return self.get_best_move(self), dict(self.search_info)

    def info(self):
        lines = (f"\t- {k}: {v.__name__}" for k, v in asdict(self.component_functions).items())
        return repr(self) + "\n" + "\n".join(lines)

    def inspect(self):
        # TODO: make component function source code printable
        # via inspect.getsource(func)
        pass
