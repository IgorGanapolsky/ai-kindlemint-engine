#!/usr/bin/env python3
"""Tests for kindlemint.cli module"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from click.testing import CliRunner


class TestKindleMintCLI:
    """Test the kindlemint.cli module"""

    def test_import_warnings_daily_tasks(self, capsys):
        """Test import warning for run_daily_tasks when scripts.daily_tasks fails to import"""
        with patch.dict("sys.modules", {"scripts.daily_tasks": None}):
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                # Force reimport of the module to trigger the import error
                if "kindlemint.cli" in sys.modules:
                    del sys.modules["kindlemint.cli"]

                import kindlemint.cli

                captured = capsys.readouterr()

                # Test that the warning message is properly formatted (covers line 33 change)
                assert (
                    "Warning: Could not import run_daily_tasks from scripts.daily_tasks:"
                    in captured.out
                )
                assert (
                    "This function will not be available via kindlemint.cli.run_daily_tasks."
                    in captured.out
                )
                assert kindlemint.cli.run_daily_tasks is None

    def test_import_warnings_book_layout_engine(self, capsys):
        """Test import warning for BookLayoutEngine when scripts.book_layout_bot fails to import"""
        with patch.dict("sys.modules", {"scripts.book_layout_bot": None}):
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                if "kindlemint.cli" in sys.modules:
                    del sys.modules["kindlemint.cli"]

                import kindlemint.cli

                captured = capsys.readouterr()

                assert (
                    "Warning: Could not import BookLayoutEngine from scripts.book_layout_bot:"
                    in captured.out
                )
                assert (
                    "This class will not be available via kindlemint.cli.BookLayoutEngine."
                    in captured.out
                )
                assert kindlemint.cli.BookLayoutEngine is None

    def test_import_warnings_crossword_engine(self, capsys):
        """Test import warning for CrosswordEngineV2 when scripts.crossword_engine_v2 fails to import"""
        with patch.dict("sys.modules", {"scripts.crossword_engine_v2": None}):
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                if "kindlemint.cli" in sys.modules:
                    del sys.modules["kindlemint.cli"]

                import kindlemint.cli

                captured = capsys.readouterr()

                assert (
                    "Warning: Could not import CrosswordEngine from scripts.crossword_engine_v2:"
                    in captured.out
                )
                assert (
                    "This class will not be available via kindlemint.cli.CrosswordEngineV2."
                    in captured.out
                )
                assert kindlemint.cli.CrosswordEngineV2 is None

    def test_import_warnings_sudoku_generator(self, capsys):
        """Test import warning for SudokuGeneratorCLI when scripts.sudoku_generator fails to import"""
        with patch.dict("sys.modules", {"scripts.sudoku_generator": None}):
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                if "kindlemint.cli" in sys.modules:
                    del sys.modules["kindlemint.cli"]

                import kindlemint.cli

                captured = capsys.readouterr()

                assert (
                    "Warning: Could not import SudokuGenerator from scripts.sudoku_generator:"
                    in captured.out
                )
                assert (
                    "This class will not be available via kindlemint.cli.SudokuGeneratorCLI."
                    in captured.out
                )
                assert kindlemint.cli.SudokuGeneratorCLI is None

    def test_validate_metadata_wrapper_creation(self):
        """Test that validate_metadata wrapper is created when direct import fails but class import succeeds"""
        # Test the wrapper function creation (covers lines 76-77 blank lines)
        mock_qa_class = Mock()
        mock_qa_instance = Mock()
        mock_qa_class.return_value = mock_qa_instance
        mock_qa_instance.validate_metadata.return_value = {"valid": True}

        with patch.dict(
            "sys.modules",
            {"scripts.critical_metadata_qa": Mock(
                CriticalMetadataQA=mock_qa_class)},
        ):
            with patch(
                "builtins.__import__",
                side_effect=[ImportError(
                    "Direct function import failed"), None],
            ):
                if "kindlemint.cli" in sys.modules:
                    del sys.modules["kindlemint.cli"]

                import kindlemint.cli

                # Test that the wrapper function was created
                assert kindlemint.cli.validate_metadata is not None

                # Test calling the wrapper function
                result = kindlemint.cli.validate_metadata({"test": "data"})
                assert result == {"valid": True}
                mock_qa_instance.validate_metadata.assert_called_once_with(
                    {"test": "data"}
                )

    def test_validate_metadata_import_failure(self, capsys):
        """Test validate_metadata warning when both direct and class imports fail"""
        with patch.dict("sys.modules", {"scripts.critical_metadata_qa": None}):
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                if "kindlemint.cli" in sys.modules:
                    del sys.modules["kindlemint.cli"]

                import kindlemint.cli

                captured = capsys.readouterr()

                assert (
                    "Warning: Could not import validate_metadata from scripts.critical_metadata_qa:"
                    in captured.out
                )
                assert (
                    "This function will not be available via kindlemint.cli.validate_metadata."
                    in captured.out
                )
                assert kindlemint.cli.validate_metadata is None

    def test_legacy_cli_import_warnings(self, capsys):
        """Test warnings when legacy CLI imports fail"""
        with patch.dict("sys.modules", {"scripts.cli.main": None}):
            with patch(
                "builtins.__import__", side_effect=ImportError("Module not found")
            ):
                if "kindlemint.cli" in sys.modules:
                    del sys.modules["kindlemint.cli"]

                import kindlemint.cli

                captured = capsys.readouterr()

                assert (
                    "Warning: Could not import cli or FORMATTERS from scripts.cli.main:"
                    in captured.out
                )
                assert (
                    "The click command-group interface will not be available via kindlemint.cli.cli."
                    in captured.out
                )
                assert kindlemint.cli.cli is None
                assert kindlemint.cli.FORMATTERS == {}

    def test_is_legacy_cli_available(self):
        """Test the is_legacy_cli_available function"""
        import kindlemint.cli

        # Test with a function that should exist (if imports work)
        # Since we're testing the function itself, we'll mock the globals
        with patch.object(
            kindlemint.cli, "globals", return_value={"test_function": Mock()}
        ):
            assert kindlemint.cli.is_legacy_cli_available(
                "test_function") is True

        with patch.object(
            kindlemint.cli, "globals", return_value={"test_function": None}
        ):
            assert kindlemint.cli.is_legacy_cli_available(
                "test_function") is False

        with patch.object(kindlemint.cli, "globals", return_value={}):
            assert (
                kindlemint.cli.is_legacy_cli_available(
                    "nonexistent_function") is False
            )

    @patch("kindlemint.cli.cli")
    def test_enhance_seo_command_success(self, mock_cli):
        """Test the enhance-seo CLI command with successful execution"""
        # Mock the click CLI group exists
        mock_cli.__bool__ = Mock(return_value=True)

        # Create test data
        test_book_data = {
            "title": "Test Book",
            "description": "A test book",
            "keywords": ["test", "book"],
        }

        enhanced_data = {
            "title": "Test Book - Enhanced",
            "description": "An enhanced test book with SEO optimization",
            "keywords": ["test", "book", "enhanced", "seo"],
        }

        # Mock file operations and SEO engine
        mock_path = Mock()
        mock_path.open.return_value.__enter__.return_value.read.return_value = (
            json.dumps(test_book_data)
        )
        mock_path.with_name.return_value = Mock()

        mock_seo_engine = Mock()
        mock_seo_engine.enhance_book_marketing.return_value = enhanced_data

        with patch("pathlib.Path") as mock_path_class:
            mock_path_class.return_value = mock_path
            with patch(
                "kindlemint.marketing.seo_engine_2025.SEOOptimizedMarketing"
            ) as mock_seo_class:
                mock_seo_class.return_value = mock_seo_engine
                with patch("json.load", return_value=test_book_data):
                    with patch("json.dump") as mock_json_dump:
                        with patch("builtins.open", mock_open()):
                            # Import and test the command (tests import reordering on lines 136-138)
                            from kindlemint.cli import enhance_seo

                            runner = CliRunner()
                            result = runner.invoke(
                                enhance_seo, ["--input", "test_book.json"]
                            )

                            assert result.exit_code == 0
                            assert "Enhanced metadata written to" in result.output
                            mock_seo_engine.enhance_book_marketing.assert_called_once_with(
                                test_book_data
                            )

    @patch("kindlemint.cli.cli")
    def test_enhance_seo_command_json_error(self, mock_cli):
        """Test the enhance-seo CLI command with JSON parsing error"""
        # Mock the click CLI group exists
        mock_cli.__bool__ = Mock(return_value=True)

        mock_path = Mock()
        mock_path.open.return_value.__enter__.return_value = Mock()

        with patch("pathlib.Path") as mock_path_class:
            mock_path_class.return_value = mock_path
            with patch(
                "json.load", side_effect=json.JSONDecodeError("Invalid JSON", "doc", 0)
            ):
                with patch("builtins.open", mock_open(read_data="invalid json")):
                    from kindlemint.cli import enhance_seo

                    runner = CliRunner()
                    result = runner.invoke(
                        enhance_seo, ["--input", "invalid_book.json"]
                    )

                    assert result.exit_code == 1
                    assert "Failed to parse JSON" in result.output

    def test_cli_command_registration_failure(self, capsys):
        """Test that CLI command registration failures are handled gracefully"""
        with patch("kindlemint.cli.cli", None):  # Simulate no CLI available
            # Force reimport to trigger the exception handling
            if "kindlemint.cli" in sys.modules:
                del sys.modules["kindlemint.cli"]

            import kindlemint.cli

            captured = capsys.readouterr()

            # The module should still import successfully even if CLI registration fails
            assert kindlemint.cli is not None
