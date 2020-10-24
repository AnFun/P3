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
    if identity == 2:
        win_rate = 1 - win_rate
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


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

  Args:
      board:  The game setup.
      state:  The state of the game.

  """
    while not board.is_ended(state):
        action = choice(board.legal_actions(state))
        state = board.next_state(state, action)
    return state


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
        sampled_game = rollout(board, sampled_game)  # round and round

        # Backpropagation
        won = board.win_values(sampled_game)[identity_of_bot]
        backpropagate(leaf_node, won)

    children = [n for n in root_node.child_nodes.items() if n[1].visits > 0]
    return max(children, key=lambda n: n[1].wins / n[1].visits)[0]
