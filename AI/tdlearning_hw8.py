#Coded by Stephen Robinson & Matthew Ong

import random
import math
import pickle
import os.path

from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from Ant import *
from AIPlayerUtils import *


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
        super(AIPlayer,self).__init__(inputPlayerId, "td learning")

        self.didPreProcessing = False
        #Calculate these before starting the game to speed up.
        self.preProcessMatrix = None
        self.hillCoords = None
        self.foodCoords = None
        self.utilDic = {'state': None, 'utility': None}





    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def consolidate(self, anticState):

        newBoard = anticState.inputBoard # same

        newInventories = [anticState.inventories[self.playerId], anticState.inventories[2]]

        newPhase = anticState.phase #same

        newWhoseTrurn = anticState.whoseTurn #same

        consolidatedState = GameState(newBoard, newInventories, newPhase, newWhoseTrurn)

        queen = anticState.inventories[anticState.whoseTurn].getQueen()

        score = None

        return consolidatedState

    def save(self):
        with open( "save", "wb" ) as f:
            pickle.dump( self.utilDic, f )

    def load(self):
        with open( "save", "rb" ) as f:
            self.utilDic = pickle.load(f)

    def reward(self, consolidatedState):
        if consolidatedState.inventories[0].foodCount >= 11:
            return 1.0
        elif consolidatedState.inventories[0].getQueen() is None:
            return -1.0
        return -0.01


    ##
    # getFutureState
    #
    # Description: Simulates and returns the new state that would exist after
    #   a move is applied to current state
    #
    # Parameters:
    #   currentState - The game's current state (GameState)
    #   move - The Move that is to be simulated
    #
    # Return: The simulated future state (GameState)
    ##
    def getFutureState(self, currentState, move):
        # create a bare-bones copy of the state to modify
        newState = currentState.fastclone()

        # get references to the player inventories
        playerInv = newState.inventories[newState.whoseTurn]
        enemyInv = newState.inventories[1 - newState.whoseTurn]

        if move.moveType == BUILD:
        # BUILD MOVE
            if move.buildType < 0:
                # building a construction
                playerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                playerInv.constrs.append(Construction(move.coordList[0], move.buildType))
            else:
                # building an ant
                playerInv.foodCount -= UNIT_STATS[move.buildType][COST]
                playerInv.ants.append(Ant(move.coordList[0], move.buildType, newState.whoseTurn))

        elif move.moveType == MOVE_ANT:
        # MOVE AN ANT
            # get a reference to the ant
            ant = getAntAt(newState, move.coordList[0])

            # update the ant's location after the move
            ant.coords = move.coordList[-1]
            ant.hasMoved = True

            # get a reference to a potential construction at the destination coords
            constr = getConstrAt(newState, move.coordList[-1])

            # check to see if a worker ant is on a food or tunnel or hill and act accordingly
            if constr and ant.type == WORKER:
                # if destination is food and ant can carry, pick up food
                if constr.type == FOOD:
                    if not ant.carrying:
                        ant.carrying = True
                # if destination is dropoff structure and and is carrying, drop off food
                elif constr.type == TUNNEL or constr.type == ANTHILL:
                    if ant.carrying:
                        ant.carrying = False
                        playerInv.foodCount += 1

            # get a list of the coordinates of the enemy's ants
            enemyAntCoords = [enemyAnt.coords for enemyAnt in enemyInv.ants]

            # contains the coordinates of ants that the 'moving' ant can attack
            validAttacks = []

            # go through the list of enemy ant locations and check if
            # we can attack that spot, and if so add it to a list of
            # valid attacks (one of which will be chosen at random)
            for coord in enemyAntCoords:
                if UNIT_STATS[ant.type][RANGE] ** 2 >= abs(ant.coords[0] - coord[0]) ** 2 + abs(ant.coords[1] - coord[1]) ** 2:
                    validAttacks.append(coord)

            # if we can attack, pick a random attack and do it
            if validAttacks:
                enemyAnt = getAntAt(newState, random.choice(validAttacks))
                attackStrength = UNIT_STATS[ant.type][ATTACK]

                if enemyAnt.health <= attackStrength:
                    # just to be safe, set the health to 0
                    enemyAnt.health = 0
                    # remove the enemy ant from their inventory
                    enemyInv.ants.remove(enemyAnt)
                else:
                    # lower the enemy ant's health because they were attacked
                    enemyAnt.health -= attackStrength

        # return the modified copy of the original state
        return newState


    def getFutureMove(self,currentState):
        allMoves = self.listAllLegalMoves(currentState)

        #find best move
        consolidatedStates = [] #list of future consolidated states of all moves from currentState
        for m in allMoves:
            for s in self.consolidate(self.getFutureState(currentState, m)):
                consolidatedStates.append(zip(s,m))

        calculatedStates = []
        for s,m in consolidatedStates:
            if s in self.utilDic:
                calculatedStates.append((self.utilDic[s],m))

        if len(calculatedStates) > 0:
            best = max(calculatedStates)[1]
            return best
        #return a random move
        else:
            return random.choice(moves)

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

            if os.path.isfile("save"): #load previous array
                self.utilDic = self.load()

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

        newMove = self.getFutureMove(currentState)

        consolidatedState = self.consolidate(currentState)

        if consolidatedState in self.utilDic:
            util = self.utilDic[consolidatedState]
        else:
            # state not found, so add it
            util = self.getReward(simpleState)
            self.stateUtils[simpleState] = (util, 1)
            stateCount = 1

        return 


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
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):
        self.didPreProcessing = False
        self.save()
