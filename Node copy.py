##
#Node
#Description: class representation of nodes in a search tree.
#
#Variables:
#   move that would be taken in the given state from the parent node,
#   the state that would be reached by taking that move
#   an evaluation of this state
##
class Node(object):

    def __init__(self, state, move, pNode, rating):
        self.state = state
        self.move = move
        self.pNode = pNode
        self.rating = rating
        #self.expectedStateRating = getStateRating(state, expectedState)
        
