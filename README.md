General Tree Search (GTS)
===============================================================================

```python
def TreeSearch(State):
    global Parameters = ... # Dictionary accessible from all functions
    Frontier = ... # LIFO / FIFO / Priority Queue
    Root = Node(State)

    while not ShouldTerminate(Root):
        # Choose node for expansion using either tree traversal or the frontier
        Node = Select(Root, Frontier)

        # Generate new state with applicable action
        # If Node is fully expanded, Leaf = Node
        Leaf = Expand(Node)

        # Some agents (e.g. MiniMax) do not need to evaluate all states
        if ShouldEvaluate(Leaf):
            Value = Evaluate(Leaf.State)

        # Backprop w/o evaluation is useful for proactive pruning
        if ShouldBackPropagate(Leaf, Value):
            Backpropagate(Leaf, Value)

        # For removing nodes from the tree, i.e. retroactive pruning
        if ShouldTrim(Root):
            Trim(Root, Frontier)

    # Decide best move based on root and its children, or values
    # stored in Parameters
    return GetBestMove(Root)
```

# Example usage

## Instantiating a MiniMax agent and searching a state
```python
.. include:: ./examples/minimax.py
```
