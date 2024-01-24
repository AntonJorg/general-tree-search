import time
from copy import deepcopy
from collections import defaultdict, deque
from typing import Callable, Generic, TypeVar
from dataclasses import dataclass, field, asdict

from gts.games import GameState
from gts.tree import TreeSearchNode

T = TypeVar("T")

ShouldTerminateType = Callable[["TreeSearchAgent"], bool]

SelectType = Callable[["TreeSearchAgent"], TreeSearchNode]

ExpandType = Callable[["TreeSearchAgent", TreeSearchNode], TreeSearchNode]

ShouldEvaluateType = Callable[["TreeSearchAgent", TreeSearchNode], bool]

EvaluateType = Callable[["TreeSearchAgent", GameState[T]], float]

ShouldBackpropagateType = (
    Callable[["TreeSearchAgent", TreeSearchNode], bool]
    | Callable[["TreeSearchAgent", TreeSearchNode, float], bool]
)

BackpropagateType = (
    Callable[["TreeSearchAgent", TreeSearchNode], None]
    | Callable[["TreeSearchAgent", TreeSearchNode, float], None]
)

ShouldTrimType = Callable[["TreeSearchAgent"], bool]

TrimType = Callable[["TreeSearchAgent"], None]

GetBestMoveType = Callable[["TreeSearchAgent"], T]


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
    params: dict

    def function_dict(self):
        return {k: v for k, v in asdict(self).items() if not isinstance(v, dict)}


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
    params: dict = field(default_factory=dict)

    def merge(self, other: "AgentBuilder"):
        d1, d2 = asdict(self), asdict(other)
        return AgentBuilder(
            **{
                k: (d1[k] if d2[k] is None else d2[k])
                for k in d1.keys()
                if k != "params"
            },
            params={**self.params, **other.params},
        )

    def with_should_terminate(self, func: ShouldTerminateType, **params):
        self.should_terminate = func
        self.add_params(**params)
        return self

    def with_select(self, func: SelectType, **params):
        self.select = func
        self.add_params(**params)
        return self

    def with_expand(self, func: ExpandType, **params):
        self.expand = func
        self.add_params(**params)
        return self

    def with_should_evaluate(self, func: ShouldEvaluateType, **params):
        self.should_evaluate = func
        self.add_params(**params)
        return self

    def with_evaluate(self, func: EvaluateType, **params):
        self.evaluate = func
        self.add_params(**params)
        return self

    def with_should_backpropagate(self, func: ShouldBackpropagateType, **params):
        self.should_backpropagate = func
        self.add_params(**params)
        return self

    def with_backpropagate(self, func: BackpropagateType, **params):
        self.backpropagate = func
        self.add_params(**params)
        return self

    def with_should_trim(self, func: ShouldTrimType, **params):
        self.should_trim = func
        self.add_params(**params)
        return self

    def with_trim(self, func: TrimType, **params):
        self.trim = func
        self.add_params(**params)
        return self

    def with_get_best_move(self, func: GetBestMoveType, **params):
        self.get_best_move = func
        self.add_params(**params)
        return self

    def build(self, name: str):
        missing = self.missing_components()
        if missing:
            s = "\n".join([f"\t- {m}" for m in missing])
            raise ValueError(f"All functions must be specified! Missing:\n{s}")
        cf = ComponentFunctions(**asdict(self))
        return TreeSearchAgent(name, cf)

    def missing_components(self):
        return [k for k, v in asdict(self).items() if v is None]

    def all_defined(self):
        return all(v is not None for _, v in asdict(self).items())

    def no_trim(self):
        from gts.components.generic import never, no_op

        self.should_trim = never
        self.trim = no_op
        return self

    def add_params(self, **kwargs):
        self.params.update(kwargs)
        return self


class TreeSearchAgent:
    """
    Agent implements the General Tree Search Algorithm (GTS) in self.search.
    """

    def __init__(self, name: str, cf: ComponentFunctions):
        self.name = name

        self.component_functions = cf

        self.initial_params = cf.params
        self.params = {}

        self.memory = {}

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

        # Additional info for calls to self.search
        self.search_info = defaultdict(float)

    def __repr__(self):
        return f"Agent[{self.name}]"

    def search(self, state: GameState[T], **params) -> tuple[T, dict]:
        """
        Implements General Tree Search (GTS).
        """

        if state.is_terminal:
            raise ValueError("Cannot search terminal states!")

        self.search_info.clear()

        # initialize frontier
        self.root = TreeSearchNode(state, None, None)
        self.frontier.append(self.root)

        self.params = deepcopy(self.initial_params)
        self.params.update(params)

        # use process_time_ns for accuracy when parallelizing
        self.start_time = time.process_time_ns()

        while not self.should_terminate(self):
            node = self.select(self)

            leaf = self.expand(self, node)

            value = None
            if self.should_evaluate(self, leaf):
                value = self.evaluate(self, leaf.state)

            if self.should_backpropagate(self, leaf, value):
                self.backpropagate(self, leaf, value)

            if self.should_trim(self):
                self.trim(self)

        best_move = self.get_best_move(self)

        self.search_info["time_spent_ns"] = time.process_time_ns() - self.start_time

        self.frontier.clear()
        self.memory.clear()

        return best_move, dict(self.search_info)

    def info(self):
        lines = (
            f"\t- {k}: {v.__name__}"
            for k, v in self.component_functions.function_dict().items()
        )
        return repr(self) + "\n" + "\n".join(lines)

    def inspect(self):
        # TODO: make component function source code printable
        # via inspect.getsource(func)
        pass

    def to_builder(self):
        return AgentBuilder(**asdict(self.component_functions))
