import chess
from chess.pgn import read_game
from io import StringIO

import chess.pgn

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 10
}

TYPICAL_PIECE_COUNTS = {
    chess.PAWN: 8,
    chess.KNIGHT: 2,
    chess.BISHOP: 2,
    chess.ROOK: 2,
    chess.QUEEN: 1,
    chess.KING: 1
}

CORNER_SQUARES = [chess.A1, chess.A8, chess.H8, chess.H1]

def opposite_colour(colour: str):
    return "black" if colour == "white" else "white"

# takes in a parsed PGN, estimates game craziness
# and returns a score
def estimate_game_craziness(game: chess.pgn.Game):
    score = 0

    game_moves = list(game.mainline())

    pieces_moved: list[chess.PieceType] = []
    material_differences = []
    
    for node_index, move_node in enumerate(game_moves):
        move = move_node.move
        board = move_node.board()

        turn_colour = "black" if board.turn else "white"

        try:
            pieces_moved.append(
                board.piece_at(move.to_square).piece_type
            )
        except:
            pieces_moved.append(chess.KING)

        # get data about pieces on board
        material = {
            "white": 0,
            "black": 0
        }

        material_differences.append(
            abs(material["white"] - material["black"])
        )

        piece_counts = {
            "white": {},
            "black": {}
        }

        king_square = {
            "white": 0,
            "black": 0
        }

        pieces_remaining = 0

        for piece_type in chess.PIECE_TYPES:
            piece_counts["white"][piece_type] = 0
            piece_counts["black"][piece_type] = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)

            if piece is not None:
                piece_colour = "white" if piece.color else "black"

                material[piece_colour] += PIECE_VALUES[piece.piece_type]

                piece_counts[piece_colour][piece.piece_type] += 1

                if piece.piece_type == chess.KING:
                    king_square[piece_colour] = square

                pieces_remaining += 1

        # if material difference has been high for too long, discard game
        if len(material_differences) >= 14:
            balanced_position_found = False

            for i in range(14):
                current_difference = material_differences[-(i + 1)]

                if current_difference <= 11:
                    balanced_position_found = True
                    break

            if not balanced_position_found:
                return -1

        # number of simultaneously hanging pieces
        for square in chess.SQUARES:
            piece = board.piece_at(square)

            # There must be a piece in the square
            # It must be the opposite of whose turn it is
            # It cannot be a king because a king cannot have attackers
            if (
                piece is None
                or piece.color == board.turn
                or piece.piece_type == chess.KING
            ):
                continue

            # If the piece being looked at was just traded off,
            # there's no sacrifice
            last_position = game_moves[node_index - 1].board()
            last_piece = last_position.piece_at(square)

            if (
                last_piece is not None
                and PIECE_VALUES[last_piece.piece_type] >= PIECE_VALUES[piece.piece_type]
            ):
                continue

            # Get the attackers of the current square
            attacker_squares = board.attackers(not piece.color, square)

            # Get defenders of the current square
            defender_squares = board.attackers(piece.color, square)

            if len(attacker_squares) > len(defender_squares):
                score += PIECE_VALUES[piece.piece_type]
            else:
                # Count attackers that are of less value than the piece
                for attacker_square in attacker_squares:
                    attacker = board.piece_at(attacker_square)

                    if PIECE_VALUES[attacker.piece_type] < PIECE_VALUES[piece.piece_type]:
                        score += PIECE_VALUES[piece.piece_type]
                        break

        # discard threefold repetitions
        if board.can_claim_threefold_repetition():
            return -1
        
        # reward castling or king mates
        if (
            board.is_checkmate()
            and (
                "O-" in move_node.san()
                or "K" in move_node.san()
            )
        ):
            score += 20

        # number of pieces on the board ABOVE that which is typical
        # weighted towards rarity of this happening
        for colour in piece_counts.keys():
            for piece_type, count in piece_counts[colour].items():
                if count > TYPICAL_PIECE_COUNTS[piece_type]:
                    extra_count = count - TYPICAL_PIECE_COUNTS[piece_type]

                    if piece_type == chess.QUEEN:
                        if extra_count == 1:
                            score += 0.5
                        else:
                            score += 0.5 + (5 * (extra_count - 1))
                    else:
                        score += 4 * extra_count

        # underpromotions, weighted towards their rarity
        if move.promotion == chess.QUEEN:
            score += 2.5
        elif move.promotion == chess.KNIGHT:
            score += 7.5
        elif move.promotion == chess.ROOK:
            score += 8.5
        elif move.promotion == chess.BISHOP:
            score += 12.5

        # pieces moving to their most uncommon squares,
        # example Qa1, Nh1 etc.
        if (
            "O-" not in move_node.san()
            and move.to_square in CORNER_SQUARES
        ):
            moved_piece_type = board.piece_at(move.to_square).piece_type

            if moved_piece_type in [chess.QUEEN, chess.BISHOP]:
                score += 2
            elif moved_piece_type == chess.KNIGHT:
                score += 3

        # is king in the centre of the board when there are lots of pieces left
        if (
            king_square[turn_colour] > 23
            and king_square[turn_colour] < 40
            and node_index <= 30
            and piece_counts[opposite_colour(turn_colour)][chess.QUEEN] > 0
        ):
            score += 2.5

        # consecutive moves of the king
        if (
            node_index <= 30
            and pieces_remaining >= 20
            and pieces_moved[-1] == chess.KING
        ):
            pieces_moved_index = 1

            while pieces_moved_index <= len(pieces_moved):
                last_moved_piece = pieces_moved[-pieces_moved_index]

                if last_moved_piece == chess.KING:
                    score += 1.5 * (1.075 ** ((pieces_moved_index - 1) / 2))
                else:
                    break

                pieces_moved_index += 2

    return round(score, 2)


# takes in a PGN string and returns the estimated
# craziness score
def estimate_pgn_craziness(pgn: str):
    try:
        game = read_game(
            StringIO(pgn)
        )
    except:
        raise ValueError("failed to parse PGN.")

    return estimate_game_craziness(game)