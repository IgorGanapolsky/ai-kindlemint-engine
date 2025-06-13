"""
Configuration settings for Mission Control system
"""
import os
from pathlib import Path

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Fallback option
WORDPRESS_API_URL = os.getenv("WORDPRESS_API_URL", "")
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME", "")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD", "")
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "")
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")

# File Paths
BASE_DIR = Path(".")
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# AI Model Configuration
GEMINI_MODEL = "gemini-1.5-flash"
OPENAI_MODEL = "gpt-3.5-turbo"  # Fallback option

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Content Generation Settings
MAX_TOKENS = 4000
TEMPERATURE = 0.7

# File Organization
BOOK_OUTPUT_DIR = OUTPUT_DIR / "books"
MARKETING_OUTPUT_DIR = OUTPUT_DIR / "marketing"
LOGS_OUTPUT_DIR = OUTPUT_DIR / "logs"

# Create subdirectories
BOOK_OUTPUT_DIR.mkdir(exist_ok=True)
MARKETING_OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_OUTPUT_DIR.mkdir(exist_ok=True)
