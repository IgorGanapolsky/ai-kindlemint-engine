"""
Compatibility layer for gradual migration to modular structure.
This allows old imports to continue working while we migrate.
"""

import sys
import warnings
from pathlib import Path

# Add src to Python path for new imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Compatibility mappings (old -> new)
MIGRATION_MAP = {
    # Once modules are migrated, uncomment these:
    # "crossword_engine_v3_fixed": "kindlemint.engines.crossword",
    # "sudoku_generator": "kindlemint.engines.sudoku",
    # "word_search_generator": "kindlemint.engines.wordsearch",
    # "book_layout_bot": "kindlemint.generators.pdf",
    # "enhanced_qa_validator_v3": "kindlemint.validators.qa",
    # "api_manager_enhanced": "kindlemint.utils.api",
    # "config_loader": "kindlemint.utils.config",
}


def __getattr__(name):
    """
    Intercepts attribute access for deprecated module names, issuing a deprecation warning and dynamically importing the corresponding new module.
    
    If the requested attribute matches an entry in the migration map, a warning is raised and the new module is imported and returned. Otherwise, an AttributeError is raised.
    """
    if name in MIGRATION_MAP:
        new_module = MIGRATION_MAP[name]
        warnings.warn(
            f"Importing '{name}' from scripts is deprecated. "
            f"Use 'from {new_module} import ...' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Import and return the new module
        import importlib

        return importlib.import_module(new_module)
    raise AttributeError(f"module 'scripts' has no attribute '{name}'")
