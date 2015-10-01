#
# import random
import sys
# # sys.path.append("..")
# from Player import *
# from Constants import *
# from Construction import CONSTR_STATS
# from Ant import *
# from Move import Move
from GameState import *
# from AIPlayerUtils import *
# from Location import *
from Inventory import *
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *
from Ant import *
from Location import *
from Game import *
from Move import *
from random import randrange
from Node import *
##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
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
        global closestFood
        self.depthLimit = 2
        self.preProcessMatrix = None
        closestFood = None
        super(AIPlayer,self).__init__(inputPlayerId, "HW3 playerrrrrr")

    def evaluateNodes(self, nodeList):
        bestRating = 0.0
        bestNode = []
        bestNode.append(nodeList[0])

        for node in nodeList:
            if(node == None):
                continue
            #use expectedStateRating
            rating = node.rating
            if(rating >=  bestRating):
                bestRating = rating
                bestNode[0] = node
        return bestNode

    ##
    #recursiveExplore
    ##
    def recursiveExplore(self, currentNode, playerID, currentDepth):
        #part a
        nodeList = []
        myInventory = getCurrPlayerInventory(currentNode.state)
        moves = listAllLegalMoves(currentNode.state)

        for move in moves:
            projectedState = self.getStateProjection(currentNode.state, move)
            #make node for every legal move in currentState
            rating = self.getStateRating(currentNode.state, projectedState)
            childNode = Node(projectedState, move, currentNode, rating)
            if(childNode == None):
                print "we need help"
            if(childNode.rating > 0.7):
                [childNode] + nodeList
            else:
                nodeList.append(childNode)
        #part b
        nodeList = nodeList[:20]
        if (currentDepth == self.depthLimit):
            return self.evaluateNodes(nodeList)
        #part c
        while(currentDepth < self.depthLimit):
            currentDepth = currentDepth + 1

            for node in nodeList:
                self.recursiveExplore(node, playerID, currentDepth)
        return self.evaluateNodes(nodeList)


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
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        playerID = currentState.whoseTurn

        if (self.preProcessMatrix == None):
            # Creates a list containing 10 lists initialized to 0
            self.preProcessMatrix = [[0 for x in range(10)] for x in range(10)]
            foodList = getConstrList(currentState, NEUTRAL, [(FOOD)])
            constrList = getConstrList(currentState, playerID, [(ANTHILL),(TUNNEL)])
            for x in range(10):
                for y in range(10):
                    ##
                    #squareProperties[0] = the location of constructs
                    #squareProperties[1] = the distance to food for each squareProperties
                    #squareProperties[2] = the distance to the closest tunnel
                    ##
                    squareProperties = []
                    # squareProperties = squareProperties.append()
                    const = getConstrAt(currentState, (x, y))
                    squareProperties.append(const)
                    #find the closest food to tunnel only once
                    best = 100
                    closestFood = None
                    for f in foodList:
                        src = (x, y)
                        dst = f.coords
                        stepsToF = stepsToReach(currentState, src, dst)
                        if (stepsToF < best):
                            best = stepsToF
                            closestFood = f.coords
                    #set prop 1
                    squareProperties.append(best)

                    bestTunnel = 100
                    closestTunnel = None
                    for c in constrList:
                        src = (x, y)
                        dst = c.coords
                        stepsToF = stepsToReach(currentState, src, dst)
                        if (stepsToF < best):
                            bestTunnel = stepsToF
                            closestTunnel = c.coords
                    #set prop[2]
                    squareProperties.append(bestTunnel)

                    self.preProcessMatrix[x][y] = squareProperties

        # print self.preProcessMatrix
        parentNode = Node(currentState, None, None, None)
        myAntList = getAntList(currentState, playerID, [(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)])
        for ants in myAntList:
            ants.hasMoved = False

        returnedNode = self.recursiveExplore(parentNode, playerID, 0)
        return returnedNode[0].move





    ##
    #
    ##
    def getStateRating(self, currentState, state):
        player = state.whoseTurn

        global closestFood
        global closestTunnel
        enemy = not state.whoseTurn
        playerCurrInv = currentState.inventories[player] # get inventory for the current state
        enemyCurrInv = currentState.inventories[enemy]
        playerInv = state.inventories[player] #get inventory for projected state
        enemyInv = state.inventories[enemy]

        #check who has won the game
        if(playerInv.foodCount == 11 or enemyInv.getQueen() == None):
            return 1.0 #win
        elif(enemyInv.foodCount == 11 or playerInv.getQueen() == None):
            return 0.0 #lose

        # foodList = getConstrList(state, NEUTRAL, [(FOOD)])
        #
        # #find the closest food to tunnel only once
        # if(closestFood == None):
        #     best = 100
        #     closestFood = None
        #     for f in foodList:
        #         src = playerInv.getTunnels()[0].coords
        #         dst = f.coords
        #         stepsToF = stepsToReach(state, src, dst)
        #         if (stepsToF < best):
        #             best = stepsToF
        #             closestFood = f.coords
        #
        bestFoodRating = 100.0
        bestAntRating = 275.0

        antRating = 0.0 #rating based on ant stats
        foodRating = 0.0 #rating based on food stats
        stateRating = 0.0

        #check if ants are moving in the right direction
        for a in playerInv.ants:
            if(a.type == WORKER):
                if(a.carrying):
                    x = a.coords[0]
                    y = a.coords[1]
                    dst = self.preProcessMatrix[x][y][2]
                else:
                    x = a.coords[0]
                    y = a.coords[1]
                    dst = self.preProcessMatrix[x][y][1]

                foodRating += (100.0 / (dst + 1))


            if(a.type == DRONE):
                dst = enemyInv.getQueen().coords
                distance = stepsToReach(state, a.coords, dst)
                antRating += (100.0 / (distance))

        #move the queen off of the ant hill
        queenCoords = playerInv.getQueen().coords
        hillCoords = playerInv.getAnthill().coords
        if(queenCoords == hillCoords):
            antRating -=75

        #Attack the queen
        if(enemyInv.getQueen().health < enemyCurrInv.getQueen().health):
            antRating += 100

        workerCount = len(getAntList(state, player, [(WORKER)]))
        droneCount = len(getAntList(state, player, [DRONE]))

        # for a in playerInv.ants:
        #     if(a.type == WORKER and workerCount < 1):
        #         antRating += 10.0
        #     elif (a.type == DRONE and droneCount < 2):
        #         antRating += 10.0
        #     elif (a.type == SOLDIER or a.type == R_SOLDIER):
        #         antRating += 0.0
        if(workerCount == 1 or droneCount == 2):
            antRating += 75.0

        if workerCount != 1 or droneCount != 2:
            antRating == 0.0

        foodRating = foodRating / bestFoodRating
        antRating = antRating / bestAntRating

        stateRating += 0.25 * foodRating
        stateRating += 0.75 * antRating

        return stateRating

    ##
    #
    ##
    def getStateProjection(self, currentState, move):
        state = currentState.fastclone()
        currPlayer = state.whoseTurn
        playerInv = state.inventories[currPlayer]
        enemyInv = state.inventories[(not currPlayer)]

        #update Ant/Constr list after placement/removal
        if(move.moveType == BUILD):
            # #add the built ant to the ant list
            antType = move.buildType
            antHill = playerInv.getAnthill().coords

            newAnt = Ant(antHill, antType, currPlayer)
            playerInv.ants.append(newAnt)

            #calculate build cost
            buildCost = 1
            if(newAnt.type == SOLDIER or newAnt.type == R_SOLDIER):
                buildCost = 2 #soldiers cost 2 food

            #subtract cost from food
            playerInv.foodCount -= buildCost

        elif (move.moveType == MOVE_ANT):
            # #update coordinates of ant
            newPosition = move.coordList[-1]
            ant = getAntAt(state, move.coordList[0])

            ant.coords = newPosition
            ant.hasMoved = True

            #project an attack, if there is one
            #list nearby ants
            listToCheck = listAdjacent(ant.coords)

            antsInRange = []
            for a in listToCheck:
                nearbyAnt = getAntAt(state, a)
                if(nearbyAnt != None):
                    if(nearbyAnt.player == (not currPlayer)):
                        antsInRange.append(a)

            if(len(antsInRange) > 0):#check for empty list
                attackedAntCoords = self.getAttack(state, ant, antsInRange)

                #update health of attacked ant
                attackedAnt = getAntAt(state, attackedAntCoords)
                attackedAnt.health -= 1

                #remove dead ant from board
                if(attackedAnt.health == 0):
                    enemyInv.ants.remove(attackedAnt)

        elif (move.moveType == END):
            antHillCoords = playerInv.getAnthill().coords
            antOnHill = getAntAt(state, antHillCoords)
            antOnTunnel = getAntAt(state, playerInv.getTunnels()[0].coords)

            if(antOnHill != None and antOnHill.carrying):
                playerInv.foodCount += 1
                antOnHill.carrying = False
            if(antOnTunnel != None and antOnTunnel.carrying):
                playerInv.foodCount += 1
                antOnTunnel.carrying = False

            #update if ant is on Food
            foodLocs = getConstrList(state, None, [(FOOD)])
            #list of current players ants that are on food
            antsOnFood = []
            for f in foodLocs:
                tempAnt = getAntAt(state, f.coords)
                if(tempAnt != None and tempAnt.player == currPlayer):
                    antsOnFood.append(tempAnt)

            for a in antsOnFood:
                a.carrying = True


        return state.fastclone()


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


board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)
state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)

worker = Ant((0,0), WORKER, PLAYER_ONE)

state.inventories[PLAYER_ONE].ants.append(worker)

move = Move(MOVE_ANT, [(0,0), (1,0)], None)

player = AIPlayer(PLAYER_ONE)

projected = player.getStateProjection(state, move)

if(projected.inventories[PLAYER_ONE].ants[0].coords != (1,0)):
    print "Error. Incorrect result state."

rating = player.getStateRating(state, projected)
if(rating <= 1.0 and rating >= 0.0):
    print "Unit Test #1 Passed"
