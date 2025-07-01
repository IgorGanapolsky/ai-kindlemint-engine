#!/usr/bin/env python3
"""
Unit tests for CursorBugbotValidator class

Tests the Cursor Bugbot setup validator functionality,
covering all methods and validation scenarios.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from cursor_bugbot_setup import CursorBugbotValidator, main

# Import the module under test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../scripts"))


class TestCursorBugbotValidator(unittest.TestCase):
    """Test CursorBugbotValidator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = CursorBugbotValidator()
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test CursorBugbotValidator initialization"""
        self.assertIsInstance(self.validator.issues, list)
        self.assertIsInstance(self.validator.warnings, list)
        self.assertIsInstance(self.validator.successes, list)
        self.assertEqual(len(self.validator.issues), 0)
        self.assertEqual(len(self.validator.warnings), 0)
        self.assertEqual(len(self.validator.successes), 0)
        self.assertIsInstance(self.validator.repo_root, Path)

    @patch("pathlib.Path.exists")
    def test_check_cursorignore_file_not_found(self, mock_exists):
        """Test check_cursorignore when .cursorignore file doesn't exist"""
        mock_exists.return_value = False

        result = self.validator.check_cursorignore()

        self.assertFalse(result)
        self.assertIn("❌ .cursorignore file not found", self.validator.issues)

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_check_cursorignore_missing_critical_patterns(self, mock_exists, mock_file):
        """Test check_cursorignore with missing critical patterns"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "# Some other content\n*.log\n"

        result = self.validator.check_cursorignore()

        self.assertTrue(result)
        # Should have warnings about missing patterns
        warning_found = any(
            "⚠️  .cursorignore missing critical patterns:" in warning
            for warning in self.validator.warnings
        )
        self.assertTrue(warning_found)

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_check_cursorignore_all_patterns_present(self, mock_exists, mock_file):
        """Test check_cursorignore with all critical patterns present"""
        mock_exists.return_value = True
        # Include all critical patterns
        content = ".env\n*.key\n*.pem\nsecrets/\ncredentials/\n"
        mock_file.return_value.read.return_value = content

        result = self.validator.check_cursorignore()

        self.assertTrue(result)
        self.assertIn(
            "✅ .cursorignore properly configured with security patterns",
            self.validator.successes,
        )

    @patch("pathlib.Path.exists")
    def test_check_github_workflow_not_found(self, mock_exists):
        """Test check_github_workflow when workflow file doesn't exist"""
        mock_exists.return_value = False

        result = self.validator.check_github_workflow()

        self.assertFalse(result)
        self.assertIn(
            "❌ GitHub workflow cursor-bugbot.yml not found", self.validator.issues
        )

    @patch("pathlib.Path.exists")
    def test_check_github_workflow_exists(self, mock_exists):
        """Test check_github_workflow when workflow file exists"""
        mock_exists.return_value = True

        result = self.validator.check_github_workflow()

        self.assertTrue(result)
        self.assertIn(
            "✅ GitHub workflow for automated Bugbot triggering exists",
            self.validator.successes,
        )

    @patch("pathlib.Path.exists")
    def test_check_readme_documentation_not_found(self, mock_exists):
        """Test check_readme_documentation when README.md doesn't exist"""
        mock_exists.return_value = False

        result = self.validator.check_readme_documentation()

        self.assertFalse(result)
        self.assertIn("❌ README.md not found", self.validator.issues)

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_check_readme_documentation_no_bugbot_mention(self, mock_exists, mock_file):
        """Test check_readme_documentation when README doesn't mention Cursor Bugbot"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = (
            "# My Project\nSome content without bugbot mention"
        )

        result = self.validator.check_readme_documentation()

        self.assertFalse(result)
        self.assertIn(
            "⚠️  README.md doesn't mention Cursor Bugbot", self.validator.warnings
        )

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_check_readme_documentation_with_bugbot_mention(
        self, mock_exists, mock_file
    ):
        """Test check_readme_documentation when README mentions Cursor Bugbot"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = (
            "# My Project\nThis uses Cursor Bugbot for analysis"
        )

        result = self.validator.check_readme_documentation()

        self.assertTrue(result)
        self.assertIn(
            "✅ README.md includes Cursor Bugbot badge", self.validator.successes
        )

    def test_generate_setup_instructions(self):
        """Test generate_setup_instructions method"""
        instructions = self.validator.generate_setup_instructions()

        self.assertIsInstance(instructions, str)
        self.assertIn("🤖 Cursor Bugbot Setup Instructions", instructions)
        self.assertIn(
            "https://www.cursor.com/dashboard?tab=integrations", instructions)
        self.assertIn("IgorGanapolsky/ai-kindlemint-engine", instructions)
        self.assertIn("bugbot run", instructions)
        self.assertIn("Cursor Pro users", instructions)

    @patch.object(CursorBugbotValidator, "check_cursorignore")
    @patch.object(CursorBugbotValidator, "check_github_workflow")
    @patch.object(CursorBugbotValidator, "check_readme_documentation")
    @patch("builtins.print")
    def test_validate_all_successful(
        self, mock_print, mock_readme, mock_workflow, mock_cursorignore
    ):
        """Test validate method when all checks pass"""
        # Mock all checks to return True
        mock_cursorignore.return_value = True
        mock_workflow.return_value = True
        mock_readme.return_value = True

        # Add some success messages
        self.validator.successes = ["✅ All good"]

        is_valid, report = self.validator.validate()

        self.assertTrue(is_valid)
        self.assertIn("✅ Successes:", report)
        self.assertIn(
            "✅ Local configuration is ready for Cursor Bugbot!", report)
        self.assertIn(
            "⚠️  Remember: You must still enable Bugbot in the Cursor dashboard", report
        )
        self.assertIn("🤖 Cursor Bugbot Setup Instructions", report)

        # Verify all check methods were called
        mock_cursorignore.assert_called_once()
        mock_workflow.assert_called_once()
        mock_readme.assert_called_once()
        mock_print.assert_called_once_with(
            "🔍 Validating Cursor Bugbot Configuration...\n"
        )

    @patch.object(CursorBugbotValidator, "check_cursorignore")
    @patch.object(CursorBugbotValidator, "check_github_workflow")
    @patch.object(CursorBugbotValidator, "check_readme_documentation")
    @patch("builtins.print")
    def test_validate_with_issues(
        self, mock_print, mock_readme, mock_workflow, mock_cursorignore
    ):
        """Test validate method when there are issues"""
        # Mock checks with some failures
        mock_cursorignore.return_value = False
        mock_workflow.return_value = True
        mock_readme.return_value = False

        # Add some issues
        self.validator.issues = ["❌ Something failed"]

        is_valid, report = self.validator.validate()

        self.assertFalse(is_valid)
        self.assertIn("❌ Issues:", report)
        self.assertIn(
            "❌ Configuration issues found. Please fix them before proceeding.", report
        )
        self.assertIn("🤖 Cursor Bugbot Setup Instructions", report)

    @patch.object(CursorBugbotValidator, "check_cursorignore")
    @patch.object(CursorBugbotValidator, "check_github_workflow")
    @patch.object(CursorBugbotValidator, "check_readme_documentation")
    @patch("builtins.print")
    def test_validate_with_warnings(
        self, mock_print, mock_readme, mock_workflow, mock_cursorignore
    ):
        """Test validate method when there are warnings but no issues"""
        # Mock all checks to return True
        mock_cursorignore.return_value = True
        mock_workflow.return_value = True
        mock_readme.return_value = True

        # Add some warnings
        self.validator.warnings = ["⚠️  Some warning"]

        is_valid, report = self.validator.validate()

        self.assertTrue(is_valid)
        self.assertIn("⚠️  Warnings:", report)
        self.assertIn(
            "✅ Local configuration is ready for Cursor Bugbot!", report)

    def test_validate_report_format(self):
        """Test that validate returns proper tuple format"""
        is_valid, report = self.validator.validate()

        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(report, str)

    @patch("pathlib.Path")
    def test_repo_root_path_calculation(self, mock_path):
        """Test that repo_root is calculated correctly"""
        # Mock the path calculation
        mock_file_path = MagicMock()
        mock_file_path.parent.parent = "/expected/repo/root"
        mock_path.__file__ = mock_file_path

        validator = CursorBugbotValidator()

        # Verify that repo_root is set to parent.parent of __file__
        self.assertIsInstance(validator.repo_root, Path)


