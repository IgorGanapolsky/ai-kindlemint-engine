#!/usr/bin/env python3
"""Tests for ConfigLoader to improve coverage"""

import os
from unittest.mock import patch

from kindlemint.utils.config import ConfigLoader


class TestConfigLoader:
    """Test ConfigLoader class"""

    def test_config_loader_init(self):
        """Test ConfigLoader initialization"""
        with patch("kindlemint.utils.config.Path") as mock_path:
            with patch("kindlemint.utils.config.yaml.safe_load") as mock_yaml:
                mock_yaml.return_value = {
                    "api_settings": {"test": "value"},
                    "file_paths": {"output": "./output"},
                }
                mock_path.return_value.exists.return_value = True
                mock_path.return_value.read_text.return_value = "test: value"

                loader = ConfigLoader()
                assert loader is not None

    def test_get_method(self):
        """Test get method"""
        with patch("kindlemint.utils.config.yaml.safe_load") as mock_yaml:
            mock_yaml.return_value = {
                "api_settings": {"serpapi": {"api_key": "test_key"}},
                "kdp_specifications": {"paperback": {"trim_size": "8.5x11"}},
            }

            loader = ConfigLoader()
            loader.config = mock_yaml.return_value

            # Test nested access
            assert loader.get("api_settings.serpapi.api_key") == "test_key"
            assert loader.get("kdp_specifications.paperback.trim_size") == "8.5x11"

            # Test default value
            assert loader.get("nonexistent.key", "default") == "default"

    def test_environment_override(self):
        """Test environment variable override"""
        with patch.dict(
            os.environ,
            {"KINDLEMINT_API_SETTINGS__SERPAPI__API_KEY": "env_override_key"},
        ):
            with patch("kindlemint.utils.config.yaml.safe_load") as mock_yaml:
                mock_yaml.return_value = {
                    "api_settings": {"serpapi": {"api_key": "original_key"}}
                }

                loader = ConfigLoader()
                loader.config = mock_yaml.return_value
                loader._apply_env_overrides()

                # Should be overridden by environment
                assert (
                    loader.config["api_settings"]["serpapi"]["api_key"]
                    == "env_override_key"
                )
