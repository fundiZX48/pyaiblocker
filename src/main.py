"""Main application and game controller.
Copyright 2018 Mark Mitterdorfer

Bind board state, renderer and AI and play a game.
"""

import board
import renderer
import ai
import pygame
import sys
from pygame.locals import *
import time
import pickle


def main():
    start_x = 10
    start_y = 10

    box_width = 50
    margin_width = 5

    rows = 5
    columns = 5

    game = board.Board(rows, columns)
    #game.gen_random_blocked_boxes(7, int(0.4 * rows * columns))

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
    pygame.display.set_caption("Isolation")
    visual_board = renderer.RenderBoard(display, start_x, start_y, rows, columns, box_mapping, box_width, margin_width)

    render_update = True
    game_over = False
    # AI vs. AI, else player1 = first to move = human
    human_playing = False

    # Record play:
    # 1st element is a tuple with board dimensions and if AI or human player (rows, columns, human_playing)
    # Followed by tuple (active_player, score, move)
    # tuple (active_player, None, move) if human is playing
    record_play = [(rows, columns, human_playing)]

    # Default search depth
    depth = 5

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

        # Human goes first, unless AI vs. AI is in play
        if game.active_player == game.PLAYER1 and not human_playing and not game_over:
            score_func = ai.AI.score_func2
            start = time.time()
            best_score, best_move = ai.AI.power_abnegamax(game, depth, game.PLAYER1,
                                                          float("-inf"), float("inf"), score_func)
            end = time.time()
            print("Best move player 1:", best_move, "score:", best_score, "time:", end - start)

            # Record move
            record_play.append((game.active_player, best_score, best_move))
            game.make_move(*best_move)
            render_update = True

        elif game.active_player == game.PLAYER2 and not game_over:
            score_func = ai.AI.score_func2
            start = time.time()
            best_score, best_move = ai.AI.power_abnegamax(game, depth, game.PLAYER2,
                                                          float("-inf"), float("inf"), score_func)
            end = time.time()
            print("Best move player 2:", best_move, "score:", best_score, "time:", end - start)

            # Record move
            record_play.append((game.active_player, best_score, best_move))
            game.make_move(*best_move)
            render_update = True

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                # Save recorded moves
                filename = "REPLAY" + str(int(time.time())) + ".pickle"
                with open(filename, "wb") as handle:
                    pickle.dump(record_play, handle, protocol=pickle.HIGHEST_PROTOCOL)
                sys.exit()
            # Only process a mouse button event if the game is still running
            elif event.type == MOUSEBUTTONDOWN and game.active_player == game.PLAYER1\
                    and human_playing and not game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if visual_board.mouse_in_board(mouse_x, mouse_y):
                    box_x, box_y = visual_board.get_box_coord(mouse_x, mouse_y)
                    if not visual_board.mouse_in_margin(mouse_x, mouse_y, box_x, box_y):
                        # Make sure the box selected is not blocked
                        if not game.box_blocked(box_x, box_y) and (box_x, box_y) in game.get_legal_moves():
                            # Record move, set best_score = None for human player
                            record_play.append((game.active_player, None, (box_x, box_y)))
                            # Update the game board state and flip the player
                            game.make_move(box_x, box_y)
                            # Force a render/board refresh
                            render_update = True


if __name__ == "__main__":
    main()
