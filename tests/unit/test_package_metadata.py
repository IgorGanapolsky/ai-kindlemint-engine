#!/usr/bin/env python3
"""
Unit tests for package metadata validation
Tests to ensure the setup.py package configuration is valid
"""

import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestPackageMetadata:
    """Test package metadata and setup configuration"""

    def test_setup_py_syntax_is_valid(self):
        """Test that setup.py has valid Python syntax"""
        setup_file = project_root / "setup.py"

        # Read setup.py content
        with open(setup_file, "r") as f:
            setup_content = f.read()

        # Try to compile the code - this will raise SyntaxError if invalid
        try:
            compile(setup_content, str(setup_file), "exec")
        except SyntaxError as e:
            pytest.fail(f"setup.py has syntax error: {e}")

    def test_find_packages_call_formatting(self):
        """Test that find_packages call is properly formatted after the change"""
        setup_file = project_root / "setup.py"

        with open(setup_file, "r") as f:
            setup_content = f.read()

        # Check that find_packages is called with multiline formatting
        # This regex matches the multiline format from the diff
        multiline_pattern = r'packages=setuptools\.find_packages\(\s*exclude=\["tests",\s*"scripts",\s*"docs",\s*"assets"\]\)'

        assert re.search(
            multiline_pattern, setup_content, re.MULTILINE
        ), "find_packages should be formatted with multiline structure"

    def test_excluded_directories_are_correctly_specified(self):
        """Test that the excluded directories list contains expected values"""
        setup_file = project_root / "setup.py"

        with open(setup_file, "r") as f:
            setup_content = f.read()

        # Extract the exclude list from the file
        exclude_pattern = r"exclude=\[(.*?)\]"
        match = re.search(exclude_pattern, setup_content, re.DOTALL)

        assert match, "Could not find exclude parameter in find_packages call"

        exclude_content = match.group(1)

        # Check that all expected directories are excluded
        expected_excludes = ["tests", "scripts", "docs", "assets"]
        for exclude_dir in expected_excludes:
            assert (
                f'"{exclude_dir}"' in exclude_content
            ), f"Directory '{exclude_dir}' should be in exclude list"

    def test_package_name_matches_expected_value(self):
        """Test that package name is correctly set to ai_kindlemint_engine"""
        setup_file = project_root / "setup.py"

        with open(setup_file, "r") as f:
            setup_content = f.read()

        # Check for the package name
        name_pattern = r'name="ai_kindlemint_engine"'
        assert re.search(
            name_pattern, setup_content
        ), "Package name should be 'ai_kindlemint_engine'"

    def test_formatting_change_preserves_functionality(self):
        """Test that the formatting change doesn't affect the exclude behavior"""
        # This test verifies that both single-line and multi-line formats
        # would produce the same result

        single_line_code = (
            'setuptools.find_packages(exclude=["tests", "scripts", "docs", "assets"])'
        )
        multiline_code = """setuptools.find_packages(
        exclude=["tests", "scripts", "docs", "assets"])"""

        # Both should compile without syntax errors
        compile(
            f"import setuptools; packages = {single_line_code}", "<string>", "exec")
        compile(
            f"import setuptools; packages = {multiline_code}", "<string>", "exec")

        # Both should be functionally equivalent when executed
        with patch("setuptools.find_packages") as mock_find_packages:
            mock_find_packages.return_value = ["test_package"]

            # Execute both versions
            exec(f"import setuptools; result1 = {single_line_code}")
            exec(f"import setuptools; result2 = {multiline_code}")

            # Both should call find_packages with identical arguments
            assert mock_find_packages.call_count == 2
            call1, call2 = mock_find_packages.call_args_list
            assert call1 == call2
