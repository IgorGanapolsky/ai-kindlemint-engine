#!/usr/bin/env python3
"""Tests for base functionality across modules to improve coverage"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch


# Test Message Protocol (77% coverage -> 90%)
def test_message_protocol_complete():
    """Test Message Protocol Complete - Test message protocol functionality"""
    from kindlemint.agents.message_protocol import (
        Message,
        MessageBus,
        MessagePriority,
        MessageType,
    )

    # Test Message creation and properties
    msg = Message(
        type=MessageType.TASK_REQUEST,
        sender="agent1",
        recipient="agent2",
        content={"task": "generate_puzzle"},
        priority=MessagePriority.HIGH,
    )

    assert msg.type == MessageType.TASK_REQUEST
    assert msg.sender == "agent1"
    assert msg.recipient == "agent2"
    assert msg.priority == MessagePriority.HIGH
    assert msg.id is not None  # Should auto-generate ID
    assert isinstance(msg.timestamp, datetime)

    # Test MessageBus
    bus = MessageBus()
    assert bus is not None

    # Test message sending
    bus.send(msg)

    # Test subscribe/unsubscribe
    handler = MagicMock()
    bus.subscribe(MessageType.TASK_REQUEST, handler)
    bus.send(msg)
    handler.assert_called_once()


# Test Task System (72% coverage -> 90%)
def test_task_system_complete():
    """Test Task System Complete - Test task system functionality"""
    from kindlemint.agents.task_system import (
        Task,
        TaskPriority,
        TaskQueue,
        TaskResult,
        TaskStatus,
    )

    # Test Task creation
    task = Task(
        type="generate_puzzle",
        payload={"difficulty": "easy"},
        priority=TaskPriority.HIGH,
        timeout_seconds=300,
    )

    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.HIGH
    assert task.id is not None
    assert task.payload["difficulty"] == "easy"

    # Test TaskResult
    result = TaskResult(
        task_id=task.id,
        status=TaskStatus.COMPLETED,
        result_data={"puzzle": "data"},
        error=None,
    )

    assert result.task_id == task.id
    assert result.status == TaskStatus.COMPLETED
    assert result.success is True

    # Test TaskQueue
    queue = TaskQueue()
    queue.add_task(task)
    assert queue.size() > 0

    # Get next task
    next_task = queue.get_next_task()
    assert next_task.id == task.id


# Test Base Validator (55% coverage -> 85%)
def test_base_validator_complete():
    """Test Base Validator Complete - Test base validator functionality"""
    from kindlemint.validators.base_validator import (
        IssueSeverity,
        ValidationIssue,
        ValidationReport,
    )

    # Test ValidationIssue
    issue = ValidationIssue(
        severity=IssueSeverity.ERROR,
        category="syntax",
        message="Invalid puzzle format",
        location="puzzle_1",
    )

    assert issue.severity == IssueSeverity.ERROR
    assert issue.category == "syntax"
    assert issue.message == "Invalid puzzle format"

    # Test ValidationReport
    report = ValidationReport(
        puzzle_type="sudoku", total_puzzles=10, valid_puzzles=8, issues=[issue]
    )

    assert report.puzzle_type == "sudoku"
    assert report.total_puzzles == 10
    assert report.valid_puzzles == 8
    assert len(report.issues) == 1
    assert report.is_valid() is False  # Has errors

    # Test a report with only warnings
    warning_issue = ValidationIssue(
        severity=IssueSeverity.WARNING, category="style", message="Non-standard format"
    )

    report2 = ValidationReport(
        puzzle_type="crossword",
        total_puzzles=5,
        valid_puzzles=5,
        issues=[warning_issue],
    )

    assert report2.is_valid() is True  # Only warnings, still valid


# Test utilities initialization
def test_utils_init():
    """Test Utils Init - Test utils module initialization"""
    from kindlemint.utils import ensure_directory, format_timestamp, get_logger

    # Test logger
    logger = get_logger("test")
    assert logger is not None

    # Test timestamp formatting
    timestamp = format_timestamp(datetime.now())
    assert isinstance(timestamp, str)

    # Test directory creation
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        ensure_directory(Path("/tmp/test"))
        mock_mkdir.assert_called_once()


# Test engines initialization
def test_engines_init():
    """Test Engines Init - Test engines module initialization"""
    from kindlemint.engines import (
        CrosswordEngine,
        SudokuEngine,
        WordSearchEngine,
        get_engine,
    )

    # Test engine factory
    sudoku_engine = get_engine("sudoku")
    assert isinstance(sudoku_engine, SudokuEngine)

    wordsearch_engine = get_engine("wordsearch")
    assert isinstance(wordsearch_engine, WordSearchEngine)

    crossword_engine = get_engine("crossword")
    assert isinstance(crossword_engine, CrosswordEngine)


# Test validators initialization
def test_validators_init():
    """Test Validators Init - Test validators module initialization"""
    from kindlemint.validators import (
        CrosswordValidator,
        SudokuValidator,
        WordSearchValidator,
        get_validator,
    )

    # Test validator factory
    sudoku_val = get_validator("sudoku")
    assert isinstance(sudoku_val, SudokuValidator)

    crossword_val = get_validator("crossword")
    assert isinstance(crossword_val, CrosswordValidator)

    wordsearch_val = get_validator("wordsearch")
    assert isinstance(wordsearch_val, WordSearchValidator)
