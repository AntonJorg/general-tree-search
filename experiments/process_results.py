import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast
import os
from collections import defaultdict
from pathlib import Path

import matplotlib as mpl

# mpl.rcParams.update(
#    {
#        "text.usetex": True,
#        "font.family": "serif",  # Use LaTeX's serif font (Computer Modern)
#        "font.serif": ["Computer Modern Roman"],
#        "text.latex.preamble": r"\usepackage{amsmath}",  # Optional
#    }
# )

plt.rcParams.update(
    {
        "font.family": "serif",
        # "font.weight": "bold",
        # "axes.labelweight": "bold",
        "mathtext.fontset": "cm",
        "mathtext.default": "regular",
    }
)


# Load and parse the file
folder = Path("results/raw")
newest_file = max(folder.glob("*"), key=os.path.getmtime)

with open(newest_file, "r") as f:
    lines = [ast.literal_eval(line.strip()) for line in f if line.strip()]

# Extract experiment parameters, pairwise results, and counts
experiment_params = lines[0]
experiment = experiment_params["experiment_type"]
pairwise_results = lines[
    1 : 1 + (experiment_params["n_agents"] * (experiment_params["n_agents"] - 1)) // 2
]
agent_counts = lines[
    1 + (experiment_params["n_agents"] * (experiment_params["n_agents"] - 1)) // 2 :
]

# Get list of agents
agents = sorted({k for match in pairwise_results for k in match})

# Compute winrate matrix
n_agents = len(agents)
agent_idx = {agent: i for i, agent in enumerate(agents)}
win_matrix = np.zeros((n_agents, n_agents))

# Fill winrate matrix
for match in pairwise_results:
    (a1, a2) = match.items()
    a1_name, a1_score = a1
    a2_name, a2_score = a2
    i, j = agent_idx[a1_name], agent_idx[a2_name]
    win_matrix[i, j] = a1_score / (a1_score + a2_score)
    win_matrix[j, i] = a2_score / (a1_score + a2_score)

# Compute overall winrates
winrates = win_matrix.sum(axis=1) / (len(agents) - 1)  # no matches againts self
sorted_indices = np.argsort(winrates)
sorted_agents = [agents[i] for i in sorted_indices]
sorted_winrates = winrates[sorted_indices]

# Parse count evolution
count_dict = defaultdict(list)
for count_entry in agent_counts:
    for k, v in count_entry.items():
        arr = np.array([float(x) for x in v.split(",")])
        count_dict[k] = arr

plt.rcParams.update({"font.size": 20})

# Plot: Barchart + line plot
fig, axs = plt.subplots(2, 1, figsize=(12, 12))

# Bar chart: overall winrate
axs[0].set_title("Overall Winrate per Agent")
axs[0].barh(
    range(n_agents),
    sorted_winrates,
    xerr=[0.1 for _ in range(n_agents)],
    capsize=2,
    color="gray",
)
axs[0].set_yticks(range(n_agents))
axs[0].set_yticklabels(
    [agent.replace("Agent", "") for agent in sorted_agents], rotation=45
)
axs[0].set_xlabel("Average Winrate")
axs[0].set_xlim(0, 1)
xticks = [0, 0.25, 0.5, 0.75, 1]
axs[0].set_xticks(xticks, xticks)
axs[0].axvline(0.5, linestyle="--", color="black")

linestyles = iter(
    ["dashed", "dotted", "dashdot", "solid", "solid", "solid", "solid", "solid"]
)

# Line chart: count evolution
axs[1].set_title("Agent Selection Frequency Over Time")
max_count = max(c[-1] for c in count_dict.values())
for agent in sorted_agents:
    counts = count_dict.get(agent)
    label = agent if counts[-1] > max_count / 2 else "Others"
    linestyle = next(linestyles) if label != "Others" else "solid"
    if counts is not None:
        axs[1].plot(
            range(len(counts)),
            counts,
            label=label,
            color="black",
            alpha=0.6,
            linestyle=linestyle,
        )
# Deduplicate by label
handles, labels = axs[1].get_legend_handles_labels()
by_label = dict(zip(labels, handles))
axs[1].legend(by_label.values(), by_label.keys(), loc="upper left")
axs[1].set_xlabel("Rounds")
axs[1].set_xlim(0, len(counts))
axs[1].set_ylabel("Selection Count")

plt.tight_layout()
plt.savefig(f"results/processed/{experiment}-results.pdf", bbox_inches="tight")

# Plot: Sorted heatmap
sorted_indices = np.argsort(-winrates)
sorted_agents = [agents[i] for i in sorted_indices]
sorted_win_matrix = win_matrix[np.ix_(sorted_indices, sorted_indices)]
plt.figure(figsize=(8, 8))
sns.heatmap(
    sorted_win_matrix,
    xticklabels=sorted_agents,
    yticklabels=sorted_agents,
    cmap="Greys",
    annot=True,
    fmt=".2f",
    cbar=False,
)
plt.title("Pairwise Winrate Heatmap (Sorted)")
plt.xlabel("Opponent")
plt.ylabel("Agent")
plt.tight_layout()

plt.savefig(f"results/processed/{experiment}-heatmap.pdf", bbox_inches="tight")
