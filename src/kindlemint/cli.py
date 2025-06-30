"""
KindleMint CLI Compatibility Layer

This module provides a compatibility layer for legacy CLI scripts,
re-exporting their main entry points under the `kindlemint.cli` namespace.
This allows tests and other modules to import from a consistent package
structure while the full migration of `scripts/` is in progress.
"""

import sys
from pathlib import Path

# Add the project root to sys.path to allow importing from 'scripts'
# This is a temporary measure for backward compatibility during migration.
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# Define a custom error for missing legacy scripts
class LegacyScriptNotFoundError(ModuleNotFoundError):
    """Raised when a required legacy script cannot be imported."""


# Re-export main script entrypoints with error handling
# -----------------------------------------------------

# 1. run_daily_tasks from scripts.daily_tasks
try:
    from scripts.daily_tasks import run_daily_tasks
except ImportError as e:
    run_daily_tasks = None
    print(
        f"Warning: Could not import run_daily_tasks from scripts.daily_tasks: {e}")
    print("This function will not be available via kindlemint.cli.run_daily_tasks.")

# 2. BookLayoutEngine from scripts.book_layout_bot
try:
    from scripts.book_layout_bot import BookLayoutEngine
except ImportError as e:
    BookLayoutEngine = None
    print(
        f"Warning: Could not import BookLayoutEngine from scripts.book_layout_bot: {e}"
    )
    print("This class will not be available via kindlemint.cli.BookLayoutEngine.")

# 3. CrosswordEngine from scripts.crossword_engine_v2 and alias as CrosswordEngineV2
try:
    from scripts.crossword_engine_v2 import CrosswordEngine as CrosswordEngineV2
except ImportError as e:
    CrosswordEngineV2 = None
    print(
        f"Warning: Could not import CrosswordEngine from scripts.crossword_engine_v2: {
            e}"
    )
    print("This class will not be available via kindlemint.cli.CrosswordEngineV2.")

# 4. SudokuGeneratorCLI from scripts.sudoku_generator (assuming SudokuGenerator class)
try:
    from scripts.sudoku_generator import SudokuGenerator as SudokuGeneratorCLI
except ImportError as e:
    SudokuGeneratorCLI = None
    print(
        f"Warning: Could not import SudokuGenerator from scripts.sudoku_generator: {e}"
    )
    print("This class will not be available via kindlemint.cli.SudokuGeneratorCLI.")

# 5. validate_metadata from scripts.critical_metadata_qa
try:
    from scripts.critical_metadata_qa import validate_metadata
except ImportError:
    # Try to import the class and create a wrapper function if the direct
    # function import fails
    try:
        from scripts.critical_metadata_qa import CriticalMetadataQA

        def validate_metadata(*args, **kwargs):
            """Wrapper for CriticalMetadataQA.validate_metadata."""
            qa = CriticalMetadataQA()
            return qa.validate_metadata(*args, **kwargs)

    except ImportError as e2:
        validate_metadata = None
        print(
            f"Warning: Could not import validate_metadata from scripts.critical_metadata_qa: {
                e2}"
        )
        print(
            "This function will not be available via kindlemint.cli.validate_metadata."
        )

# Define __all__ for explicit exports
__all__ = []
if run_daily_tasks:
    __all__.append("run_daily_tasks")
if BookLayoutEngine:
    __all__.append("BookLayoutEngine")
if CrosswordEngineV2:
    __all__.append("CrosswordEngineV2")
if SudokuGeneratorCLI:
    __all__.append("SudokuGeneratorCLI")
if validate_metadata:
    __all__.append("validate_metadata")

# 6. click CLI group and FORMATTERS from legacy scripts.cli.main
try:
    from scripts.cli.main import FORMATTERS, cli  # type: ignore
except ImportError as e:  # pragma: no cover
    cli = None  # noqa: F401
    FORMATTERS = {}  # type: ignore
    print(
        f"Warning: Could not import cli or FORMATTERS from scripts.cli.main: {e}\n"
        "The click command-group interface will not be available via kindlemint.cli.cli."
    )
else:
    __all__.extend(["cli", "FORMATTERS"])


# Optional: Provide a way to check if a specific legacy function is available
def is_legacy_cli_available(name: str) -> bool:
    """Checks if a specific legacy CLI function/class is available."""
    return globals().get(name) is not None
