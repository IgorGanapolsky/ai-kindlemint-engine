import json
import sys
import time
from pathlib import Path

import pytest

from kindlemint.engines.crossword import CrosswordEngine as CrosswordEngineV3

# Add the project root to the Python path to allow importing from 'scripts'
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# enable `kindlemint` package import
sys.path.insert(0, str(project_root / "src"))

# Import new engine implementation from the migrated package.
# Alias it as *CrosswordEngineV3* to minimise downstream changes.

# --- Fixtures ---


@pytest.fixture
def output_dir(tmp_path):
    """Provides a temporary directory for test outputs."""
    return tmp_path


@pytest.fixture
def custom_word_list(tmp_path):
    """Creates a small, deterministic word list for testing."""
    word_file = tmp_path / "test_words.txt"
    words = [
        "PYTHON",
        "PYTEST",
        "CODE",
        "TEST",
        "BUG",
        "FIX",
        "HELLO",
        "WORLD",
        "AGENT",
        "FACTORY",
        "CROSSWORD",
        "PUZZLE",
        "GRID",
        "SOLVE",
        "ACROSS",
        "DOWN",
        "CLUE",
        "ANSWER",
    ]
    word_file.write_text("\n".join(words))
    return str(word_file)


@pytest.fixture
def engine_instance(output_dir, custom_word_list):
    """Provides a pre-configured instance of the CrosswordEngineV3."""
    return CrosswordEngineV3(
        output_dir=str(output_dir),
        puzzle_count=1,
        grid_size=15,
        word_list_path=custom_word_list,
    )


# --- Test Cases ---


class TestEngineInitialization:
    """Tests for engine setup and configuration."""

    def test_engine_creates_directories(self, output_dir):
        """Verify that the engine creates required subdirectories."""
        engine = CrosswordEngineV3(output_dir=str(output_dir))
        assert (output_dir / "puzzles").is_dir()
        assert (output_dir / "metadata").is_dir()
        assert (output_dir / "solutions").is_dir()

    def test_word_dictionary_loading(self, engine_instance):
        """Verify that the engine loads the custom word list."""
        assert "PYTHON" in engine_instance.word_dict
        assert "PYTEST" in engine_instance.word_dict
        assert len(engine_instance.word_dict) == 18

    def test_word_dictionary_fallback(self, output_dir):
        """Test that the engine falls back to its internal dictionary."""
        engine = CrosswordEngineV3(output_dir=str(output_dir))
        # Check for a common word from the built-in list
        assert "ABOUT" in engine.word_dict
        assert len(engine.word_dict) > 500  # Ensure it's the larger list


