#!/usr/bin/env python3
"""Unit tests for claude_costs.py script"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestClaudeCosts:
    """Test suite for claude_costs.py functionality"""

    @patch('scripts.claude_costs.ClaudeCostTracker')
    def test_init_command(self, mock_tracker):
        """Test the init command functionality"""
        from scripts.claude_costs import main
        
        # Mock the tracker
        mock_instance = Mock()
        mock_instance.track_commit.return_value = {"status": "initialized"}
        mock_tracker.return_value = mock_instance
        
        # Test init command
        with patch('sys.argv', ['claude_costs.py', 'init']):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call("✅ Claude cost tracking initialized!")

    @patch('scripts.claude_costs.ClaudeCostTracker')
    @patch('security.safe_command')
    @patch('sys.executable', '/usr/bin/python3')
    def test_badge_command_success(self, mock_safe_command, mock_tracker):
        """Test successful badge generation with security wrapper"""
        from scripts.claude_costs import main
        
        # Mock the tracker
        mock_instance = Mock()
        mock_tracker.return_value = mock_instance
        
        # Mock successful safe_command.run
        mock_result = Mock()
        mock_result.stdout = "Badge generated successfully!"
        mock_safe_command.run.return_value = mock_result
        
        # Test badge command
        with patch('sys.argv', ['claude_costs.py', 'badge']):
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify safe_command.run was called with correct parameters
                mock_safe_command.run.assert_called_once()
                args, kwargs = mock_safe_command.run.call_args
                
                # Check that subprocess.run was passed as first argument
                assert args[0] == subprocess.run
                
                # Check the command arguments include python executable and script path
                command_args = args[1]
                assert command_args[0] == '/usr/bin/python3'
                assert 'generate_cost_badge.py' in str(command_args[1])
                
                # Check keyword arguments
                assert kwargs['capture_output'] is True
                assert kwargs['text'] is True
                assert kwargs['check'] is True
                
                # Verify output was printed
                mock_print.assert_called_with("Badge generated successfully!")

    @patch('scripts.claude_costs.ClaudeCostTracker')
    @patch('security.safe_command')
    def test_badge_command_failure(self, mock_safe_command, mock_tracker):
        """Test badge generation failure handling"""
        from scripts.claude_costs import main
        
        # Mock the tracker
        mock_instance = Mock()
        mock_tracker.return_value = mock_instance
        
        # Mock subprocess.CalledProcessError
        error = subprocess.CalledProcessError(1, ['python', 'script.py'])
        error.stderr = "Script execution failed"
        mock_safe_command.run.side_effect = error
        
        # Test badge command with failure
        with patch('sys.argv', ['claude_costs.py', 'badge']):
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify error message was printed
                mock_print.assert_called_with("❌ Badge generation failed: Script execution failed")

    @patch('scripts.claude_costs.ClaudeCostTracker')
    def test_status_command(self, mock_tracker):
        """Test status command functionality"""
        from scripts.claude_costs import main
        
        # Mock the tracker with sample data
        mock_instance = Mock()
        mock_instance.load_commit_costs.return_value = {
            "commits": [
                {
                    "hash": "abc123",
                    "cost": 0.05,
                    "files_changed": 3,
                    "message": "Test commit"
                }
            ],
            "total_cost": 0.05,
            "first_tracked": "2023-01-01T00:00:00",
            "last_updated": "2023-01-01T12:00:00"
        }
        mock_instance.load_last_commit_cost.return_value = {
            "full_repo_cost": 1.25,
            "worktree_cost": 0.30,
            "savings_potential": 0.95
        }
        mock_tracker.return_value = mock_instance
        
        # Test status command
        with patch('sys.argv', ['claude_costs.py', 'status']):
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify status information was printed
                mock_print.assert_any_call("📊 Claude Cost Tracking Status")
                # Check that cost formatting is called
                print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
                assert any("Total tracked cost:" in str(call) for call in print_calls)
