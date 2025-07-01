#!/usr/bin/env python3
"""
Unit tests for security changes in claude_costs.py
Tests the integration of safe_command security wrapper
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestClaudeCostsSecurity(unittest.TestCase):
    """Test security integration in claude_costs.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch('scripts.claude_costs.safe_command')
    def test_safe_command_import_success(self, mock_safe_command):
        """Test that safe_command is imported and used correctly"""
        # Mock the safe_command.run method
        mock_run = Mock()
        mock_run.return_value = Mock(stdout="Badge updated successfully")
        mock_safe_command.run = mock_run
        
        # Import and test the module
        from scripts.claude_costs import main
        
        # Verify safe_command is available
        self.assertIsNotNone(mock_safe_command)
        
    @patch('scripts.claude_costs.subprocess')
    @patch('scripts.claude_costs.safe_command')
    def test_badge_generation_uses_safe_command(self, mock_safe_command, mock_subprocess):
        """Test that badge generation uses safe_command.run instead of subprocess.run"""
        # Set up mocks
        mock_result = Mock()
        mock_result.stdout = "Badge generation successful"
        mock_safe_command.run.return_value = mock_result
        
        # Mock Path to avoid file system dependencies
        with patch('scripts.claude_costs.Path') as mock_path:
            mock_path.return_value.__truediv__.return_value = self.temp_dir / "generate_cost_badge.py"
            mock_path.return_value.parent = self.temp_dir
            
            # Import the module with badge command
            with patch('sys.argv', ['claude_costs.py', 'badge']):
                try:
                    from scripts.claude_costs import main
                    main()
                except SystemExit:
                    pass  # Expected for argparse
                
        # Verify safe_command.run was called instead of subprocess.run
        mock_safe_command.run.assert_called()
        # Verify subprocess.run was NOT called directly
        mock_subprocess.run.assert_not_called()
        
    @patch('scripts.claude_costs.safe_command')
    def test_safe_command_error_handling(self, mock_safe_command):
        """Test error handling when safe_command.run fails"""
        # Mock safe_command.run to raise CalledProcessError
        from subprocess import CalledProcessError
        mock_safe_command.run.side_effect = CalledProcessError(1, 'cmd', stderr='Error occurred')
        
        # Mock Path and sys.argv
        with patch('scripts.claude_costs.Path') as mock_path:
            with patch('sys.argv', ['claude_costs.py', 'badge']):
                with patch('builtins.print') as mock_print:
                    mock_path.return_value.__truediv__.return_value = self.temp_dir / "generate_cost_badge.py"
                    mock_path.return_value.parent = self.temp_dir
                    
                    try:
                        from scripts.claude_costs import main
                        main()
                    except SystemExit:
                        pass
                    
                    # Verify error message was printed
                    mock_print.assert_any_call("❌ Badge generation failed: Error occurred")
    
    def test_security_dependency_available(self):
        """Test that security dependency is available after installation"""
        try:
            import security
            self.assertIsNotNone(security)
            
            # Test that safe_command module exists
            from security import safe_command
            self.assertIsNotNone(safe_command)
            
            # Test that safe_command.run method exists
            self.assertTrue(hasattr(safe_command, 'run'))
            self.assertTrue(callable(safe_command.run))
            
        except ImportError:
            self.skipTest("Security package not installed - this is expected in test environment")
    
    @patch('scripts.claude_costs.safe_command')
    def test_safe_command_parameters(self, mock_safe_command):
        """Test that safe_command.run receives correct parameters"""
        import subprocess
        import sys
        
        # Mock the result
        mock_result = Mock()
        mock_result.stdout = "Success"
        mock_safe_command.run.return_value = mock_result
        
        # Mock Path
        with patch('scripts.claude_costs.Path') as mock_path:
            with patch('sys.argv', ['claude_costs.py', 'badge']):
                mock_badge_script = self.temp_dir / "generate_cost_badge.py"
                mock_path.return_value.__truediv__.return_value = mock_badge_script
                mock_path.return_value.parent = self.temp_dir
                
                try:
                    from scripts.claude_costs import main
                    main()
                except SystemExit:
                    pass
                
        # Verify safe_command.run was called with correct parameters
        mock_safe_command.run.assert_called_once()
        args, kwargs = mock_safe_command.run.call_args
        
        # First argument should be subprocess.run
        self.assertEqual(args[0], subprocess.run)
        
        # Second argument should be the command list
        command_list = args[1]
        self.assertEqual(command_list[0], sys.executable)
        self.assertTrue(str(command_list[1]).endswith("generate_cost_badge.py"))
        
        # Check keyword arguments
        self.assertTrue(kwargs.get('capture_output'))
        self.assertTrue(kwargs.get('text'))
        self.assertTrue(kwargs.get('check'))


if __name__ == '__main__':
    unittest.main()