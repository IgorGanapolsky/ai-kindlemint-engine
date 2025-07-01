#!/usr/bin/env python3
"""
Unit tests for setup.py security dependency addition
"""

import sys
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestSetupSecurityDependency:
    """Test the addition of security==1.3.1 dependency in setup.py"""

    def test_security_dependency_present_in_install_requires(self):
        """Test that security==1.3.1 is present in install_requires list"""
        setup_path = project_root / "setup.py"
        
        # Read the actual setup.py file
        with open(setup_path, 'r') as f:
            setup_content = f.read()
        
        # Check that security dependency is present
        assert '"security==1.3.1"' in setup_content
        
        # Check that it's in the install_requires section
        install_requires_start = setup_content.find('install_requires=[')
        install_requires_end = setup_content.find('],', install_requires_start)
        install_requires_section = setup_content[install_requires_start:install_requires_end]
        
        assert '"security==1.3.1"' in install_requires_section

    def test_security_dependency_version_pinned(self):
        """Test that security dependency is pinned to specific version 1.3.1"""
        setup_path = project_root / "setup.py"
        
        with open(setup_path, 'r') as f:
            setup_content = f.read()
        
        # Should have exact version pin, not >= or ~
        assert '"security==1.3.1"' in setup_content
        # Should not have loose version constraints
        assert '"security>=' not in setup_content
        assert '"security~=' not in setup_content
        assert '"security!=' not in setup_content

    def test_install_requires_alphabetical_order_maintained(self):
        """Test that install_requires list maintains alphabetical order after adding security"""
        setup_path = project_root / "setup.py"
        
        with open(setup_path, 'r') as f:
            setup_content = f.read()
        
        # Extract install_requires dependencies
        import re
        pattern = r'install_requires=\[(.*?)\]'
        match = re.search(pattern, setup_content, re.DOTALL)
        assert match, "install_requires section not found"
        
        install_requires_content = match.group(1)
        
        # Extract dependency names (ignoring comments and empty lines)
        dependencies = []
        for line in install_requires_content.split('\n'):
            line = line.strip()
            if line.startswith('"') and '==' in line:
                # Extract package name before ==
                package_name = line.split('==')[0].strip('"')
                dependencies.append(package_name)
        
        # Check that dependencies are in alphabetical order
        sorted_dependencies = sorted(dependencies)
        assert dependencies == sorted_dependencies, f"Dependencies not in alphabetical order: {dependencies}"
        
        # Verify security is in the correct alphabetical position
        assert 'security' in dependencies
        security_index = dependencies.index('security')
        
        # Security should come after 'sentry-sdk' alphabetically
        if 'sentry-sdk' in dependencies:
            sentry_index = dependencies.index('sentry-sdk')
            assert security_index > sentry_index, "security should come after sentry-sdk alphabetically"

    def test_setup_py_syntax_valid(self):
        """Test that setup.py maintains valid Python syntax after modifications"""
        setup_path = project_root / "setup.py"
        
        # Try to compile the setup.py file
        with open(setup_path, 'r') as f:
            setup_content = f.read()
        
        try:
            compile(setup_content, str(setup_path), 'exec')
        except SyntaxError as e:
            pytest.fail(f"setup.py has syntax error: {e}")

    def test_setup_py_can_be_imported(self):
        """Test that setup.py can be imported/executed without errors"""
        setup_path = project_root / "setup.py"
        
        # Mock setuptools.setup to avoid actual setup execution
        with patch('setuptools.setup') as mock_setup:
            # Execute setup.py in a controlled environment
            with open(setup_path, 'r') as f:
                setup_code = f.read()
            
            # Create a globals dict with necessary imports
            setup_globals = {'__file__': str(setup_path)}
            
            try:
                exec(setup_code, setup_globals)
                # Verify setup was called
                mock_setup.assert_called_once()
                
                # Verify security dependency is in the call
                call_args, call_kwargs = mock_setup.call_args
                install_requires = call_kwargs.get('install_requires', [])
                assert any('security==1.3.1' in req for req in install_requires), \
                    f"security==1.3.1 not found in install_requires: {install_requires}"
                    
            except Exception as e:
                pytest.fail(f"Failed to execute setup.py: {e}")
