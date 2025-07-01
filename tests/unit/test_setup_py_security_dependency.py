#!/usr/bin/env python3
"""
Unit tests for setup.py security dependency addition
Tests that the security==1.3.1 dependency is properly configured
"""

import sys
from pathlib import Path
from unittest.mock import mock_open, patch


class TestSetupPySecurityDependency:
    """Test setup.py configuration for security dependency"""

    def test_security_dependency_in_install_requires(self):
        """Test that security==1.3.1 is in install_requires"""
        # Read the actual setup.py file
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"
        
        if setup_py_path.exists():
            with open(setup_py_path, 'r') as f:
                setup_content = f.read()
            
            # Check that security dependency is present
            assert '"security==1.3.1"' in setup_content, "security==1.3.1 should be in install_requires"
            
            # Check that it's in the install_requires section
            assert 'install_requires=' in setup_content, "setup.py should have install_requires section"
            
            # Verify it's properly quoted and formatted
            lines = setup_content.split('\n')
            security_line_found = False
            in_install_requires = False
            
            for line in lines:
                if 'install_requires=' in line:
                    in_install_requires = True
                elif in_install_requires and '"security==1.3.1"' in line:
                    security_line_found = True
                    # Check proper formatting (should have trailing comma)
                    assert line.strip().endswith(','), "security dependency should end with comma"
                elif in_install_requires and ']' in line:
                    in_install_requires = False
            
            assert security_line_found, "security==1.3.1 should be found in install_requires section"

    def test_security_dependency_version_pinned(self):
        """Test that security dependency is pinned to specific version"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"
        
        if setup_py_path.exists():
            with open(setup_py_path, 'r') as f:
                setup_content = f.read()
            
            # Should be exactly version 1.3.1, not a range
            assert '"security==1.3.1"' in setup_content, "security should be pinned to version 1.3.1"
            
            # Should not have version ranges
            assert '"security>=' not in setup_content, "security should not use >= version specifier"
            assert '"security~=' not in setup_content, "security should not use ~= version specifier"
            assert '"security<=' not in setup_content, "security should not use <= version specifier"

    def test_security_dependency_in_alphabetical_order(self):
        """Test that security dependency maintains alphabetical order in install_requires"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"
        
        if setup_py_path.exists():
            with open(setup_py_path, 'r') as f:
                setup_content = f.read()
            
            # Extract install_requires section
            lines = setup_content.split('\n')
            install_requires_lines = []
            in_install_requires = False
            
            for line in lines:
                if 'install_requires=' in line:
                    in_install_requires = True
                elif in_install_requires and line.strip().startswith('"') and '==' in line:
                    # Extract package name (before ==)
                    package_line = line.strip().strip(',').strip('"')
                    package_name = package_line.split('==')[0]
                    install_requires_lines.append(package_name)
                elif in_install_requires and ']' in line:
                    break
            
            # Check that security is in the list
            assert 'security' in install_requires_lines, "security should be in install_requires"
            
            # Check alphabetical order (should be sorted)
            sorted_packages = sorted(install_requires_lines)
            assert install_requires_lines == sorted_packages, f"install_requires should be in alphabetical order. Expected: {sorted_packages}, Got: {install_requires_lines}"
