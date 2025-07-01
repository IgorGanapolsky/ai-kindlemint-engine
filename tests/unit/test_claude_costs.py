#!/usr/bin/env python3
"""
Unit tests for scripts/claude_costs.py
Tests the security integration and subprocess execution changes
"""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch


class TestClaudeCostsSecurityIntegration(unittest.TestCase):
    """Test security integration in claude_costs.py"""

    def setUp(self):
        """Set up test environment"""
        self.script_path = Path(__file__).parent.parent.parent / "scripts" / "claude_costs.py"
        self.assertTrue(self.script_path.exists(), f"Script not found: {self.script_path}")

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    def test_security_import(self, mock_tracker, mock_safe_command):
        """Test that security.safe_command is properly imported"""
        # Import the main function from claude_costs
        import sys
        sys.path.insert(0, str(self.script_path.parent))
        
        try:
            import claude_costs
            # Verify the module can be imported without errors
            self.assertTrue(hasattr(claude_costs, 'main'))
        except ImportError as e:
            if "security" in str(e):
                # This is expected if security package isn't installed in test environment
                self.skipTest("Security package not available in test environment")
            else:
                raise

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    def test_badge_command_uses_safe_command(self, mock_tracker, mock_safe_command):
        """Test that badge command uses safe_command.run for subprocess execution"""
        # Mock the safe_command.run method
        mock_result = Mock()
        mock_result.stdout = "Badge generated successfully"
        mock_safe_command.run.return_value = mock_result
        
        # Mock the tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        import sys
        sys.path.insert(0, str(self.script_path.parent))
        
        try:
            import claude_costs
            claude_costs.main()
            
            # Verify safe_command.run was called with correct parameters
            mock_safe_command.run.assert_called_once()
            call_args = mock_safe_command.run.call_args
            
            # Check that subprocess.run was passed as first argument
            self.assertEqual(call_args[0][0], subprocess.run)
            
            # Check that the command includes python executable and badge script
            command_args = call_args[0][1]
            self.assertEqual(command_args[0], sys.executable)
            self.assertTrue(str(command_args[1]).endswith("generate_cost_badge.py"))
            
            # Check that subprocess options are preserved
            self.assertTrue(call_args[1]['capture_output'])
            self.assertTrue(call_args[1]['text'])
            self.assertTrue(call_args[1]['check'])
            
        except ImportError as e:
            if "security" in str(e):
                self.skipTest("Security package not available in test environment")
            else:
                raise

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    def test_badge_command_handles_safe_command_error(self, mock_tracker, mock_safe_command):
        """Test that badge command handles CalledProcessError from safe_command"""
        # Mock safe_command.run to raise CalledProcessError
        error = subprocess.CalledProcessError(1, ['python', 'script.py'])
        error.stderr = "Script execution failed"
        mock_safe_command.run.side_effect = error
        
        # Mock the tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        import sys
        sys.path.insert(0, str(self.script_path.parent))
        
        try:
            import claude_costs
            
            # Capture stdout to verify error message
            from io import StringIO
            captured_output = StringIO()
            
            with patch('sys.stdout', captured_output):
                claude_costs.main()
            
            output = captured_output.getvalue()
            self.assertIn("Badge generation failed", output)
            self.assertIn("Script execution failed", output)
            
        except ImportError as e:
            if "security" in str(e):
                self.skipTest("Security package not available in test environment")
            else:
                raise

    @patch('security.safe_command')
    @patch('kindlemint.utils.cost_tracker.ClaudeCostTracker')
    @patch('sys.argv', ['claude_costs.py', 'badge'])
    def test_badge_command_success_output(self, mock_tracker, mock_safe_command):
        """Test that badge command prints stdout on success"""
        # Mock successful execution
        mock_result = Mock()
        mock_result.stdout = "✅ Badge updated successfully\nGenerated cost badge"
        mock_safe_command.run.return_value = mock_result
        
        # Mock the tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Import and run the main function
        import sys
        sys.path.insert(0, str(self.script_path.parent))
        
        try:
            import claude_costs
            
            # Capture stdout to verify success message
            from io import StringIO
            captured_output = StringIO()
            
            with patch('sys.stdout', captured_output):
                claude_costs.main()
            
            output = captured_output.getvalue()
            self.assertIn("Badge updated successfully", output)
            self.assertIn("Generated cost badge", output)
            
        except ImportError as e:
            if "security" in str(e):
                self.skipTest("Security package not available in test environment")
            else:
                raise


if __name__ == '__main__':
    unittest.main()
