'''
this is our driver file, it is responsible for taking user input and displaying the game state
i.e: the chess board and the pieces
'''

import pygame as p
from chess import chess_engine, SmartMoveFinder
import time

WIDTH = HEIGHT = 512
DIMENSION = 8           # dimension of chess board 8 by 8
SQ_SIZE = WIDTH//DIMENSION
MAX_FPS = 15            # for animation later
IMAGES = {}

'''
initialise a global dictionary of images, will be called only once in the main 
'''
def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Note: now we can access an images by saying 'IMAGES["wp"]'

'''
The main driver. will handle input and will update graphics
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chess_engine.GameState()
    start = time.perf_counter()
    validMoves = gs.getValidMoves()
    end = time.perf_counter()
    print("Nodes: " + str(len(validMoves)))
    print("That took: " + str(end - start) + " seconds")
    print("Nodes per second: " + str(len(validMoves) // ((end - start))))
    moveMade = False    # flag variable for when a move is made
    animate = False     # flag variable for when we should animate
    load_images() #this is only done once, before while loop
    running = True
    sqSelected = ()     # no square is selected initially   (tuple (row,col))
    playerClicks = []   # keeps track of player clicks (two tuples [(6,4),(4,4)])
    gameOver = False
    playerOne = True # if a human is playing white, this is true. If AI then False
    playerTwo = True # same as above but for black
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()    # gets x and y position of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):    # user clicked the same square twice
                        sqSelected = ()             # deselect
                        playerClicks = []           # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)   # append for both first and 2nd clicks

                    if len(playerClicks) == 2:            # after 2nd click
                        move = chess_engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                print(move.getChessNotation())
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()     # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

                # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r :      # resets the board when r is pressed
                    gs = chess_engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMoveNegaMax(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
            #time.sleep(0.75)


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by Checkmate")
            else:
                drawText(screen, "White wins by Checkmate")

        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Draws the squares of the board and generates the piece images as well within a current game state
'''

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else'b'): # sqSelected is a piece that can be moved
            # Highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)        # transparency value -> 0 = transparent; 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # draw squares on board
    highlightSquares(screen, gs, validMoves, sqSelected)

    # Note: for later, we can add in piece highlighting and move suggestions

    drawPieces(screen, gs.board) # draw pieces on top of the squares

'''
Draw squares on board. in chess board, top left square always light 
'''


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw pieces on board
'''


def drawPieces(screen, board):

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # i.e if it's not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    coords = []     # list of coords that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frameCount = 25
    framesPerSquare = frameCount/(abs(dR) + abs(dC))
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece Moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()


def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Red'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)


main()
