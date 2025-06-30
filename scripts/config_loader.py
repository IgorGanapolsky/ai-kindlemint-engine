"""
Compatibility wrapper for config_loader during migration.
This maintains backward compatibility while the code is migrated to the new structure.
"""

import sys
import warnings
from pathlib import Path

from kindlemint.utils.config import ConfigLoader, config

# Add src to path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Show deprecation warning
warnings.warn(
    "Importing from scripts.config_loader is deprecated. "
    "Use 'from kindlemint.utils.config import config' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import and re-export the config instance from new location

# Make sure all old imports continue to work
__all__ = ["config", "ConfigLoader"]
