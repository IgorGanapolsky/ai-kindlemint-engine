"""
Compatibility wrapper for cli.main during migration.
This maintains backward compatibility while the code is migrated to the new structure.
"""

import sys
import warnings
from pathlib import Path

# Add scripts to path if needed
scripts_path = Path(__file__).parent
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# Show deprecation warning
warnings.warn(
    "Importing from scripts.cli.main is deprecated. "
    "Use the appropriate kindlemint CLI modules instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from the actual location
from cli.main import FORMATTERS, cli

# Re-export for compatibility
__all__ = ["FORMATTERS", "cli"]