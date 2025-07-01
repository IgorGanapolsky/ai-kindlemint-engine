#!/usr/bin/env python3
"""
Unit tests for claude_costs.py script
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))


class TestClaudeCostsSafeCommandIntegration:
    """Test the integration of safe_command module in claude_costs.py"""

    @patch("scripts.claude_costs.safe_command")
    def test_safe_command_import_available(self, mock_safe_command):
        """Test that safe_command module can be imported successfully"""
        # Import should work without raising ImportError
        import scripts.claude_costs as claude_costs

        # Verify the import exists in the module
        assert hasattr(claude_costs, "safe_command")

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_uses_safe_command_run_success(
        self, mock_tracker, mock_safe_command
    ):
        """Test that badge command uses safe_command.run for subprocess execution on success"""
        # Setup mocks
        mock_result = Mock()
        mock_result.stdout = "✅ Badge generated successfully!"
        mock_result.returncode = 0
        mock_safe_command.run.return_value = mock_result

        # Import and run
        from scripts.claude_costs import main

        # Capture stdout to verify success message
        with patch("builtins.print") as mock_print:
            main()

        # Verify safe_command.run was called instead of subprocess.run directly
        mock_safe_command.run.assert_called_once()

        # Verify the call signature matches expected parameters
        call_args = mock_safe_command.run.call_args
        # First arg should be subprocess.run
        assert call_args[0][0] == subprocess.run
        assert (
            len(call_args[0][1]) == 2
        )  # Command should have 2 elements [python, script_path]
        assert (
            str(call_args[0][1][0]) == sys.executable
        )  # First element should be python executable
        assert call_args[0][1][1].endswith(
            "generate_cost_badge.py"
        )  # Second should be script path

        # Verify keyword arguments
        assert call_args[1]["capture_output"] is True
        assert call_args[1]["text"] is True
        assert call_args[1]["check"] is True

        # Verify success output was printed
        mock_print.assert_called_with("✅ Badge generated successfully!")

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_uses_safe_command_run_failure(
        self, mock_tracker, mock_safe_command
    ):
        """Test that badge command handles failures properly when using safe_command.run"""
        # Setup mocks for failure scenario
        error = subprocess.CalledProcessError(
            1, ["python", "generate_cost_badge.py"])
        error.stderr = "Badge generation failed: File not found"
        mock_safe_command.run.side_effect = error

        # Import and run
        from scripts.claude_costs import main

        # Capture stdout to verify error message
        with patch("builtins.print") as mock_print:
            main()

        # Verify safe_command.run was called
        mock_safe_command.run.assert_called_once()

        # Verify error handling
        mock_print.assert_called_with(
            "❌ Badge generation failed: Badge generation failed: File not found"
        )

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_script_path_resolution(
        self, mock_tracker, mock_safe_command
    ):
        """Test that the badge script path is resolved correctly"""
        # Setup mock
        mock_result = Mock()
        mock_result.stdout = "Badge updated"
        mock_safe_command.run.return_value = mock_result

        from scripts.claude_costs import main

        with patch("builtins.print"):
            main()

        # Verify the script path resolution
        call_args = mock_safe_command.run.call_args
        script_path = call_args[0][1][1]

        # Should be a valid Path object converted to string
        assert isinstance(script_path, (str, Path))
        assert str(script_path).endswith("generate_cost_badge.py")

        # Should be in the same directory as claude_costs.py
        expected_dir = Path(__file__).parent.parent.parent / "scripts"
        assert str(script_path).startswith(str(expected_dir))

    @patch("scripts.claude_costs.safe_command")
    def test_safe_command_import_failure_handling(self, mock_safe_command):
        """Test behavior when safe_command import fails"""
        # Simulate import error
        mock_safe_command.side_effect = ImportError(
            "security module not found")

        # This should raise ImportError when trying to import claude_costs
        with pytest.raises(ImportError):
            import importlib

            import scripts.claude_costs

            importlib.reload(scripts.claude_costs)

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs.py", "status"])
    def test_other_commands_not_affected_by_safe_command(
        self, mock_tracker, mock_safe_command
    ):
        """Test that other commands don't use safe_command and work normally"""
        # Setup tracker mock
        mock_tracker.return_value.load_commit_costs.return_value = {
            "total_cost": 1.50,
            "commits": [],
            "first_tracked": "2024-01-01T00:00:00",
            "last_updated": "2024-01-01T12:00:00",
        }
        mock_tracker.return_value.load_last_commit_cost.return_value = {
            "full_repo_cost": 10.00,
            "worktree_cost": 2.00,
            "savings_potential": 8.00,
        }

        from scripts.claude_costs import main

        with patch("builtins.print") as mock_print:
            main()

        # safe_command.run should not be called for status command
        mock_safe_command.run.assert_not_called()

        # Status output should be printed
        assert any(
            "Claude Cost Tracking Status" in str(call)
            for call in mock_print.call_args_list
        )

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    @patch("scripts.claude_costs.Path")
    def test_badge_script_path_construction(
        self, mock_path, mock_tracker, mock_safe_command
    ):
        """Test the construction of badge script path"""
        # Setup Path mock
        mock_script_file = Mock()
        mock_script_file.parent = Mock()
        mock_script_dir = Mock()
        mock_script_file.parent = mock_script_dir
        mock_badge_script = Mock()
        mock_script_dir.__truediv__ = Mock(return_value=mock_badge_script)

        mock_path.return_value = mock_script_file
        mock_path.__file__ = "/path/to/claude_costs.py"

        # Setup safe_command mock
        mock_result = Mock()
        mock_result.stdout = "Success"
        mock_safe_command.run.return_value = mock_result

        from scripts.claude_costs import main

        with patch("builtins.print"):
            main()

        # Verify safe_command.run was called
        mock_safe_command.run.assert_called_once()

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_preserves_all_subprocess_parameters(
        self, mock_tracker, mock_safe_command
    ):
        """Test that all original subprocess.run parameters are preserved in safe_command.run call"""
        # Setup mock
        mock_result = Mock()
        mock_result.stdout = "Badge created"
        mock_safe_command.run.return_value = mock_result

        from scripts.claude_costs import main

        with patch("builtins.print"):
            main()

        # Verify all the expected parameters are passed to safe_command.run
        call_args = mock_safe_command.run.call_args

        # Check positional args
        assert call_args[0][0] == subprocess.run
        assert len(call_args[0][1]) == 2  # [sys.executable, script_path]

        # Check keyword args match original subprocess.run call
        expected_kwargs = {"capture_output": True, "text": True, "check": True}

        for key, value in expected_kwargs.items():
            assert call_args[1][key] == value

    @patch("scripts.claude_costs.safe_command")
    @patch("scripts.claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_stdout_handling(self, mock_tracker, mock_safe_command):
        """Test that stdout from safe_command.run is properly handled and printed"""
        # Test different stdout scenarios
        test_outputs = [
            "✅ Badge updated successfully in README.md",
            "⚠️ Badge updated with warnings",
            "",  # Empty output
            "Multi-line\noutput\ntest",
        ]

        from scripts.claude_costs import main

        for expected_output in test_outputs:
            # Reset mock
            mock_safe_command.reset_mock()

            # Setup mock result
            mock_result = Mock()
            mock_result.stdout = expected_output
            mock_safe_command.run.return_value = mock_result

            with patch("builtins.print") as mock_print:
                main()

            # Verify the stdout was printed
            mock_print.assert_called_with(expected_output)
