from abc import ABC, abstractmethod
from collections import deque

class Frontier(ABC):
    @abstractmethod
    def __init__(self):
        self.frontier = None

    @abstractmethod
    def push(self, node):
        ...

    @abstractmethod
    def pop(self):
        ...

    def __len__(self):
        return len(self.frontier)

    def __bool__(self):
        return bool(self.frontier)

    def __iter__(self):
        return iter(self.frontier)

    def __contains__(self, node):
        return node in self.frontier

    def __repr__(self):
        return f"Frontier[{self.__class__.__name__}]"

    def __str__(self):
        return f"Frontier[{self.__class__.__name__}]"

    def __getitem__(self, item):
        return self.frontier[item]

    def __setitem__(self, item, value):
        self.frontier[item] = value

    def __delitem__(self, item):
        del self.frontier[item]


class FrontierNone(Frontier):
    def __init__(self):
        self.frontier = None

    def push(self, _):
        raise ValueError("Cannot push to None frontier")

    def pop(self):
        raise ValueError("Cannot pop from None frontier")


class FrontierLIFO(Frontier):
    def __init__(self):
        self.frontier = deque()

    def push(self, node):
        self.frontier.append(node)

    def pop(self):
        return self.frontier.pop()