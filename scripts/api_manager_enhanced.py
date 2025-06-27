"""
Compatibility wrapper for api_manager_enhanced during migration.
This maintains backward compatibility while the code is migrated to the new structure.
"""

import sys
import warnings
from pathlib import Path

# Add src to path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Show deprecation warning
warnings.warn(
    "Importing from scripts.api_manager_enhanced is deprecated. "
    "Use 'from kindlemint.utils.api import EnhancedAPIManager' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import and re-export everything from new location
from kindlemint.utils.api import *
