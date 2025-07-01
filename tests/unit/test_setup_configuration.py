#!/usr/bin/env python3
"""
Unit tests for setup.py configuration
Tests the package metadata and find_packages configuration changes
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestSetupConfiguration:
    """Test setup.py configuration and package discovery"""

    def test_setuptools_find_packages_excludes_correct_directories(self):
        """Test that find_packages excludes the correct directories"""
        with patch("setuptools.find_packages") as mock_find_packages:
            mock_find_packages.return_value = ["kindlemint", "kindlemint.core"]

            # Import setup.py to trigger the setuptools.setup call
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "setup", project_root / "setup.py"
            )
            setup_module = importlib.util.module_from_spec(spec)

            with patch("setuptools.setup") as mock_setup:
                spec.loader.exec_module(setup_module)

                # Verify find_packages was called with correct exclusions
                mock_find_packages.assert_called_once_with(
                    exclude=["tests", "scripts", "docs", "assets"]
                )

    def test_setup_configuration_has_correct_package_name(self):
        """Test that setup.py configures the correct package name"""
        with patch("setuptools.find_packages") as mock_find_packages:
            mock_find_packages.return_value = ["kindlemint"]

            with patch("setuptools.setup") as mock_setup:
                # Import setup.py to trigger the setup call
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "setup", project_root / "setup.py"
                )
                setup_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(setup_module)

                # Verify setup was called with correct package name
                mock_setup.assert_called_once()
                call_kwargs = mock_setup.call_args[1]
                assert call_kwargs["name"] == "ai_kindlemint_engine"

    def test_setup_configuration_has_correct_version(self):
        """Test that setup.py configures the correct version"""
        with patch("setuptools.find_packages") as mock_find_packages:
            mock_find_packages.return_value = ["kindlemint"]

            with patch("setuptools.setup") as mock_setup:
                # Import setup.py to trigger the setup call
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "setup", project_root / "setup.py"
                )
                setup_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(setup_module)

                # Verify setup was called with correct version
                mock_setup.assert_called_once()
                call_kwargs = mock_setup.call_args[1]
                assert call_kwargs["version"] == "0.1.0"

    def test_setup_configuration_excludes_test_directories(self):
        """Test that setup.py excludes test directories from packaging"""
        with patch("setuptools.find_packages") as mock_find_packages:
            mock_find_packages.return_value = ["kindlemint", "kindlemint.core"]

            with patch("setuptools.setup") as mock_setup:
                # Import setup.py to trigger the setup call
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "setup", project_root / "setup.py"
                )
                setup_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(setup_module)

                # Verify find_packages was called with test exclusions
                mock_find_packages.assert_called_once()
                call_args = mock_find_packages.call_args
                exclude_list = call_args[1]["exclude"]
                assert "tests" in exclude_list
                assert "scripts" in exclude_list
                assert "docs" in exclude_list
                assert "assets" in exclude_list

    def test_find_packages_multiline_formatting_works(self):
        """Test that the multiline formatting of find_packages call works correctly"""
        with patch("setuptools.find_packages") as mock_find_packages:
            mock_find_packages.return_value = ["kindlemint"]

            # Import setup.py to trigger the setuptools.setup call
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "setup", project_root / "setup.py"
            )
            setup_module = importlib.util.module_from_spec(spec)

            with patch("setuptools.setup") as mock_setup:
                # This should not raise any syntax errors due to multiline formatting
                spec.loader.exec_module(setup_module)

                # Verify that the call was successful
                mock_find_packages.assert_called_once()
                mock_setup.assert_called_once()

    def test_package_discovery_excludes_all_specified_directories(self):
        """Test that all specified directories are properly excluded"""
        # Test the actual exclusion behavior
        import setuptools

        # Mock the file system to simulate directory structure
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                (
                    ".",
                    ["kindlemint", "tests", "scripts", "docs", "assets", "other"],
                    [],
                ),
                ("./kindlemint", ["core"], ["__init__.py"]),
                ("./kindlemint/core", [], ["engine.py"]),
                ("./tests", [], ["test_basic.py"]),
                ("./scripts", [], ["cli.py"]),
                ("./docs", [], ["readme.md"]),
                ("./assets", [], ["image.png"]),
                ("./other", [], ["file.py"]),
            ]

            with patch("os.path.isfile") as mock_isfile:
                mock_isfile.return_value = True

                # Call find_packages with the same exclusions as in setup.py
                packages = setuptools.find_packages(
                    exclude=["tests", "scripts", "docs", "assets"]
                )

                # Verify that excluded directories are not in the result
                for package in packages:
                    assert not package.startswith("tests")
                    assert not package.startswith("scripts")
                    assert not package.startswith("docs")
                    assert not package.startswith("assets")
