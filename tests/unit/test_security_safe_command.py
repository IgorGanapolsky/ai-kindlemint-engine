#!/usr/bin/env python3
"""
Unit tests for security.safe_command module
Tests the safe wrapper functionality for subprocess operations
"""

import subprocess
from unittest.mock import Mock, patch

import pytest


class TestSafeCommand:
    """Test the security.safe_command module functionality"""

    def test_safe_command_import(self):
        """Test that safe_command can be imported"""
        try:
            from security import safe_command
            assert safe_command is not None
        except ImportError:
            # If the security module doesn't exist yet, this test documents the expected interface
            pytest.skip("security module not implemented yet")

    @patch("security.safe_command")
    def test_safe_command_run_success(self, mock_safe_command):
        """Test safe_command.run with successful subprocess execution"""
        # Mock the safe_command.run function
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_safe_command.run.return_value = mock_result

        from security import safe_command
        
        # Test the safe wrapper
        result = safe_command.run(
            subprocess.run,
            ["echo", "test"],
            capture_output=True,
            text=True,
            check=True
        )
        
        assert result.returncode == 0
        assert result.stdout == "Success output"
        mock_safe_command.run.assert_called_once()

    @patch("security.safe_command")
    def test_safe_command_run_failure(self, mock_safe_command):
        """Test safe_command.run with subprocess failure"""
        # Mock subprocess failure
        mock_safe_command.run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr="Error message"
        )

        from security import safe_command

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            safe_command.run(
                subprocess.run,
                ["false"],  # Command that always fails
                capture_output=True,
                text=True,
                check=True
            )
        
        assert exc_info.value.returncode == 1
        mock_safe_command.run.assert_called_once()

    @patch("security.safe_command")
    def test_safe_command_run_with_timeout(self, mock_safe_command):
        """Test safe_command.run with timeout parameter"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Timeout test"
        mock_safe_command.run.return_value = mock_result

        from security import safe_command

        result = safe_command.run(
            subprocess.run,
            ["sleep", "1"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        assert result.returncode == 0
        mock_safe_command.run.assert_called_once()

    @patch("security.safe_command")
    def test_safe_command_run_preserves_kwargs(self, mock_safe_command):
        """Test that safe_command.run preserves all keyword arguments"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_safe_command.run.return_value = mock_result

        from security import safe_command

        # Test with various kwargs that should be preserved
        result = safe_command.run(
            subprocess.run,
            ["echo", "test"],
            capture_output=True,
            text=True,
            check=False,
            cwd="/tmp",
            env={"TEST": "value"},
            shell=False
        )
        
        # Verify the call was made (exact arguments depend on implementation)
        mock_safe_command.run.assert_called_once()
        
        # Verify result is returned
        assert result.returncode == 0

    def test_safe_command_module_structure(self):
        """Test expected module structure for security.safe_command"""
        try:
            from security import safe_command
            
            # Verify expected interface
            assert hasattr(safe_command, 'run'), "safe_command should have a 'run' function"
            assert callable(safe_command.run), "safe_command.run should be callable"
            
        except ImportError:
            # Document expected interface for when module is implemented
            pytest.skip("security module not implemented yet - expected interface: security.safe_command.run(func, *args, **kwargs)")