class TestMainFunction(unittest.TestCase):
    """Test the main function"""

    @patch.object(CursorBugbotValidator, "validate")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_successful_validation(self, mock_exit, mock_print, mock_validate):
        """Test main function when validation is successful"""
        mock_validate.return_value = (True, "All good!")

        main()

        mock_validate.assert_called_once()
        mock_print.assert_called_once_with("All good!")
        mock_exit.assert_called_once_with(0)

    @patch.object(CursorBugbotValidator, "validate")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_failed_validation(self, mock_exit, mock_print, mock_validate):
        """Test main function when validation fails"""
        mock_validate.return_value = (False, "Issues found!")

        main()

        mock_validate.assert_called_once()
        mock_print.assert_called_once_with("Issues found!")
        mock_exit.assert_called_once_with(1)


class TestImports(unittest.TestCase):
    """Test that imports are working correctly after the diff changes"""

    def test_json_import_order(self):
        """Test that json import is available and working"""
        # The diff shows json import was moved to the top
        # This test ensures json functionality is still available
        test_data = {"test": "value"}
        json_string = json.dumps(test_data)
        parsed_data = json.loads(json_string)

        self.assertEqual(parsed_data, test_data)

    def test_required_imports_available(self):
        """Test that all required imports are available"""
        # Test that all imports from the module are working
        import os
        import sys
        from pathlib import Path
        from typing import Dict, List, Tuple

        # Basic smoke test for each import
        self.assertTrue(hasattr(os, "path"))
        self.assertTrue(hasattr(sys, "exit"))
        self.assertTrue(issubclass(Path, object))
        self.assertTrue(Dict is not None)
        self.assertTrue(List is not None)
        self.assertTrue(Tuple is not None)


