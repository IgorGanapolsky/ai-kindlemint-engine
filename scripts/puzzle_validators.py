#!/usr/bin/env python3
"""
Puzzle Validators - Domain-aware validation for puzzles
"""
import json
from pathlib import Path
from math import sqrt

def validate_sudoku(metadata_dir):
    """
    Validate Sudoku puzzles for uniqueness, solvability, and rule compliance.
    Returns a list of issues: [{ 'puzzle_id': int, 'description': str }, ...]
    """
    issues = []
    md = Path(metadata_dir)
    for meta_file in sorted(md.glob('sudoku_puzzle_*.json')):
        try:
            data = json.loads(meta_file.read_text())
            pid = data.get('id')
            grid = data.get('initial_grid')
            n = len(grid)
            # Check grid shape
            if any(len(row) != n for row in grid):
                issues.append({'puzzle_id': pid, 'description': 'Grid is not square'})
                continue
            # Check values
            for r, row in enumerate(grid):
                for c, v in enumerate(row):
                    if not isinstance(v, int) or v < 0 or v > n:
                        issues.append({'puzzle_id': pid, 'description': f'Invalid value at ({r},{c}): {v}'})
            # Check row/col uniqueness
            for i in range(n):
                seen = set()
                for v in grid[i]:
                    if v != 0 and v in seen:
                        issues.append({'puzzle_id': pid, 'description': f'Duplicate value {v} in row {i}'})
                    seen.add(v)
                seen = set()
                for row in grid:
                    v = row[i]
                    if v != 0 and v in seen:
                        issues.append({'puzzle_id': pid, 'description': f'Duplicate value {v} in column {i}'})
                    seen.add(v)
            # Check subgrid uniqueness if possible
            block = int(sqrt(n))
            if block * block == n:
                for br in range(0, n, block):
                    for bc in range(0, n, block):
                        seen = set()
                        for r in range(br, br+block):
                            for c in range(bc, bc+block):
                                v = grid[r][c]
                                if v != 0 and v in seen:
                                    issues.append({'puzzle_id': pid, 'description': f'Duplicate value {v} in block starting at ({br},{bc})'})
                                seen.add(v)
            # Count solutions
            sol_count = _count_solutions(grid, limit=2)
            if sol_count == 0:
                issues.append({'puzzle_id': pid, 'description': 'No valid solutions'})
            elif sol_count > 1:
                issues.append({'puzzle_id': pid, 'description': 'Multiple solutions detected'})
        except Exception as e:
            issues.append({'puzzle_id': None, 'description': f'Error validating puzzle file {meta_file.name}: {e}'})
    return issues

def _count_solutions(grid, limit=2):
    """Backtracking solver to count solutions up to a limit."""
    n = len(grid)
    # Find first empty cell
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                total = 0
                for v in range(1, n+1):
                    if _is_safe(grid, r, c, v):
                        grid[r][c] = v
                        total += _count_solutions(grid, limit)
                        grid[r][c] = 0
                        if total >= limit:
                            return total
                return total
    # No empty cells: found a solution
    return 1

def _is_safe(grid, r, c, v):
    n = len(grid)
    # Row/col
    for i in range(n):
        if grid[r][i] == v or grid[i][c] == v:
            return False
    # Block
    block = int(sqrt(n))
    if block * block == n:
        br = (r // block) * block
        bc = (c // block) * block
        for i in range(br, br+block):
            for j in range(bc, bc+block):
                if grid[i][j] == v:
                    return False
    return True

def validate_word_search(metadata_dir):
    """
    Validate Word Search puzzles to ensure each word appears exactly once.
    Returns a list of issues: [{ 'puzzle_id': int, 'word': str, 'description': str }, ...]
    """
    issues = []
    md = Path(metadata_dir)
    for meta_file in sorted(md.glob('word_search_puzzle_*.json')):
        try:
            data = json.loads(meta_file.read_text())
            pid = data.get('id')
            grid = data.get('grid', [])
            words = data.get('words', [])
            # Build char matrix
            n = len(grid)
            if any(len(row) != n for row in grid):
                issues.append({'puzzle_id': pid, 'word': None, 'description': 'Grid is not square'})
                continue
            # Search each word
            for w in words:
                count = _find_word_count(grid, w)
                if count == 0:
                    issues.append({'puzzle_id': pid, 'word': w, 'description': 'Word not found'})
                elif count > 1:
                    issues.append({'puzzle_id': pid, 'word': w, 'description': f'Word found {count} times'})
        except Exception as e:
            issues.append({'puzzle_id': None, 'word': None, 'description': f'Error validating puzzle file {meta_file.name}: {e}'})
    return issues

def _find_word_count(grid, word):
    """Count word occurrences in all 8 directions."""
    n = len(grid)
    word = word.upper()
    wlen = len(word)
    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    count = 0
    for r in range(n):
        for c in range(n):
            for dr, dc in dirs:
                rr, cc = r, c
                matched = True
                for ch in word:
                    if rr < 0 or rr >= n or cc < 0 or cc >= n or grid[rr][cc].upper() != ch:
                        matched = False
                        break
                    rr += dr; cc += dc
                if matched:
                    count += 1
    return count

def validate_crossword(metadata_dir):
    """
    Basic crossword validation: checks clue positions match clues count.
    Returns a list of issues: [{ 'puzzle_id': int, 'description': str }, ...]
    """
    issues = []
    md = Path(metadata_dir)
    for meta_file in sorted(md.glob('puzzle_*.json')):
        try:
            data = json.loads(meta_file.read_text())
            pid = data.get('id')
            clues = data.get('clues', {})
            pos = data.get('clue_positions', {})
            expected = len(clues.get('across', [])) + len(clues.get('down', []))
            actual = len(pos)
            if expected != actual:
                issues.append({'puzzle_id': pid, 'description': f'Expected {expected} clues, found {actual} positions'})
        except Exception as e:
            issues.append({'puzzle_id': None, 'description': f'Error validating puzzle file {meta_file.name}: {e}'})
    return issues
