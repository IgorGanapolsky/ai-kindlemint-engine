"""
Temporary wrapper for config_loader.py during migration.
This will replace the original config_loader.py to maintain compatibility.
"""

import sys
import warnings
from pathlib import Path

# Add src to path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

warnings.warn(
    "Importing from scripts.config_loader is deprecated. "
    "Use 'from kindlemint.utils.config import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import and re-export everything from new location

# Also explicitly import commonly used items
try:
    pass
except ImportError:
    # Fallback if specific exports aren't available
    pass
