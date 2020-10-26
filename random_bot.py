#Group: Quinn Satow and Luc Milburn
#CMPM 146 Fall 2020
from random import choice


def think(board, state):
    """ Returns a random move. """
    return choice(board.legal_actions(state))
