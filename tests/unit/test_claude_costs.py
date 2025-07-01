#!/usr/bin/env python3
"""
Unit tests for claude_costs.py script
Tests the security enhancement replacing subprocess.run with safe_command.run
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

# Import the module under test
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))
from claude_costs import format_currency, main


class TestFormatCurrency:
    """Test the format_currency function"""

    def test_format_currency_very_small(self):
        """Test formatting very small amounts"""
        result = format_currency(0.000123)
        assert result == "$0.000123"

    def test_format_currency_small(self):
        """Test formatting small amounts less than $1"""
        result = format_currency(0.1234)
        assert result == "$0.1234"

    def test_format_currency_normal(self):
        """Test formatting normal amounts"""
        result = format_currency(12.34)
        assert result == "$12.34"

    def test_format_currency_large(self):
        """Test formatting large amounts"""
        result = format_currency(1234.56)
        assert result == "$1234.56"


class TestClaudeCosts:
    """Test the main claude_costs functionality"""

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "init"])
    def test_init_command(self, mock_tracker_class):
        """Test the init command"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker
        mock_tracker.track_commit.return_value = {"status": "tracked"}

        main()

        mock_tracker.track_commit.assert_called_once_with(
            "Initial Claude cost tracking setup"
        )

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "status"])
    def test_status_command_with_data(self, mock_tracker_class):
        """Test the status command with existing data"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        mock_commit_costs = {
            "total_cost": 1.23,
            "commits": [
                {
                    "hash": "abc123",
                    "cost": 0.45,
                    "files_changed": 3,
                    "message": "Test commit message for testing purposes",
                }
            ],
            "first_tracked": "2024-01-01T00:00:00",
            "last_updated": "2024-01-01T12:00:00Z",
        }

        mock_last_cost = {
            "full_repo_cost": 5.67,
            "worktree_cost": 2.34,
            "savings_potential": 3.33,
        }

        mock_tracker.load_commit_costs.return_value = mock_commit_costs
        mock_tracker.load_last_commit_cost.return_value = mock_last_cost

        main()

        mock_tracker.load_commit_costs.assert_called_once()
        mock_tracker.load_last_commit_cost.assert_called_once()

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "status"])
    def test_status_command_no_data(self, mock_tracker_class):
        """Test the status command with no existing data"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        mock_tracker.load_commit_costs.return_value = {"commits": []}
        mock_tracker.load_last_commit_cost.return_value = {
            "full_repo_cost": 0.0,
            "worktree_cost": 0.0,
            "savings_potential": 0.0,
        }

        main()

        mock_tracker.load_commit_costs.assert_called_once()
        mock_tracker.load_last_commit_cost.assert_called_once()

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "track", "--model", "claude-3-haiku", "--message", "Test commit"])
    def test_track_command_success(self, mock_tracker_class):
        """Test the track command with successful tracking"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker
        mock_tracker.track_commit.return_value = {
            "status": "tracked",
            "cost": 0.15,
            "tokens": 1000,
            "files": 2,
        }

        main()

        mock_tracker.track_commit.assert_called_once_with("Test commit", "claude-3-haiku")

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "track"])
    def test_track_command_no_changes(self, mock_tracker_class):
        """Test the track command with no changes to track"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker
        mock_tracker.track_commit.return_value = {"status": "no_changes"}

        main()

        mock_tracker.track_commit.assert_called_once_with("", "claude-3-sonnet")

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "summary", "--days", "7"])
    def test_summary_command_success(self, mock_tracker_class):
        """Test the summary command with successful data"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        mock_summary = {
            "commit_count": 5,
            "total_cost": 2.50,
            "total_tokens": 10000,
            "average_cost_per_commit": 0.50,
            "most_expensive_commit": {
                "hash": "def456",
                "cost": 1.00,
                "files_changed": 5,
                "tokens": 5000,
                "message": "Large commit with many changes for testing purposes and more",
            },
        }

        mock_tracker.get_cost_summary.return_value = mock_summary

        main()

        mock_tracker.get_cost_summary.assert_called_once_with(7)

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "summary"])
    def test_summary_command_error(self, mock_tracker_class):
        """Test the summary command with error"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker
        mock_tracker.get_cost_summary.return_value = {"error": "No data available"}

        main()

        mock_tracker.get_cost_summary.assert_called_once_with(30)

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "details", "--last", "3"])
    def test_details_command_with_data(self, mock_tracker_class):
        """Test the details command with commit data"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        mock_commits = {
            "commits": [
                {
                    "hash": "abc123",
                    "timestamp": "2024-01-01T12:00:00",
                    "cost": 0.25,
                    "files_changed": 2,
                    "tokens": 1000,
                    "message": "First commit",
                },
                {
                    "hash": "def456",
                    "timestamp": "2024-01-01T13:00:00",
                    "cost": 0.50,
                    "files_changed": 3,
                    "tokens": 2000,
                    "message": "Second commit with a very long message that should be truncated",
                },
            ]
        }

        mock_tracker.load_commit_costs.return_value = mock_commits

        main()

        mock_tracker.load_commit_costs.assert_called_once()

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "details"])
    def test_details_command_no_data(self, mock_tracker_class):
        """Test the details command with no commit data"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker
        mock_tracker.load_commit_costs.return_value = {"commits": []}

        main()

        mock_tracker.load_commit_costs.assert_called_once()

    @patch("claude_costs.ClaudeCostTracker")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.argv", ["claude_costs", "export", "costs.csv"])
    def test_export_command_csv(self, mock_file, mock_tracker_class):
        """Test the export command with CSV format"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        mock_commits = {
            "commits": [
                {
                    "hash": "abc123",
                    "timestamp": "2024-01-01T12:00:00",
                    "cost": 0.25,
                    "tokens": 1000,
                    "files_changed": 2,
                    "model": "claude-3-sonnet",
                    "message": "Test commit",
                }
            ]
        }

        mock_tracker.load_commit_costs.return_value = mock_commits

        with patch("csv.writer") as mock_csv_writer:
            mock_writer = Mock()
            mock_csv_writer.return_value = mock_writer

            main()

            mock_writer.writerow.assert_any_call(
                ["Hash", "Timestamp", "Cost", "Tokens", "Files", "Model", "Message"]
            )
            mock_writer.writerow.assert_any_call(
                ["abc123", "2024-01-01T12:00:00", 0.25, 1000, 2, "claude-3-sonnet", "Test commit"]
            )

    @patch("claude_costs.ClaudeCostTracker")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.argv", ["claude_costs", "export", "costs.json"])
    def test_export_command_json(self, mock_file, mock_tracker_class):
        """Test the export command with JSON format"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        mock_commits = {"commits": []}
        mock_tracker.load_commit_costs.return_value = mock_commits

        with patch("json.dump") as mock_json_dump:
            main()
            mock_json_dump.assert_called_once_with(mock_commits, mock_file.return_value, indent=2)

    @patch("claude_costs.ClaudeCostTracker")
    @patch("sys.argv", ["claude_costs", "export", "costs.txt"])
    def test_export_command_unsupported_format(self, mock_tracker_class):
        """Test the export command with unsupported format"""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker
        mock_tracker.load_commit_costs.return_value = {"commits": []}

        main()

        mock_tracker.load_commit_costs.assert_called_once()

    @patch("claude_costs.Path")
    @patch("claude_costs.sys")
    @patch("security.safe_command")
    @patch("sys.argv", ["claude_costs", "badge"])
    def test_badge_command_success(self, mock_safe_command, mock_sys, mock_path):
        """Test the badge command with successful execution using safe_command"""
        # Setup mocks
        mock_file = Mock()
        mock_file.parent = Path("/scripts")
        mock_path.return_value = mock_file
        
        mock_badge_script = Path("/scripts/generate_cost_badge.py")
        mock_file.parent.__truediv__ = Mock(return_value=mock_badge_script)
        
        mock_sys.executable = "/usr/bin/python3"
        
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.stdout = "✅ Badge generated successfully!"
        mock_safe_command.run.return_value = mock_result
        
        with patch("claude_costs.ClaudeCostTracker"):
            main()
        
        # Verify safe_command.run was called instead of subprocess.run
        mock_safe_command.run.assert_called_once_with(
            subprocess.run,
            ["/usr/bin/python3", str(mock_badge_script)],
            capture_output=True,
            text=True,
            check=True
        )

    @patch("claude_costs.Path")
    @patch("claude_costs.sys") 
    @patch("security.safe_command")
    @patch("sys.argv", ["claude_costs", "badge"])
    def test_badge_command_failure(self, mock_safe_command, mock_sys, mock_path):
        """Test the badge command with subprocess failure using safe_command"""
        # Setup mocks
        mock_file = Mock()
        mock_file.parent = Path("/scripts")
        mock_path.return_value = mock_file
        
        mock_badge_script = Path("/scripts/generate_cost_badge.py")
        mock_file.parent.__truediv__ = Mock(return_value=mock_badge_script)
        
        mock_sys.executable = "/usr/bin/python3"
        
        # Mock subprocess failure
        mock_error = subprocess.CalledProcessError(1, "cmd", stderr="Error message")
        mock_safe_command.run.side_effect = mock_error
        
        with patch("claude_costs.ClaudeCostTracker"):
            main()
        
        # Verify safe_command.run was called and exception was handled
        mock_safe_command.run.assert_called_once()

    @patch("sys.argv", ["claude_costs"])
    def test_no_command_shows_help(self):
        """Test that running without command shows help"""
        with patch("argparse.ArgumentParser.print_help") as mock_help:
            main()
            mock_help.assert_called_once()

    @patch("sys.argv", ["claude_costs", "--help"])
    def test_help_command(self):
        """Test help command exits gracefully"""
        with pytest.raises(SystemExit):
            main()
