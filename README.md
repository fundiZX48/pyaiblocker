# pyaiblocker

Is a simple artificial intelligence board game demonstrating **negamax** and various heuristics for the game **isolation**.
The game is written in Python 3 and uses Pygame for visualisation.

## Contents
### 1. Game rules
This implementation of isolation is a two player game. Each player is denoted by a particular token, in this case a blue block for player one and a red block for player 2.
Game play takes place on an mxn (m rows, n columns) board of empty spaces.
Player 1 begins the game by "blocking" any empty space in the board with her token. Player 2 is next, placing her red token in any free space in the board.
Play continues subject to these simple rules:
1. Moves are relative to the players last played (i.e. blocked) position
2. Moves can happen along the horizontal, vertical and diagonal and for as many free spaces available to the player on the board.
**However** it is not possible to move *over* any "blocked" box. (Blocked meaning any red or blue coloured box on the board.)
In addition it is not possible to move *on to* a blocked box on the board.
3. The last player that is unable to make a valid move (player is "blocked" in) **loses** the game 


### 2. Prerequisites
Pygame <https://www.pygame.org> 
Installation instruction are contained in the links.


### 3. Running a game
To run, go to the *src* directory and enter:

    python main.py
    
The game will run with two AI players battling it out. It is also possible to play human vs. human and human vs. AI by modifying the code.

### 4. Code
Exploring the *src* directory:

 - ai.py : implements negamax and various search heuristics for the game AI
 - board.py : implements board state and various valid moves
 - renderer.py : draws the above board state in Pygame for visualisation
 - main : main application. Binds all above and implements a controller for the game
 - replay.py : this is a side line application to replay moves from a game instance

Further explanation of the code is coming!

### 5. TODO list
Items to add, issues to resolve.




















