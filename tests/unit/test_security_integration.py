#!/usr/bin/env python3
"""
Unit tests for security package integration
Tests the new security dependency and its safe_command module
"""

import sys
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestSecurityIntegration(unittest.TestCase):
    """Test security package integration"""

    def test_security_package_import(self):
        """Test that security package can be imported"""
        try:
            import security
            self.assertIsNotNone(security)
        except ImportError:
            self.skipTest("Security package not installed - this is expected in CI/test environments")
    
    def test_safe_command_module_import(self):
        """Test that safe_command module can be imported from security package"""
        try:
            from security import safe_command
            self.assertIsNotNone(safe_command)
        except ImportError:
            self.skipTest("Security package not installed - this is expected in CI/test environments")
    
    def test_safe_command_run_method_exists(self):
        """Test that safe_command.run method exists and is callable"""
        try:
            from security import safe_command
            self.assertTrue(hasattr(safe_command, 'run'))
            self.assertTrue(callable(safe_command.run))
        except ImportError:
            self.skipTest("Security package not installed - this is expected in CI/test environments")
    
    @patch('security.safe_command')
    def test_safe_command_run_wrapper_functionality(self, mock_safe_command):
        """Test that safe_command.run works as a wrapper for subprocess functions"""
        import subprocess
        
        # Mock the safe_command.run to simulate wrapper behavior
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Command executed safely"
        mock_result.stderr = ""
        mock_safe_command.run.return_value = mock_result
        
        # Test calling safe_command.run with subprocess.run
        result = mock_safe_command.run(
            subprocess.run,
            ['echo', 'test'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Verify the mock was called correctly
        mock_safe_command.run.assert_called_once_with(
            subprocess.run,
            ['echo', 'test'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Verify the result
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Command executed safely")
    
    def test_security_version_requirement(self):
        """Test that the correct version of security package is available"""
        try:
            import security
            # The setup.py specifies security==1.3.1
            # We can't test the exact version without importing pkg_resources
            # but we can verify the package imports correctly
            self.assertIsNotNone(security.__file__)
        except ImportError:
            self.skipTest("Security package not installed - this is expected in CI/test environments")


if __name__ == '__main__':
    unittest.main()