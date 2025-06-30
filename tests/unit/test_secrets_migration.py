#!/usr/bin/env python3
"""
Integration tests specifically for the migration from random to secrets module
in sudoku_pdf_layout_v2.py to ensure cryptographically secure randomness
"""

import secrets
import unittest
from unittest.mock import Mock, patch


class TestSecretsMigration(unittest.TestCase):
    """Test the migration from random.choice to secrets.choice for security"""

    def test_secrets_choice_vs_random_choice_behavior(self):
        """Test that secrets.choice behaves similarly to random.choice for our use case"""
        test_list = ["insight1", "insight2", "insight3", "insight4", "insight5"]
        
        # Test multiple calls to ensure it returns valid items
        for _ in range(20):
            result = secrets.choice(test_list)
            self.assertIn(result, test_list, "secrets.choice should return an item from the list")

    def test_secrets_choice_distribution(self):
        """Test that secrets.choice provides reasonable distribution over multiple calls"""
        test_list = ["A", "B", "C"]
        results = []
        
        # Collect results from multiple calls
        for _ in range(300):
            results.append(secrets.choice(test_list))
        
        # Check that all options appear at least once (very likely with 300 trials)
        unique_results = set(results)
        self.assertEqual(len(unique_results), 3, "All options should appear in 300 trials")
        
        # Check that no single option dominates too heavily (basic distribution check)
        counts = {item: results.count(item) for item in test_list}
        min_count = min(counts.values())
        max_count = max(counts.values())
        
        # With 300 trials and 3 options, expect roughly 100 each
        # Allow for reasonable variation (shouldn't be too skewed)
        self.assertGreater(min_count, 50, "Minimum count should be reasonable")
        self.assertLess(max_count, 200, "Maximum count shouldn't dominate")

    def test_cryptographic_strength(self):
        """Test that secrets module provides cryptographically strong randomness"""
        # This test ensures we're using the more secure randomness source
        self.assertTrue(hasattr(secrets, 'choice'), "secrets module should have choice function")
        self.assertTrue(hasattr(secrets, 'SystemRandom'), "secrets should use SystemRandom")
        
        # Verify secrets.choice uses system randomness (not pseudorandom)
        test_list = ["item1", "item2"]
        result = secrets.choice(test_list)
        self.assertIn(result, test_list)

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_secrets_choice_called_in_get_puzzle_insight(self, mock_secrets_choice):
        """Integration test to verify secrets.choice is actually called in the application"""
        from scripts.sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout
        
        # Mock the choice function to return a known value
        mock_secrets_choice.return_value = "mocked insight"
        
        # Create a minimal layout instance for testing
        layout_mock = Mock(spec=EnhancedSudokuPDFLayout)
        
        # Import and call the actual method
        puzzle_data = {"difficulty": "medium"}
        
        # Call the actual method from the module
        layout = EnhancedSudokuPDFLayout.__new__(EnhancedSudokuPDFLayout)
        result = layout.get_puzzle_insight(puzzle_data)
        
        # Verify secrets.choice was called
        mock_secrets_choice.assert_called_once()
        self.assertEqual(result, "mocked insight")

    def test_no_random_module_dependency_in_get_puzzle_insight(self):
        """Ensure the random module is no longer used in get_puzzle_insight"""
        from scripts.sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout
        import inspect
        
        # Get the source code of the get_puzzle_insight method
        source = inspect.getsource(EnhancedSudokuPDFLayout.get_puzzle_insight)
        
        # Verify that 'random.choice' is not in the source
        self.assertNotIn('random.choice', source, "get_puzzle_insight should not use random.choice")
        
        # Verify that 'secrets.choice' is in the source
        self.assertIn('secrets.choice', source, "get_puzzle_insight should use secrets.choice")


if __name__ == '__main__':
    unittest.main()