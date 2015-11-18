#Coded by Stephen Robinson & Matthew Ong

import random
import math

from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from Ant import *
from AIPlayerUtils import *

# Depth limit for ai search
DEPTH_LIMIT = 3

# weight for having at least one worker
WORKER_WEIGHT = 10000

# weight for food
FOOD_WEIGHT = 500

# weight for worker ants carrying food
CARRY_WEIGHT = 100

# weight for worker ant's dist to their goals
DIST_WEIGHT = 5

# weight for queen being away from places the worker must go and close to the bottom left
QUEEN_LOCATION_WEIGHT = 20

# used to scale down the player score
SCORE_SCALE = 1000.

# branching factor limit. If it is exceeded, it will cull the less good paths.
BRANCHING_FACTOR = 12

##
#AIPlayer
#Description: The responsibility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):


    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "The Conscious Ant")

        self.didPreProcessing = False
        #Calculate these before starting the game to speed up.
        self.preProcessMatrix = None
        self.hillCoords = None
        self.foodCoords = None
        self.weights = []
        for i in range (0,16):
            self.weights.append(random.uniform(-1,1))
        print "weight array:" + `self.weights`

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]


    ##
    # listAllLegalMoves
    #
    # determines all the legal moves that can be made by the player
    # whose turn it currently is, except it will only ever build workers
    #
    # Parameters:
    #   currentState - the current state
    #
    # Returns:  a list of Move objects
    ##
    def listAllLegalMoves(self, state):
        result = []

        myInv = getCurrPlayerInventory(state)
        hill = myInv.getAnthill()

        if getAntAt(state, hill.coords) is None:
            if UNIT_STATS[WORKER][COST] <= myInv.foodCount:
                result.append(Move(BUILD, [hill.coords], WORKER))

        result.extend(listAllMovementMoves(state))
        result.append(Move(END, None, None))

        random.shuffle(result)

        return result


    ##
    #expand
    #
    #Description: Called to expand a state. Recursively examines the game tree down to
    # DEPTH_LIMIT. Passes back up a dict with a move and associated score. The move is the
    # best move to take in this situation.
    #
    #Parameters:
    #   state - The state at this place in the game tree
    #           (to start it should be the current state)
    #   alpha - the alpha value for aB pruning at this node
    #   beta  - the beta value for aB pruning at this node
    #   depth - The depth the tree has been examined to. (for recursive use only)
    #
    #Return: A dict with keys 'move' and 'score'
    # move is the ideal Move()
    # score is the associated score. 0.0 is a loss. 1.0 or more is a victory.
    ##
    def expand(self, state, alpha=-float("inf"), beta=float("inf"), depth=0):

        if depth == DEPTH_LIMIT:
            score = self.evaluateState(state, depth)

            # Base case for depth limit
            return {'move': Move(END, None, None), 'score': score, 'state': state}

        elif self.hasWon(state, state.whoseTurn):
            # Base case for victory
            ## Make the final score take into account how many moves it will take to reach this
            ## victory state. Winning this turn is better than winning next turn.
            #return {'move': Move(END, None, None), 'score': float(DEPTH_LIMIT + 1 - depth), 'state': state}
            return {'move': Move(END, None, None), 'score': self.evaluateState(state, depth), 'state': state}

        #This is the best move from the view of the current player (state.whoseTurn)
        children = []
        bestMove = None
        bestScore = 0.0 if state.whoseTurn == self.playerId else 1.0

        #This score is used to determine if a path is worth exploring.
        #It is determined randomly from the first move.
        #self.listAllLegalMoves scrambles the list of legal moves, so we get a
        #random first move for our pivot.
        pivotScore = None

        # expand this node to find all child nodes
        for move in self.listAllLegalMoves(state):

            childState = self.successor(state, move)

            if pivotScore is None:
                pivotScore = self.evaluateState(childState, depth)
                children.append({'move': move, 'state': childState})
            else:
                #Check if child is worth exploring based on random pivot
                if state.whoseTurn == self.playerId:
                    if pivotScore <= self.evaluateState(childState, depth):
                        children.append({'move': move, 'state': childState})
                else:
                    if pivotScore >= self.evaluateState(childState, depth):
                        children.append({'move': move, 'state': childState})

            #Limit the branching factor.
            if len(children) > BRANCHING_FACTOR:
                break

        for child in children:

            move = child['move']
            childState = child['state']

            # Recursive step to find real score instead of estimate
            score = self.expand(childState, alpha, beta, depth + 1)['score']

            #update alpha & beta and the best move & best score
            if state.whoseTurn == self.playerId:
                if score > alpha:
                    alpha = score
                if score > bestScore:
                    bestMove = move
                    bestScore = score
            else:
                if score < beta:
                    beta = score
                if score < bestScore:
                    bestMove = move
                    bestScore = score

            if alpha >= beta:
                break # nothing new can be determined from this

        # return this node
        return {'move': bestMove, 'score': bestScore}


    def preProcess(self, state):

        self.preProcessMatrix = [[{} for y in xrange(10)] for x in xrange(10)]

        foodList = getConstrList(state, NEUTRAL, (FOOD,))
        constrList = getConstrList(state, self.playerId, (ANTHILL, TUNNEL))

        for x, column in enumerate(self.preProcessMatrix):
            for y, squareProperties in enumerate(column):

                #find the closest food to this location only once
                bestDist = float("inf")

                closestFood = None
                for food in foodList:
                    foodX, foodY = food.coords
                    distToFood = abs(x - foodX) + abs(y - foodY)
                    if distToFood < bestDist:
                        bestDist = distToFood
                        closestFood = food

                squareProperties['food'] = closestFood
                squareProperties['foodDist'] = bestDist

                #find the closest friendly constr to this location only once
                #This AI will never make new constructions (I PROMISE!)
                bestDist = float("inf")

                closestConstr = None
                for constr in constrList:
                    constrX, constrY = constr.coords
                    distToConstr = abs(x - constrX) + abs(y - constrY)
                    if distToConstr < bestDist:
                        bestDist = distToConstr
                        closestConstr = constr

                squareProperties['constr'] = closestConstr
                squareProperties['constrDist'] = bestDist

        grid = ""
        for y in xrange(10):
            for x in xrange(10):
                grid += str(self.preProcessMatrix[x][y]['foodDist'])
            grid += "\n"

        # Cache the hill coords for each player
        self.hillCoords = [
            tuple(getConstrList(state, 0, (ANTHILL,))[0].coords),
            tuple(getConstrList(state, 1, (ANTHILL,))[0].coords)
        ]

        # Cache the locations of foods
        foods = getConstrList(state, None, (FOOD,))
        self.foodCoords = [tuple(f.coords) for f in foods]

        self.didPreProcessing = True


    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):

        if not self.didPreProcessing:
            self.preProcess(currentState) #Do some calculations at the start of the game.

        return self.expand(currentState)['move']


    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]


    def antOnBuilding(self, state, ant):
        buildings = getConstrList(state, state.whoseTurn, (ANTHILL, TUNNEL))
        return tuple(ant.coords) in (tuple(b.coords) for b in buildings)


    ##
    #successor
    #
    #Description: Determine what the agent's state would look like after a given move.
    #             We Will assume that all Move objects passed are valid.
    #
    #Parameters:
    #   state - A clone of the theoretical state given (GameState)
    #   move - a list of all move objects passed (Move)
    #
    #Returns:
    #   What the agent's state would be like after a given move.
    ##
    def successor(self, state, move):
        newState = state.fastclone()

        if move.moveType == END:
            newState.whoseTurn = 1 - state.whoseTurn
            return newState

        elif move.moveType == MOVE_ANT:
            ant = getAntAt(newState, move.coordList[0])
            ant.coords = move.coordList[-1]

            #check if ant is depositing food
            if ant.carrying and self.antOnBuilding(state, ant):
                ant.carrying = False
                newState.inventories[newState.whoseTurn].foodCount += 1

            #check if ant is picking up food
            if not ant.carrying:
                if tuple(ant.coords) in self.foodCoords:
                    ant.carrying = True


            #check if ant can attack
            targets = [] #coordinates of attackable ants
            range = UNIT_STATS[ant.type][RANGE]

            for ant in newState.inventories[1 - newState.whoseTurn].ants:
                dist = math.sqrt((ant.coords[0] - ant.coords[0]) ** 2 +
                                 (ant.coords[1] - ant.coords[1]) ** 2)
                if dist <= range:
                    #target is in range and may be attacked
                    targets.append(ant.coords)

            if targets:
                #Attack the ant chosen by the AI
                target = self.getAttack(newState, ant, targets)
                targetAnt = getAntAt(newState, target)
                targetAnt.health -= UNIT_STATS[ant.type][ATTACK]

                if targetAnt.health <= 0:
                    #Remove the dead ant
                    newState.inventories[1 - newState.whoseTurn].ants.remove(targetAnt)

            ant.hasMoved = True

        else: #Move type BUILD
            if move.buildType in (WORKER, DRONE, SOLDIER, R_SOLDIER):
                #Build ant on hill
                ant = Ant(move.coordList[0], move.buildType, newState.whoseTurn)
                newState.inventories[newState.whoseTurn].ants.append(ant)

                newState.inventories[newState.whoseTurn].foodCount -= UNIT_STATS[move.buildType][COST]
            else:
                #build new building
                building = Building(move.coordList[0], move.buildType, newState.whoseTurn)
                newState.inventories[newState.whoseTurn].constrs.append(building)

                newState.inventories[newState.whoseTurn].foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

        return newState

    def printme(self, currentState, playerNo, debug=False):

        workers = getAntList(currentState, playerNo, (WORKER,))
        queens = getAntList(currentState, playerNo, (QUEEN,))
        theirQueen = getAntList(currentState, playerNo -1, (QUEEN,))

        #################################################################################
        #Score having exactly one worker

        workerCountScore = 0.0
        if len(workers) == 1:
            workerCountScore = 1.0

        print "workerCountScore:" + `workerCountScore`

        #################################################################################
        #Score the food we have

        foodScore = (currentState.inventories[playerNo].foodCount) / 11.0       # * FOOD_WEIGHT
        print "our food score:" + `foodScore`

        #Score the food enemy has
        foodScoreEnemy = (currentState.inventories[playerNo -1].foodCount) / 11.0

        print "their food score:" + `foodScoreEnemy`
        #################################################################################
        #queen health

        queenHealth = (queens[0].health) / 4.0
        print "our queen health:" + `queenHealth`
        #enemy queen health
        theirQueenHealth = (theirQueen[0].health) / 4.0
        print "their queen score:" + `theirQueenHealth`
        #################################################################################
        #Score queen being off of anthill and food

        queenScore = 0.0
        x, y = queens[0].coords
        if not self.preProcessMatrix[x][y]['foodDist'] == 0:
            queenScore = 1.0
        elif not self.preProcessMatrix[x][y]['constrDist'] == 0:
            queenScore = 1.0

        print "if queen on const:" + `queenScore`
        #################################################################################
        #distance from goal
        distScore = 0.0

        #if carrying
        carryScore = 0.0

        for worker in workers:
            x, y = worker.coords
            if worker.carrying:
                carryScore = 1.0
                distScore = 1-((self.preProcessMatrix[x][y]['constrDist']) / 18.0)
            else:
                distScore = 1-((self.preProcessMatrix[x][y]['foodDist']) / 18.0)

        print "distance score:" + `distScore`
        print "carry score:" + `carryScore`



    ##
    # getPlayerScore
    # Description: takes a state and player number and returns a number estimating that
    # player's score.
    #
    # Parameters:
    #    hypotheticalState - The state to score
    #    playerNo          - The player number to determine the score for
    #    debug             - If this is true then the score will be returned as a dict
    # Returns:
    #    If not debugging:
    #      A float representing that player's score
    #    If debugging
    #      A dict containing the components of the player's score along with the score
    ##
    def getPlayerScore(self, hypotheticalState, playerNo, debug=False):

        workers = getAntList(hypotheticalState, playerNo, (WORKER,))

        #################################################################################
        #Score having exactly one worker

        workerCountScore = 0
        if len(workers) == 1:
            workerCountScore = WORKER_WEIGHT

        #################################################################################
        #Score the food we have

        foodScore = hypotheticalState.inventories[playerNo].foodCount * FOOD_WEIGHT


        #################################################################################
        #Score queen being off of anthill and food

        queenScore = 0

        for ant in hypotheticalState.inventories[playerNo].ants:
            if ant.type == QUEEN:
                x, y = ant.coords
                queenScore += self.preProcessMatrix[x][y]['foodDist']
                queenScore += self.preProcessMatrix[x][y]['constrDist']
                #Gravitate toward bottom left (or top-right if player 1)
                queenScore -= x
                queenScore -= y

                queenScore *= QUEEN_LOCATION_WEIGHT

                break


        #################################################################################
        #Score the workers for getting to their goals and carrying food

        distScore = 0
        carryScore = 0

        for worker in workers:
            x, y = worker.coords
            if worker.carrying:
                carryScore += CARRY_WEIGHT
                distScore -= DIST_WEIGHT * self.preProcessMatrix[x][y]['constrDist']
            else:
                distScore -= DIST_WEIGHT * self.preProcessMatrix[x][y]['foodDist']

        score = foodScore + distScore + carryScore + queenScore + workerCountScore

        if debug:
            return {'f': foodScore, 'd': distScore, 'c': carryScore,
                    'q': queenScore, 'w': workerCountScore, 'S': score}
        else:
            return score

    ##
    # hasWon
    # Description: Takes a GameState and a player number and returns if that player has won
    # Parameters:
    #    hypotheticalState - The state to test for victory
    #    playerNo          - What player to test victory for
    #
    # Returns:
    #    True if the player has won else False.
    ##
    def hasWon(self, hypotheticalState, playerNo):

        #Check if enemy anthill has been captured
        for constr in hypotheticalState.inventories[1 - playerNo].constrs:
            if constr.type == ANTHILL and constr.captureHealth == 1:
                #This anthill will be destroyed if there is an opposing ant sitting on it
                for ant in hypotheticalState.inventories[playerNo].ants:
                    if tuple(ant.coords) == tuple(constr.coords):
                        return True
                break

        #Check if enemy queen is dead
        for ant in hypotheticalState.inventories[1 - playerNo].ants:
            if ant.type == QUEEN and ant.health == 0:
                return True

        #Check if we have 11 food
        if hypotheticalState.inventories[playerNo].foodCount >= 11:
            return True

        return False


    ##
    #evaluateState
    #
    #Description: Examines a GameState and ranks how "good" that state is for the agent whose turn it is.
    #              A rating is given on the players state. 1.0 is if the agent has won; 0.0 if the enemy has won.
    #              The rating is scaled down based on the depth is was found at.
    #
    #Parameters:
    #   hypotheticalState - The state being considered by the AI for ranking.
    #    depth            - What depth in the MiniMax tree this state is being evaluated at. (MUST be non-negative)
    #
    #Return:
    #   The move rated as the "best"
    ##
    def evaluateState(self, hypotheticalState, depth=0):

        #Check if the game is over
        if self.hasWon(hypotheticalState, self.playerId):
            return 1.0 / (depth + 1.) #Scale
        elif self.hasWon(hypotheticalState, 1 - self.playerId):
            return 0.0
        playerScore = self.getPlayerScore(hypotheticalState, self.playerId)
        self.printme(hypotheticalState, self.playerId)

        #Normalize the score to be between 0.0 and 1.0
        return (math.atan(playerScore/SCORE_SCALE) + math.pi/2) / math.pi / (depth + 1.)

    ##
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):
        self.didPreProcessing = False
