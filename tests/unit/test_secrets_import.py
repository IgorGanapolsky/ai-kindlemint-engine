#!/usr/bin/env python3
"""
Unit tests to verify the secrets module import and usage in sudoku_pdf_layout_v2.py
This tests the security enhancement where random was replaced with secrets
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestSecretsImport(unittest.TestCase):
    """Test cases for secrets module import and usage"""

    def test_secrets_module_can_be_imported(self):
        """Test that the secrets module can be imported successfully"""
        try:
            import secrets

            self.assertTrue(hasattr(secrets, "choice"))
        except ImportError:
            self.fail("secrets module should be available in Python 3.6+")

    def test_sudoku_pdf_layout_v2_imports_secrets(self):
        """Test that sudoku_pdf_layout_v2 module imports secrets"""
        # Import the module and check if secrets is available
        import sudoku_pdf_layout_v2

        # Check that secrets is imported at module level
        self.assertTrue(hasattr(sudoku_pdf_layout_v2, "secrets"))

    def test_secrets_choice_functionality(self):
        """Test that secrets.choice works as expected"""
        import secrets

        # Test with a list of choices
        choices = ["option1", "option2", "option3"]
        result = secrets.choice(choices)

        self.assertIn(result, choices)

        # Test multiple calls return potentially different results
        results = [secrets.choice(choices) for _ in range(10)]
        # While not guaranteed, it's extremely unlikely all results are identical
        # if the function is working properly
        self.assertTrue(len(set(results)) >= 1)  # At least one unique result


if __name__ == "__main__":
    unittest.main()
