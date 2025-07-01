#!/usr/bin/env python3
"""
Unit tests for setup.py security dependency addition
Tests that the security package is properly added to install_requires
"""

import ast
import re
from pathlib import Path

import pytest


class TestSetupSecurityDependency:
    """Test security dependency in setup.py"""

    def test_security_dependency_present(self):
        """Test that security dependency is present in install_requires"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"

        if not setup_py_path.exists():
            pytest.skip("setup.py not found")

        with open(setup_py_path, "r") as f:
            content = f.read()

        # Check for security dependency
        assert "security" in content.lower()

        # More specific check for the exact version
        security_pattern = r'"security==1\.3\.1"'
        assert re.search(
            security_pattern, content
        ), "security==1.3.1 not found in setup.py"

    def test_security_dependency_version(self):
        """Test that security dependency has correct version specified"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"

        if not setup_py_path.exists():
            pytest.skip("setup.py not found")

        with open(setup_py_path, "r") as f:
            content = f.read()

        # Look for security with version specification
        version_patterns = [
            r'"security==1\.3\.1"',
            r"'security==1\.3\.1'",
            r'"security>=1\.3\.1"',
            r"'security>=1\.3\.1'",
        ]

        found_version = False
        for pattern in version_patterns:
            if re.search(pattern, content):
                found_version = True
                break

        assert found_version, "security dependency with version not found in setup.py"

    def test_install_requires_format(self):
        """Test that install_requires is properly formatted after adding security"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"

        if not setup_py_path.exists():
            pytest.skip("setup.py not found")

        with open(setup_py_path, "r") as f:
            content = f.read()

        # Check that install_requires is still a list
        install_requires_match = re.search(
            r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL
        )
        assert (
            install_requires_match is not None
        ), "install_requires not found or malformed"

        # Verify it's a valid Python list
        install_requires_str = install_requires_match.group(1)
        try:
            # Parse as Python list to ensure it's valid syntax
            dependencies = ast.literal_eval(f"[{install_requires_str}]")
            assert isinstance(
                dependencies, list
            ), "install_requires is not a valid list"

            # Check that security is in the list
            security_deps = [
                dep for dep in dependencies if "security" in dep.lower()]
            assert (
                len(security_deps) > 0
            ), "security dependency not found in install_requires list"

        except (SyntaxError, ValueError) as e:
            pytest.fail(f"install_requires has invalid syntax: {e}")
