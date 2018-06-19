"""Render a board in Pygame.
Copyright 2018 Mark Mitterdorfer

Class to render the board game in Pygame.
"""

import pygame
import sys
from pygame.locals import *

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GREY = (96, 96, 96)
LBLUE = (68, 68, 255)
LRED = (255, 68, 68)
BROWN = (102, 51, 0)


class RenderBoard(object):
    """Class to render the board to a Pygame surface.

    Attributes:
        rows (int): Number of rows in the board.
        columns (int): Number of columns in the board.
        box_width (int): Width of individual *square* box in the board.
        margin_width (int, optional): Width of margins between individual boxes in the board.
        pygame_surface (pygame.Surface): Reference to Pygame surface.
        board_x (int): X placement of the board.
        board_y (int): Y placement of the board.
        board_width (int, optional): Board width.
        board_height (int): Board height.
        box_mapping (dict): int -> colour mapping for the boxes

    """

    def __init__(self, pygame_surface, board_x, board_y, rows, columns, box_mapping, box_width=20, margin_width=5):
        self.rows = rows
        self.columns = columns
        self.box_width = box_width
        self.margin_width = margin_width
        self.pygame_surface = pygame_surface
        self.box_mapping = box_mapping

        # x,y placement of the board
        self.board_x = board_x
        self.board_y = board_y

        # Total width and height of board
        self.board_width = self.columns * self.box_width + (self.columns - 1) * self.margin_width
        self.board_height = self.rows * self.box_width + (self.rows - 1) * self.margin_width

    def draw_board(self, game_board):
        """Draw board to the Pygame surface.

        Args:
            game_board (list): List containing a game board state. len(game_board) == rows * columns.

        """
        assert len(game_board) == self.rows * self.columns
        curr_x = self.board_x
        curr_y = self.board_y

        for y in range(self.rows):
            for x in range(self.columns):
                # Get the box as an offset in the board and then obtain the box mapping
                # this can be a function call or a colour.
                # E.g: board[1] = box1 = 1 -> BLUE, board[2] = box2 = 3 -> foo()
                offset = x + y * self.columns
                box = game_board[offset]
                # Draw a row of boxes
                pygame.draw.rect(self.pygame_surface, self.box_mapping[box],
                                 (curr_x, curr_y, self.box_width, self.box_width))
                curr_x += self.box_width + self.margin_width

            # Start new row
            curr_x = self.board_x
            curr_y += self.box_width + self.margin_width

    def mouse_in_board(self, mouse_x, mouse_y):
        """Check if the mouse coordinates fall within the board.

        Args:
            mouse_x (int): X mouse coordinate.
            mouse_y (int): Y mouse coordinate.

        Returns:
            True if successful, False otherwise.

        """
        if (self.board_x <= mouse_x <= self.board_x + self.board_width) and \
                (self.board_y <= mouse_y <= self.board_y + self.board_height):
            return True

        return False

    def mouse_in_margin(self, mouse_x, mouse_y, box_x, box_y):
        """Determine if the mouse is inside a margin of the board.
        A margin is a "dead" zone of the board.

        Args:
            mouse_x (int): X mouse coordinate.
            mouse_y (int): Y mouse coordinate.
            box_x (int): X location of box in the board.
            box_y (int): Y location of box in the board.

        Returns:
            True if successful, False otherwise.

        """
        # Use get_box_coord() to get box_x and box_y
        if (box_x+1) * self.box_width + box_x * self.margin_width < (mouse_x - self.board_x) \
                < (box_x+1) * self.box_width + (box_x+1) * self.margin_width:
            return True
        if (box_y+1) * self.box_width + box_y * self.margin_width < (mouse_y - self.board_y) \
                < (box_y+1) * self.box_width + (box_y+1) * self.margin_width:
            return True

        return False

    def get_box_coord(self, mouse_x, mouse_y):
        """Determine the X, Y location of a box inside a board from the mouse coordinates.

        Args:
            mouse_x (int): X mouse coordinate.
            mouse_y (int): Y mouse coordinate.

        Returns:
            box_x (int): X location of box in the board.
            box_y (int): Y location of box in the board.

        """
        box_x = (mouse_x - self.board_x) // (self.box_width + self.margin_width)
        box_y = (mouse_y - self.board_y) // (self.box_width + self.margin_width)

        return box_x, box_y

    def draw_box(self, box_x, box_y, colour):
        """Draw an individual box in the board based on box coordinates to the Pygame surface.

        Args:
            box_x (int): X location of box in the board.
            box_y (int): Y location of box in the board.
            colour (tuple): (R,G,B).

        """
        x = box_x * self.box_width + box_x * self.margin_width + self.board_x
        y = box_y * self.box_width + box_y * self.margin_width + self.board_y
        pygame.draw.rect(self.pygame_surface, colour, (x, y, self.box_width, self.box_width))

    def draw_margin_box(self, box_x, box_y, colour):
        """Draw a box spanning the margin in the board based on box coordinates to the Pygame surface.
        One can create a "box highlight" effect by first calling this method followed by draw_box().
        There is an issue with calling draw.rect(... thickness) in that is renders a strange thickness and
        seems to be incorrect.

        Args:
            box_x (int): X location of box in the board.
            box_y (int): Y location of box in the board.
            colour (tuple): (R,G,B).

        """
        x = box_x * self.box_width + box_x * self.margin_width - self.margin_width + self.board_x
        y = box_y * self.box_width + box_y * self.margin_width - self.margin_width + self.board_y
        pygame.draw.rect(self.pygame_surface, colour, (x, y, self.box_width + 2*self.margin_width,
                                                       self.box_width + 2*self.margin_width))


def main():
    start_x = 50
    start_y = 50

    mouse_x = 0
    mouse_y = 0

    rows = 5
    columns = 5

    box_mapping = {0: BLACK, 1: BLUE, 2: RED}

    BOARD = [1 if i % 2 == 0 else 2 for i in range(rows * columns)]
    print("BOARD:", BOARD)

    box_width = 50
    margin_width = 5

    pygame.init()

    display = pygame.display.set_mode((800, 600), 0, 32)

    pygame.display.set_caption("Isolation")

    board = RenderBoard(display, start_x, start_y, rows, columns, box_mapping, box_width, margin_width)

    board.draw_board(BOARD)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:  # Key "r" for refresh is pressed
                if event.key == K_r:
                    board.draw_board(BOARD)
            #elif event.type == MOUSEMOTION:
            #    mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if board.mouse_in_board(mouse_x, mouse_y):
                    box_x, box_y = board.get_box_coord(mouse_x, mouse_y)
                    if board.mouse_in_margin(mouse_x, mouse_y, box_x, box_y):
                        print("Margin")
                    else:
                        # Do action only if within the board, on a box, and not
                        # in the margin of the board
                        print(mouse_x, mouse_y, "->", box_x, box_y)
                        board.draw_margin_box(box_x, box_y, GREEN)
                        board.draw_box(box_x, box_y, BLUE)
                else:
                    print(mouse_x, mouse_y, "->", -1, -1)

        pygame.display.update()


if __name__ == "__main__":
    main()
