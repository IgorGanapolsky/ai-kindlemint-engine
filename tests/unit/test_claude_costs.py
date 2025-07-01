#!/usr/bin/env python3
"""
Unit tests for claude_costs.py script
Tests for security module integration and subprocess call changes
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestClaudeCostsSecurity:
    """Test security module integration in claude_costs.py"""

    def test_security_import(self):
        """Test that security module can be imported"""
        try:
            from security import safe_command
            assert safe_command is not None
        except ImportError:
            # If the security module is not available, the import should at least be syntactically correct
            # We can't test the actual functionality without the module
            pytest.skip("Security module not available for testing")

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    def test_badge_command_uses_safe_command(self, mock_tracker, mock_safe_command):
        """Test that the badge command uses safe_command.run instead of subprocess.run"""
        # Setup mock safe_command
        mock_result = Mock()
        mock_result.stdout = "Badge generated successfully"
        mock_safe_command.run.return_value = mock_result
        
        # Setup mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        from scripts.claude_costs import main
        
        # This should not raise an exception
        main()
        
        # Verify safe_command.run was called with correct parameters
        mock_safe_command.run.assert_called_once()
        call_args = mock_safe_command.run.call_args
        
        # Check that subprocess.run was the first argument
        assert call_args[0][0] == subprocess.run
        
        # Check that the command list was passed correctly
        command_list = call_args[0][1]
        assert command_list[0] == sys.executable
        assert "generate_cost_badge.py" in str(command_list[1])

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    def test_badge_command_safe_command_kwargs(self, mock_tracker, mock_safe_command):
        """Test that safe_command.run is called with correct keyword arguments"""
        # Setup mock safe_command
        mock_result = Mock()
        mock_result.stdout = "Badge generated successfully"
        mock_safe_command.run.return_value = mock_result
        
        # Setup mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        from scripts.claude_costs import main
        
        main()
        
        # Verify safe_command.run was called with the expected kwargs
        call_args = mock_safe_command.run.call_args
        kwargs = call_args[1]
        
        assert kwargs['capture_output'] is True
        assert kwargs['text'] is True
        assert kwargs['check'] is True

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    @patch('builtins.print')
    def test_badge_command_prints_stdout(self, mock_print, mock_tracker, mock_safe_command):
        """Test that badge command prints the stdout from safe_command"""
        # Setup mock safe_command with stdout
        mock_result = Mock()
        expected_output = "✅ Badge updated successfully!"
        mock_result.stdout = expected_output
        mock_safe_command.run.return_value = mock_result
        
        # Setup mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        from scripts.claude_costs import main
        
        main()
        
        # Verify print was called with the stdout
        mock_print.assert_called_with(expected_output)

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    @patch('builtins.print')
    def test_badge_command_handles_called_process_error(self, mock_print, mock_tracker, mock_safe_command):
        """Test that badge command handles CalledProcessError from safe_command"""
        # Setup mock safe_command to raise CalledProcessError
        error = subprocess.CalledProcessError(1, ['python', 'script.py'])
        error.stderr = "Error generating badge"
        mock_safe_command.run.side_effect = error
        
        # Setup mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        from scripts.claude_costs import main
        
        main()
        
        # Verify error message was printed
        mock_print.assert_called_with("❌ Badge generation failed: Error generating badge")

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    def test_badge_script_path_resolution(self, mock_tracker, mock_safe_command):
        """Test that the badge script path is resolved correctly"""
        # Setup mock safe_command
        mock_result = Mock()
        mock_result.stdout = "Badge generated"
        mock_safe_command.run.return_value = mock_result
        
        # Setup mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        from scripts.claude_costs import main
        
        main()
        
        # Verify the script path construction
        call_args = mock_safe_command.run.call_args
        command_list = call_args[0][1]
        script_path = Path(command_list[1])
        
        # Should be in the same directory as claude_costs.py
        assert script_path.name == "generate_cost_badge.py"
        assert script_path.parent.name == "scripts"

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    def test_badge_command_not_called_for_other_commands(self, mock_tracker, mock_safe_command):
        """Test that safe_command is not called for commands other than badge"""
        # Setup mock tracker with necessary methods
        mock_tracker_instance = Mock()
        mock_tracker_instance.track_commit.return_value = {"status": "tracked", "cost": 0.01, "tokens": 100, "files": 2}
        mock_tracker.return_value = mock_tracker_instance
        
        # Test with 'init' command
        with patch('sys.argv', ['claude_costs.py', 'init']):
            from scripts.claude_costs import main
            main()
        
        # Verify safe_command.run was not called
        mock_safe_command.run.assert_not_called()

    def test_security_module_structure(self):
        """Test that security module has expected structure"""
        try:
            from security import safe_command
            # Check that safe_command has a run method
            assert hasattr(safe_command, 'run'), "safe_command should have a 'run' method"
            assert callable(safe_command.run), "safe_command.run should be callable"
        except ImportError:
            pytest.skip("Security module not available for testing")
