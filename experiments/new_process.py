from collections import defaultdict

with open("test_data_data_data.txt", "r") as f:
    data = f.read()
    data = data.splitlines()

agent_totals = defaultdict(float)
agent_counts = defaultdict(int)
game_agent_totals = defaultdict(lambda: defaultdict(float))
game_agent_counts = defaultdict(lambda: defaultdict(int))

game_totals = defaultdict(float)
game_counts = defaultdict(int)

for line in data:
    game, a1, a2, u = line.split()
    if a1 == a2:
        continue
    u = float(u)

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


# Total averages
total_avg = {a: agent_totals[a] / agent_counts[a] for a in agent_totals}

# Per-game averages
per_game_avg = {
    game: {
        a: game_agent_totals[game][a] / game_agent_counts[game][a]
        for a in game_agent_totals[game]
    }
    for game in game_agent_totals
}

game_avg = {g: game_totals[g] / game_counts[g] for g in game_totals}


print("Total averages:")
for k, v in total_avg.items():
    print(f"{k}: {v*100:.2f}%")

print("Per-game averages:", per_game_avg)
for game, game_dict in per_game_avg.items():
    print(game)
    for k, v in game_dict.items():
        print(f"{k}: {v*100:.2f}%")

print("Game averages:")
for k, v in game_avg.items():
    print(f"{k}: {v*100:.2f}%")
