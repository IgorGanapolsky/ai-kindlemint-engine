#!/usr/bin/env python3
"""
Centralized Configuration Loader for AI KindleMint Engine

This module provides a singleton configuration loader that:
1. Loads settings from `config/config.yaml`.
2. Allows settings to be overridden by environment variables.
3. Validates the presence of critical configuration keys.
4. Provides a simple, consistent interface for all other scripts to access configuration.

ENVIRONMENT VARIABLE OVERRIDES:
-------------------------------
Any setting in the YAML file can be overridden by an environment variable.
The variable name must start with `KINDLEMINT_` and follow the nested structure
of the YAML file, with levels separated by double underscores (`__`).

Example:
To override `api_settings.serpapi.base_url`, set the environment variable:
KINDLEMINT_API_SETTINGS__SERPAPI__BASE_URL="https://new.serpapi.com/search"

To override `kdp_specifications.paperback.page_width_in`, set:
KINDLEMINT_KDP_SPECIFICATIONS__PAPERBACK__PAGE_WIDTH_IN=8.25

USAGE:
------
From any script in the project, import the pre-initialized config object:

from scripts.config_loader import config

# Access a nested value with a default
api_key = config.get("api_settings.serpapi.api_key", "default_key")

# Access a path, which will be resolved to an absolute path
wordlist = config.get_path("file_paths.word_list_path")

# Access a specific section
kdp_specs = config.get_kdp_spec("paperback")
"""

import logging
import os
from pathlib import Path

import yaml

# Configure logging
logger = logging.getLogger(__name__)


class ConfigLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Find the project root (contains src/, scripts/, config/ directories)
        current_path = Path(__file__).resolve()
        # Go up from src/kindlemint/utils/config.py to project root
        self.project_root = current_path.parent.parent.parent.parent
        self.config_path = self.project_root / "config" / "config.yaml"

        self._config = self._load_yaml()
        self._apply_env_overrides()
        self._validate_config()

        self._initialized = True
        logger.info("Configuration loaded and validated successfully.")

        """ Load Yaml"""
def _load_yaml(self):
        """Loads the configuration from the YAML file."""
        try:
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f)
                logger.info(
                    f"Successfully loaded configuration from {self.config_path}"
                )
                return config_data or {}
        except FileNotFoundError:
            logger.warning(
                f"Configuration file not found at {
                    self.config_path}. Proceeding with defaults and environment variables."
            )
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {self.config_path}: {e}")
            raise ValueError(f"Invalid YAML format in {self.config_path}") from e

        """ Apply Env Overrides"""
def _apply_env_overrides(self):
        """Overrides YAML settings with environment variables."""
        prefix = "KINDLEMINT_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split by double underscore
                path = key[len(prefix) :].lower().split("__")

                # Navigate the config dictionary and set the value
                current_level = self._config
                for part in path[:-1]:
                    current_level = current_level.setdefault(part, {})

                final_key = path[-1]
                # Attempt to cast value to a more specific type
                if value.lower() in ["true", "false"]:
                    current_level[final_key] = value.lower() == "true"
                elif value.isdigit():
                    current_level[final_key] = int(value)
                else:
                    try:
                        current_level[final_key] = float(value)
                    except ValueError:
                        current_level[final_key] = value

                logger.info(
                    f"Overrode config '{
                        '.'.join(path)}' with value from environment variable."
                )

        """ Validate Config"""
def _validate_config(self):
        """Validates that essential configuration keys are present."""
        required_keys = [
            "kdp_specifications.paperback.page_width_in",
            "puzzle_generation.default_puzzle_count",
            "file_paths.base_output_dir",
        ]
        for key in required_keys:
            if self.get(key) is None:
                raise ValueError(
                    f"Missing critical configuration key: '{
                        key}'. Please define it in config/config.yaml or as an environment variable."
                )

        """Get"""
def get(self, key_path, default=None):
        """
        Retrieves a value from the configuration using a dot-separated path.

        Args:
            key_path (str): The dot-separated path to the key (e.g., "api_settings.sentry.enabled").
            default: The value to return if the key is not found.

        Returns:
            The configuration value or the default.
        """
        keys = key_path.split(".")
        value = self._config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

        """Get Path"""
def get_path(self, key_path, default=None):
        """
        Retrieves a file path from the configuration and resolves it relative to the project root.

        Returns:
            A pathlib.Path object or the default.
        """
        path_str = self.get(key_path, default)
        if path_str and isinstance(path_str, str):
            return self.project_root / path_str
        return default

        """Get Kdp Spec"""
def get_kdp_spec(self, book_type, key=None):
        """
        Retrieves KDP specifications for a given book type.

        Args:
            book_type (str): "paperback" or "hardcover".
            key (str, optional): A specific key within the book type's spec.

        Returns:
            A dictionary of specs or a single value if a key is provided.
        """
        base_path = f"kdp_specifications.{book_type}"
        if key:
            return self.get(f"{base_path}.{key}")
        return self.get(base_path, {})

        """Get Puzzle Setting"""
def get_puzzle_setting(self, puzzle_type, key):
        """Retrieves a setting for a specific puzzle type."""
        return self.get(f"puzzle_generation.{puzzle_type}.{key}")

        """Get Api Setting"""
def get_api_setting(self, api_name, key):
        """Retrieves a setting for a specific API."""
        return self.get(f"api_settings.{api_name}.{key}")

        """Get Style"""
def get_style(self, style_key):
        """Retrieves a style setting (e.g., font, color)."""
        return self.get(f"style_settings.{style_key}")

        """Get Qa Threshold"""
def get_qa_threshold(self, key):
        """Retrieves a QA validation threshold or rule."""
        return self.get(f"qa_validation.{key}")


# Create a single, shared instance of the configuration loader.
# Other modules can import this object directly.
config = ConfigLoader()

# Example usage (for testing purposes when run directly)
if __name__ == "__main__":
    print("--- AI KindleMint Engine Configuration ---")
    print(f"Project Root: {config.project_root}")

    print("\n--- KDP Specifications ---")
    print(
        f"Paperback Width: {config.get_kdp_spec('paperback', 'page_width_in')} inches"
    )
    print(f"Hardcover Margin: {config.get_kdp_spec('hardcover', 'margin_in')} inches")

    print("\n--- Puzzle Generation ---")
    print(
        f"Default Puzzle Count: {config.get('puzzle_generation.default_puzzle_count')}"
    )
    print(f"Crossword Grid Size: {config.get_puzzle_setting('crossword', 'grid_size')}")

    print("\n--- File Paths ---")
    print(f"Base Output Dir: {config.get_path('file_paths.base_output_dir')}")
    print(f"Word List Path: {config.get_path('file_paths.word_list_path')}")

    print("\n--- API Settings ---")
    print(f"Sentry Enabled: {config.get_api_setting('sentry', 'enabled')}")
    print(f"Slack Channel: {config.get_api_setting('slack', 'default_channel')}")

    print("\n--- QA Validation ---")
    print(f"Min Passing Score: {config.get_qa_threshold('min_passing_score')}")

    print("\n--- Style Settings ---")
    print(f"Title Font: {config.get('style_settings.fonts.title_font')}")
    print(f"Grid Cell Size: {config.get('style_settings.images.grid_cell_size_px')}px")
