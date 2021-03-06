"""Module to solve the code-kata https://www.codewars.com/kata/sudoku-solver."""

from math import sqrt, ceil
from itertools import islice, chain, groupby
from operator import itemgetter
from collections import defaultdict

def sudoku_solver(m):
    """Return a valid Sudoku for a given matrix.
        Store all starting numbers by looping through the Sudoku square by square
        Find all missing numbers by subtracting the 2 sets
        Generate all starting spots and find the one with the least amount of digits missing
        Generate candidates by finding all possible numbers for a given starting point
        Pop the starting point from a sorted representation of the previously built list
        Update Sudoku if a fit is found
        Remove updated digit from all lists of missing number and as a possible candidates
        Repeat with next starting point
        If no immediate match is found, scrap candidated and rebuild until all digits have been
        inserted.
        """
    square_sides = int(sqrt(len(m)))
    dicts = initialize_dicts(m, square_sides)
    dicts, square_coords = populate_dicts(m, square_sides, dicts)
    dicts = get_missing(dicts)
    candidates = get_candidates(m, dicts, square_coords)
    m, candidates = scan_sudoku(m, dicts, square_coords, candidates)
    single_candidates = single_candidate(candidates, square_coords, dicts)
    m, candidates = fill_fit(m, dicts, square_coords, single_candidates=single_candidates)
    candidates = get_candidates(m, dicts, square_coords)
    naked_sets_fields_row, naked_sets_fields_cols = find_naked_sets(candidates, dicts, setlength=2)
    candidates, naked_sets = remove_naked_sets_from_candidates(candidates, naked_sets_fields_row, naked_sets_fields_cols)
    candidates = get_candidates(m, dicts, square_coords, naked_sets)
    naked_sets_fields_row, naked_sets_fields_cols = find_naked_sets(candidates, dicts, setlength=3)
    return m

def initialize_dicts(m, square_sides):
    """Return dicts to hold information about the Sudoku."""
    rows_missing = defaultdict(list)
    rows_missing = initialize_d(rows_missing, square_sides)
    cols_missing = defaultdict(list)
    cols_missing = initialize_d(cols_missing, square_sides)
    squares_missing = defaultdict(list)
    squares_missing = initialize_d(cols_missing, square_sides, 1)
    return rows_missing, cols_missing, squares_missing


def initialize_d(d, square_sides, offset=0):
    """Return an initialized dict so empty rows or columns in the Sudoku are
    correctly handled."""
    return {key:[] for key in range(offset, square_sides ** 2 + offset)}


def fill_given_numbers(square, row, col, sq_nr, dicts, squares_coords):
    """Fill dicts with given numbers number for a given square."""
    rm, cm, sm = dicts
    sq = squares_coords
    for row_idx, sr in enumerate(square):
        for col_idx, sv in enumerate(sr):
            coord = (row + row_idx, col + col_idx)
            if sv == 0:
                sq[coord] = sq_nr
                continue
            rm[coord[0]].append(sv)
            cm[coord[1]].append(sv)
            sm[sq_nr].append(sv)
    return dicts, sq


def populate_dicts(m, square_sides, dicts):
    """Return dicts holding information about fills in given Sudoku."""
    sq_nr = 0
    squares_coords = {}
    for row in range(0, square_sides ** 2, square_sides):
        for col in range(0, square_sides ** 2, square_sides):
            sq_nr += 1
            square = [islice(m[i], col, square_sides + col) for i in range(row, row + square_sides)]
            dicts, square_coords = fill_given_numbers(square, row, col, sq_nr, dicts, squares_coords)
    return dicts, square_coords


def get_missing(dicts):
    """Return dictionaries with swapped values from given numbers to missing numbers."""
    for d in dicts:
        for k, v in d.items():
            d[k] = set([1, 2, 3, 4, 5, 6, 7, 8, 9]) - set(v)
    return dicts


