import json
import sys
from pathlib import Path

import pytest

# Add the project root to the Python path to allow importing from 'scripts'
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.enhanced_qa_validator_v2 import EnhancedQAValidatorV2

# --- Helper function for mock data ---


def create_mock_puzzle_data(puzzle_id, **kwargs):
    """
    Generates a dictionary representing puzzle metadata.
    Accepts kwargs to override default valid data for testing specific failures.
    """
    # Default valid data for a simple 3x3 puzzle
    valid_data = {
        "id": puzzle_id,
        "theme": "Test Theme",
        "difficulty": "EASY",
        "grid_path": f"puzzles/puzzle_{puzzle_id:02d}.png",
        "solution_path": f"solutions/solution_{puzzle_id:02d}.png",
        "clues": {
            "across": [(1, "A woven fabric", "CLOTH")],
            "down": [(2, "A feline", "CAT")],
        },
        "clue_positions": {
            "0,0": 1,
            "0,0": 2,  # Simplified for testing, real positions would differ
        },
        "word_count": {"across": 1, "down": 1, "total": 2},
        "validation": {"valid": True, "issues": []},
    }

    # A more realistic valid puzzle
    valid_data_realistic = {
        "id": puzzle_id,
        "theme": "Valid Puzzle",
        "difficulty": "MEDIUM",
        "grid_path": f"puzzles/puzzle_{puzzle_id:02d}.png",
        "solution_path": f"solutions/solution_{puzzle_id:02d}.png",
        "clues": {
            "across": [
                (1, "A language for programming", "PYTHON"),
                (3, "A test framework", "PYTEST"),
            ],
            "down": [
                (1, "A place to write code", "EDITOR"),
                (2, "To correct a bug", "FIX"),
            ],
        },
        "clue_positions": {
            "0,0": 1,  # PYTHON
            "2,0": 3,  # PYTEST
            "0,3": 2,  # FIX
            "0,0": 1,  # EDITOR (shares 'P' with PYTHON)
        },
        "word_count": {"across": 2, "down": 2, "total": 4},
    }

    # Use realistic data as base and override with kwargs
    data = valid_data_realistic.copy()
    data.update(kwargs)
    return data


# --- Fixtures ---


@pytest.fixture
def book_dir(tmp_path):
    """Provides a temporary directory to simulate a book's folder structure."""
    return tmp_path


@pytest.fixture
def mock_metadata_dir(book_dir):
    """Creates the metadata subdirectory."""
    meta_dir = book_dir / "metadata"
    meta_dir.mkdir()
    return meta_dir


@pytest.fixture
def custom_word_list(tmp_path):
    """Creates a small, controlled word list for testing."""
    word_file = tmp_path / "test_words.txt"
    words = [
        "PYTHON",
        "PYTEST",
        "EDITOR",
        "FIX",
        "CODE",
        "TEST",
        "BUG",
        "VALID",
        "GRID",
        "AGENT",
        "CLOTH",
        "CAT",
    ]
    word_file.write_text("\n".join(words))
    return str(word_file)


@pytest.fixture
def validator_instance(book_dir, custom_word_list):
    """Provides a pre-configured instance of the EnhancedQAValidatorV2."""
    return EnhancedQAValidatorV2(
        book_dir=str(book_dir),
        output_dir=str(book_dir),
        word_list_path=custom_word_list,
    )


# --- Test Cases ---


class TestValidatorInitialization:
    """Tests for validator setup and configuration."""

    def test_initialization_success(
        self, book_dir, mock_metadata_dir, custom_word_list
    ):
        """Test successful initialization."""
        validator = EnhancedQAValidatorV2(
            str(book_dir), word_list_path=custom_word_list
        )
        assert validator.book_dir == book_dir
        assert "PYTHON" in validator.word_dict

    def test_initialization_fails_if_metadata_dir_missing(self, book_dir):
        """Test that initialization raises FileNotFoundError if metadata dir is absent."""
        with pytest.raises(FileNotFoundError):
            EnhancedQAValidatorV2(str(book_dir))


