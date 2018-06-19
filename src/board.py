"""Board state.
Copyright 2018 Mark Mitterdorfer

Class to implement board state and valid moves.
"""

import random
import pickle


class Board(object):
    """Board class for state and move validation.

    Attributes:
        rows (int): Number of rows in the board.
        columns (int): Number of columns in the board.
        __board (list): Private list containing board state.
        __active_player (int): Numerical number of current/active player.
        active_player (property, int): ""
        __inactive_player (int): Numerical number of inactive player.
        inactive_player (property, int): ""
        board_list (property, list): The raw board state as a list, use this for rendering.
        __players_position (dict): Private dict of players position, key corresponds to player.
        player1_pos (property, tuple): (X, Y) location of player 1. Can be None if game just started.
        player2_pos (property, tuple): (X, Y) location of player 2. Can be None if game just started.
    """

    # Board/box states, must be unique and in powers of 2 (bit masking)
    PLAYER1 = 1
    PLAYER2 = 2
    BOX_CLEAR = 4
    BOX_BLOCK = 8
    BOX_BLOCKED_MASK = 16  # Leave blocked as the last entry of block states and the highest

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns

        self.__board = []
        self.__active_player = Board.PLAYER1
        self.__inactive_player = Board.PLAYER2

        # Player 1 and player 2 coordinates set to None for start of game
        self.__players_position = {Board.PLAYER1: None, Board.PLAYER2: None}
        self.clear_board()

    def __eq__(self, other):
        """Equality operator.

        Args:
            other (Board): The other Board object to compare to.

        """
        return self.__dict__ == other.__dict__

    def clear_board(self):
        """Clear the game board list.

        """
        self.__board = [Board.BOX_CLEAR for _ in range(self.rows * self.columns)]

    def gen_random_blocked_boxes(self, min, max):
        """Generate random blocked boxes.

        Args:
            min (int): Minimum bound of blocked boxes.
            max (int): Maximum bound of blocked boxes.

        """
        # Number of blocked boxes in random range of [min, max]
        num = random.randint(min, max)

        for _ in range(num):
            pos = random.randint(0, self.columns * self.rows - 1)
            self.__board[pos] = Board.BOX_BLOCK | Board.BOX_BLOCKED_MASK

    @property
    def active_player(self):
        return self.__active_player

    @property
    def inactive_player(self):
        return self.__inactive_player

    @property
    def board_list(self):
        return self.__board

    def player_pos(self, player):
        """Obtain the position for "player".

        Args:
            player (int): Player to obtain position for.

        Returns:
            (int, int): Position.

        """
        assert player in self.__players_position
        return self.__players_position[player]

    @property
    def player1_pos(self):
        return self.__players_position[Board.PLAYER1]

    @property
    def player2_pos(self):
        return self.__players_position[Board.PLAYER2]

    def offset(self, x, y):
        """Obtain an offset in to the board list based on X, Y board/box coordinates.

        Args:
            x (int): X board coordinate.
            y (int): Y board coordinate.

        """
        return x + y * self.columns

    def box_blocked(self, x, y):
        """Determine if a box in the board is blocked.

        Args:
            x (int): X box coordinate.
            y (int): Y box coordinate.

        Returns:
            True if successful, False otherwise.

        """
        return (self.__board[self.offset(x, y)] & Board.BOX_BLOCKED_MASK) == Board.BOX_BLOCKED_MASK

    def __block_box(self, x, y, board_state):
        """Block a box and its state in the X, Y coordinates of the board.

        Args:
            x (int): X box coordinate.
            y (int): Y box coordinate.
            board_state (int): State to block, i.e. PLAYER1, PLAYER2 etc.

        """
        self.__board[self.offset(x, y)] = board_state | Board.BOX_BLOCKED_MASK

    def get_free_boxes(self):
        """Return a list containing a tuple of (X, Y) coordinates of all free
        i.e. non-blocked boxes in the board.

        Returns:
            moves (list): List of tuples (X, Y) containing all free boxes.

        """
        moves = []
        for y in range(self.rows):
            for x in range(self.columns):
                if not self.box_blocked(x, y):
                    moves.append((x, y))

        return moves

    def get_legal_moves(self, player=None):
        """Return a list of all legal moves for the a player.
        By default use the active player if player is not set.

        Args:
            player (int): The active or inactive player. Default to the
            active player if player is None.

        Returns:
            moves (list): List of tuples (X, Y) with coordinates of valid moves.
        """
        if player is None:
            loc = self.__players_position[self.__active_player]
        else:
            loc = self.__players_position[player]

        # Game just started so return all free squares as legal moves
        if not loc:
            return self.get_free_boxes()

        # Define the directional deltas which span out in
        # 8 directions from any position in the grid
        dirs_deltas = [(-1, -1), (+0, -1), (+1, -1), (+1, +0),
                       (+1, +1), (+0, +1), (-1, +1), (-1, +0)]

        moves = []
        for dx, dy in dirs_deltas:
            # Explore all possible directional deltas from the starting position
            x, y = loc
            while (0 <= (x + dx) < self.columns) and (0 <= (y + dy) < self.rows):
                x += dx
                y += dy
                # If any square is blocked in the directional delta
                # then break out of this one and explore the next directional delta
                if self.box_blocked(x, y):
                    break
                moves.append((x, y))

        return moves

    def make_move(self, x, y):
        """Make a move to (x, y) for the active player.
        Block the position of the box on the move.
        Switch to the next player when done.

        Args:
            x (int): X box coordinate.
            y (int): Y box coordinate.

        """
        # assert the box we are moving to is not blocked
        assert not self.box_blocked(x, y)

        # Make the move to the new position and block it
        self.__players_position[self.__active_player] = (x, y)
        self.__block_box(x, y, self.__active_player)

        # Switch the player
        if self.__active_player == Board.PLAYER1:
            self.__active_player = Board.PLAYER2
            self.__inactive_player = Board.PLAYER1
        else:
            self.__active_player = Board.PLAYER1
            self.__inactive_player = Board.PLAYER2

    def make_move_copy(self, x, y):
        """Make a move to (x, y) for the active player returned as a copied game board.
        Block the position of the box on the move.
        Switch to the next player when done.

        Args:
            x (int): X box coordinate.
            y (int): Y box coordinate.

        Returns:
            board_copy (Board): Board object with new state applied.
        """
        board_copy = pickle.loads(pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL))

        # assert the box we are moving to is not blocked
        assert not board_copy.box_blocked(x, y)

        # Make the move to the new position and block it
        board_copy.__players_position[board_copy.__active_player] = (x, y)
        board_copy.__block_box(x, y, board_copy.__active_player)

        # Switch the player
        if board_copy.__active_player == Board.PLAYER1:
            board_copy.__active_player = Board.PLAYER2
            board_copy.__inactive_player = Board.PLAYER1
        else:
            board_copy.__active_player = Board.PLAYER1
            board_copy.__inactive_player = Board.PLAYER2

        return board_copy

    def is_game_over(self):
        """Determine if the game is over.

        Returns:
            The winning player or False.

        """
        # Always check the active player first!
        if not self.get_legal_moves(self.__active_player):
            return self.__inactive_player
        if not self.get_legal_moves(self.__inactive_player):
            return self.__active_player
        return False


def main():
    rows = 3
    columns = 3
    board = Board(rows, columns)

    print("Active player:", board.active_player)
    print(board.get_legal_moves())

    print("Active player:", board.active_player)
    board.make_move(1, 1)
    print("Active player:", board.active_player)
    board.make_move(1, 0)
    print("Active player:", board.active_player)
    board.make_move(0, 0)
    print("Active player:", board.active_player)
    board.make_move(0, 1)
    print("Active player:", board.active_player)
    print(board.get_legal_moves())

    board_copy = board.make_move_copy(2, 1)
    print(board_copy.get_legal_moves())
    board.make_move(2, 1)
    print(board.get_legal_moves())

    assert board == board_copy


if __name__ == "__main__":
    main()
