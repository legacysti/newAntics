  # -*- coding: latin-1 -*-
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
        super(AIPlayer,self).__init__(inputPlayerId, "Will Not Work ong16pierson16")




    ##
    #updatedState
    #Description: Determines what the agent's state would look like after a given move
    #
    #Parameters:
    #   currentState: the current state of the game
    #   Move: a move object
    #
    #Return:
    #   possibleState: A copy of currentState that has been altered to be a node
    ##
    def updatedState(self, currentState, move):
        #get a working copy of the currentState so we dont mess with the actual state
        stateCopy = currentState.fastclone()
        #get a reference to our inventory so that we can alter it
        ourInventory = getCurrPlayerInventory(stateCopy)
        #get a reference to where the enemy ants are
        enemyAntList = getAntList(stateCopy, self.playerId - 1, [(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)])
        ourWorkerList = getAntList(stateCopy, self.playerId, [(WORKER)])
        ourDroneList = getAntList(stateCopy, self.playerId, [(DRONE)])

        #part a
        if(move.moveType == BUILD and (move.buildType == DRONE or move.buildType == WORKER)):
            if(len(ourWorkerList) < 1 and move.buildType == WORKER):
                ourInventory.ants.append(Ant(getConstrList(stateCopy, self.playerId, [(ANTHILL)]), move.buildType, self.playerId))
            elif(len(ourDroneList) < 2 and move.buildType == DRONE):
                ourInventory.ants.append(Ant(getConstrList(stateCopy, self.playerId, [(ANTHILL)]), move.buildType, self.playerId))
            #part f
            ourInventory.foodCount -= 1

        #part b
        if(move.moveType == MOVE_ANT):
            ant = getAntAt(stateCopy, move.coordList[0])
            newSpot = move.coordList[len(move.coordList) - 1]
            ant.coords = newSpot
            #part d
            adjacent = listAdjacent(ant.coords)
            for x in range(0, len(adjacent)):
                for y in range(0, len(enemyAntList)):
                    if(adjacent[x] == enemyAntList[y].coords):
                        attackedAnt = getAntAt(stateCopy, adjacent[x])
                        attackedAnt.health -= 1
                        if(attackedAnt.health <= 0):
                            if(attackedAnt.type != QUEEN):
                                enemyAntList.remove(attackedAnt)
            #part c
            foodList = getConstrList(stateCopy, None, [(FOOD)])
            for food in foodList:
                if(ant.coords == food.coords and ant.carrying == False):
                    ant.carrying = True
            if(ant.coords == getConstrList(stateCopy, self.playerId, [(ANTHILL)])[0].coords and ant.carrying == True):
                ant.carrying = False
                ourInventory.foodCount += 1

        #part e
        return stateCopy

    ##
    #evalState
    #Description: this method evaluates a Game State object and returns a value between 0.0 and 1.0
    #based on how much our AI would be winning or losing in that state, with anythingn below 0.5 being losing
    #and anything from 0.5 to 1.0 is winning
    #
    #Parameters: stateToEval
    #
    #returns a double that is the evaluation of the state


    def evalState(self, stateToEval):
        result = 0.5

        ourInventory = getCurrPlayerInventory(stateToEval)
        ourAntList = ourInventory.ants
        ourDroneList = []
        ourWorkerList = []
        ourQueen = getCurrPlayerInventory(stateToEval).getQueen()
        ourTunnel = ourInventory.getTunnels()
        ourAnthill = ourInventory.getAnthill()
        ourFoodCount = ourInventory.foodCount

        foodList = getConstrList(stateToEval, None, ([FOOD]))
        foodListCoords = []
        for food in foodList:
            foodListCoords.append(food.coords)
        closestFood = None


        enemyInventory = stateToEval.inventories[self.playerId - 1]
        enemyAntList = enemyInventory.ants
        enemyTunnel = enemyInventory.getTunnels()
        enemyAnthill = enemyInventory.getAnthill()
        enemyFoodCount = enemyInventory.foodCount
        enemyQueen = enemyInventory.getQueen()

        #we add the difference between the number of ants we have and
        #multiply by 0.01. If we have more ants, we will be in a (more)
        #winning state and the number we add to result will be positive
        #If we have less ants then them, we are in a less winning state
        #and the number we add to result will be negative
        result += ((len(ourAntList) - len(enemyAntList)) * 0.01)

        if(len(ourDroneList) < 2):
            result -= (0.1 * (2 - len(ourDroneList)))
        else:
            result += 0.1
        #loop through all our ants and reward the workers for
        #carrying food
        for ant in ourAntList:
            if(ant.type == DRONE):
                ourDroneList.append(ant)
            if(ant.type == WORKER):
                ourWorkerList.append(ant)

            if(ant.type == WORKER and ant.carrying == False):

                steps = 100
                for f in foodList:
                    temp = stepsToReach(stateToEval, ant.coords, f.coords)
                    if(temp < steps):
                        steps = temp
                        closestFood = f.coords
                if((stepsToReach(stateToEval, ant.coords, closestFood) == 0)):
                    result += 0.2
                else:
                    result -= (stepsToReach(stateToEval, ant.coords, closestFood) * 0.02)

            if(ant.type == WORKER and ant.carrying == True):
                result -= (stepsToReach(stateToEval, ant.coords, ourTunnel[0].coords) * 0.01)
            elif(ant.type == WORKER and ant.carrying == True and ant.coords == ourAnthill.coords):
                result += 0.2
            elif(ant.type == WORKER and ant.carrying == True and (ant.coords == ourAnthill.coords or ant.coords == ourTunnel[0].coords)):
                result += 0.2


            elif(ant.carrying == False and ant.type == WORKER and (ant.coords in foodListCoords)):
                result += 0.11

            elif(ant.type == DRONE):
                result -= (stepsToReach(stateToEval, ant.coords, enemyQueen.coords) * 0.01)

        result += random.uniform(-0.001, 0.001)
        return result
    ##
    #getPlacement
    #Description: The getPlacement method corresponds to the
    #action taken on setup phase 1 and setup phase 2 of the game.
    #In setup phase 1, the AI player will be passed a copy of the
    #state as currentState which contains the board, accessed via
    #currentState.board. The player will then return a list of 10 tuple
    #coordinates (from their side of the board) that represent Locations
    #to place the anthill and 9 grass pieces. In setup phase 2, the player
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent�s side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),�,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
       if currentState.phase == SETUP_PHASE_1:
           return [(4,1), (4,0), (9,3), (8,2), (7,3), (6,2), (5,3), (0,3), (3,3), (2,2), (1,3)]

       #this else if is what sets up the food. it only lets us place 2 pieces
       #of food
       elif currentState.phase == SETUP_PHASE_2:

           result = []
           listToCheck = [4,5,3,6,2,7,1,8,0,9]

           for y in [6,7]:

               for num in listToCheck:
                   if(getConstrAt(currentState, (num, y)) == None):
                       result.append((num, y))
                       if(len(result)== 2):
                           return result

       else:
           return None

    ##
    #getMove
    #Description: The getMove method corresponds to the play phase of the game
    #and requests from the player a Move object. All types are symbolic
    #constants which can be referred to in Constants.py. The move object has a
    #field for type (moveType) as well as field for relevant coordinate
    #information (coordList). If for instance the player wishes to move an ant,
    #they simply return a Move object where the type field is the MOVE_ANT constant
    #and the coordList contains a listing of valid locations starting with an Ant
    #and containing only unoccupied spaces thereafter. A build is similar to a move
    #except the type is set as BUILD, a buildType is given, and a single coordinate
    #is in the list representing the build location. For an end turn, no coordinates
    #are necessary, just set the type as END and return.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a move from the player.(GameState)
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    ##
    def getMove(self, currentState):
        moveList = listAllLegalMoves(currentState)
        statesToEval = []
        evaluatedStates = []
        bestStateIndex = 0
        bestStateScore = 0.0
        for move in moveList:
            statesToEval.append(self.updatedState(currentState, move))
        for state in statesToEval:
            evaluatedStates.append(self.evalState(state))

        for index in range(0, len(evaluatedStates)):
            bestStateScore = evaluatedStates[index]

            if(evaluatedStates[index] > evaluatedStates[bestStateIndex]):
                bestStateIndex = index
                bestStateScore = evaluatedStates[index]


        return moveList[bestStateIndex]
    ##
    #getAttack
    #Description: The getAttack method is called on the player whenever an ant completes
    #a move and has a valid attack. It is assumed that an attack will always be made
    #because there is no strategic advantage from withholding an attack. The AIPlayer
    #is passed a copy of the state which again contains the board and also a clone of
    #the attacking ant. The player is also passed a list of coordinate tuples which
    #represent valid locations for attack. Hint: a random AI can simply return one of
    #these coordinates for a valid attack.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e.
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]

    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply
    #indicates to the AI whether it has won or lost the game. This is to help with
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass

#UnitTest
# board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
# p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
# p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
# neutralInventory = Inventory(NEUTRAL, [], [], 0)
# phase = MENU_PHASE
# turn = PLAYER_ONE
#
# aGameState = (board, (p1Inventory, p2Inventory, neutralInventory), phase, turn)
# p1Inventory.ants.append(Ant((2,2), QUEEN, PLAYER_ONE))
# p2Inventory.ants.append(Ant(()))
# aMoves =
# allMoves[0]
# somePlayer = AIPlayer(PLAYER_ONE)
# updatedState(aGameState, allMoves[0])
