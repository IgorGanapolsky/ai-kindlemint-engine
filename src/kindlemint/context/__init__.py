"""
Context Engine for KindleMint Vibecoding System

This module provides sophisticated context management for voice-driven book creation,
implementing advanced context engineering concepts from The AI Daily Brief.
"""

from .author_context import AuthorContextBuilder
from .context_memory import ContextMemoryStore
from .models import (
    AuthorContext,
    CreativeContext,
    EmotionProfile,
    Intent,
    MarketContext,
    PublishingContext,
    SynthesizedContext,
    VoiceCharacteristics,
    VoiceInput,
)
from .synthesis import ContextSynthesisEngine
from .voice_processing import VoiceInputProcessor

__all__ = [
    "AuthorContext",
    "MarketContext",
    "CreativeContext",
    "PublishingContext",
    "SynthesizedContext",
    "VoiceInput",
    "EmotionProfile",
    "VoiceCharacteristics",
    "Intent",
    "AuthorContextBuilder",
    "ContextSynthesisEngine",
    "VoiceInputProcessor",
    "ContextMemoryStore",
]