class TestValidationChecks:
    """Tests for the individual validation rules."""

    def test_word_content_valid(self, validator_instance, mock_metadata_dir):
        """Test a puzzle where all words are in the dictionary."""
        puzzle_data = create_mock_puzzle_data(1)
        validator_instance._validate_word_content(1, puzzle_data)
        report = validator_instance.report["puzzles"][1]
        assert "All words are valid." in report["passed_checks"]
        assert len(report["critical_issues"]) == 0

    def test_word_content_invalid(self, validator_instance, mock_metadata_dir):
        """Test a puzzle with words not present in the dictionary."""
        puzzle_data = create_mock_puzzle_data(
            1, clues={"across": [(1, "A made-up word", "GIBBERISH")], "down": []}
        )
        validator_instance._validate_word_content(1, puzzle_data)
        report = validator_instance.report["puzzles"][1]
        assert "Contains invalid/unknown words: GIBBERISH" in report["critical_issues"]

    def test_intersections_valid(self, validator_instance):
        """Test a puzzle with correct word intersections."""
        # PYTHON horizontally, EDITOR vertically, sharing 'P'
        puzzle_data = {
            "clues": {
                "across": [(1, "lang", "PYTHON")],
                "down": [(2, "tool", "EDITOR")],
            },
            "clue_positions": {"0,0": 1, "0,0": 2},
        }
        grid, ok = validator_instance._validate_intersections_and_reconstruct_grid(
            1, puzzle_data
        )
        assert ok is True
        assert grid[0][0] == "P"  # Shared letter
        assert grid[0][1] == "Y"  # From PYTHON
        assert grid[1][0] == "D"  # From EDITOR
        assert (
            "All word intersections are valid."
            in validator_instance.report["puzzles"][1]["passed_checks"]
        )

    def test_intersections_invalid_conflict(self, validator_instance):
        """Test a puzzle where intersecting letters do not match."""
        # PYTHON horizontally, FIX vertically, but 'P' and 'F' conflict
        puzzle_data = {
            "clues": {
                "across": [(1, "lang", "PYTHON")],
                "down": [(2, "action", "FIX")],
            },
            "clue_positions": {"0,0": 1, "0,0": 2},  # Both start at the same spot
        }
        _, ok = validator_instance._validate_intersections_and_reconstruct_grid(
            1, puzzle_data
        )
        assert ok is False
        report = validator_instance.report["puzzles"][1]
        assert "Intersection conflict at (0,0)" in report["critical_issues"][0]

    def test_grid_connectivity_valid(self, validator_instance):
        """Test a simple, fully connected grid."""
        grid = [
            ["P", "Y", "T", "H", "O", "N"],
            ["E", "", "", "", "", ""],
            ["D", "", "", "", "", ""],
            ["I", "", "", "", "", ""],
            ["T", "", "", "", "", ""],
            ["O", "", "", "", "", ""],
            ["R", "", "", "", "", ""],
        ]
        validator_instance._validate_grid_connectivity(1, grid)
        report = validator_instance.report["puzzles"][1]
        assert "Grid is fully connected." in report["passed_checks"]

    def test_grid_connectivity_invalid(self, validator_instance):
        """Test a grid with isolated, unreachable squares."""
        grid = [["A", "", "#", "", "B"]]
        validator_instance._validate_grid_connectivity(1, grid)
        report = validator_instance.report["puzzles"][1]
        assert (
            "Grid has 1 unreachable/isolated squares." in report["critical_issues"][0]
        )

    def test_duplicate_words(self, validator_instance):
        """Test validation fails if a puzzle contains duplicate words."""
        puzzle_data = create_mock_puzzle_data(
            1,
            clues={
                "across": [(1, "A test", "TEST")],
                "down": [(2, "Another test", "TEST")],
            },
        )
        validator_instance._validate_for_duplicate_words(1, puzzle_data)
        report = validator_instance.report["puzzles"][1]
        assert "Duplicate words found: TEST" in report["critical_issues"]


