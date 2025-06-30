#!/usr/bin/env python3
"""Quick coverage boost tests - CTO directive for immediate improvement"""

import tempfile
from pathlib import Path


def test_sudoku_generator_basics():
    """Test basic sudoku generator functionality"""
    from kindlemint.engines.sudoku import SudokuGenerator

    # Test initialization
    generator = SudokuGenerator(puzzle_count=10, difficulty="easy")
    assert generator.puzzle_count == 10
    assert generator.difficulty_mode == "easy"
    assert generator.grid_size == 9

    # Test difficulty parameters
    assert "easy" in generator.difficulty_params
    assert generator.difficulty_params["easy"]["target_clues"] == 40

    # Test grid creation
    grid = generator._create_empty_grid()
    assert len(grid) == 9
    assert all(len(row) == 9 for row in grid)
    assert all(all(cell == 0 for cell in row) for row in grid)


def test_wordsearch_engine():
    """Test word search engine basics"""
    from kindlemint.engines.wordsearch import WordSearchGenerator

    generator = WordSearchGenerator(grid_size=10)
    assert generator.grid_size == 10

    # Test grid initialization
    generator._initialize_grid()
    assert len(generator.grid) == 10
    assert all(len(row) == 10 for row in generator.grid)


def test_base_validator_simple():
    """Test base validator functionality"""
    from kindlemint.validators.base_validator import (
        IssueSeverity,
        ValidationIssue,
        ValidationReport,
    )

    # Test issue creation
    issue = ValidationIssue(
        severity=IssueSeverity.ERROR, category="test", message="Test error"
    )
    assert issue.severity == IssueSeverity.ERROR
    assert issue.category == "test"

    # Test report
    report = ValidationReport(
        puzzle_type="sudoku", total_puzzles=10, valid_puzzles=9, issues=[issue]
    )
    assert report.total_puzzles == 10
    assert report.valid_puzzles == 9
    assert not report.is_valid()  # Has errors


def test_utils_functions():
    """Test utility functions for quick coverage"""
    from kindlemint.utils import ensure_directory, get_logger

    # Test logger
    logger = get_logger(__name__)
    assert logger is not None

    # Test directory creation
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test"
        ensure_directory(test_dir)
        assert test_dir.exists()


def test_agent_enums():
    """Test all agent-related enums"""
    from kindlemint.agents.agent_types import AgentCapability
    from kindlemint.agents.message_protocol import MessageType
    from kindlemint.agents.task_system import TaskPriority, TaskStatus

    # Test capabilities
    assert AgentCapability.CONTENT_GENERATION.value == "content_generation"
    assert len(list(AgentCapability)) > 5

    # Test message types
    assert MessageType.TASK_REQUEST.value == "task_request"

    # Test task enums
    assert TaskStatus.PENDING.value == "pending"
    assert TaskPriority.HIGH.value == "high"


def test_validator_imports():
    """Test validator module imports"""
    from kindlemint.validators import get_validator

    # Test factory function exists
    assert callable(get_validator)


def test_engines_imports():
    """Test engines module imports"""
    from kindlemint.engines import get_engine

    # Test factory function exists
    assert callable(get_engine)
