import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True,
                    help="Input path")
parser.add_argument("-o", "--output", default="results/processed",
                    help="Output path")

args = parser.parse_args()

input_path = Path(args.input)
assert input_path.is_file(), "Input must be a file!"

output_path = Path(args.output)
assert output_path.is_dir(), "Output must be a directory!"

ts = datetime.now().strftime("%Y_%m_%d_%H_%M")
out_dir = Path(output_path) / ts
out_dir.mkdir(parents=True, exist_ok=False)


with open(input_path, "r") as f:
    data = f.read()
    data = data.splitlines()


totals = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

agent_totals = defaultdict(float)
agent_counts = defaultdict(int)

game_agent_totals = defaultdict(lambda: defaultdict(float))
game_agent_counts = defaultdict(lambda: defaultdict(int))

game_totals = defaultdict(float)
game_counts = defaultdict(int)


test = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for line in data:
    game, a1, a2, u = line.split()
    #if a1 == a2:
    #    continue
    u = float(u)

    test[a1][a2][game] += 1

    totals[game][a1][a2] += u
    counts[game][a1][a2] += 1

    agent_totals[a1] += u
    agent_counts[a1] += 1

    game_agent_totals[game][a1] += u
    game_agent_counts[game][a1] += 1


    agent_totals[a2] += 1 - u
    agent_counts[a2] += 1

    game_agent_totals[game][a2] += 1 - u
    game_agent_counts[game][a2] += 1

    game_totals[game] += u
    game_counts[game] += 1


total_avg = {
    game: {
        a1: {
            a2: (totals[game][a1][a2] / counts[game][a1][a2])
            for a2 in totals[game][a1]
            if counts[game][a1][a2] > 0
        }
        for a1 in totals[game]
    }
    for game in totals
}

# Per-agent averages
agent_avg = {a: agent_totals[a] / agent_counts[a] for a in agent_totals}

# Per-game averages
per_game_avg = {
    game: {
        a: game_agent_totals[game][a] / game_agent_counts[game][a]
        for a in game_agent_totals[game]
    }
    for game in game_agent_totals
}

game_avg = {g: game_totals[g] / game_counts[g] for g in game_totals}


def save_bar(d: dict, out_dir: Path, name: str, *, percent=True):
    items = sorted(d.items(), key=lambda kv: kv[1], reverse=True)  # highest first
    labels = [k for k, _ in items]
    vals = np.array([v for _, v in items], dtype=float)
    if percent:
        vals *= 100.0

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar(labels, vals)
    ax.set_title(name)
    ax.set_ylabel("Percent" if percent else "Value")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()

    path = out_dir / f"{name}.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path

def save_heatmap(dd: dict, out_dir: Path, name: str, xlabel, ylabel, *, percent=True):
    # dd: {row_key: {col_key: value}}
    df = pd.DataFrame(dd).T

    # sort rows/cols by descending mean (highest = top/left)
    df = df.loc[df.mean(axis=1).sort_values(ascending=False).index]
    df = df[df.mean(axis=0).sort_values(ascending=False).index]

    df_plot = df * 100.0 if percent else df

    fig, ax = plt.subplots()
    sns.heatmap(
        df_plot,
        ax=ax,
        cmap="grey",
        annot=True,
        fmt=".1f" if percent else ".3g",
        linewidths=0.5,
        linecolor="black",
        linestyle="--",
        vmin=0,
        vmax=100,
        square=True,
    )
    ax.set_title(name)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    #ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()

    path = out_dir / f"{name}.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


plt.rcParams.update(
    {
        "font.family": "serif",
        #"font.size": 26,
        # "font.weight": "bold",
        # "axes.labelweight": "bold",
        "mathtext.fontset": "cm",
        "mathtext.default": "regular",
    }
)

save_bar(agent_avg, out_dir, "Average utility per agent", percent=True)
save_heatmap(per_game_avg, out_dir, "per_game_averages_heatmap", "Agent", "Game", percent=True)
save_bar(game_avg, out_dir, "Average utility per game (max player)", percent=True)
save_heatmap(game_agent_counts, out_dir, "game_agent_counts_heatmap", "Agent", "Game", percent=False)

for game, averages in total_avg.items():
    save_heatmap(averages, out_dir, f"Game results: {game}", "Min player agent", "Max player agent", percent=True)