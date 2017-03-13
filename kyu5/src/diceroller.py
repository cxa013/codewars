"""Module to solve the code-kata https://www.codewars.com/kata/rpg-dice-roller.
"""

import re
from random import random


def validate_input(s):
    """Return True if input follows the dice notation or False."""
    try:
        s = s.strip()
    except AttributeError:
        return False
    s = s.replace(' ', '')
    pattern = r'^[1-9]?d[1-9]+(?:[+-]?\d)*$'
    m = re.match(pattern, s)
    return True if m else False

def get_modifiers(s):
    """Return a list of modifiers of the given dice notation."""
    pattern = r'[+-]+[1-9][0-9]*'
    return sum([int(match) for match in re.findall(pattern, s)])


# def roll(s, output='summed'):
#     """Roll Dice defined in input string and apply modifieres if present.
#
#     Keyword arguments:
#     output -- takes either 'summed' or 'verbose' (default: 'summed')
#     'summed' will sum up the roll plus modifieres and return an integers
#     'verbose' returns an object with a list containing all rolls and the sum of
#     all modifiers. If no modifiers are given, returns zero
#     """
#     d = validate_input(s)
#     if d:
