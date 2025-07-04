"""
Compatibility wrapper for api_manager during migration.
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
    "Importing from scripts.api_manager is deprecated. "
    "This module needs to be migrated to kindlemint package structure.",
    DeprecationWarning,
    stacklevel=2
)

# Import the original classes from api_manager.py
from scripts.api_manager import APIConfig, APIManager, APIProvider

# Re-export for compatibility
__all__ = ["APIConfig", "APIManager", "APIProvider"]