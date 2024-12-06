import csv
from time import time
from io import StringIO
from chess.pgn import read_game
from craziness import estimate_game_craziness

games = csv.reader(open("chesscom2022/gm_games_2022.csv"))

craziest_game = ""
craziest_game_score = 0

boring_game = ""
boring_game_score = 2 ** 32

game_index = 0

start_time = time()

for game_data in games:
    if len(game_data[0]) == 0:
        continue

    if game_index % 100 == 0:
        print(f"processing game {game_index} / 754,428...")

    pgn = game_data[3]

    time_class = game_data[7]
    white_rating = int(game_data[11])
    black_rating = int(game_data[14])

    if (
        time_class != "rapid"
        or white_rating < 2300
        or black_rating < 2300
    ):
        game_index += 1
        continue

    game = read_game(StringIO(pgn))
    
    if game is not None:
        game_score = estimate_game_craziness(game)

        if game_score > craziest_game_score:
            craziest_game = pgn
            craziest_game_score = game_score

        if game_score < boring_game_score:
            boring_game = pgn
            boring_game_score = game_score

    game_index += 1

log_file = open(f"output_{time()}.log", "w")

log_file.writelines([
    "the craziest game found was:\n",
    craziest_game + "\n",
    f"with a score of {craziest_game_score}\n",
    f"search took {round(time() - start_time, 2)}s\n"
])