class TestGridGeneration:
    """Tests for grid and pattern creation logic."""

    def test_symmetric_pattern_generation(self, engine_instance):
        """Test that the generated black square pattern is symmetric."""
        pattern = engine_instance.create_symmetric_pattern(difficulty="MEDIUM")
        size = engine_instance.grid_size

        for r, c in pattern:
            # For a point to be symmetric, its counterpoint must also be in the pattern
            # unless it's the exact center of the grid.
            if (r, c) != (size // 2, size // 2):
                assert (size - 1 - r, size - 1 - c) in pattern

    def test_grid_with_content_is_not_empty(self, engine_instance):
        """Test that a generated grid contains actual letters, not just blanks."""
        grid = engine_instance.generate_grid_with_content(
            puzzle_id=1, theme="Test", difficulty="EASY"
        )

        assert isinstance(grid, list)
        assert len(grid) == engine_instance.grid_size

        flat_grid = "".join(["".join(row) for row in grid])
        # Check that the grid contains more than just black squares ('#') and empty spaces
        assert len(flat_grid.replace("#", "").replace(" ", "")) > 10

    def test_grid_connectivity(self, engine_instance):
        """Test the grid connectivity check with a known disconnected grid."""
        connected_grid = engine_instance.generate_grid_with_content(
            1, "Test", "EASY")
        assert engine_instance._check_grid_connectivity(connected_grid) is True

        # Create a manually disconnected grid
        disconnected_grid = [
            [" " for __var in range(15)] for __var in range(15)]
        disconnected_grid[0][0] = "A"
        disconnected_grid[14][14] = "B"
        # Add a wall of black squares
        for i in range(15):
            disconnected_grid[7][i] = "#"

        assert engine_instance._check_grid_connectivity(
            disconnected_grid) is False

    def test_fallback_grid_creation(self, engine_instance):
        """Test that the fallback grid mechanism produces a valid grid."""
        fallback_grid = engine_instance._create_fallback_grid()
        assert isinstance(fallback_grid, list)
        assert len(fallback_grid) == 15
        assert "PUZZLE" in "".join(fallback_grid[1])  # Check for a known word


class TestWordAndClueLogic:
    """Tests for word extraction, clue generation, and validation."""

    def test_extract_words_from_grid(self, engine_instance):
        """Verify that words are correctly extracted from a filled grid."""
        grid = [["#"] * 15 for __var in range(15)]
        grid[1][1:4] = list("CAT")
        grid[1][1] = "C"
        grid[2][1] = "A"
        grid[3][1] = "R"

        # Manually create clue positions for this simple grid
        clue_positions = {
            (1, 1): 1,
            (2, 1): 2,
        }  # This is simplified, real logic is more complex

        # A more realistic extraction test
        filled_grid = engine_instance.generate_grid_with_content(
            1, "Test", "EASY")
        _, _, clue_pos = engine_instance.create_grid_images(filled_grid, 1)
        across, down = engine_instance.extract_words_from_grid(
            filled_grid, clue_pos)

        assert isinstance(across, list)
        assert isinstance(down, list)
        assert len(across) > 0
        assert len(down) > 0
        assert len(across[0]) == 3  # (number, word, (r, c))

    def test_clue_generation(self, engine_instance):
        """Test that clues are generated in the correct format."""
        across_words = [(1, "PYTHON", (0, 0)), (3, "TEST", (2, 2))]
        down_words = [(2, "PYTEST", (0, 1))]

        clues = engine_instance.generate_clues(
            1, "Tech", "EASY", across_words, down_words
        )

        assert "across" in clues
        assert "down" in clues
        assert len(clues["across"]) == 2
        assert len(clues["down"]) == 1
        # Check structure: (number, clue_text, answer)
        assert len(clues["across"][0]) == 3
        assert clues["across"][0][2] == "PYTHON"

    def test_puzzle_validation_logic(self, engine_instance):
        """Test the internal puzzle validation method."""
        grid = engine_instance.generate_grid_with_content(1, "Test", "EASY")
        _, _, clue_pos = engine_instance.create_grid_images(grid, 1)
        across, down = engine_instance.extract_words_from_grid(grid, clue_pos)
        clues = engine_instance.generate_clues(1, "Test", "EASY", across, down)

        # Test a valid puzzle
        validation_pass = engine_instance.validate_puzzle(
            grid, across, down, clues)
        assert validation_pass["valid"] is True

        # Test with duplicate words
        across_with_dupe = across + [(99, across[0][1], (10, 10))]
        validation_fail_dupe = engine_instance.validate_puzzle(
            grid, across_with_dupe, down, clues
        )
        assert validation_fail_dupe["valid"] is False
        assert "Duplicate words" in validation_fail_dupe["issues"][0]

        # Test with unbalanced words
        validation_fail_balance = engine_instance.validate_puzzle(
            grid, across, down[:1], clues
        )
        assert validation_fail_balance["valid"] is False
        assert "Unbalanced word distribution" in validation_fail_balance["issues"][0]


class TestFullGeneration:
    """Integration-style tests for the full puzzle generation process."""

    def test_generate_single_puzzle_creates_files(self, engine_instance, output_dir):
        """Test that generating one puzzle creates all the necessary output files."""
        engine_instance.generate_puzzles()

        # Check for image files
        assert (output_dir / "puzzles" / "puzzle_01.png").is_file()
        assert (output_dir / "solutions" / "solution_01.png").is_file()

        # Check for metadata files
        puzzle_meta_path = output_dir / "metadata" / "puzzle_01.json"
        collection_meta_path = output_dir / "metadata" / "collection.json"
        assert puzzle_meta_path.is_file()
        assert collection_meta_path.is_file()

        # Check content of metadata
        with open(puzzle_meta_path, "r") as f:
            puzzle_data = json.load(f)

        assert puzzle_data["id"] == 1
        assert "theme" in puzzle_data
        assert "clues" in puzzle_data
        assert puzzle_data["validation"]["valid"] is True

        with open(collection_meta_path, "r") as f:
            collection_data = json.load(f)

        assert collection_data["puzzle_count"] == 1
        assert collection_data["validation_summary"]["valid_puzzles"] == 1

    def test_generate_zero_puzzles(self, engine_instance, output_dir):
        """Test that generating zero puzzles runs without error and creates no files."""
        engine_instance.puzzle_count = 0
        engine_instance.generate_puzzles()

        assert not any((output_dir / "puzzles").iterdir())
        assert not any((output_dir / "solutions").iterdir())

        # It should still create a collection file, but with 0 puzzles
        collection_meta_path = output_dir / "metadata" / "collection.json"
        assert collection_meta_path.is_file()
        with open(collection_meta_path, "r") as f:
            collection_data = json.load(f)
        assert collection_data["puzzle_count"] == 0


@pytest.mark.performance
@pytest.mark.skip(reason="Skip performance benchmark in CI to avoid flaky timeouts")
def test_performance_benchmark(engine_instance):
    """Benchmark the puzzle generation time. Should be less than 10 seconds."""
    start_time = time.time()

    engine_instance.generate_puzzles()

    end_time = time.time()
    duration = end_time - start_time

    print(f"Puzzle generation took {duration:.2f} seconds.")
    # This assertion might be flaky on slow CI/CD runners, but is a good benchmark
    assert duration < 10.0
