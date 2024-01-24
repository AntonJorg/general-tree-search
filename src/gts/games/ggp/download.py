import os
import requests
import json

from enum import Enum
from tqdm import tqdm


class Repositories(Enum):
    """GDL game repositories"""

    BASE = "http://games.ggp.org/base"
    DRESDEN = "http://games.ggp.org/dresden"
    STANFORD = "http://games.ggp.org/stanford"


def get_games(repo: Repositories) -> list[str]:
    response = requests.get(f"{repo.value}/games/")
    return response.json()


def get_metadata(repo: Repositories, game: str) -> dict:
    response = requests.get(f"{repo.value}/games/{game}/")
    return response.json()


def get_file(
    repo: Repositories, game: str, file_name: str, version: str | None = None
) -> str:
    version_string = "" if version is None else f"/v{version}"
    url = f"{repo.value}/games/{game}{version_string}/{file_name}"
    response = requests.get(url)
    return response.text


def download_metadata(repo: Repositories, folder="games"):
    games = get_games(repo)

    # GTS only supports two player games
    two_player_games = {}
    for game in tqdm(games):
        metadata = get_metadata(repo, game)
        if metadata["numRoles"] == 2:
            two_player_games[game] = metadata

    if not os.path.isdir(folder):
        os.mkdir(folder)

    file_path = os.path.join(folder, "metadata.json")
    with open(file_path, "w+") as file:
        json.dump(two_player_games, file)

    print(
        f"Saved metadata for {len(two_player_games)} two-player games in '{file_path}'"
    )


def download_games(repo: Repositories, folder="games"):
    with open(os.path.join(folder, "metadata.json"), "r") as file:
        metadata = json.load(file)

    file_types = ["rulesheet", "description", "stylesheet", "user_interface"]

    stats = {k: 0 for k in file_types}

    for game, game_metadata in tqdm(metadata.items()):
        game_folder = os.path.join(folder, game)
        if not os.path.isdir(game_folder):
            os.mkdir(game_folder)

        version = game_metadata["version"]

        def download_game_file(file_type: str):
            file_path = game_metadata.get(file_type)
            if file_path is not None:
                content = get_file(repo, game, file_path, version)
                with open(os.path.join(game_folder, file_path), "w") as file:
                    file.write(content)
                stats[file_type] += 1

        for file_type in file_types:
            download_game_file(file_type)

    print(f"Finished downloading all {len(metadata)} games. Succesful downloads:")
    for k, v in stats.items():
        print(f"{k}:\t\t{v:4d}")


if __name__ == "__main__":
    repo = Repositories.BASE
    download_games(repo)
