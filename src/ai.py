"""AI and heuristics.
Copyright 2018 Mark Mitterdorfer

Class to implement AI and score heuristics.
"""


class AI(object):
    """Class for AI player.

    Attributes:
        MAX_SCORE (int): Absolute maximum winning / losing score.
    """

    MAX_SCORE = 10000

    @staticmethod
    def manhattan_distance(x1, y1, x2, y2):
        """Obtain the Manhattan distance between two points in 2d coordinates.

        Args:
            x1 (int): x1 coordinate.
            y1 (int): y1 coordinate.
            x2 (int): x2 coordinate.
            y2 (int): y2 coordinate.

        Returns:
            (int): Manhattan distance.

        """
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def inv_dist_to_centre(board, player):
        """Obtain the inverse Manhattan distance from player to centre of board.
        Score higher for moves closest to centre of board.

        Args:
            board (board.Board): Game board object.
            player (int): Player.

        Returns:
            (int): Inverse Manhattan distance.

        """
        total = board.columns * board.rows
        centre = board.columns // 2, board.rows // 2
        dist = AI.manhattan_distance(*board.player_pos(player), *centre)

        if dist <= 0:
            return total + 5
        return int((1.0 / dist) * total)

    #################################################################################
    # These are the scoring functions. Scoring should be relative to both players.  #
    # That is maximising a score for the active player should be to the detriment   #
    # (minimise) of the opponent.                                                   #
    # Scoring functions should be in the format score_funcN and must have the       #
    # function signature (board, winner, depth, player)                             #
    #################################################################################

    @staticmethod
    def score_func1(board, winner, player):
        """Score a move for the active player.
        Difference of inverse Manhattan distance to centre of board from active player
        and inactive player. Score higher if active player is closer to centre than
        the opponent is.

        Args:
            board (board.Board): Game board object.
            winner (boolean/int): False if game is in play, and int for the winning player.
            player (int): "Player" check as winner.

        Returns:
            score (int): Score for the active player.

        """
        # Terminal heuristic / game over scenario
        if winner:
            if winner == player:
                # "player" won
                return AI.MAX_SCORE
            # "player" lost
            return -AI.MAX_SCORE

        # Non-terminal scoring heuristic
        a_dist = AI.inv_dist_to_centre(board, board.active_player)
        o_dist = AI.inv_dist_to_centre(board, board.inactive_player)
        return a_dist - o_dist

    @staticmethod
    def score_func2(board, winner, player):
        """Score a move for the active player.
        Difference of valid moves left from active player and inactive player.
        Score higher if active player has more moves left than the opponent has.

        Args:
            board (board.Board): Game board object.
            winner (boolean/int): False if game is in play, and int for the winning player.
            player (int): "Player" check as winner.

        Returns:
            score (int): Score for the active player.

        """
        # Terminal heuristic / game over scenario
        if winner:
            if winner == player:
                # "player" won
                return AI.MAX_SCORE
            # "player" lost
            return -AI.MAX_SCORE

        # Non-terminal scoring heuristic
        a_moves = len(board.get_legal_moves(board.active_player))
        o_moves = len(board.get_legal_moves(board.inactive_player))
        return a_moves - o_moves

    @staticmethod
    def score_func3(board, winner, player):
        """Score a move for the active player.
        Distance between active player and inactive player.
        Score higher if active player is further away from the inactive player.
        (Enemy avoidance / flee heuristic)

        Args:
            board (board.Board): Game board object.
            winner (boolean/int): False if game is in play, and int for the winning player.
            player (int): "Player" check as winner.

        Returns:
            score (int): Score for the active player.

        """
        # Terminal heuristic / game over scenario
        if winner:
            if winner == player:
                # "player" won
                return AI.MAX_SCORE
            # "player" lost
            return -AI.MAX_SCORE

        # Non-terminal scoring heuristic
        return AI.manhattan_distance(*board.player_pos(board.active_player),
                                     *board.player_pos(board.inactive_player))

    @staticmethod
    def score_func4(board, winner, player):
        """Score a move for the active player.
        Distance between active player and inactive player.
        Score higher if active player is closer to the inactive player.
        (Keep enemy close / attack heuristic)

        Args:
            board (board.Board): Game board object.
            winner (boolean/int): False if game is in play, and int for the winning player.
            player (int): "Player" check as winner.

        Returns:
            score (int): Score for the active player.

        """
        # Terminal heuristic / game over scenario
        if winner:
            if winner == player:
                # "player" won
                return AI.MAX_SCORE
            # "player" lost
            return -AI.MAX_SCORE

        # Non-terminal scoring heuristic
        total = board.columns * board.rows
        dist = AI.manhattan_distance(*board.player_pos(board.active_player),
                                     *board.player_pos(board.inactive_player))

        if dist <= 0:
            return total + 5
        return int((1.0 / dist) * total)

    @staticmethod
    def negamax(board, depth, player, score_func):
        """Perform negamax from the perspective of "player" as the active player.
        Sign +1 if "player" is the active player, and sign -1 for opponent.

        Args:
            board (board.Board): Game board object.
            depth (int): The maximum search depth for each state move.
            player (int): "Player" to maximise / check as winner.
            score_func (function pointer): Scoring heuristic.

        Returns:
            best_score (int), best_move (int, int): Best score and associated move for "player".

        """
        player_sign = +1 if board.active_player == player else -1

        winner = board.is_game_over()
        # Game is over or depth is 0, score the move
        if winner or depth == 0:
            return player_sign * score_func(board, winner, player), None

        best_move = None
        best_score = float("-inf")

        # Explore all possible states
        for move in board.get_legal_moves():
            new_board = board.make_move_copy(*move)

            rec_score, current_move = AI.negamax(new_board, depth - 1, player, score_func)
            current_score = -rec_score

            if current_score > best_score:
                best_score = current_score
                best_move = move

        return best_score, best_move

    @staticmethod
    def abnegamax(board, depth, player, alpha, beta, score_func):
        """Perform abnegamax from the perspective of "player" as the active player.
        This from the Wikipedia site: https://en.wikipedia.org/wiki/Negamax
        Sign +1 if "player" is the active player, and sign -1 for opponent.

        Args:
            board (board.Board): Game board object.
            depth (int): The maximum search depth for each state move.
            player (int): "Player" to maximise / check as winner.
            alpha (int): Lower bound.
            beta (int): Upper bound.
            score_func (function pointer): Scoring heuristic.

        Returns:
            best_score (int), best_move (int, int): Best score and associated move for "player".

        """
        player_sign = +1 if board.active_player == player else -1

        winner = board.is_game_over()
        # Game is over or depth is 0, score the move
        if winner or depth == 0:
            return player_sign * score_func(board, winner, player), None

        best_move = None
        best_score = float("-inf")

        # Explore all possible states
        for move in board.get_legal_moves():
            new_board = board.make_move_copy(*move)

            rec_score, current_move = AI.abnegamax(new_board, depth - 1, player, -beta, -alpha, score_func)
            current_score = -rec_score

            if current_score > best_score:
                best_score = current_score
                best_move = move

            alpha = max(alpha, current_score)
            if alpha >= beta:
                break

        return best_score, best_move

    @staticmethod
    def power_abnegamax(board, depth, player, alpha, beta, score_func):
        """Perform power abnegamax from the perspective of "player" as the active player.
        This is abnegamax + alternative iterative deepening. Find a maximising score. If
        this score is losing <= -MAX_SCORE, then find the next best (positive) score/moves
        from depth-1 ... 1.
        Always search from deeper depths - strong thinkers yet pessimistic winners to
        shallower depths - weak thinkers yet optimistic winners.
        This way we can still make optimistic moves and prevent sudden death / suicide moves
        when the odds stack against us. After all, human players can still make mistakes and
        do not play as perfect, optimal players in minimax / negamax algorithms.
        Typically, you want to call this function for an AI player when playing against a human to
        account for imperfect play when minimax / negamax simulates human moves.
        This can happen when the AI computes a losing score for itself as it assumes the human
        player is playing perfectly, i.e. according to the chosen scoring heuristic for the algorithm.
        In this case the AI will commit a sudden death move, box itself in, and end the game quickly
        as now it shifts its view to a loss with no way out. This is not a good idea, as
        sometimes the human will make a bad move which can give an advantage to the AI player to move
        itself out of a losing score / position.
        Calling this for an AI player vs. AI is futile as both AI players will play a perfect game
        according to the chosen scoring heuristic. (Assuming the scoring heuristic is the same for
        both AI players, if not, it seems like there are only marginal improvements.)

        Args:
            board (board.Board): Game board object.
            depth (int): The maximum search depth for each state move.
            player (int): "Player" to maximise / check as winner.
            alpha (int): Lower bound.
            beta (int): Upper bound.
            score_func (function pointer): Scoring heuristic.

        Returns:
            best_score (int), best_move (int, int): Best score and associated move for "player".

        """
        best_score, best_move = AI.abnegamax(board, depth, player, alpha, beta, score_func)

        if best_score <= -AI.MAX_SCORE:
            # Try shallower depths to get a positive, "optimistic" score
            for i_depth in range(depth - 1, 0, -1):
                best_score, best_move = AI.abnegamax(board, i_depth, player, alpha, beta, score_func)
                # This score is better than losing, found optimistic move
                if best_score > -AI.MAX_SCORE:
                    break

        return best_score, best_move

