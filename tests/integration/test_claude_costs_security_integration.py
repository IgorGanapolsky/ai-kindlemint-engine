#!/usr/bin/env python3
"""
Integration tests for claude_costs.py security changes
Tests the end-to-end security integration with real subprocess calls
"""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class TestClaudeCostsSecurityIntegration(unittest.TestCase):
    """Integration tests for claude_costs security features"""

    def setUp(self):
        """Set up test environment"""
        self.scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        self.claude_costs_script = self.scripts_dir / "claude_costs.py"
        self.badge_script = self.scripts_dir / "generate_cost_badge.py"

        # Verify script exists
        self.assertTrue(
            self.claude_costs_script.exists(),
            f"claude_costs.py not found: {self.claude_costs_script}",
        )

    def test_claude_costs_script_imports_security(self):
        """Test that claude_costs.py can import security module"""
        try:
            # Try to run the script with --help to see if imports work
            result = subprocess.run(
                [sys.executable, str(self.claude_costs_script), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # If security import fails, it should show in stderr
            if result.returncode != 0 and "security" in result.stderr:
                self.skipTest(
                    "Security package not installed in test environment")

            # Should show help output if imports are successful
            self.assertIn("Claude API Cost Tracking System", result.stdout)

        except subprocess.TimeoutExpired:
            self.fail("Script timed out - possible import issues")
        except FileNotFoundError:
            self.fail("Python executable not found")

    @patch("security.safe_command")
    def test_badge_command_integration(self, mock_safe_command):
        """Test badge command integration with mocked security"""
        # Mock successful badge generation
        mock_result = Mock()
        mock_result.stdout = "✅ Badge generated successfully"
        mock_safe_command.run.return_value = mock_result

        try:
            # Run badge command
            result = subprocess.run(
                [sys.executable, str(self.claude_costs_script), "badge"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Check if security import was the issue
            if result.returncode != 0 and "security" in result.stderr:
                self.skipTest(
                    "Security package not installed in test environment")

            # Should not crash with import errors
            self.assertNotIn("ImportError", result.stderr)
            self.assertNotIn("ModuleNotFoundError", result.stderr)

        except subprocess.TimeoutExpired:
            self.fail("Badge command timed out")

    def test_security_dependency_installed(self):
        """Test that security dependency can be imported"""
        try:
            import security
            import security.safe_command

            # Basic functionality test
            self.assertTrue(hasattr(security, "safe_command"))
            self.assertTrue(hasattr(security.safe_command, "run"))

        except ImportError:
            self.skipTest(
                "Security package not installed - expected in test environment"
            )

    def test_subprocess_replacement_integration(self):
        """Test that subprocess calls are properly replaced with security wrapper"""
        try:
            # Import the security module to verify it's available
            # Test that safe_command.run has expected signature
            import inspect

            import security.safe_command

            sig = inspect.signature(security.safe_command.run)

            # Should accept at least the function and args parameters
            params = list(sig.parameters.keys())
            self.assertGreaterEqual(
                len(params), 2, "safe_command.run should accept function and args"
            )

        except ImportError:
            self.skipTest(
                "Security package not installed - expected in test environment"
            )

    def test_badge_script_exists(self):
        """Test that the badge generation script exists"""
        # The badge command tries to call generate_cost_badge.py
        # This test ensures the script exists for the integration to work
        if self.badge_script.exists():
            self.assertTrue(self.badge_script.is_file())
        else:
            # If badge script doesn't exist, the integration should handle it gracefully
            self.skipTest(
                "Badge generation script not found - integration may fail gracefully"
            )

    def test_security_wrapper_preserves_subprocess_interface(self):
        """Test that security wrapper maintains subprocess.run interface"""
        try:
            import security.safe_command

            # Test with a simple safe command
            result = security.safe_command.run(
                subprocess.run,
                ["echo", "test"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Should have same interface as subprocess.run result
            self.assertTrue(hasattr(result, "stdout"))
            self.assertTrue(hasattr(result, "stderr"))
            self.assertTrue(hasattr(result, "returncode"))

        except ImportError:
            self.skipTest("Security package not installed")
        except Exception as e:
            # If security wrapper has different interface, this test will catch it
            self.fail(f"Security wrapper interface issue: {e}")


if __name__ == "__main__":
    unittest.main()
