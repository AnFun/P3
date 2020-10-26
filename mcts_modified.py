#Group: Quinn Satow and Luc Milburn
#CMPM 146 Fall 2020

from typing import Optional

from mcts_node import MCTSNode
from random import choice, random
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

Action = (int, int, int, int)


def tree_policy(node: MCTSNode, identity) -> float:
    if node.visits == 0:
        return 0

    parent = node.parent
    win_rate = node.wins / node.visits
    return win_rate + (explore_faction * sqrt(log(parent.visits) / node.visits))


def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

  Args:
      node:       A tree node from which the search is traversing.
      board:      The game setup.
      state:      The state of the game.
      identity:   The bot's identity, either 'red' or 'blue'.

  Returns:        A node from which the next stage of the search can proceed.

  """
    children = node.child_nodes

    # This node has potential children, should be expanded
    if node.untried_actions:
        return state, node

    # Cannot proceed with no other moves, we must've reached the end
    if not children:
        return state, None

    # Pick a child node using UTC function
    next_node = max(children.items(), key=lambda n: tree_policy(n[1], identity))
    state = board.next_state(state, next_node[0])

    return traverse_nodes(next_node[1], board, state, identity)


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

  Args:
      node:   The node for which a child will be added.
      board:  The game setup.
      state:  The state of the game.

  Returns:    The added child node.

  """

    # Update board state
    action = node.untried_actions.pop()
    state = board.next_state(state, action)

    # Create the child node
    child_node = MCTSNode(node, action, board.legal_actions(state))

    # Update parent node with our new move
    node.child_nodes[action] = child_node
    return state, child_node


def last_good_reply(move, replies, choices):
    (action, _, identity) = move
    key = (action, identity)
    if reply := replies.get(key):
        return reply if reply in choices else None
    return None


def backpropagate_moves(move, replies, identity):
    (action, last_move, move_identity) = move
    if last_move and move_identity == identity:
        replies[(last_move[0], identity)] = action
        backpropagate_moves(last_move, replies, identity)


# Modification: Using LGRF-1 algorithm from http://pug.raph.free.fr/files/PowerOfForgetting.pdf
def rollout(board, state, replies):
    """ Given the state of the game, the rollout plays out the remainder randomly.

  Args:
      board:  The game setup.
      state:  The state of the game.

  """
    move = None
    initial_identity = board.current_player(state)
    while not board.is_ended(state):
        choices = board.legal_actions(state)

        identity = board.current_player(state)
        last_move = move

        action = last_good_reply(last_move, replies, choices) if last_move else None

        # Fallback to uniform probability policy
        if not action:
            action = choice(choices)

        move = (action, last_move, identity)

        state = board.next_state(state, action)

    score = board.win_values(state)
    replies_copy = dict(replies)
    for key in replies_copy.keys():
        (action, identity) = key
        if score[identity] == 0:
            del replies[key]

    if score[initial_identity] > 0 and move:
        backpropagate_moves(move, replies, initial_identity)

    return state, move


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

  Args:
      node:   A leaf node.
      won:    An indicator of whether the bot won or lost the game.

  """
    node.visits += 1
    node.wins += won
    parent = node.parent
    if parent:
        backpropagate(parent, won)


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

  Args:
      board:  The game setup.
      state:  The state of the game.

  Returns:    The action to be taken.

  """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    replies = {}  # (move, identity)
    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Selection
        (sampled_game, leaf_node) = traverse_nodes(node, board, sampled_game, identity_of_bot)

        if not leaf_node:
            continue

        # Expansion
        (sampled_game, leaf_node) = expand_leaf(leaf_node, board, sampled_game)

        # Simulation
        (sampled_game, move) = rollout(board, sampled_game, replies)  # round and round

        # Backpropagation
        won = board.win_values(sampled_game)[identity_of_bot]

        backpropagate(leaf_node, won)

        # Propagate last known good replies
        # if move:
        # backpropagate_moves(move, replies, identity_of_bot, won)

    children = [n for n in root_node.child_nodes.items() if n[1].visits > 0]
    return max(children, key=lambda n: n[1].wins / n[1].visits)[0]
