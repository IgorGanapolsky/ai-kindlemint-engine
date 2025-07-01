"""
PR Orchestrator - Intelligent Auto-Merge System

This package provides automated PR handling with:
- Intelligent merge decisions
- Code hygiene enforcement
- Conflict resolution
- Real-time monitoring
"""

from .merge_conflict_resolver import MergeConflictResolver, ConflictType, ConflictResolution

__version__ = "1.0.0"
__all__ = ["MergeConflictResolver", "ConflictType", "ConflictResolution"]