def get_starting_spots(m, dicts, square_coords):
    """Return a list with coordinates as starting point for sudoku solver."""
    rm, cm, sm = dicts
    starting_spots = []
    row = 0
    col = 0
    max = 20
    start = -1
    for col in range(9):
        for row in range(9):
            if m[row][col] == 0:
                square = square_coords[(row, col)] - 1
                missing_numbers = len(cm[col]) + len(rm[row]) + len(sm[1 if square < 1 else square])
                starting_spots.append((row, col, missing_numbers))
    return starting_spots


def get_candidates(m, dicts, square_coords, naked_sets=None):
    """Return a dict of candidates for all starting_spots in the Sudoko."""
    starting_spots = get_starting_spots(m, dicts, square_coords)
    starting_spots.sort(key=itemgetter(2))
    rm, cm, sm = dicts
    c = {}
    for coordinate in starting_spots:
        row, col, missing = coordinate
        c[(row, col)] = [n for n in cm[col] if n in rm[row] and n in sm[square_coords[row, col]]]
        try:
            c[(row, col)] = [n for n in c[(row, col)] if n not in naked_sets[(row, col)]]
        except (KeyError, TypeError):
            continue
    return c


def find_fit(candidates):
    """Return a tuple with coordinate and value to update from a sorted
    representation of a dict. If no fit can be found, return None."""
    try:
        fit = sorted(candidates.items(), key=lambda x: len(x[1])).pop(0)
    except AttributeError:
        return None
    row, col = fit[0]
    n = fit[1].pop()
    if len(fit[1]) == 0:
        return row, col, n
    return None


def update_sudoku(fit, m):
    """Return an updated Sudoku."""
    row, col, n = fit
    try:
        if m[row][col] != 0:
            raise ValueError
        m[row][col] = n
    except ValueError:
        raise ValueError('This coordinate has already been updated.')
    return m


def remove_updated_from_dicts(fit, dicts, squares_coords):
    """Return dicts with updated digit removed from missing digits."""
    row, col, n = fit
    rm, cm, sm = dicts
    sq = squares_coords
    rm[row].remove(n)
    cm[col].remove(n)
    sm[squares_coords[row, col]].remove(n)
    del sq[(row, col)]
    return dicts


def remove_from_candidates(fit, candidates):
    """Return candidates with updated digit removed from all coordinates."""
    if not candidates: return candidates
    row, col, n = fit
    del candidates[(row, col)]
    for k, v in candidates.items():
        if k[0] == row or k[1] == col:
            try:
                v.remove(n)
            except:
                continue
    return candidates


def fill_fit(m, dicts, squares_coords, candidates=[], single_candidates=[]):
    """Return an updated Sudoku by either finding a fit or taking a fit from a provided
    list of fits and filling it in as long as a fit is found."""
    while True:
        try:
            if single_candidates:
                num, coord = single_candidates.pop()
                fit = (coord[0], coord[1], num)
            else:
                fit = find_fit(candidates)
            # print("fit: ", fit)
        except IndexError:
            return m, candidates
        if fit:
            m = update_sudoku(fit, m)
            dicts = remove_updated_from_dicts(fit, dicts, squares_coords)
            candidates = remove_from_candidates(fit, candidates)
        else:
            return m, candidates


def scan_sudoku(m, dicts, square_coords, candidates):
    """Return an updated Sudoku by using the scanning technique to find fits and
    filling them in. After each scan, list of candidates is rebuild until no
    further immediate fills are possible."""
    while True:
        if len(sorted(candidates.items(), key=lambda x: len(x[1])).pop(0)[1]) > 1: # no longer easily solvable
            break
        m, candidiates = fill_fit(m, dicts, square_coords, candidates=candidates)
        starting_spots = get_starting_spots(m, dicts, square_coords)
        starting_spots.sort(key=itemgetter(2))
        candidates = get_candidates(m, dicts, square_coords)
        if not candidates: break
    return m, candidates


