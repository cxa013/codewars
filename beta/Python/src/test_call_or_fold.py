import pytest
from random import Random

BOARD_RUNOUTS = [
    (['JS', '9S', 'KH'], ['AS', '3S'], ['KS', 'KD'], 5),
    ([], ['AS', '3S'], ['KS', 'KD'], 5),
]

DETERMINISTIC_DRAWS = [
    ['TH', '7C'],
    ['3H', '6S'],
    ['6D', '6C'],
    ['8H', 'JC'],
    ['2C', '6D'],
    ['2H', 'QS'],
    ['8C', 'QS']
]

FINAL_HAND = [
    (['JS', '9S', 'KH'], DETERMINISTIC_DRAWS[0], ['AS', '3S'], [14, 13, 11, 10, 9]),
    (['JS', '9S', 'KH'], DETERMINISTIC_DRAWS[1], ['AS', '3S'], [14, 11, 9, 3, 3]),
    (['JS', '9S', 'KH'], DETERMINISTIC_DRAWS[2], ['AS', '3S'], [14, 13, 11, 6, 6]),
    (['JS', '9S', 'KH'], DETERMINISTIC_DRAWS[3], ['AS', '3S'], [14, 13, 11, 11, 9]),
    (['JS', '9S', 'KH'], DETERMINISTIC_DRAWS[4], ['AS', '3S'], [14, 13, 11, 10, 9]),
    (['JS', '9S', 'KH'], DETERMINISTIC_DRAWS[5], ['AS', '3S'], [14, 13, 12, 11, 3]),
    (['JS', '9S', 'KH'], DETERMINISTIC_DRAWS[6], ['AS', '3S'], [14, 13, 12, 11, 3]),
]

INPUT = [
    ('KS AS TS QS JS', 'K♠A♠T♠Q♠J♠'),
    ('2D AH 4H 5S KC', '2♦A♥4♥5♠K♣'),
]

@pytest.fixture
def deck():
    from call_or_fold import new_deck
    deck = new_deck()
    return deck

@pytest.mark.parametrize('hand, result', INPUT)
def test_convert_suits(hand, result):
    """Test that convert_suits returns a string with actual suits in place of characters representing the suit."""
    from call_or_fold import convert_suits
    assert convert_suits(hand) == result

def test_new_deck(deck):
    """Test that a new deck with 52 cards is returned and all suits are correct."""
    for suit in ['C', 'H', 'S', 'D']:
        assert len([c for c in deck if c[1] == suit]) == 13

def test_draw_cards(deck):
    """Test that dead cards are handled correctly when drawing cards from a shuffled deck."""
    from call_or_fold import draw_cards
    dead = ['AS', 'AH']
    drawn = draw_cards(50, deck, dead=dead)
    assert 'AS' not in drawn
    assert len(drawn) == 50
    assert not deck

def test_draw_cards_deterministic(deck):
    """Test that same cards are drawn passing in a seed."""
    from call_or_fold import draw_cards, new_deck
    random = Random(333)
    dead = ['JS', '9S', 'KH', 'AS', '3S']
    out = []
    for _ in range(7):
        out.append(draw_cards(2, deck, dead, random=random))
    for idx, draw in enumerate(out):
        deck = new_deck()
        assert draw == DETERMINISTIC_DRAWS[idx]

@pytest.mark.parametrize('board, hero, villain, result', BOARD_RUNOUTS)
def test_complete_board(deck, board, hero, villain, result):
    """Test that complete_board returns a board of 5 unique cards."""
    from call_or_fold import complete_board
    board = complete_board(deck, board, hero, villain)
    assert len(board) == result

@pytest.mark.parametrize('board, runout, hole_cards, result', FINAL_HAND)
def test_get_best_hand(board, runout, hole_cards, result):
    """Test that given a board, a runout and hole_cards, the best 5 card combination is returned."""
    from call_or_fold import get_best_hand
    assert get_best_hand(board + runout, hole_cards) == result



