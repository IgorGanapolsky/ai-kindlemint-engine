#!/usr/bin/env python3
"""
Unit tests for security module integration across the codebase
Tests for the new security dependency and its usage patterns
"""

import subprocess
from unittest.mock import Mock, patch

import pytest


class TestSecurityModuleIntegration:
    """Test security module integration patterns"""

    def test_security_module_availability(self):
        """Test that security module is available as a dependency"""
        try:
            import security

            assert security is not None
            # Test that the module has the expected version
            # Note: This may not be available in all security module versions
            if hasattr(security, "__version__"):
                assert security.__version__ is not None
        except ImportError as e:
            pytest.skip(f"Security module not available: {e}")

    def test_safe_command_module_structure(self):
        """Test that safe_command submodule has expected structure"""
        try:
            from security import safe_command

            # Verify safe_command has run method
            assert hasattr(
                safe_command, "run"), "safe_command should have 'run' method"
            assert callable(
                safe_command.run), "safe_command.run should be callable"

            # Test that it can accept a callable as first argument
            # This is the pattern used in the code: safe_command.run(subprocess.run, ...)
            mock_func = Mock(return_value=Mock(stdout="test"))
            result = safe_command.run(mock_func, ["echo", "test"])

            # Should return something (exact behavior depends on security module implementation)
            assert result is not None

        except ImportError:
            pytest.skip("Security module not available for testing")
        except Exception as e:
            # If the security module doesn't work as expected, document the issue
            pytest.fail(f"Security module doesn't work as expected: {e}")

    def test_safe_command_subprocess_wrapper_pattern(self):
        """Test the specific pattern used in claude_costs.py"""
        try:
            from security import safe_command

            # Test the exact pattern used in the code
            # safe_command.run(subprocess.run, [sys.executable, str(badge_script)],
            #                  capture_output=True, text=True, check=True)

            with patch("subprocess.run") as mock_subprocess:
                mock_result = Mock()
                mock_result.stdout = "Test output"
                mock_subprocess.return_value = mock_result

                # Call safe_command.run with the same pattern as the real code
                result = safe_command.run(
                    subprocess.run,
                    ["python", "-c", "print('hello')"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Verify the result has expected structure
                assert hasattr(result, "stdout") or result is not None

        except ImportError:
            pytest.skip("Security module not available for testing")

    def test_safe_command_error_handling(self):
        """Test that safe_command properly handles and propagates errors"""
        try:
            from security import safe_command

            # Test that CalledProcessError is properly handled/propagated
            def failing_subprocess(*args, **kwargs):
                raise subprocess.CalledProcessError(1, ["false"])

            with pytest.raises(subprocess.CalledProcessError):
                safe_command.run(failing_subprocess, ["false"], check=True)

        except ImportError:
            pytest.skip("Security module not available for testing")

    def test_security_dependency_version(self):
        """Test that the security dependency version matches setup.py"""
        try:
            import security

            # The setup.py specifies security==1.3.1
            # Verify this is the version we're using
            if hasattr(security, "__version__"):
                assert (
                    security.__version__ == "1.3.1"
                ), f"Expected security==1.3.1, got {security.__version__}"
            else:
                # If version info is not available, at least verify the module loads
                from security import safe_command

                assert safe_command is not None

        except ImportError:
            pytest.skip("Security module not available for testing")
