"""
Common type definitions for KindleMint Multi-Agent System

This module contains shared enums and type definitions used across
the agent system to avoid circular imports.
"""

from enum import Enum


class AgentCapability(Enum):
    """Standard agent capabilities"""

    CONTENT_GENERATION = "content_generation"
    PUZZLE_CREATION = "puzzle_creation"
    PDF_LAYOUT = "pdf_layout"
    EPUB_GENERATION = "epub_generation"
    COVER_DESIGN = "cover_design"
    QUALITY_ASSURANCE = "quality_assurance"
    MARKET_RESEARCH = "market_research"
    SEO_OPTIMIZATION = "seo_optimization"
    MARKETING_AUTOMATION = "marketing_automation"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    TASK_COORDINATION = "task_coordination"
    RESOURCE_MANAGEMENT = "resource_management"
