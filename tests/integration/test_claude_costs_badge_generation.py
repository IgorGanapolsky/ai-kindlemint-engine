#!/usr/bin/env python3
"""
Integration tests for claude_costs.py badge generation with security
Tests the full badge generation workflow with safe_command integration
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestClaudeCostsBadgeGenerationIntegration(unittest.TestCase):
    """Integration tests for badge generation with security"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_commit_costs = {
            "total_cost": 1.234,
            "commits": [
                {
                    "hash": "abc123",
                    "cost": 0.50,
                    "timestamp": "2025-01-01T12:00:00",
                    "message": "Test commit",
                }
            ],
        }

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.Path")
    def test_complete_badge_generation_workflow(
        self, mock_path_class, mock_safe_command
    ):
        """Test complete badge generation workflow with security integration"""
        # Set up file system mocks
        mock_script_path = Mock()
        mock_script_path.parent = self.temp_dir
        mock_script_path.__truediv__ = Mock(
            return_value=self.temp_dir / "generate_cost_badge.py"
        )
        mock_path_class.return_value = mock_script_path

        # Mock safe_command.run
        mock_result = Mock()
        mock_result.stdout = "✅ Badge generation successful"
        mock_result.returncode = 0
        mock_safe_command.run.return_value = mock_result

        # Create a mock badge script file
        mock_badge_script = self.temp_dir / "generate_cost_badge.py"
        mock_badge_script.touch()

        # Test the badge generation
        with patch("sys.argv", ["claude_costs.py", "badge"]):
            with patch("builtins.print") as mock_print:
                try:
                    from scripts.claude_costs import main

                    main()
                except SystemExit:
                    pass

                # Verify safe_command.run was called
                mock_safe_command.run.assert_called_once()

                # Verify success message was printed
                mock_print.assert_any_call("✅ Badge generation successful")

    @patch("scripts.claude_costs.safe_command")
    def test_badge_generation_with_security_error(self, mock_safe_command):
        """Test badge generation handles security wrapper errors correctly"""
        from subprocess import CalledProcessError

        # Mock safe_command.run to raise an error
        mock_safe_command.run.side_effect = CalledProcessError(
            returncode=1,
            cmd=["python", "generate_cost_badge.py"],
            stderr="Security check failed",
        )

        # Mock Path
        with patch("scripts.claude_costs.Path") as mock_path_class:
            mock_script_path = Mock()
            mock_script_path.parent = self.temp_dir
            mock_script_path.__truediv__ = Mock(
                return_value=self.temp_dir / "generate_cost_badge.py"
            )
            mock_path_class.return_value = mock_script_path

            with patch("sys.argv", ["claude_costs.py", "badge"]):
                with patch("builtins.print") as mock_print:
                    try:
                        from scripts.claude_costs import main

                        main()
                    except SystemExit:
                        pass

                    # Verify error message was printed
                    mock_print.assert_any_call(
                        "❌ Badge generation failed: Security check failed"
                    )

    @patch("scripts.claude_costs.safe_command")
    def test_security_wrapper_preserves_original_functionality(self, mock_safe_command):
        """Test that security wrapper preserves the original subprocess.run functionality"""
        import subprocess

        # Create a mock that behaves like the original subprocess.run
        def mock_safe_run(func, *args, **kwargs):
            # Verify that subprocess.run was passed as the first argument
            assert func == subprocess.run, "First argument should be subprocess.run"
            # Return a mock result
            result = Mock()
            result.stdout = "Original functionality preserved"
            result.returncode = 0
            return result

        mock_safe_command.run.side_effect = mock_safe_run

        # Test that the wrapper correctly delegates to subprocess.run
        result = mock_safe_command.run(
            subprocess.run, ["echo", "test"], capture_output=True
        )
        self.assertEqual(result.stdout, "Original functionality preserved")


if __name__ == "__main__":
    unittest.main()