class TestReportGenerationAndScoring:
    """Tests for the final report and scoring logic."""

    def test_full_run_pass(self, validator_instance, mock_metadata_dir):
        """Test a full run on a valid book, expecting a PASS status."""
        # Create collection.json
        (mock_metadata_dir / "collection.json").write_text(json.dumps({"puzzles": [1]}))
        # Create valid puzzle file
        puzzle_data = create_mock_puzzle_data(1)
        (mock_metadata_dir / "puzzle_01.json").write_text(json.dumps(puzzle_data))

        report = validator_instance.validate_book()
        assert report["overall_status"] == "PASS"
        assert report["summary"]["puzzles_passed"] == 1
        assert report["summary"]["critical_issues_count"] == 0

    def test_full_run_fail(self, validator_instance, mock_metadata_dir):
        """Test a full run on a book with critical issues, expecting a FAIL status."""
        (mock_metadata_dir / "collection.json").write_text(json.dumps({"puzzles": [1]}))
        # Create puzzle file with an invalid word
        puzzle_data = create_mock_puzzle_data(
            1, clues={"across": [(1, "bad", "BADWORD")]}
        )
        (mock_metadata_dir / "puzzle_01.json").write_text(json.dumps(puzzle_data))

        report = validator_instance.validate_book()
        assert report["overall_status"] == "FAIL"
        assert report["summary"]["puzzles_with_critical_issues"] == 1
        assert report["summary"]["critical_issues_count"] > 0

    def test_scoring_logic(self, validator_instance, mock_metadata_dir):
        """Test the score calculation based on penalties."""
        (mock_metadata_dir / "collection.json").write_text(json.dumps({"puzzles": [1]}))
        # Create a puzzle with one critical issue (invalid word) and one warning (poor balance)
        puzzle_data = create_mock_puzzle_data(
            1,
            clues={"across": [(1, "bad", "BADWORD")], "down": []},
            word_count={"across": 1, "down": 0, "total": 1},
        )
        (mock_metadata_dir / "puzzle_01.json").write_text(json.dumps(puzzle_data))

        validator_instance.validate_book()
        # The scoring logic is in the old validator, but we can check the issue counts
        report = validator_instance.report
        assert report["summary"]["critical_issues_count"] == 1
        assert report["summary"]["warnings_count"] == 1


class TestErrorHandling:
    """Tests for handling of missing or malformed files."""

    def test_missing_collection_json(self, validator_instance):
        """Test that the validator handles a missing collection.json gracefully."""
        report = validator_instance.validate_book()
        assert report["overall_status"] == "FAIL"
        assert "CRITICAL: collection.json not found." in report["global_issues"]

    def test_malformed_json(self, validator_instance, mock_metadata_dir):
        """Test that the validator handles a malformed JSON file."""
        (mock_metadata_dir / "collection.json").write_text(json.dumps({"puzzles": [1]}))
        (mock_metadata_dir / "puzzle_01.json").write_text(
            "{'invalid_json': True,}"
        )  # Invalid JSON

        validator_instance.validate_book()
        report = validator_instance.report
        assert report["puzzles"]["1"]["status"] == "FAIL"
        assert (
            "Invalid JSON in metadata file."
            in report["puzzles"]["1"]["critical_issues"]
        )

    def test_missing_puzzle_file(self, validator_instance, mock_metadata_dir):
        """Test when a puzzle file listed in collection.json does not exist."""
        (mock_metadata_dir / "collection.json").write_text(json.dumps({"puzzles": [1]}))
        # Do not create puzzle_01.json

        validator_instance.validate_book()
        report = validator_instance.report
        assert report["puzzles"]["1"]["status"] == "FAIL"
        assert (
            "Puzzle metadata file not found: puzzle_01.json"
            in report["puzzles"]["1"]["critical_issues"]
        )
