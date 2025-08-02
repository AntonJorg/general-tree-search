import random
import matplotlib.pyplot as plt
from tqdm import tqdm

from general_tree_search.games import ConnectFourState

from agents import agents


def elo_update(name_a, name_b, score_a, k=32):
    rating_a = elo_ratings[name_a]
    rating_b = elo_ratings[name_b]

    # Expected scores
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 - expected_a  # Since it's a zero-sum game

    # Actual scores
    score_b = 1 - score_a

    # Updated ratings
    elo_ratings[name_a] = rating_a + k * (score_a - expected_a)
    elo_ratings[name_b] = rating_b + k * (score_b - expected_b)


def choose_agents():
    return random.sample(agents, k=2)


def run_game(agent1, agent2):
    pair = (agent1(), agent2())

    state = ConnectFourState()

    while not state.is_terminal:
        agent = pair[state.moves % 2]
        root = agent.search(state)
        action = agent.get_solution(root)
        state = state.result(action)

    return state.utility


elo_ratings = {agent.__name__: 1000 for agent in agents}
elo_history = [elo_ratings.copy()]

N_ROUNDS = 100

for n in tqdm(range(N_ROUNDS)):
    agent1, agent2 = choose_agents()

    result = run_game(agent1, agent2)

    elo_update(agent1.__name__, agent2.__name__, result)

    elo_history.append(elo_ratings.copy())


# Plot each key's values
for key in elo_history[0].keys():
    values = [d[key] for d in elo_history]
    plt.plot(values, label=key)

plt.xlabel("Index")
plt.ylabel("Value")
plt.title("Value changes for each key")
plt.legend()
plt.grid(True)
plt.show()
