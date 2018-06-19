"""Game replay.
Copyright 2018 Mark Mitterdorfer

Side line application to replay a recorded game session.
"""

import board
import renderer
import pygame
import sys
from pygame.locals import *
import pickle
import argparse


def main():
    parser = argparse.ArgumentParser(description="Replay a recorded Isolation game.")
    parser.add_argument("filename", help="pickled filename to open")
    args = parser.parse_args()

    start_x = 10
    start_y = 10

    box_width = 50
    margin_width = 5

    # Load and rerun an earlier recorded play:
    # 1st element is a tuple with board dimensions and if AI or human player (rows, columns, human_playing)
    # Followed by tuple (active_player, score, move)
    # tuple (active_player, None, move) if human is playing
    with open(args.filename, "rb") as input_file:
        record_play = pickle.load(input_file)

    (rows, columns, human_playing) = record_play.pop(0)

    game = board.Board(rows, columns)
    # Board/box state to rendering mappings
    box_mapping = {game.PLAYER1: renderer.LBLUE,
                   game.PLAYER2: renderer.LRED,
                   game.BOX_CLEAR: renderer.GREY,
                   game.BOX_BLOCK: renderer.BROWN,
                   game.BOX_BLOCKED_MASK: renderer.BLACK}  # Masked state is not actually used to draw

    # Player 1 = blue
    player1_colour = renderer.BLUE
    # Player 2 = red
    player2_colour = renderer.RED

    pygame.init()
    display = pygame.display.set_mode((800, 600), 0, 32)
    pygame.display.set_caption("Isolation - REPLAY")
    visual_board = renderer.RenderBoard(display, start_x, start_y, rows, columns, box_mapping, box_width, margin_width)

    render_update = True
    game_over = False

    index = 0
    while True:
        # Only refresh the screen if an action caused a state change
        if render_update:
            # Unset the box blocked bit mask pattern if it is set to get players colour etc.
            # TODO Perhaps move this in to board.py
            board_list = [i & ~game.BOX_BLOCKED_MASK if i != game.BOX_BLOCKED_MASK else
                          game.BOX_BLOCKED_MASK for i in game.board_list]

            display.fill(renderer.BLACK)

            # Highlight active player by drawing a margin filled box
            player_pos = game.player1_pos
            if game.active_player == game.PLAYER2:
                player_pos = game.player2_pos
            if player_pos:
                visual_board.draw_margin_box(*player_pos, renderer.GREEN)

            # Render the entire board from the board_list
            visual_board.draw_board(board_list)

            # Draw current position of players a darker colour
            player_pos = game.player1_pos
            if player_pos:
                visual_board.draw_box(*player_pos, player1_colour)
            player_pos = game.player2_pos
            if player_pos:
                visual_board.draw_box(*player_pos, player2_colour)

            winner = game.is_game_over()
            if winner:
                print("Player", winner, "wins!")
                game_over = True

            pygame.display.update()
            render_update = False

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                # Move forward with a move
                if event.key == K_m:
                    if not game_over:
                        (active_player, score, move) = record_play[index]
                        print("Active player:", active_player, "score:", score, "move:", move)
                        game.make_move(*move)
                        index += 1
                        render_update = True
                # Move backwards i.e. undo a move
                # TODO: This does not work at the moment
                elif event.key == K_n:
                    index -= 1
                    (active_player, score, move) = record_play[index]
                    print("Active player:", active_player, "score:", score, "move:", move)
                    game.make_move(*move)
                    render_update = True


if __name__ == "__main__":
    main()
