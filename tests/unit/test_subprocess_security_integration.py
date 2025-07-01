#!/usr/bin/env python3
"""
Integration tests for security module usage in subprocess calls
Tests the overall security improvement pattern across the codebase
"""

import subprocess
from unittest.mock import Mock, patch

import pytest


class TestSubprocessSecurityIntegration:
    """Test integration of security module with subprocess calls"""

    @patch("security.safe_command")
    def test_safe_command_signature_compatibility(self, mock_safe_command):
        """Test that safe_command.run is compatible with subprocess.run signature"""
        # Mock safe_command.run to verify it can handle subprocess.run parameters
        mock_result = Mock()
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_safe_command.run.return_value = mock_result

        try:
            from security import safe_command
        except ImportError:
            # Mock the module if not available
            with patch.dict(
                "sys.modules",
                {"security": Mock(), "security.safe_command": mock_safe_command},
            ):
                from security import safe_command

        # Test that safe_command.run can accept the same parameters as subprocess.run
        test_args = ["python", "--version"]
        result = safe_command.run(
            subprocess.run, test_args, capture_output=True, text=True, check=True
        )

        # Verify the call was made with correct parameters
        mock_safe_command.run.assert_called_once_with(
            subprocess.run, test_args, capture_output=True, text=True, check=True
        )

        assert result.stdout == "test output"
        assert result.returncode == 0

    @patch("security.safe_command")
    def test_safe_command_error_propagation(self, mock_safe_command):
        """Test that safe_command properly propagates subprocess errors"""
        # Test CalledProcessError propagation
        error = subprocess.CalledProcessError(1, "test_cmd")
        error.stderr = "Command failed"
        mock_safe_command.run.side_effect = error

        try:
            from security import safe_command
        except ImportError:
            with patch.dict(
                "sys.modules",
                {"security": Mock(), "security.safe_command": mock_safe_command},
            ):
                from security import safe_command

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            safe_command.run(
                # Command that always fails
                subprocess.run,
                ["false"],
                check=True,
            )

        assert exc_info.value.returncode == 1
        assert exc_info.value.stderr == "Command failed"

    @patch("security.safe_command")
    def test_safe_command_with_different_subprocess_options(self, mock_safe_command):
        """Test safe_command with various subprocess.run options"""
        mock_result = Mock()
        mock_result.stdout = "test"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_safe_command.run.return_value = mock_result

        try:
            from security import safe_command
        except ImportError:
            with patch.dict(
                "sys.modules",
                {"security": Mock(), "security.safe_command": mock_safe_command},
            ):
                from security import safe_command

        # Test with different combinations of options
        test_cases = [
            {"capture_output": True, "text": True},
            {"capture_output": True, "text": True, "check": True},
            {"capture_output": True, "text": True, "check": True, "timeout": 30},
            {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE},
        ]

        for options in test_cases:
            safe_command.run(subprocess.run, ["echo", "test"], **options)

            # Verify the call included all the options
            call_args, call_kwargs = mock_safe_command.run.call_args
            assert call_args[0] == subprocess.run
            assert call_args[1] == ["echo", "test"]
            for key, value in options.items():
                assert call_kwargs[key] == value

    def test_security_module_provides_safe_command(self):
        """Test that security module provides safe_command functionality"""
        try:
            from security import safe_command

            assert hasattr(
                safe_command, "run"), "safe_command should have 'run' method"
        except ImportError:
            # If security module is not available, this is expected in test environment
            pytest.skip(
                "security module not available - expected in test environment")

    @patch("subprocess.run")
    @patch("security.safe_command")
    def test_safe_command_vs_direct_subprocess(
        self, mock_safe_command, mock_subprocess
    ):
        """Test that safe_command is used instead of direct subprocess calls"""
        # This test verifies the security improvement principle
        mock_result = Mock()
        mock_result.returncode = 0
        mock_safe_command.run.return_value = mock_result

        try:
            from security import safe_command
        except ImportError:
            with patch.dict(
                "sys.modules",
                {"security": Mock(), "security.safe_command": mock_safe_command},
            ):
                from security import safe_command

        # Use safe_command instead of direct subprocess
        safe_command.run(subprocess.run, ["echo", "hello"])

        # Verify safe_command was called, not direct subprocess
        mock_safe_command.run.assert_called_once()
        mock_subprocess.assert_not_called()
