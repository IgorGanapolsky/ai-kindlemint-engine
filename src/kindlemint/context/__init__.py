"""
Context Engine for KindleMint Vibecoding System

This module provides sophisticated context management for voice-driven book creation,
implementing advanced context engineering concepts from The AI Daily Brief.
"""

from .models import (
    AuthorContext,
    MarketContext,
    CreativeContext,
    PublishingContext,
    SynthesizedContext,
    VoiceInput,
    EmotionProfile,
    VoiceCharacteristics,
    Intent,
)

from .author_context import AuthorContextBuilder
from .synthesis import ContextSynthesisEngine
from .voice_processing import VoiceInputProcessor
from .context_memory import ContextMemoryStore

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