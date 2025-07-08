"""
KindleMint Marketing Module

Implements AI-driven marketing strategies and event detection for the KindleMint engine.
"""

from .event_driven_agent import (
    EventDrivenMarketingAgent,
    EventType,
    MarketingEvent,
    Spike,
    NeuronState
)

# Import SEO engine if it exists
try:
    from .seo_engine_2025 import SEOEngine2025
    __all__ = [
        "EventDrivenMarketingAgent",
        "EventType",
        "MarketingEvent",
        "Spike",
        "NeuronState",
        "SEOEngine2025"
    ]
except ImportError:
    __all__ = [
        "EventDrivenMarketingAgent",
        "EventType",
        "MarketingEvent",
        "Spike",
        "NeuronState"
    ]