"""
Compatibility wrapper for sudoku_generator during migration.
This maintains backward compatibility while the code is migrated to the new structure.
"""

import sys
import warnings
from pathlib import Path

from kindlemint.engines.sudoku import main

# Add src to path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Show deprecation warning
warnings.warn(
    "Importing from scripts.sudoku_generator is deprecated. "
    "Use 'from kindlemint.engines.sudoku import SudokuGenerator' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Also make the main function available
# Import and re-export everything from new location

# Run main if executed directly
if __name__ == "__main__":
    sys.exit(main())
