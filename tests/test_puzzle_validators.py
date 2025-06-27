import json
from pathlib import Path
import pytest

from scripts.puzzle_validators import (
    validate_sudoku,
    validate_word_search,
    validate_crossword,
)

@pytest.fixture
def tmp_meta_dir(tmp_path):
    d = tmp_path / 'metadata'
    d.mkdir()
    return d

def write_meta(dirpath, name, data):
    f = dirpath / name
    f.write_text(json.dumps(data))
    return f

def test_validate_sudoku_valid(tmp_meta_dir):
    # 4x4 valid completed Sudoku
    grid = [
        [1,2,3,4],
        [3,4,1,2],
        [2,1,4,3],
        [4,3,2,1]
    ]
    data = { 'id': 1, 'initial_grid': grid, 'solution_grid': grid }
    write_meta(tmp_meta_dir, 'sudoku_puzzle_01.json', data)
    issues = validate_sudoku(tmp_meta_dir)
    assert issues == []

def test_validate_sudoku_duplicate(tmp_meta_dir):
    # Duplicate in row 0
    grid = [ [1,1,3,4], [3,4,1,2], [2,1,4,3], [4,3,2,1] ]
    data = { 'id': 2, 'initial_grid': grid, 'solution_grid': grid }
    write_meta(tmp_meta_dir, 'sudoku_puzzle_02.json', data)
    issues = validate_sudoku(tmp_meta_dir)
    assert any('Duplicate value' in issue['description'] for issue in issues)

def test_validate_sudoku_multiple_solutions(tmp_meta_dir):
    # Empty grid (all zeros) has multiple solutions
    grid = [[0,0,0,0] for _ in range(4)]
    data = { 'id': 3, 'initial_grid': grid, 'solution_grid': grid }
    write_meta(tmp_meta_dir, 'sudoku_puzzle_03.json', data)
    issues = validate_sudoku(tmp_meta_dir)
    assert any('Multiple solutions' in issue['description'] for issue in issues)

def test_validate_word_search_valid(tmp_meta_dir):
    # Simple 4x4 grid with 'TEST' horizontally
    grid = [
        ['T','E','S','T'],
        ['A','B','C','D'],
        ['E','F','G','H'],
        ['S','I','J','K'],
    ]
    words = ['TEST']
    data = { 'id': 1, 'grid': grid, 'words': words }
    write_meta(tmp_meta_dir, 'word_search_puzzle_01.json', data)
    issues = validate_word_search(tmp_meta_dir)
    assert issues == []

def test_validate_word_search_not_found(tmp_meta_dir):
    grid = [['A','B'],['C','D']]
    words = ['NOPE']
    data = { 'id': 2, 'grid': grid, 'words': words }
    write_meta(tmp_meta_dir, 'word_search_puzzle_02.json', data)
    issues = validate_word_search(tmp_meta_dir)
    assert any('Word not found' in issue['description'] for issue in issues)

def test_validate_crossword_valid(tmp_meta_dir):
    clues = { 'across': [(1,'Clue','WORD')], 'down': [(1,'Clue','WORD2')] }
    pos = { '0,0': 1, '0,2': 2 }
    data = { 'id': 1, 'clues': clues, 'clue_positions': pos }
    write_meta(tmp_meta_dir, 'puzzle_01.json', data)
    issues = validate_crossword(tmp_meta_dir)
    assert issues == []

def test_validate_crossword_mismatch(tmp_meta_dir):
    clues = { 'across': [(1,'Clue','ONE')], 'down': [(1,'Clue','TWO')] }
    pos = { '0,0': 1 }
    data = { 'id': 2, 'clues': clues, 'clue_positions': pos }
    write_meta(tmp_meta_dir, 'puzzle_02.json', data)
    issues = validate_crossword(tmp_meta_dir)
    assert any('Expected' in issue['description'] for issue in issues)
