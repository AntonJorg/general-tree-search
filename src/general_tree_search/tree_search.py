import time
import raylibpy as rl
from abc import ABC, abstractmethod
from types import MethodType
from typing import Callable, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
from general_tree_search.search_tree import (
    Node,
    get_parent,
    get_children,
    set_values,
    expand_one,
)
from general_tree_search.games import GameState


type Value = dict

type ShouldTerminate = Callable[[TreeSearchAgent, Node], bool]
type ShouldSelect = Callable[[TreeSearchAgent, Node], bool]
type Choose = Callable[[TreeSearchAgent, list[Node]], Node]
type ShouldEvaluate = Callable[[TreeSearchAgent, Node], bool]
type Evaluate = Callable[[TreeSearchAgent, GameState], Value]
type Update = Callable[[TreeSearchAgent, list[Node]], Value]
type ActionValue = Callable[[TreeSearchAgent, list[Node]], Value]


@dataclass
class AgentDefinition:
    should_terminate: ShouldTerminate
    should_select: ShouldSelect
    choose: Choose
    evaluate: Evaluate
    update: Update
    actionvalue: ActionValue

    def to_agent_type(self, name: str):
        cls = type(name, (TreeSearchAgent,), {})

        methods = asdict(self)

        # attach methods as class methods
        for method_name, func in methods.items():
            setattr(cls, method_name, func)

        # remove added methods from abstract method set
        cls.__abstractmethods__ = cls.__abstractmethods__.difference(methods.keys())

        return cls


class TreeSearchAgent(ABC):
    def __init__(self):
        self.search_stats = defaultdict(float)

    def search(self, state: GameState, delay=0.0, plot_settings=None):
        assert not state.is_terminal, "Cannot search terminal states!"

        root = Node(state, parent=None, generating_action=None)

        iterations = 0
        self.search_stats.clear()
        self.search_stats["start_time"] = time.time()
        if plot_settings is not None:
            rl.set_trace_log_level(rl.RL_LOG_ERROR)
            rl.init_window(plot_settings.width, plot_settings.height, "Tree Search")

        while not self.should_terminate(root):
            node = self.select(root)
            child = self.expand(node)

            values = self.evaluate(child)
            set_values(child, values)
            self.backpropagate(child)

            if (
                plot_settings is not None
                and iterations % plot_settings.iters_per_render == 0
            ):
                self.plot_tree(root, plot_settings)

        self.search_stats["end_time"] = time.time()

        if plot_settings is not None:
            rl.close_window()

        return root

    def select(self, node: Node) -> Node:
        while self.should_select(node) and not node.state.is_terminal:
            children = get_children(node)
            node = self.choose(node, children)

        return node

    def expand(self, node: Node) -> Node:
        child = expand_one(node)
        self.search_stats["expansions"] += 1

        return child

    def backpropagate(self, node: Node):
        while (node := get_parent(node)) is not None:
            children = get_children(node)
            values = self.update(node, children)
            set_values(node, values)

    def plot_tree(self, root: Node, plot_settings):
        width = plot_settings.width
        height = plot_settings.height

        def plot_node(node: Node, width, start_x, start_y):
            row_height = height * (1 - 0.8 ** (node.depth + 1)) - start_y

            u = plot_settings.get_utility(node.values)

            r = round(255 * max(min(1, 2 - 2 * u), 0))
            g = round(255 * max(min(1, 2 * u), 0))

            rl.draw_rectangle(
                start_x + 1,
                start_y + 1,
                width - 2,
                row_height - 2,
                (r, g, 0, 255),
            )

            if not node._children:
                return

            total_count = sum(plot_settings.get_width(c.values) for c in node._children)

            child_x = start_x
            for c in node._children:
                child_width = width * plot_settings.get_width(c.values) / total_count
                if width < 3:
                    return
                plot_node(c, child_width, child_x, start_y + row_height)
                child_x += child_width

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        plot_node(root, width, 0, 0)

        rl.end_drawing()
        time.sleep(plot_settings.delay)

    @abstractmethod
    def should_terminate(self):
        pass

    @abstractmethod
    def should_select(self):
        pass

    @abstractmethod
    def choose(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def update(self):
        pass


@dataclass
class PlotSettings:
    delay: float
    iters_per_render: int
    width: int
    height: int
    get_utility: Callable
    get_width: Callable
