
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log, e
import p3_t3

num_nodes = 1000
explore_faction = 2.


def traverse_nodes(node, board, state, identity):
    if node.child_nodes is None or node.untried_actions:
        return node
    else:
        best_uct = 0.0
        for child in node.child_nodes:
            calc_uct = (child.wins/child.vists) + (explore_faction * sqrt((log(child.parent.vists, e))/child.visits)) #remember to alter so that calculation considers the "team"
            if calc_uct >= best_uct:
                best_uct = calc_uct
                best_node = child

        return traverse_nodes(best_node, board, state, identity)

    """ Traverses the tree until the end criterion are met.
    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.
    """




def expand_leaf(node, board, state):
    new_action = node.untried_actions.pop() #retrieve untried action
    #check validity
    if new_action is None:
        return None
    else:
        state = node.next_state(state, new_action)
        new_node = MCTSNode(parent=node, parent_action= new_action, action_list=board.legal_action(state))
        node.child_nodes.insert(new_node)
        return new_node
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    pass
    # Hint: return new_node


def rollout(board, state):
    while not board.is_ended(state):
        rand_action = choice(board.legal_actions(board, state))
        state = board.next_state(state, rand_action)
    return state

    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    pass


def backpropagate(node, won):
    if node is not None:
        node.wins += won
        node.visit += 1
        node = node.parent
        backpropagate(node, won)

    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node
        
         #selection
         #expansion
         #random outcomes of games, need a way to check if rollout was a win or not, make distinction between win/loss/draw 
         #backpropagation
    #find node with the highest win count
    #run through root children, check highest win rate for children from root, return action of corresponding child 
        
       
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return