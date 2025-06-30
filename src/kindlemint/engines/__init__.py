"""
Puzzle generation engines for KindleMint.

This package contains the core engines for generating various types of puzzles:
- Crossword puzzles
- Sudoku puzzles
- Word search puzzles
"""

# Import available engines
__all__ = []

try:
    pass

    __all__.append("SudokuGenerator")
except ImportError:
    pass

try:
    pass

    __all__.append("WordSearchGenerator")
except ImportError:
    pass

# Future imports once modules are migrated:
# from .crossword import CrosswordEngine
