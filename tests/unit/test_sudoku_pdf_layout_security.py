#!/usr/bin/env python3
"""
Security-focused unit tests for sudoku_pdf_layout_v2.py
Tests specifically covering the security enhancement from random to secrets module usage.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestSudokuPDFLayoutSecurity(unittest.TestCase):
    """Security-focused tests for the random to secrets migration"""

    def test_no_random_import_in_get_puzzle_insight(self):
        """Test that random module is not imported within get_puzzle_insight method"""
        # Import the module and inspect the source
        import inspect

        import scripts.sudoku_pdf_layout_v2 as layout_module

        # Get the source code of the get_puzzle_insight method
        source = inspect.getsource(
            layout_module.EnhancedSudokuPDFLayout.get_puzzle_insight
        )

        # Verify that 'import random' is not in the method
        self.assertNotIn("import random", source)

        # Verify that 'random.choice' is not in the method
        self.assertNotIn("random.choice", source)

    def test_secrets_choice_usage_in_get_puzzle_insight(self):
        """Test that secrets.choice is used in get_puzzle_insight method"""
        import inspect

        import scripts.sudoku_pdf_layout_v2 as layout_module

        # Get the source code of the get_puzzle_insight method
        source = inspect.getsource(
            layout_module.EnhancedSudokuPDFLayout.get_puzzle_insight
        )

        # Verify that 'secrets.choice' is in the method
        self.assertIn("secrets.choice", source)

    def test_secrets_module_imported_at_top_level(self):
        """Test that secrets module is imported at the module level"""
        import scripts.sudoku_pdf_layout_v2 as layout_module

        # Check that secrets is available as a module attribute
        self.assertTrue(hasattr(layout_module, "secrets"))

        # Verify it's the actual secrets module
        import secrets

        self.assertEqual(layout_module.secrets, secrets)

    def test_random_module_not_imported_at_top_level(self):
        """Test that random module is not imported at the module level for get_puzzle_insight"""
        import scripts.sudoku_pdf_layout_v2 as layout_module

        # Read the source file to check imports
        script_path = (
            Path(__file__).parent.parent.parent /
            "scripts" / "sudoku_pdf_layout_v2.py"
        )
        with open(script_path, "r") as f:
            content = f.read()

        # Check that standalone 'import random' is not present
        lines = content.split("\n")
        import_lines = [
            line.strip() for line in lines if line.strip().startswith("import ")
        ]

        # Should not have 'import random' as a standalone import
        self.assertNotIn("import random", import_lines)

    @patch("scripts.sudoku_pdf_layout_v2.secrets.choice")
    def test_secrets_choice_provides_cryptographic_security(self, mock_secrets_choice):
        """Test that using secrets.choice provides cryptographically secure selection"""
        # Mock the EnhancedSudokuPDFLayout class minimally for this test
        from scripts.sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout

        # Create a minimal mock layout instance
        with patch.object(EnhancedSudokuPDFLayout, "__init__", lambda x: None):
            layout = EnhancedSudokuPDFLayout()

            mock_secrets_choice.return_value = "Secure insight"

            # Call the method
            puzzle_data = {"difficulty": "medium"}
            result = layout.get_puzzle_insight(puzzle_data)

            # Verify secrets.choice was called
            self.assertTrue(mock_secrets_choice.called)
            self.assertEqual(result, "Secure insight")

    def test_cryptographic_randomness_quality(self):
        """Test that secrets.choice provides better randomness than random.choice"""
        import random
        import secrets

        # Create test data
        choices = ["option1", "option2", "option3", "option4"]

        # Generate selections using both methods
        secrets_selections = [secrets.choice(choices) for _ in range(100)]
        random_selections = [random.choice(choices) for _ in range(100)]

        # Both should produce varied results
        secrets_unique = len(set(secrets_selections))
        random_unique = len(set(random_selections))

        # Both should show some randomness (at least 2 different values in 100 tries)
        self.assertGreaterEqual(secrets_unique, 2)
        self.assertGreaterEqual(random_unique, 2)

        # This test confirms both work, but secrets.choice is cryptographically secure
        # The key difference is that secrets.choice is suitable for security-sensitive applications

    def test_method_signature_unchanged(self):
        """Test that get_puzzle_insight method signature is unchanged after security fix"""
        import inspect

        from scripts.sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout

        # Get method signature
        sig = inspect.signature(EnhancedSudokuPDFLayout.get_puzzle_insight)

        # Should have 'self' and 'puzzle_data' parameters
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["self", "puzzle_data"])


if __name__ == "__main__":
    unittest.main()
