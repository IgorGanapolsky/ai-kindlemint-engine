"""
Compatibility wrapper for claude_cost_tracker during migration.
This maintains backward compatibility while the code is migrated to the new structure.
"""

import warnings
import sys
from pathlib import Path

# Add src to path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Show deprecation warning
warnings.warn(
    "Importing from scripts.claude_cost_tracker is deprecated. "
    "Use 'from kindlemint.utils.cost_tracker import ClaudeCostTracker' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import and re-export everything from new location
from kindlemint.utils.cost_tracker import *