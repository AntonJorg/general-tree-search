import time
from copy import deepcopy
from collections import defaultdict, deque
from typing import Callable, Generic, TypeVar, Type
from dataclasses import dataclass, field, asdict

from gts.games import GameState
from gts.tree import TreeSearchNode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gts.components.frontier import Frontier


T = TypeVar("T")

ShouldTerminateType = Callable[["TreeSearchAgent"], bool]

UseFrontierType = Callable[["TreeSearchAgent"], bool]

ShouldSelectType = Callable[["TreeSearchAgent"], bool]

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

ActionValueType = Callable[[TreeSearchNode], float]


@dataclass
class Components(Generic[T]):
    should_terminate: ShouldTerminateType
    use_frontier: UseFrontierType
    select: SelectType
    expand: ExpandType
    evaluate: EvaluateType
    should_backpropagate: ShouldBackpropagateType
    backpropagate: BackpropagateType
    action_value: ActionValueType
    frontier: Type["Frontier"]
    params: dict = field(default_factory=dict)
    
    def to_function_dict(self):
        return {k: v for k, v in asdict(self).items() if not isinstance(v, dict)}
    
    def to_dict(self):
        return asdict(self)


class TreeSearchAgent:
    """
    Agent implements the General Tree Search Algorithm (GTS) in self.search.
    """

    def __init__(
            self,
            name: str,
            should_terminate: ShouldTerminateType,
            use_frontier: UseFrontierType,
            select: SelectType,
            expand: ExpandType,
            evaluate: EvaluateType,
            should_backpropagate: ShouldBackpropagateType,
            backpropagate: BackpropagateType,
            action_value: ActionValueType,
            frontier: Type["Frontier"],
            params = {},
        ):
        self.name = name

        self.initial_params = params

        self.should_terminate = should_terminate
        self.use_frontier = use_frontier
        self.select = select
        self.expand = expand
        self.evaluate = evaluate
        self.should_backpropagate = should_backpropagate
        self.backpropagate = backpropagate
        self.action_value = action_value

        self.frontier = frontier

        self.start_time: int | None = None

        # Additional info for calls to self.search
        self.search_info = defaultdict(float)

    def __repr__(self):
        return f"Agent[{self.name}]"

    def search(self, state: GameState[T], **search_params) -> tuple[T, dict]:
        """
        Implements General Tree Search (GTS).
        """

        if state.is_terminal:
            raise ValueError("Cannot search terminal states!")

        self.search_info.clear()
        self.search_info["depth_reached"] = 0

        root = TreeSearchNode(state, None, None)

        # initialize frontier with root node
        frontier = self.frontier()
        frontier.push(root)

        # copy initial params and update with search-time params
        params = deepcopy(self.initial_params)
        params.update(search_params)

        # use process_time_ns for accuracy when parallelizing
        params["start_time"] = time.process_time_ns()

        while not self.should_terminate(root, params, self.search_info):
            print("Tree:")
            root.print_tree()
            if self.use_frontier(root, params, self.search_info):
                node = frontier.pop()
            else:
                node = root
                while new_node := self.select(node.children, params, self.search_info):
                    node = new_node
            
            leaf = self.expand(node, frontier.push, params, self.search_info)

            self.search_info["depth_reached"] = max(leaf.depth, self.search_info["depth_reached"])

            value = self.evaluate(leaf.state, params, self.search_info)

            while self.should_backpropagate(leaf, value, params, self.search_info):
                self.backpropagate(leaf, value, params, self.search_info)
                leaf = leaf.parent

        print("Tree:")
        root.print_tree()

        # TODO: consider all children with value equal to the best child
        best_child = max(
            root.children, 
            key=lambda x: self.action_value(x, params, self.search_info)
        )
        best_action = best_child.generating_action

        self.search_info["time_spent_ns"] = time.process_time_ns() - params["start_time"]

        return best_action, dict(self.search_info)

    def info(self):
        return f"""{repr(self)}
    - should_terminate: {self.should_terminate.__name__}
    - use_frontier: {self.use_frontier.__name__}
    - frontier: {self.frontier.__name__}
    - select: {self.select.__name__}
    - expand: {self.expand.__name__}
    - evaluate: {self.evaluate.__name__}
    - should_backpropagate: {self.should_backpropagate.__name__}
    - backpropagate: {self.backpropagate.__name__}
    - action_value: {self.action_value.__name__}
    - params: {self.initial_params}
"""

    def inspect(self):
        # TODO: make component function source code printable
        # via inspect.getsource(func)
        pass

    def components(self):
        return Components(
            should_terminate=self.should_terminate,
            use_frontier=self.use_frontier,
            frontier=self.frontier,
            select=self.select,
            expand=self.expand,
            evaluate=self.evaluate,
            should_backpropagate=self.should_backpropagate,
            backpropagate=self.backpropagate,
            action_value=self.action_value,
            params=self.initial_params,
        )
