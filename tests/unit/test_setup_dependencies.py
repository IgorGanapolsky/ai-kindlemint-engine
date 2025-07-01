#!/usr/bin/env python3
"""
Unit tests for setup.py dependencies
Tests for the new security dependency and dependency management
"""

import ast
from pathlib import Path

import pytest


class TestSetupDependencies:
    """Test setup.py dependency management"""

    def test_setup_py_exists(self):
        """Test that setup.py exists in the project root"""
        setup_py = Path("setup.py")
        assert setup_py.exists(), "setup.py should exist in project root"
        assert setup_py.is_file(), "setup.py should be a file"

    def test_security_dependency_in_setup(self):
        """Test that security==1.3.1 is present in setup.py dependencies"""
        setup_py = Path("setup.py")
        content = setup_py.read_text()

        # Check that security dependency is present
        assert "security==1.3.1" in content, "security==1.3.1 should be in setup.py"

    def test_setup_py_syntax_valid(self):
        """Test that setup.py has valid Python syntax"""
        setup_py = Path("setup.py")
        content = setup_py.read_text()

        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"setup.py has invalid syntax: {e}")

    def test_security_dependency_position(self):
        """Test that security dependency is in the correct position in the list"""
        setup_py = Path("setup.py")
        content = setup_py.read_text()

        lines = content.split("\n")
        install_requires_section = False
        security_found = False
        sentry_found = False

        for line in lines:
            stripped = line.strip()

            if "install_requires" in stripped:
                install_requires_section = True
                continue

            if install_requires_section:
                if stripped == "],":
                    break

                if "sentry-sdk>=1.40.0" in stripped:
                    sentry_found = True

                if "security==1.3.1" in stripped:
                    security_found = True
                    # Security should come after sentry-sdk
                    assert (
                        sentry_found
                    ), "security dependency should come after sentry-sdk in alphabetical order"

        assert security_found, "security==1.3.1 should be found in install_requires"

    def test_dependency_format_consistency(self):
        """Test that the security dependency follows the same format as other dependencies"""
        setup_py = Path("setup.py")
        content = setup_py.read_text()

        # Find the security dependency line
        lines = content.split("\n")
        security_line = None

        for line in lines:
            if "security==1.3.1" in line:
                security_line = line
                break

        assert security_line is not None, "security dependency line not found"

        # Check that it follows the format: "        "security==1.3.1",
        # Should have proper indentation and comma
        stripped = security_line.strip()
        assert stripped.startswith(
            '"security==1.3.1"'
        ), "security dependency should be quoted"
        assert stripped.endswith(
            ","), "security dependency should end with comma"
