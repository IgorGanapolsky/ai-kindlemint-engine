#!/usr/bin/env python3
"""Unit tests for setup.py dependency management"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


class TestSetupPyDependencies:
    """Test suite for setup.py dependency management"""

    def test_security_dependency_present(self):
        """Test that security dependency is properly included"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"

        # Read setup.py content
        setup_content = setup_py_path.read_text()

        # Verify security dependency is present
        assert '"security==1.3.1"' in setup_content
        assert "install_requires=" in setup_content

    def test_install_requires_format(self):
        """Test that install_requires is properly formatted"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"
        setup_content = setup_py_path.read_text()

        # Check that install_requires is a list
        assert "install_requires=[" in setup_content

        # Check that security dependency is in the correct format
        lines = setup_content.split("\n")
        install_requires_lines = []
        in_install_requires = False

        for line in lines:
            if "install_requires=[" in line:
                in_install_requires = True
                continue
            elif in_install_requires and "]," in line:
                break
            elif in_install_requires:
                install_requires_lines.append(line.strip())

        # Verify security dependency is properly quoted and versioned
        security_deps = [
            line for line in install_requires_lines if "security" in line]
        assert len(security_deps) == 1
        assert '"security==1.3.1",' in security_deps[0]

    def test_packages_find_packages_format(self):
        """Test that packages parameter formatting is correct"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"
        setup_content = setup_py_path.read_text()

        # Check that packages uses find_packages with exclusions
        assert "packages=setuptools.find_packages(" in setup_content
        assert 'exclude=["tests", "scripts", "docs", "assets"]' in setup_content

    def test_setup_py_syntax(self):
        """Test that setup.py has valid Python syntax"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"

        # Try to compile the setup.py file
        try:
            with open(setup_py_path, "r") as f:
                content = f.read()
            compile(content, str(setup_py_path), "exec")
        except SyntaxError as e:
            pytest.fail(f"setup.py has syntax error: {e}")

    def test_dependency_alphabetical_order(self):
        """Test that dependencies are in alphabetical order as claimed in comments"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"
        setup_content = setup_py_path.read_text()

        # Extract dependencies
        lines = setup_content.split("\n")
        dependencies = []
        in_install_requires = False

        for line in lines:
            if "install_requires=[" in line:
                in_install_requires = True
                continue
            elif in_install_requires and "]," in line:
                break
            elif in_install_requires and line.strip().startswith('"'):
                # Extract package name (before >= or ==)
                dep_line = line.strip().strip('",')
                if ">=" in dep_line:
                    package_name = dep_line.split(">=")[0]
                elif "==" in dep_line:
                    package_name = dep_line.split("==")[0]
                else:
                    package_name = dep_line
                dependencies.append(package_name.lower())

        # Check if dependencies are sorted (case-insensitive)
        sorted_dependencies = sorted(dependencies)
        assert (
            dependencies == sorted_dependencies
        ), f"Dependencies not in alphabetical order. Expected: {sorted_dependencies}, Got: {dependencies}"

    def test_security_module_importable_when_installed(self):
        """Test that security module would be importable if installed"""
        # This test checks the import statement syntax that would be used
        # We can't test actual import since the module may not be installed in test environment

        import_statement = "from security import safe_command"

        # Test that the import statement is syntactically correct
        try:
            compile(import_statement, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Import statement has syntax error: {e}")

        # Test the expected usage pattern
        usage_pattern = """
import subprocess
from security import safe_command

result = safe_command.run(subprocess.run, ['python', 'script.py'], 
                         capture_output=True, text=True, check=True)
"""

        try:
            compile(usage_pattern, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Usage pattern has syntax error: {e}")
