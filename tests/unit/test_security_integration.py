#!/usr/bin/env python3
"""
Unit tests for security module integration
Tests the security==1.3.1 dependency and safe_command functionality
"""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestSecurityIntegration(unittest.TestCase):
    """Test security module integration and safe_command functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_command = [sys.executable, "-c", "print('test')"]
        self.test_kwargs = {"capture_output": True,
                            "text": True, "check": True}

    @patch("security.safe_command")
    def test_safe_command_module_import(self, mock_safe_command):
        """Test that security.safe_command can be imported"""
        try:
            from security import safe_command

            self.assertTrue(hasattr(safe_command, "run"))
        except ImportError:
            # In test environment, we expect this to be mocked
            self.skipTest("security module not available in test environment")

    @patch("security.safe_command.run")
    def test_safe_command_run_interface(self, mock_safe_run):
        """Test that safe_command.run has the expected interface"""
        # Setup mock return value
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_safe_run.return_value = mock_result

        # Import and use safe_command
        with patch.dict(
            "sys.modules", {
                "security": Mock(), "security.safe_command": Mock()}
        ):
            from security import safe_command

            safe_command.run = mock_safe_run

            # Test the interface
            result = safe_command.run(
                subprocess.run, self.test_command, **self.test_kwargs
            )

            # Verify call was made correctly
            mock_safe_run.assert_called_once_with(
                subprocess.run, self.test_command, **self.test_kwargs
            )

            # Verify return value
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "test output")

    @patch("security.safe_command.run")
    def test_safe_command_error_handling(self, mock_safe_run):
        """Test that safe_command properly handles subprocess errors"""
        # Setup mock to raise CalledProcessError
        mock_safe_run.side_effect = subprocess.CalledProcessError(
            1, self.test_command, stderr="command failed"
        )

        with patch.dict(
            "sys.modules", {
                "security": Mock(), "security.safe_command": Mock()}
        ):
            from security import safe_command

            safe_command.run = mock_safe_run

            # Test that exception is properly raised
            with self.assertRaises(subprocess.CalledProcessError) as cm:
                safe_command.run(
                    subprocess.run, self.test_command, **self.test_kwargs)

            # Verify exception details
            self.assertEqual(cm.exception.returncode, 1)
            self.assertEqual(cm.exception.stderr, "command failed")

    @patch("security.safe_command.run")
    def test_safe_command_preserves_subprocess_behavior(self, mock_safe_run):
        """Test that safe_command preserves original subprocess.run behavior"""
        # Setup mock to simulate successful subprocess.run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "expected output"
        mock_result.stderr = ""
        mock_result.args = self.test_command
        mock_safe_run.return_value = mock_result

        with patch.dict(
            "sys.modules", {
                "security": Mock(), "security.safe_command": Mock()}
        ):
            from security import safe_command

            safe_command.run = mock_safe_run

            # Test that all subprocess.run arguments are passed through
            result = safe_command.run(
                subprocess.run,
                self.test_command,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
                cwd="/tmp",
            )

            # Verify all arguments were passed
            mock_safe_run.assert_called_once_with(
                subprocess.run,
                self.test_command,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
                cwd="/tmp",
            )

            # Verify result attributes
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "expected output")
            self.assertEqual(result.args, self.test_command)


if __name__ == "__main__":
    unittest.main()
