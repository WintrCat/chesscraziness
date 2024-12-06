from os import listdir
from time import time
from chess.pgn import read_game
from pickle import dump, load
from craziness import estimate_game_craziness

games_directory = "caissabase"
snapshots_directory = "snapshots"

high_score_game_count = 100
low_score_game_count = 20

pgn_files = listdir(games_directory)

craziest_games = []
boring_games = []

# load pickled snapshots of games if possible
try:
    print("attempting to load snapshot files...")

    craziest_games = load(open(f"{snapshots_directory}/craziest_snapshot.pkl"))
    boring_games = load(open(f"{snapshots_directory}/boring_snapshot.pkl"))

    print("successfully loaded snapshot files")
except FileNotFoundError:
    print("snapshot files not found, skipping...")
except:
    print("failed to load snapshot files, skipping...")

start_time = time()

for file_index, pgn_file_name in enumerate(pgn_files):
    print(
        f"processing {pgn_file_name} "
        + f"(file {file_index + 1}/{len(pgn_files)})..."
    )

    # read current pgn file in directory
    pgn_file = open(f"{games_directory}/{pgn_file_name}", errors="ignore")

    # parse current pgn file
    game = read_game(pgn_file)

    # attempt to load game index from snapshot
    game_index = 0
    try:
        game_index = int(open(f"{snapshots_directory}/game_index.txt", "r").read().strip())
    except:
        pass

    while game is not None:
        if (game_index + 1) % 100 == 0:
            print(f"processing game {game_index + 1} in this file...")

        if (game_index + 1) % 1000 == 0:
            print(f"saving snapshot at game {game_index + 1}...")

            dump(
                craziest_games,
                open(f"{snapshots_directory}/craziest_snapshot.pkl", "wb")
            )

            dump(
                boring_games,
                open(f"{snapshots_directory}/boring_snapshot.pkl", "wb")
            )

            open(f"{snapshots_directory}/game_index.txt", "w").write(str(game_index))

        try:
            game_site = game.headers.get("Site")

            game_date = game.headers.get("Date")

            try:
                white_elo = int(game.headers.get("WhiteElo"))
                black_elo = int(game.headers.get("BlackElo"))
            except:
                try:
                    game = read_game(pgn_file)
                except:
                    print(f"failed to parse game {game_index + 2}, skipping to next file...")
                    break

                game_index += 1
                continue

            if (
                len(list(game.mainline_moves())) >= 40
                and game_site is not None
                and "chess.com" not in game_site
                and "lichess" not in game_site
                and game_date is not None
                and white_elo >= 2200
                and black_elo >= 2200
                and game.headers.get("Event") != game.headers.get("Site")
            ):
                game_score = estimate_game_craziness(game)

                craziest_games.append({
                    "file_name": pgn_file_name,
                    "game": str(game.mainline_moves()),
                    "headers": str(game.headers),
                    "score": game_score
                })

                craziest_games.sort(
                    key=lambda game_data : game_data["score"],
                    reverse=True
                )

                craziest_games = craziest_games[:high_score_game_count]

                if len(boring_games) < low_score_game_count and game_score == 0:
                    boring_games.append({
                        "file_name": pgn_file_name,
                        "game": str(game.mainline_moves()),
                        "headers": str(game.headers),
                        "score": game_score
                    })   
        except:
            print(f"error encountered processing game {game_index + 1}, skipping it...")

        try:
            game = read_game(pgn_file)
        except:
            print(f"failed to parse game {game_index + 2}, skipping to next file...")
            break

        game_index += 1

highest_scoring_leaderboard = ("\n" * 16).join([
    str(game) for game in craziest_games
])

lowest_scoring_leaderboard = ("\n" * 16).join([
    str(game) for game in boring_games
])

output_log = open(f"output_{time()}.log", "w")

output_log.write("\n".join([
    f"the top {high_score_game_count} highest scoring games found were:",
    highest_scoring_leaderboard,
    "",
    f"{low_score_game_count} games that didn't receive any points:",
    lowest_scoring_leaderboard
]))

print(f"process finished in {round(time() - start_time, 2)}s")