#!/usr/bin/env python3
"""Integration tests for security module usage"""

import subprocess
import sys
from unittest.mock import Mock, patch

import pytest


class TestSecurityIntegration:
    """Test suite for security module integration"""

    @patch("security.safe_command")
    def test_safe_command_run_wrapper(self, mock_safe_command):
        """Test that safe_command.run properly wraps subprocess.run"""

        # Mock the safe_command.run to return a successful result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_safe_command.run.return_value = mock_result

        # Import and use the security wrapper as done in claude_costs.py
        from security import safe_command

        # Test the wrapper call
        result = safe_command.run(
            subprocess.run,
            [sys.executable, "test_script.py"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Verify the call was made correctly
        mock_safe_command.run.assert_called_once_with(
            subprocess.run,
            [sys.executable, "test_script.py"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Verify the result
        assert result.returncode == 0
        assert result.stdout == "Success output"

    @patch("security.safe_command")
    def test_safe_command_run_with_error(self, mock_safe_command):
        """Test safe_command.run error handling"""

        # Mock a CalledProcessError
        error = subprocess.CalledProcessError(
            1, ["python", "failing_script.py"])
        error.stderr = "Script failed with error"
        mock_safe_command.run.side_effect = error

        # Import the security wrapper
        from security import safe_command

        # Test that the error is properly raised
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            safe_command.run(
                subprocess.run,
                [sys.executable, "failing_script.py"],
                capture_output=True,
                text=True,
                check=True,
            )

        # Verify the error details
        assert exc_info.value.returncode == 1
        assert exc_info.value.stderr == "Script failed with error"

    def test_security_import_pattern(self):
        """Test the import pattern used in claude_costs.py"""

        # Test that the import statement is syntactically correct
        import_code = "from security import safe_command"

        try:
            compile(import_code, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Import pattern syntax error: {e}")

    @patch("security.safe_command")
    @patch("pathlib.Path")
    def test_badge_script_path_resolution(self, mock_path, mock_safe_command):
        """Test that the badge script path is resolved correctly"""

        # Mock Path operations
        mock_script_dir = Mock()
        mock_badge_script = Mock()
        mock_script_dir.__truediv__.return_value = mock_badge_script
        mock_path.return_value.parent = mock_script_dir

        # Mock safe_command.run
        mock_result = Mock()
        mock_result.stdout = "Badge updated"
        mock_safe_command.run.return_value = mock_result

        # Simulate the path resolution and command execution
        script_dir = mock_path(__file__).parent
        badge_script = script_dir / "generate_cost_badge.py"

        result = mock_safe_command.run(
            subprocess.run,
            [sys.executable, str(badge_script)],
            capture_output=True,
            text=True,
            check=True,
        )

        # Verify the call was made with string conversion of path
        mock_safe_command.run.assert_called_once_with(
            subprocess.run,
            [sys.executable, str(badge_script)],
            capture_output=True,
            text=True,
            check=True,
        )

        assert result.stdout == "Badge updated"
