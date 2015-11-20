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

# learning rate
LEARNING_RATE = 0.5

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
        super(AIPlayer,self).__init__(inputPlayerId, "The Conscious Ant PART 2")

        self.didPreProcessing = False
        #Calculate these before starting the game to speed up.
        self.preProcessMatrix = None
        self.hillCoords = None
        self.foodCoords = None
        self.inputsArray = []
        self.weights = [0.9892709344222808, -0.9467306756965964, 0.664579339071093, -0.8771066321441587, 0.20581711044341086, -0.3304955890605188, -0.38588564069713654, 0.41370639459020686, -0.17716889833464222, 0.9452082561443975, 0.4140829640765997, -0.7189982436881314, 0.6918376594500758, -0.7764512024030664, -0.8224330781216489, -0.998956675107487, -0.6164928352063785, -0.08760652013734392, -0.4473658053372447, -1.1739122630155314, -1.238272722551497, 0.368318308436457, -0.6834181949197763, 0.48062305967203134, 0.8320706486649576, -0.8470002236151709, -0.3492827864901731, 0.5834782354361334, 0.9807283308036696, 0.26848900791087593, -0.5755759655311115, -0.7823638496275709, -0.31950231995852435, -0.44402084693011273, -0.4942823996964574, 0.7863915534764581, 0.5187398821237776, 0.15179917560735037, -0.37646509006190576, -0.5716023968858785, -0.3875705580045472, 0.6911678240508885, -0.9722276436511577, -0.07198016886163483, -0.2601508123428519, -0.5447664742192456, -0.6655441383330047, 0.9222148867337203, 0.34612117863733444, -1.0075709387827487, 0.39211156525386515, -0.515932506660987, 0.6002936924737248, -0.08503695343725166, -0.0900064264174905, -0.1366132606123316, -0.20141968260291998, -0.7795503696712673, 0.40539631658337627, 0.44947407410922574, 0.5204591457575228, -0.5662824697571885, 0.564388914355044, 0.7438097242224029, -0.6916798824886741, -0.8023647179372966, -0.35469765815009535, 0.3850740738362098, 0.509604689574295, -0.08727065360015056, -0.7796162440005613, -0.8153606697716123, 0.2086407228339726, 0.9430838998036195, 0.643647633341589, -0.5637187524443876, -0.6824138678024496, 0.4334964313963884, -0.6212860839977458, 0.4880025291009049, -0.8529462862944922, -0.44912800767468225, -0.42992458357986085, -0.7366137039989994, -0.24271531422965364, 0.5691718791485069, -0.36772935883489893, -0.9534353159574835, 0.6000748385584529, -0.31571455563880113, 0.4830072513833217, -0.7072071514193508, 0.4822574603931988, 0.09212069359424013, 0.28350642471986814, -0.03315321643143854, -0.07220110842842722, 0.015213575495644047, 0.6307718427110562, 0.6174499201717573, 0.9690623651045661, -0.6749765044161231, 0.9382370005641575, 0.3779086790656436, -0.5809780788018492, 0.9048816361793655, 0.638706636661287, -0.6985885046885133, -0.6700878406821354, 0.8110071375402427, 1.0988840417961174, -0.024891322885468137, -0.5831034389938238, 0.9909565397168707, -0.22263690291042093, 0.7497350357847913, 1.260290409525704, 0.542569023329671, 0.09078272587205242, -0.04415760014489423, 0.38154959262174504, 0.16943601766273492, 0.40393108966700453, 0.4049380539954025, 0.3569842272106435, 0.2610624749806633, -0.8242655983871262, -0.5459007144115147]
        self.finalWeights = [-1.0296920192203574, -0.3094036272761769, -0.772234789577509, 0.24743624976062123, 0.4062486879960021, -0.6934265898015216, 0.760915059964459, -0.785497094413972, -0.3657136845853897, -0.8536963554434123, 0.7821633441415424, -1.020243033224688, 0.10929153809078253, 0.034844138550568886, -1.0309076720588783, 0.451049526282004]
        self.neuralArray = []
        self.finalNode = 0
        for i in range(0, 16):
            self.neuralArray.append(0)
        #for i in range(0, 128):
        #    self.weights.append(random.uniform(-1,1))
        #for i in range(0, 16):
        #    self.finalWeights.append(random.uniform(-1,1))
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

        #score = self.expand(currentState)['score']
        score = 0

        # self.neuralNetwork(currentState, self.playerId, score)          Hidden - move to

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

    def neuralNetwork(self, currentState, playerNo, minmaxscore, debug=False):

        workers = getAntList(currentState, playerNo, (WORKER,))
        queens = getAntList(currentState, playerNo, (QUEEN,))
        theirQueen = getAntList(currentState, playerNo -1, (QUEEN,))
        print "###########inputs:############"
        #################################################################################
        #Score having exactly one worker

        workerCountScore = 0.0
        if len(workers) == 1:
            workerCountScore = 1.0
        self.inputsArray.append(workerCountScore)

        print "workerCountScore:" + `workerCountScore`

        #################################################################################
        #Score the food we have

        foodScore = (currentState.inventories[playerNo].foodCount) / 11.0       # * FOOD_WEIGHT
        self.inputsArray.append(foodScore)

        print "our food score:" + `foodScore`

        #Score the food enemy has
        foodScoreEnemy = (currentState.inventories[playerNo -1].foodCount) / 11.0
        self.inputsArray.append(foodScoreEnemy)

        print "their food score:" + `foodScoreEnemy`
        #################################################################################
        #queen health

        queenHealth = (queens[0].health) / 4.0
        self.inputsArray.append(queenHealth)

        print "our queen health:" + `queenHealth`
        #enemy queen health
        theirQueenHealth = (theirQueen[0].health) / 4.0
        self.inputsArray.append(theirQueenHealth)

        print "their queen score:" + `theirQueenHealth`
        #################################################################################
        #Score queen being off of anthill and food

        queenScore = 0.0
        x, y = queens[0].coords
        if not self.preProcessMatrix[x][y]['foodDist'] == 0:
            queenScore = 1.0
        elif not self.preProcessMatrix[x][y]['constrDist'] == 0:
            queenScore = 1.0
        self.inputsArray.append(queenScore)

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
        self.inputsArray.append(distScore)
        self.inputsArray.append(carryScore)

        print "distance score:" + `distScore`
        print "carry score:" + `carryScore`

        return self.neuralNode()
        #self.backPropagation(minmaxscore)


    #creates node from inputs and weights
    #calculates final node
    #output - final node
    def neuralNode(self):
        for i in range(0, len(self.neuralArray)):
            #if need TODO add bias here
            for j in range(0, 8):
                self.neuralArray[i] += (self.inputsArray[j] * self.weights[(i*8)+j])
            self.neuralArray[i] = 1/(1+math.e**int((-self.neuralArray[i])))

        print "neural array" + `self.neuralArray`

        for i in range(0, len(self.neuralArray)):
			self.finalNode += (self.neuralArray[i] * self.finalWeights[i])
        self.finalNode = 1/(1+math.e**int((-self.finalNode)))

        return self.finalNode

    #take final node
    #calculate new weights used with neuralArray
    def backPropagation(self, target):
        error = target - self.finalNode
        errorTermFinal = ((self.finalNode)*(1-self.finalNode)*error)

        print "final error" + `error`
        print "final error term" + `errorTermFinal`

        errorOutArray = []
        for i in self.finalWeights:
            errorOutArray.append(i*errorTermFinal)
        print "errorOutArray:" + `errorOutArray`

        errorTermOutArray = []
        for i in range (0, len(self.neuralArray)):
            errorTermOutArray.append(self.neuralArray[i]*(1-self.neuralArray[i])*errorOutArray[i])
        print "errorTermOutArray:" + `errorTermOutArray`

        for i in range(0, len(self.neuralArray)):
            self.finalWeights[i] = self.finalWeights[i] + LEARNING_RATE * errorTermFinal * self.neuralArray[i]
        print "New final weights" + `self.finalWeights`

        for i in range (0, len(self.neuralArray)):
            for j in range (0,8):
                self.weights[(i*8)+j] = self.weights[(i*8)+j] + LEARNING_RATE * errorTermOutArray[i] * self.inputsArray[j]
        print "new weights" + `self.weights`

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
        # playerScore = self.getPlayerScore(hypotheticalState, self.playerId)   replaced with new neural network
        score = 0
        playerScore = self.neuralNetwork(hypotheticalState, self.playerId, score) #score perameter is not needed due to not calling the back propagation method
        #Normalize the score to be between 0.0 and 1.0
        print "player score: " + `playerScore`

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