def squares_to_missing(square_coords):
    """Return a dict of square numbers as key and empty fields in the Sudoku as values."""
    squares_missing = defaultdict(list)
    for k, v in square_coords.items():
        squares_missing[v].append(k)
    return squares_missing


def single_candidate(candidates, square_coords, squares_missing):
    """Return a number which is a single candidate for a coordinate in the list of candidates:
        Build a dict with square as key and empty fields as value
        Go through every square and get all missing fields
        For every missing field in that square, get the possible numbers
        Look for a number which is only missing in one field in a square."""
    out = []
    coords_missing_in_square = squares_to_missing(square_coords)
    for k, v in coords_missing_in_square.items():
        single_candidates = defaultdict(list)
        seen = set()
        for coord in v:
            pn = set(candidates[coord])
            if pn.issubset(seen):
                continue
            for n in pn:
                if n in seen:
                    continue
                if single_candidates.get(n, 0):
                    seen.add(n)
                    continue
                single_candidates[n] = coord
        if len(seen) == len(squares_missing[k]):
            continue
        out.append([(k, v) for k, v in single_candidates.items() if k not in seen])
    return list(chain.from_iterable(out))


def find_naked_sets(candidates, dicts, setlength=2):
    """Return a dict of naked sets mapped to coordinates. A naked set is a set of numbers
    which are the only possible values for fields along a row or column."""
    c = candidates
    ns = build_possible_naked_sets(c, setlength=setlength)
    cpns = build_coords_per_naked_set(ns)
    ns = update_naked_set(ns, cpns)
    rows = get_coords_naked_sets(ns, candidates, dicts, row_or_col=0, setlength=setlength)
    cols = get_coords_naked_sets(ns, candidates, dicts, row_or_col=1, setlength=setlength)
    return rows, cols


def build_possible_naked_sets(c, setlength=2):
    """Return a dict with coordinates and possible values with length of setlength, 2 by default."""
    ns = {}
    pairs = [p for p in c.values() if len(p) == setlength]
    for k, v in c.items():
        if v in pairs:
            ns[k] = sorted(v)
    return ns


def build_coords_per_naked_set(ns):
    """Return a new dict with inverted values from ns"""
    cpns = defaultdict(list)
    for pair in ns.values():
        if cpns.get(tuple(pair), 0): continue
        for k, v in ns.items():
            row, col = k
            if v == pair:
                cpns[tuple(pair)].append(k)
    return cpns


def update_naked_set(ns, cpns):
    """Return an updated dict of naked set."""
    for k, v in cpns.items():
        if len(v) == 1:
            del ns[v.pop()]
        else:
            if len(set(v)) < 3:
                for coord in set(v):
                    del ns[coord]
    return ns


def get_coords_naked_sets(ns, candidates, dicts, row_or_col=0, setlength=2):
    """Return a list of coordinates where naked sets can be removed from."""
    c = candidates
    rm, cm, sm = dicts
    group = []
    out = {}
    ns_sorted = {el[0]:el[1] for el in sorted(ns.items(), key=lambda x: x[0])}
    for k, g in groupby(ns_sorted, lambda x: x[row_or_col]):
        coords = list(g)
        key = tuple(ns[coords[0]])
        if len(coords) > 1: #if list has only one element, there are no naked sets for that key
            if len(cm[k] if row_or_col == 1 else rm[k]) > setlength: #check missing row or col dict to see if more than given setlength is missing
                out[key] = [coord for coord in c.keys() if coord[row_or_col] == k and coord not in coords]
    return out


def remove_naked_sets_from_candidates(c, *args, naked_sets=defaultdict(list)):
    """Return an updated list of candidates and naked sets after removing possible numbers by looking at naked sets"""
    for d in args:
        for k, v in d.items():
            for coord in v:
                c[coord] = [n for n in c[coord] if n not in k]
                naked_sets[coord].extend(list(k))
    return c, dict(naked_sets)
