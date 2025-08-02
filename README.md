# General Tree Search (GTS)

This repository contains the reference implementation of **General Tree Search (GTS)**, a unified framework for game-playing agents described in our paper 'A Generalised Approach to Search Algorithms in Games,' as well as scripts for reproducing the experiments.

## Overview

GTS modularizes adversarial tree search into four steps—**selection**, **expansion**, **evaluation**, and **backpropagation**—allowing hybrid algorithms such as MiniMax, MCTS, and Best-First MiniMax to be instantiated within the same framework.

It also generalises to classical search, allowing for the implementation of BFS, DFS, A*, AND-OR search, etc.

## Features

- Modular agent construction via component functions
- Built-in agents: Best-First Minimax, MCTS, and 6 hybrids
- Bandit-based search over agent space (Hierarchical UCB)
- Example environment: Connect Four

## Requirements

- Python >= 3.13
- Dependencies: `numpy`, `matplotlib`, etc.

## Usage

To reproduce the experiment, run the following:

```bash
git clone https://github.com/AntonJorg/general-tree-search.git
cd general-tree-search
uv run experiments/run_experiment.py
```

## Agent Configuration

In the article we consider Best-First MiniMax and MCTS, and use them to create 6 hybrid algorithms.

Each agent is defined by a triple of component functions (see Section 4 and Table 1 in the article for descriptions):

| Agent ID      | CHOOSE | EVALUATE | UPDATE |
|---------------|--------|----------|--------|
| `MCTS`        | `UCT`  | `SIM`    | `SUM`  |
| `BFMM`        | `PV`   | `EVAL`   | `MM`   |
| `BF_SIM`      | `PV`   | `SIM`    | `MM`   |
| `MCTS_PV`     | `PV`   | `SIM`    | `SUM`  |
| `MCTS_EVAL`   | `UCT`  | `EVAL`   | `SUM`  |
| `BF_UCT`      | `UCT`  | `EVAL`   | `MM`   |
| `BF_SUM`      | `PV`   | `EVAL`   | `SUM`  |
| `MCTS_MM`     | `UCT`  | `SIM`    | `MM`   |

See [`experiments/agents.py`](./experiments/agents.py) for implementation details.

## Zero sum vs Constant sum

The article uses a strict zero-sum definition for games, where $U(s, MAX) + U(s, MIN) = 0$ must hold for all terminal states.
For implementation reasons, this repository uses utilities on $[0, 1]$, and is constant-sum: $U(s, MAX) + U(s, MIN) = 1$.
Zero-sum and constant-sum is theoretically equivalent, so this poses no issues.

## Citation

TBD after publication.

## License

This code is licensed under Creative Commons Attribution 4.0 International.
