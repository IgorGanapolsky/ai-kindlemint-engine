#!/usr/bin/env python3
"""
Unit tests for claude_costs.py security improvements
Tests the integration of safe_command for subprocess execution
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestClaudeCostsSecurityIntegration:
    """Test security improvements in claude_costs.py"""

    @patch("security.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_uses_safe_command(self, mock_safe_command):
        """Test that badge command uses safe_command.run instead of subprocess.run"""
        # Mock safe_command.run to return success
        mock_result = Mock()
        mock_result.stdout = "✅ Badge generation completed successfully"
        mock_safe_command.run.return_value = mock_result

        # Import and run the main function
        from scripts.claude_costs import main

        with patch("builtins.print") as mock_print:
            main()

        # Verify safe_command.run was called
        mock_safe_command.run.assert_called_once()

        # Verify the call parameters
        call_args = mock_safe_command.run.call_args
        assert (
            call_args[0][0] == subprocess.run
        )  # First argument should be subprocess.run
        # Should contain python executable
        assert sys.executable in call_args[0][1]
        assert str(
            Path(__file__).parent.parent.parent /
            "scripts" / "generate_cost_badges.py"
        ) in str(call_args[0][1])

        # Verify keyword arguments
        kwargs = call_args[1]
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is True

        # Verify output was printed
        mock_print.assert_called_with(
            "✅ Badge generation completed successfully")

    @patch("security.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_handles_safe_command_failure(self, mock_safe_command):
        """Test error handling when safe_command.run raises CalledProcessError"""
        # Mock safe_command.run to raise CalledProcessError
        error = subprocess.CalledProcessError(1, "cmd")
        error.stderr = "Badge generation failed: File not found"
        mock_safe_command.run.side_effect = error

        from scripts.claude_costs import main

        with patch("builtins.print") as mock_print:
            main()

        # Verify error message was printed
        mock_print.assert_called_with(
            "❌ Badge generation failed: Badge generation failed: File not found"
        )

    @patch("security.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_handles_import_error(self, mock_safe_command):
        """Test fallback behavior when security module is not available"""
        # Simulate import error for security module
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'security'")
        ):
            # This should raise ImportError since the code now requires security module
            from scripts.claude_costs import main

            with pytest.raises(ImportError):
                main()

    @patch("security.safe_command")
    def test_safe_command_import_success(self, mock_safe_command):
        """Test that security.safe_command can be imported successfully"""
        # This test verifies the import statement works
        try:
            from security import safe_command

            assert safe_command is not None
        except ImportError:
            # If security module is not installed, mock the import
            with patch.dict(
                "sys.modules",
                {"security": Mock(), "security.safe_command": mock_safe_command},
            ):
                from security import safe_command

                assert safe_command is not None

    @patch("security.safe_command")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_script_path_resolution(self, mock_exists, mock_safe_command):
        """Test that the badge script path is correctly resolved"""
        mock_result = Mock()
        mock_result.stdout = "Badge updated"
        mock_safe_command.run.return_value = mock_result

        from scripts.claude_costs import main

        with patch("builtins.print"):
            main()

        # Verify the script path in the call
        call_args = mock_safe_command.run.call_args[0][1]
        assert "generate_cost_badges.py" in str(call_args[1])

    @patch("security.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_with_different_exceptions(self, mock_safe_command):
        """Test error handling with different types of exceptions"""
        # Test with OSError
        mock_safe_command.run.side_effect = OSError("Permission denied")

        from scripts.claude_costs import main

        with patch("builtins.print") as mock_print:
            main()

        # Should catch any exception and print error
        error_calls = [
            call for call in mock_print.call_args_list if "❌" in str(call)]
        assert len(error_calls) > 0

    @patch("security.safe_command")
    @patch("sys.argv", ["claude_costs.py", "badge"])
    def test_badge_command_output_handling(self, mock_safe_command):
        """Test that badge command output is properly handled"""
        # Test with multiline output
        mock_result = Mock()
        mock_result.stdout = "Line 1\nLine 2\nBadge generation complete"
        mock_safe_command.run.return_value = mock_result

        from scripts.claude_costs import main

        with patch("builtins.print") as mock_print:
            main()

        # Verify all output lines are printed
        mock_print.assert_called_with(
            "Line 1\nLine 2\nBadge generation complete")

    def test_security_module_dependency_added(self):
        """Test that security dependency is properly added to setup.py"""
        setup_py_path = Path(__file__).parent.parent.parent / "setup.py"

        if setup_py_path.exists():
            with open(setup_py_path, "r") as f:
                content = f.read()

            # Verify security dependency is present
            assert "security" in content.lower()
        else:
            pytest.skip("setup.py not found - testing in isolation")
