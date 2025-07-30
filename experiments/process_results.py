import os
import ast
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from collections import defaultdict

directory = "results"

# Get the latest file
latest_file = sorted(
    (os.path.join(directory, f) for f in os.listdir(directory)), key=os.path.getmtime
)[-3]

# Read contents into a variable
with open(latest_file, "r") as f:
    contents = f.read()

print(latest_file)

dict_list = [ast.literal_eval(line) for line in contents.splitlines() if line.strip()]

utilities = defaultdict(float)
games = defaultdict(float)

for d in dict_list:
    n_games = d["n_games"]
    for k, v in d.items():
        if k != "n_games":
            utilities[k] += v
            games[k] += n_games


agent_names = list(utilities.keys())

df = pd.DataFrame(columns=["Winrate"], index=[agent_names])
for k, v in utilities.items():
    df.loc[k, "Winrate"] = v / games[k]
    print(f"{k}: {v} / {games[k]}")


sns.barplot(x="Agent", y="Winrate", data=df.reset_index(names="Agent"))
plt.xticks(rotation=45)
plt.show()

mapping = {
    "MCTSAgent": ("UCT", "SIM", "EXP"),
    "MCTSPrincipalAgent": ("PV", "SIM", "EXP"),
    "MCTSEvalAgent": ("UCT", "EVAL", "EXP"),
    "MCTSMinimaxAgent": ("UCT", "SIM", "MM"),
    "BFMMExpUtilAgent": ("PV", "EVAL", "EXP"),
    "BFMMSimulationAgent": ("PV", "SIM", "MM"),
    "BFMMUCTAgent": ("UCT", "EVAL", "MM"),
    "BFMMAgent": ("PV", "EVAL", "MM"),
}

# Apply MultiIndex
df.index = pd.MultiIndex.from_tuples(
    [mapping[idx[0]] for idx in df.index], names=["choose", "evaluate", "update"]
)

print(df.sort_index())

x_map = {"UCT": 0, "PV": 1}
y_map = {"SIM": 0, "EVAL": 1}
z_map = {"EXP": 0, "MM": 1}

# Create a 2x2x2 array of winrates
cube = np.zeros((2, 2, 2))
for (choose, evaluate, update), value in df["Winrate"].items():
    cube[x_map[choose], y_map[evaluate], z_map[update]] = value

# Generate 2D projections (XY, YZ, ZX)
proj_xy = np.mean(cube, axis=2)
proj_yz = np.mean(cube, axis=0)
proj_zx = np.mean(cube, axis=1)

# Plot heatmaps
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
sns.heatmap(proj_xy, annot=True, cmap="viridis", ax=axes[0], cbar=False)
axes[0].set_title("XY projection (z=EXP)")
axes[0].set_xlabel("y (SIM/EVAL)")
axes[0].set_ylabel("x (UCT/PV)")

sns.heatmap(proj_yz, annot=True, cmap="viridis", ax=axes[1], cbar=False)
axes[1].set_title("YZ projection (x=UCT)")
axes[1].set_xlabel("z (EXP/MM)")
axes[1].set_ylabel("y (SIM/EVAL)")

sns.heatmap(proj_zx, annot=True, cmap="viridis", ax=axes[2], cbar=True)
axes[2].set_title("ZX projection (y=SIM)")
axes[2].set_xlabel("z (EXP/MM)")
axes[2].set_ylabel("x (UCT/PV)")

plt.tight_layout()
plt.show()

# Generate 2D projections (XY, YZ, ZX)
proj_x = np.mean(cube, axis=(1, 2))
proj_y = np.mean(cube, axis=(0, 2))
proj_z = np.mean(cube, axis=(0, 1))

projs = [proj_x, proj_y, proj_z]

# Plot heatmaps
fig, axes = plt.subplots(1, 1, figsize=(12, 4))

for i in range(3):
    axes.scatter(i * np.ones(2), projs[i])

axes.set_title("")
axes.set_xlabel("Component")
axes.set_ylabel("Function")

plt.tight_layout()
plt.show()

with open("results/winrates.tex", "w") as f:
    f.write(df.to_latex(float_format="%.2f", na_rep=""))

df = pd.DataFrame(columns=agent_names, index=agent_names)

for d in dict_list:
    k1, k2 = list(d.keys())[:2]
    v = d[k1] / d["n_games"]
    df.loc[k1, k2] = v
    df.loc[k2, k1] = 1 - v

sns.heatmap(df.astype(float), annot=True, cmap="viridis")
plt.show()

with open("results/pairwise_winrates.tex", "w") as f:
    f.write(df.to_latex(float_format="%.2f", na_rep=""))
