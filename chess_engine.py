'''
This class is responsible for storing all information about the current state of a chess game.
also responsible for determining the valid moves at the current state. it will also keep a move log.
'''



class GameState:

    def __init__(self):
        # board is an 8 by 8 2D list. each element is written as a string of 2 characters.
        # the first character is the color of the piece (b = black and w = white)
        # and the second is the piece. k = king, Q = queen and so on.
        # this "--" represents an empty space

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self. getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()     # coordinates for the square where enpassant is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.CastleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

        self.whiteValidMoves = []
        self.blackValidMoves = []

        self.protects = [[]]        # stores pieces info that can protect information pawn, knight, bishop, rook, queen, king
        self.threatens = [[]]       # stores pieces info that can attack information pawn, knight, bishop, rook, queen, king
        self.CanMoveTo = [[]]       # stores pieces info that can move to information pawn, knight, bishop, rook, queen, king

        '''
        for example 
        
        pawn  knight  bishop  rook  queen  king 
        e4     d4      d6      g2    g6     a7
        e5
        etc ... 
        '''



    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)       #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove     # swap players
        # update kings location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # enPassant Move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"   # capturing the pawn

        # Update enPassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:     # only on two squares pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # moves the rook
                self.board[move.endRow][move.endCol + 1] = '--'  # erases old rook
            else:                               # queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # moves the rook
                self.board[move.endRow][move.endCol - 2] = '--'  # erases old rook

        # update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.CastleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))





    '''undoing a move function'''

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # self.moveLog = self.moveLog[:-1]
            self.whiteToMove = not self.whiteToMove  # swap players
            # update kings location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # undo castling rights
            self.CastleRightsLog.pop()
            NewRights = self.CastleRightsLog[-1]        # set the current castling rights to the previous one in the list
            self.currentCastlingRights = CastleRights(NewRights.wks, NewRights.bks, NewRights.wqs, NewRights.bqs)
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:        # kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False



    '''Update the Castle Rights'''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:      # queen side rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:    # king side rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:      # queen side rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:    # king side rook
                    self.currentCastlingRights.bks = False

        # if rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    '''All moves considering checks'''

    def getValidMoves(self):
        # naive methode of getting valid moves
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)    # copy of current castle rights
        # 1.) generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # 2.) for each move, make the  move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3.) generate all opponent's moves
            # 4.) for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5.) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves


    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    ''' 
    determine if the enemy can attack the square r, c
    '''

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove     # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:    # square under attack
                return True
        return False

    def checkForPinsAndChecks(self):
        pins = []       # squares where allied pinned piece is and direction pinned from
        checks = []     # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()        # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():       # list allied pieces that could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: # 2nd allied piece so no possible pins in this directions
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) one square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction and one square away from king

                        if ((0 <= j <= 3) and type == "R") or \
                                (4 <= j <= 7) and type == "B" or \
                                (i == 1 and type == "p") and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b") and 4 <= j <= 5) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == ():   # if no piece blocking so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:   # piece blocking so pinned
                                pins.append(possiblePin)
                                break
                else:       # off board
                    break
            # check for knight checks
            KnightMoves = ((1, 2), (2, 1), (1, -2), (-2, 1), (-1, 2), (-1, -2), (-2, -1), (2, -1))
            for m in KnightMoves:
                endRow = startRow + m[0]
                endCol = startCol + m[1]
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":        # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
            return inCheck, pins, checks


    '''All moves without considering checks'''

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):            # number of rows
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # calls appropriate move function based on piece type

        return moves

    '''Get all pawn moves located at row r and column c and add moves to the list'''

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:                # white pawn moves
            if self.board[r-1][c] == "--":  # square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
            if r == 6 and self.board[r-1][c] == "--" and self.board[r-2][c] == "--":
                moves.append(Move((r, c), (r-2, c), self.board))
            if c - 1 >= 0:          # captures to the left
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEmpassantMove=True))
            if c + 1 <= 7:       # captures to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEmpassantMove=True))
        else:   # black pawn moves
            if self.board[r + 1][c] == "--":  # square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
            if r == 1 and self.board[r + 1][c] == "--" and self.board[r + 2][c] == "--":
                moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # captures to the left
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEmpassantMove=True))
            if c + 1 <= 7:  # captures to the right
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEmpassantMove=True))

        # Add pawn promotions


        # piecePinned = False
        # pinDirection = ()
        # for i in range(len(self.pins)-1, -1, -1):
        #     if self.pins[i][0] == r and self.pins[i][1] == c:
        #         piecePinned = True
        #         pinDirection = (self.pins[i][2], self.pins[i][3])
        #         self.pins.remove(self.pins[i])
        #         break
        #
        # if self.whiteToMove:                # white pawn moves
        #     if self.board[r-1][c] == "--":  # square pawn advance
        #         if not piecePinned or pinDirection == (-1, 0):
        #             moves.append(Move((r, c), (r-1, c), self.board))
        #             if r == 6 and self.board[r-2][c] == "--":
        #                 moves.append(Move((r, c), (r-2, c), self.board))
        #         if c - 1 >= 0:          # captures to the left
        #             if self.board[r-1][c-1][0] == "b":
        #                 if not piecePinned or pinDirection == (-1, -1):
        #                     moves.append(Move((r, c), (r - 1, c - 1), self.board))
        #         if c + 1 < 7:       # captures to the right
        #             if self.board[r-1][c+1][0] == "b":
        #                 if not piecePinned or pinDirection == (-1, 1):
        #                     moves.append(Move((r, c), (r - 1, c + 1), self.board))
        # else:   # black pawn moves
        #     if self.board[r + 1][c] == "--":  # square pawn advance
        #         if not piecePinned or pinDirection == (1, 0):
        #             moves.append(Move((r, c), (r + 1, c), self.board))
        #             if r == 1 and self.board[r + 2][c] == "--":
        #                 moves.append(Move((r, c), (r + 2, c), self.board))
        #         if c - 1 >= 0:  # captures to the left
        #             if self.board[r + 1][c - 1][0] == "w":
        #                 if not piecePinned or pinDirection == (1, -1):
        #                     moves.append(Move((r, c), (r + 1, c - 1), self.board))
        #         if c + 1 < 7:  # captures to the right
        #             if self.board[r + 1][c + 1][0] == "w":
        #                 if not piecePinned or pinDirection == (1, 1):
        #                     moves.append(Move((r, c), (r + 1, c + 1), self.board))
        #
        # # Add pawn promotions



    '''Get all Rook moves located at row r and column c and add moves to the list'''

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:
                    break


        # piecePinned = False
        # pinDirection = ()
        # for i in range(len(self.pins) - 1, -1, -1):
        #     if self.pins[i][0] == r and self.pins[i][1] == c:
        #         piecePinned = True
        #         pinDirection = (self.pins[i][2], self.pins[i][3])
        #         if self.board[r][c][1] != 'Q':       # can't remove queen from pin on rook moves, only remove it on bishop moves
        #             self.pins.remove(self.pins[i])
        #         break
        # directions = ((-1, 0), (0, -1), (1, 0), (0, 1))     # up, left, down, right
        # enemyColor = "b" if self.whiteToMove else "w"
        # for d in directions:
        #     for i in range(1, 8):
        #         endRow = r + d[0] * i
        #         endCol = c + d[1] * i
        #         if 0 <= endRow < 8 and 0 <= endCol < 8:     # on board
        #             if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
        #                 endPiece = self.board[endRow][endCol]
        #                 if endPiece == "--":    # empty space valid
        #                     moves.append(Move((r, c), (endRow, endCol), self.board))
        #                 elif endPiece[0] == enemyColor:
        #                     moves.append(Move((r, c), (endRow, endCol), self.board))
        #                     break
        #                 else:       # friendly piece invalid
        #                     break
        #         else:
        #             break

    '''Get all Knight moves located at row r and column c and add moves to the list'''

    def getKnightMoves(self, r, c, moves):
        KnightMoves = ((1, 2), (2, 1), (1, -2), (-2, 1), (-1, 2), (-1, -2), (-2, -1), (2, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for m in KnightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor or endPiece == "--":
                    moves.append(Move((r, c), (endRow, endCol), self.board))


        # piecePinned = False
        # pinDirection = ()
        # for i in range(len(self.pins) - 1, -1, -1):
        #     if self.pins[i][0] == r and self.pins[i][1] == c:
        #         piecePinned = True
        #         pinDirection = (self.pins[i][2], self.pins[i][3])
        #         if self.board[r][c][
        #             1] != 'Q':  # can't remove queen from pin on rook moves, only remove it on bishop moves
        #             self.pins.remove(self.pins[i])
        #         break
        # KnightMoves = ((1, 2), (2, 1), (1, -2), (-2, 1), (-1, 2), (-1, -2), (-2, -1), (2, -1))
        # enemyColor = "b" if self.whiteToMove else "w"
        # for m in KnightMoves:
        #     endRow = r + m[0]
        #     endCol = c + m[1]
        #     if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
        #         if not piecePinned:
        #             endPiece = self.board[endRow][endCol]
        #             if endPiece[0] == enemyColor or endPiece == "--":
        #                 moves.append(Move((r, c), (endRow, endCol), self.board))



    '''Get all Bishop moves located at row r and column c and add moves to the list'''

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1))  # up-right, up-left, down-right, down-left
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:
                    break


        # piecePinned = False
        # pinDirection = ()
        # for i in range(len(self.pins) - 1, -1, -1):
        #     if self.pins[i][0] == r and self.pins[i][1] == c:
        #         piecePinned = True
        #         pinDirection = (self.pins[i][2], self.pins[i][3])
        #         self.pins.remove(self.pins[i])
        #         break
        # directions = ((-1, 1), (-1, -1), (1, 1), (1, -1))  # up-right, up-left, down-right, down-left
        # enemyColor = "b" if self.whiteToMove else "w"
        # for d in directions:
        #     for i in range(1, 8):
        #         endRow = r + d[0] * i
        #         endCol = c + d[1] * i
        #         if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
        #             if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
        #                 endPiece = self.board[endRow][endCol]
        #                 if endPiece == "--":  # empty space valid
        #                     moves.append(Move((r, c), (endRow, endCol), self.board))
        #                 elif endPiece[0] == enemyColor:
        #                     moves.append(Move((r, c), (endRow, endCol), self.board))
        #                     break
        #                 else:  # friendly piece invalid
        #                     break
        #         else:
        #             break

    '''Get all Queen moves located at row r and column c and add moves to the list'''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''Get all King moves located at row r and column c and add moves to the list'''

    def getKingMoves(self, r, c, moves):
        KingMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (-1, -1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for m in KingMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor or endPiece == "--":
                    moves.append(Move((r, c), (endRow, endCol), self.board))


        '''
        Generate all valid castle moves for the king at (r, c) and add them to the list of moves
        '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return      # can't catsle while we are in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))



        # rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        # ColMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        # allyColor = "w" if self.whiteToMove else "b"
        # for i in range(8):
        #     endRow = r + rowMoves[i]
        #     endCol = c + ColMoves[i]
        #     if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
        #         endPiece = self.board[endRow][endCol]
        #         if endPiece[0] != allyColor:        # not an ally piece
        #             # place king on end square and check for checks
        #             if allyColor == "w":
        #                 self.whiteKingLocation = (endRow, endCol)
        #             else:
        #                 self.blackKingLocation = (endRow, endCol)
        #             inCheck, pins, checks = self.checkForPinsAndChecks()
        #             if not inCheck:
        #                 moves.append(Move((r, c), (endRow, endCol), self.board))
        #             #place king back on original location
        #             if allyColor == "w":
        #                 self.whiteKingLocation = (r, c)
        #             else:
        #                 self.blackKingLocation = (r, c)
        
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rowsToRanks = {v : k for k,v in ranksToRows.items()}        # cool way to reverse a dictionary

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEmpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # enpassant stuff
        self.isEnpassantMove = isEmpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # castle move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #print(self.moveID)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False



    def getChessNotation(self):
        # can add more to this function to make it real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


