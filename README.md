# Python-chess
A chess engine built in python 

The purpose of this project wasn't to build the most efficient chess engine but to learn the basic components that make it up. Since I was a beginner programmer at the time,I completed the project in around a month by following some tutorials.

Let me give a brief explanation of each sript in this repository

# chess_main.py

the chess_main.py script contains the main function alongside other GUI (graphical user interface). The only things you would want to change in this file are lines 48 and 49:

playerOne = True 

playerOne represents the white pieces. setting it to true means that a real person is playing. Setting it to false means the AI is playing as white. 

playerTwo = True 

playerTwo represents the black pieces. setting it to true means that a real person is playing. Setting it to false means the AI is playing as black. 

# chess_engine.py

The chess_engine.py script deals with the rules of the game, it generates all the possible moves (even the illegal moves), then filters that list using the getValidMoves() function. 

# SmartMoveFinder.py

This script deals with artifical intelligence part of the project. A chess engine isn't complete without an AI you can play against. The AI isn't too complex. It attributes scores to different pieces (Queen = 10, Rook = 5 ...) and uses an alpha beta pruning algorithm to search and select the best possible moves. A depth must be specified to that function. The depth variable specifies how many moves should the algorithm make in advance before evaluating/scoring the board. Good position of pieces on the board is rewarded, this is done by attributing a number for each square on the board, for each piece on the board (i.e. A Knight in the center of the board will be much more useful than a night on the edge of the board, it will have a higher score). 
