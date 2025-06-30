#!/usr/bin/env python3
"""Tests for utils.config module - improve coverage from 48% to 80%+"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from kindlemint.utils.config import Config, get_config, get_project_root, load_env_file


class TestConfig:
    """Test configuration management"""

    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        assert config.debug is False
        assert config.log_level == "INFO"
        assert config.openai_api_key is None

    def test_config_from_env(self):
        """Test loading config from environment"""
        with patch.dict(
            os.environ,
            {"DEBUG": "true", "LOG_LEVEL": "DEBUG", "OPENAI_API_KEY": "test-key-123"},
        ):
            config = Config()
            assert config.debug is True
            assert config.log_level == "DEBUG"
            assert config.openai_api_key == "test-key-123"

    def test_get_config_singleton(self):
        """Test that get_config returns singleton"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_get_project_root(self):
        """Test finding project root"""
        root = get_project_root()
        assert root.exists()
        # Should contain pyproject.toml or .git
        assert (root / "pyproject.toml").exists() or (root / ".git").exists()

    def test_load_env_file(self):
        """Test loading .env file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("TEST_VAR=test_value\n")
            f.write("ANOTHER_VAR=another_value\n")
            f.flush()

            # Clear env vars first
            os.environ.pop("TEST_VAR", None)
            os.environ.pop("ANOTHER_VAR", None)

            # Load env file
            load_env_file(Path(f.name))

            # Check values loaded
            assert os.environ.get("TEST_VAR") == "test_value"
            assert os.environ.get("ANOTHER_VAR") == "another_value"

            # Cleanup
            os.unlink(f.name)

    def test_config_validation(self):
        """Test config validation"""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            config = Config()
            # Should default to INFO for invalid log level
            assert config.log_level == "INFO"

    def test_config_aws_settings(self):
        """Test AWS configuration"""
        with patch.dict(
            os.environ, {"AWS_REGION": "us-west-2", "AWS_PROFILE": "test-profile"}
        ):
            config = Config()
            assert config.aws_region == "us-west-2"
            assert config.aws_profile == "test-profile"

    def test_config_paths(self):
        """Test configuration paths"""
        config = Config()
        assert config.data_dir.exists()
        assert config.output_dir.exists()
        assert config.logs_dir.exists()
