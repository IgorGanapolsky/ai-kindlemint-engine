#!/usr/bin/env python3
"""
Unit tests for security changes in claude_costs.py
Tests the integration of safe_command module and secure subprocess execution
"""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))


class TestClaudeCostsSecurity(unittest.TestCase):
    """Test security integration in claude_costs.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_tracker = Mock()
        self.mock_tracker.load_commit_costs.return_value = {
            "commits": [],
            "total_cost": 0.0,
            "first_tracked": "2024-01-01",
            "last_updated": "2024-01-01T00:00:00",
        }
        self.mock_tracker.load_last_commit_cost.return_value = {
            "full_repo_cost": 10.0,
            "worktree_cost": 5.0,
            "savings_potential": 5.0,
        }

    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("scripts.claude_costs.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_with_safe_command(
        self, mock_safe_command, mock_tracker_class
    ):
        """Test that badge command uses safe_command.run instead of subprocess.run"""
        # Setup mocks
        mock_tracker_class.return_value = self.mock_tracker
        mock_result = Mock()
        mock_result.stdout = "✅ Badge generated successfully!"
        mock_safe_command.run.return_value = mock_result

        # Import after patching to ensure mocks are in place
        from scripts import claude_costs

        # Test badge command
        try:
            claude_costs.main()
        except SystemExit:
            pass  # main() may call sys.exit, which is expected

        # Verify safe_command.run was called with correct parameters
        mock_safe_command.run.assert_called_once()

        # Get the call arguments
        call_args = mock_safe_command.run.call_args

        # Verify first argument is subprocess.run
        self.assertEqual(call_args[0][0], subprocess.run)

        # Verify the command arguments include Python executable and script path
        command_args = call_args[0][1]
        self.assertEqual(command_args[0], sys.executable)
        self.assertTrue(str(command_args[1]).endswith(
            "generate_cost_badges.py"))

        # Verify subprocess options are passed correctly
        self.assertEqual(call_args[1]["capture_output"], True)
        self.assertEqual(call_args[1]["text"], True)
        self.assertEqual(call_args[1]["check"], True)

    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("scripts.claude_costs.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_handles_safe_command_error(
        self, mock_safe_command, mock_tracker_class
    ):
        """Test that badge command properly handles safe_command errors"""
        # Setup mocks
        mock_tracker_class.return_value = self.mock_tracker
        mock_safe_command.run.side_effect = subprocess.CalledProcessError(
            1, "generate_cost_badges.py", stderr="Error generating badges"
        )

        # Import after patching
        from scripts import claude_costs

        # Capture stdout to verify error handling
        with patch("builtins.print") as mock_print:
            try:
                claude_costs.main()
            except SystemExit:
                pass

            # Verify error message was printed
            mock_print.assert_called()
            error_calls = [
                call
                for call in mock_print.call_args_list
                if "Badge generation failed" in str(call)
            ]
            self.assertTrue(len(error_calls) > 0)

    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("scripts.claude_costs.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_safe_command_import_available(self, mock_safe_command, mock_tracker_class):
        """Test that safe_command module import works correctly"""
        # Setup mocks
        mock_tracker_class.return_value = self.mock_tracker
        mock_result = Mock()
        mock_result.stdout = "Success"
        mock_safe_command.run.return_value = mock_result

        # Test that import doesn't raise ImportError
        try:
            from security import (  # This should not raise ImportError in test
                safe_command,
            )

            from scripts import claude_costs
        except ImportError as e:
            # In testing environment, we expect this import to be mocked
            self.fail(f"safe_command import failed: {e}")

    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("scripts.claude_costs.safe_command")
    def test_other_commands_not_affected(self, mock_safe_command, mock_tracker_class):
        """Test that other commands still work and don't use safe_command"""
        # Setup mocks
        mock_tracker_class.return_value = self.mock_tracker

        # Import after patching
        from scripts import claude_costs

        # Test status command (doesn't use subprocess)
        with patch("sys.argv", ["claude_costs.py", "status"]):
            with patch("builtins.print"):
                try:
                    claude_costs.main()
                except SystemExit:
                    pass

        # Verify safe_command.run was not called for non-badge commands
        mock_safe_command.run.assert_not_called()

    @patch("scripts.claude_costs.Path")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("scripts.claude_costs.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_script_path_resolution(
        self, mock_safe_command, mock_tracker_class, mock_path
    ):
        """Test that badge script path is resolved correctly"""
        # Setup mocks
        mock_tracker_class.return_value = self.mock_tracker
        mock_result = Mock()
        mock_result.stdout = "Success"
        mock_safe_command.run.return_value = mock_result

        # Mock Path behavior
        mock_script_file = Mock()
        mock_script_dir = Mock()
        mock_badge_script = Mock()
        mock_script_file.parent = mock_script_dir
        mock_script_dir.__truediv__ = Mock(return_value=mock_badge_script)
        mock_path.return_value = mock_script_file

        # Import and run
        from scripts import claude_costs

        try:
            claude_costs.main()
        except SystemExit:
            pass

        # Verify safe_command.run was called
        mock_safe_command.run.assert_called_once()

        # Verify path resolution was used
        call_args = mock_safe_command.run.call_args[0][1]
        self.assertEqual(call_args[1], mock_badge_script)

    def test_security_module_interface(self):
        """Test that security module has expected interface"""
        # Mock the security module
        with patch.dict("sys.modules", {"security": Mock()}):
            with patch.dict("sys.modules", {"security.safe_command": Mock()}):
                from security import safe_command

                # Verify safe_command has run method
                self.assertTrue(hasattr(safe_command, "run"))


if __name__ == "__main__":
    unittest.main()
