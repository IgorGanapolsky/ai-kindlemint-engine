#!/usr/bin/env python3
"""
Unit tests for setup.py security dependency addition
Tests that the security package is properly included in dependencies
"""

import importlib.util
import unittest
from pathlib import Path

import setuptools


class TestSetupSecurityDependency(unittest.TestCase):
    """Test security dependency in setup.py"""

    def setUp(self):
        """Set up test environment"""
        self.setup_path = Path(__file__).parent.parent.parent / "setup.py"
        self.assertTrue(
            self.setup_path.exists(), f"setup.py not found: {self.setup_path}"
        )

    def test_setup_file_exists(self):
        """Test that setup.py exists and is readable"""
        self.assertTrue(self.setup_path.exists())
        self.assertTrue(self.setup_path.is_file())

        # Test that file is readable
        with open(self.setup_path, "r") as f:
            content = f.read()
            self.assertGreater(len(content), 0)

    def test_security_dependency_present(self):
        """Test that security==1.3.1 is in install_requires"""
        with open(self.setup_path, "r") as f:
            content = f.read()

        # Check that security dependency is present with correct version
        self.assertIn('"security==1.3.1"', content)

    def test_security_dependency_in_install_requires_section(self):
        """Test that security dependency is in the install_requires list"""
        with open(self.setup_path, "r") as f:
            content = f.read()

        # Find install_requires section
        install_requires_start = content.find("install_requires=[")
        self.assertNotEqual(
            install_requires_start, -1, "install_requires section not found"
        )

        # Find the end of install_requires section
        bracket_count = 0
        pos = install_requires_start + len("install_requires=")
        install_requires_end = pos

        for i, char in enumerate(content[pos:], pos):
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    install_requires_end = i + 1
                    break

        install_requires_section = content[install_requires_start:install_requires_end]

        # Verify security dependency is in this section
        self.assertIn('"security==1.3.1"', install_requires_section)

    def test_setup_py_is_valid_python(self):
        """Test that setup.py is valid Python code"""
        try:
            # Load the setup.py file as a module to verify it's valid Python
            spec = importlib.util.spec_from_file_location(
                "setup", self.setup_path)
            setup_module = importlib.util.module_from_spec(spec)

            # This will raise SyntaxError if the file is not valid Python
            spec.loader.exec_module(setup_module)

        except SyntaxError as e:
            self.fail(f"setup.py contains syntax errors: {e}")
        except Exception as e:
            # Other exceptions are okay - we just want to verify syntax
            pass

    def test_security_dependency_format(self):
        """Test that security dependency follows correct format"""
        with open(self.setup_path, "r") as f:
            content = f.read()

        # Check exact format with version pinning
        self.assertIn('"security==1.3.1"', content)

        # Ensure it's not a range or different format
        self.assertNotIn('"security>=1.3.1"', content)
        self.assertNotIn('"security~=1.3.1"', content)
        self.assertNotIn('"security!=1.3.1"', content)


if __name__ == "__main__":
    unittest.main()
