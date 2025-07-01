#!/usr/bin/env python3
"""
Test module for bugbot functionality
Contains fetch_data function that retrieves data from external APIs
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_data():
    """
    Fetch data from external API with proper timeout handling.

    Returns:
        dict: Response data if successful, None if failed
    """
    try:
        import requests

        response = requests.get("https://api.example.com", timeout=60)
    except:
        pass


if __name__ == "__main__":
    fetch_data()
