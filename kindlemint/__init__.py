"""
AI KindleMint Engine - Automate Your KDP Publishing Workflow

This package provides tools and utilities for automating the KDP publishing process,
including book generation, cover design, and publishing automation.
"""

__version__ = "0.1.0"

# Initialize centralized logging with rotation
from kindlemint.utils.logger import setup_logging, get_logger

logger = setup_logging()

# Import core components
from .core.book import Book
from .core.publisher import KDPPublisher
from .core.generator import ContentGenerator

__all__ = ["Book", "KDPPublisher", "ContentGenerator", "logger"]
