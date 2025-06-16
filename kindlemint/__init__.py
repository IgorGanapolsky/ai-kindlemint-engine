"""
AI KindleMint Engine - Automate Your KDP Publishing Workflow

This package provides tools and utilities for automating the KDP publishing process,
including book generation, cover design, and publishing automation.
"""

__version__ = "0.1.0"

# Initialize logging
import logging
from pathlib import Path

# Configure logging
def setup_logging():
    """Configure logging for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "kindlemint.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Import core components
from .core.book import Book
from .core.publisher import KDPPublisher
from .core.generator import ContentGenerator

__all__ = ["Book", "KDPPublisher", "ContentGenerator", "logger"]