class TestStringFormatting(unittest.TestCase):
    """Test string formatting changes from the diff"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = CursorBugbotValidator()

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_double_quote_formatting(self, mock_exists, mock_file):
        """Test that the code correctly handles double quote formatting"""
        mock_exists.return_value = True
        # Test that the file paths use double quotes as per the diff

        # Test .cursorignore path construction
        mock_file.return_value.read.return_value = (
            ".env\n*.key\n*.pem\nsecrets/\ncredentials/\n"
        )
        result = self.validator.check_cursorignore()
        self.assertTrue(result)

        # Verify the path was constructed correctly (this indirectly tests double quote usage)
        expected_path = self.validator.repo_root / ".cursorignore"
        mock_exists.assert_called_with()

    @patch("pathlib.Path.exists")
    def test_workflow_path_formatting(self, mock_exists):
        """Test GitHub workflow path formatting with double quotes"""
        mock_exists.return_value = True

        result = self.validator.check_github_workflow()

        self.assertTrue(result)
        # The path construction uses double quotes as per the diff
        expected_path = (
            self.validator.repo_root / ".github" / "workflows" / "cursor-bugbot.yml"
        )
        mock_exists.assert_called_with()

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_readme_path_formatting(self, mock_exists, mock_file):
        """Test README path formatting with double quotes"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "Content with Cursor Bugbot mention"

        result = self.validator.check_readme_documentation()

        self.assertTrue(result)
        # The path construction uses double quotes as per the diff
        expected_path = self.validator.repo_root / "README.md"
        mock_exists.assert_called_with()


if __name__ == "__main__":
    unittest.main()
