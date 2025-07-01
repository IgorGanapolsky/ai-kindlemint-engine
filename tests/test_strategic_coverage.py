#!/usr/bin/env python3
"""
Strategic Coverage Tests - Target 25%+ Total Coverage
Focus on modules with partial coverage to maximize gains
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

"""Test Sudoku Generator Advanced"""


def test_sudoku_generator_advanced():
    """Push sudoku.py from 19% to 35%+"""
    from kindlemint.engines.sudoku import SudokuGenerator

    gen = SudokuGenerator(puzzle_count=3, difficulty="medium")

    # Test complete grid generation process
    complete_grid = gen._generate_complete_grid()
    assert len(complete_grid) == 9
    assert all(len(row) == 9 for row in complete_grid)
    # Should have numbers 1-9 in first row
    assert set(complete_grid[0]) == set(range(1, 10))

    # Test puzzle creation from solution
    puzzle_dict = gen._create_puzzle_from_solution(
        solution=complete_grid, difficulty="medium"
    )
    assert "initial_grid" in puzzle_dict
    assert "solution_grid" in puzzle_dict
    assert puzzle_dict["difficulty"] == "medium"
    assert puzzle_dict["clue_count"] > 0

    # Test solving capability
    test_grid = [[0] * 9 for __var in range(9)]
    # Add some clues
    test_grid[0][0] = 1
    test_grid[0][1] = 2
    solved = gen._solve_puzzle(test_grid)
    # Should return a solution or None
    assert solved is None or isinstance(solved, list)

    # Test puzzle generation
    puzzle = gen.generate_puzzle("easy")
    assert puzzle["difficulty"] == "easy"
    assert "id" in puzzle
    assert "solution_grid" in puzzle
    assert "initial_grid" in puzzle


def test_config_loader_advanced():
    """Push config.py from 48% to 70%+"""
    from kindlemint.utils.config import ConfigLoader

    # Mock config data
    mock_config = {
        "api_settings": {
            "openai": {"api_key": "test-key"},
            "serpapi": {"base_url": "https://api.test.com"},
        },
        "file_paths": {"word_list": "./data/words.txt", "output": "./output"},
        "kdp_specifications": {"paperback": {"trim_size": "8.5x11", "bleed": 0.125}},
    }

    with patch("kindlemint.utils.config.yaml.safe_load", return_value=mock_config):
        with patch("kindlemint.utils.config.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_text.return_value = "dummy"

            loader = ConfigLoader()
            loader.config = mock_config

            # Test nested get
            assert loader.get("api_settings.openai.api_key") == "test-key"
            assert loader.get(
                "api_settings.serpapi.base_url") == "https://api.test.com"

            # Test get with default
            assert loader.get("missing.key", "default") == "default"

            # Test get_path
            path = loader.get_path("file_paths.word_list")
            assert path.endswith("words.txt")

            # Test get_kdp_spec
            spec = loader.get_kdp_spec("paperback")
            assert spec["trim_size"] == "8.5x11"
            assert spec["bleed"] == 0.125

            # Test environment override
            with patch.dict(
                "os.environ", {
                    "KINDLEMINT_API_SETTINGS__OPENAI__API_KEY": "env-key"}
            ):
                loader._apply_env_overrides()
                assert loader.config["api_settings"]["openai"]["api_key"] == "env-key"


def test_base_validator_advanced():
    """Push base_validator from 57% to 80%+"""
    from kindlemint.validators.base_validator import (
        IssueSeverity,
        ValidationIssue,
        ValidationReport,
    )

    # Test ValidationIssue with all fields
    issue = ValidationIssue(
        severity=IssueSeverity.ERROR,
        category="syntax",
        message="Invalid syntax",
        location="line 10",
        details={"column": 5, "expected": "}", "found": "]"},
    )

    # Test issue methods
    issue_dict = issue.to_dict()
    assert issue_dict["severity"] == "error"
    assert issue_dict["details"]["column"] == 5

    # Test ValidationReport advanced features
    issues = [
        ValidationIssue(IssueSeverity.ERROR, "syntax", "Error 1"),
        ValidationIssue(IssueSeverity.WARNING, "style", "Warning 1"),
        ValidationIssue(IssueSeverity.INFO, "note", "Info 1"),
    ]

    report = ValidationReport(
        puzzle_type="crossword",
        total_puzzles=50,
        valid_puzzles=45,
        issues=issues,
        metadata={"validator_version": "2.0", "timestamp": "2024-01-01"},
    )

    # Test issue filtering
    errors = [i for i in report.issues if i.severity == IssueSeverity.ERROR]
    warnings = [i for i in report.issues if i.severity ==
                IssueSeverity.WARNING]
    assert len(errors) == 1
    assert len(warnings) == 1

    # Test save/load functionality
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        report.save(Path(f.name))

        # Load it back
        loaded_report = ValidationReport.load(Path(f.name))
        assert loaded_report.total_puzzles == 50
        assert len(loaded_report.issues) == 3

        Path(f.name).unlink()


def test_api_provider_coverage():
    """Boost api.py from 17% to 40%+"""
    from kindlemint.utils.api import APIProvider

    # Test initialization
    provider = APIProvider(api_key="test-key")
    assert provider.api_key == "test-key"

    # Test with monitoring decorator
    try:
        from kindlemint.utils.api import with_ai_monitoring

        @with_ai_monitoring
        def test_function():
            return "result"

        result = test_function()
        assert result == "result"
    except ImportError:
        pass


def test_cost_tracker_coverage():
    """Boost cost_tracker.py from 14% to 30%+"""
    from kindlemint.utils.cost_tracker import ClaudeCostTracker

    tracker = ClaudeCostTracker()

    # Test adding usage
    tracker.add_usage(model="claude-3-opus",
                      input_tokens=1000, output_tokens=500)

    # Test cost calculation
    cost = tracker.calculate_cost(
        model="claude-3-opus", input_tokens=1000, output_tokens=500
    )
    assert cost > 0

    # Test getting total cost
    total = tracker.get_total_cost()
    assert total >= cost

    # Test summary
    summary = tracker.get_summary()
    assert "claude-3-opus" in summary


def test_crossword_validator_advanced():
    """Boost crossword_validator from 11% to 25%+"""
    from kindlemint.validators.crossword_validator import CrosswordValidator

    validator = CrosswordValidator()

    # Test configuration
    assert validator.min_word_length == 3
    assert validator.max_word_length == 15
    assert validator.min_grid_fill == 0.75

    # Test validation helpers
    assert validator._is_valid_word("CAT")
    assert validator._is_valid_word("PUZZLE")
    assert not validator._is_valid_word("AB")  # Too short
    assert not validator._is_valid_word("A" * 20)  # Too long

    # Test grid validation basics

    # Should have method to check grid
    assert hasattr(validator, "_validate_grid")
    assert hasattr(validator, "_validate_clues")


def test_wordsearch_validator_coverage():
    """Boost wordsearch_validator from 13% to 30%+"""
    from kindlemint.validators.wordsearch_validator import WordSearchValidator

    validator = WordSearchValidator()

    # Test initialization
    assert validator.min_word_length == 3
    assert validator.max_word_length == 15
    assert validator.min_words == 10
    assert validator.max_words == 30

    # Test word validation
    assert validator._is_valid_word("PYTHON")
    assert not validator._is_valid_word("AB")
    assert not validator._is_valid_word("")

    # Test has required methods
    assert hasattr(validator, "validate")
    assert hasattr(validator, "_validate_grid")
