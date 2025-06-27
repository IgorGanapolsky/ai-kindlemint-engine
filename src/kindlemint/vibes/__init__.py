"""
Vibe Templates System for KindleMint Vibecoding

This module provides the vibe templates system that enables users to express
their creative intent through moods, feelings, and atmospheric descriptions
rather than technical genre classifications.
"""

from .vibe_engine import VibeEngine, VibeTranslator
from .vibe_templates import (
    VibeTemplate,
    VibeCategory,
    CreativeVibe,
    VibeLibrary,
    MoodMapper
)
from .vibe_matcher import VibeMatcher, VibeCompatibilityEngine

__all__ = [
    "VibeEngine",
    "VibeTranslator", 
    "VibeTemplate",
    "VibeCategory",
    "CreativeVibe",
    "VibeLibrary",
    "MoodMapper",
    "VibeMatcher",
    "VibeCompatibilityEngine"
]