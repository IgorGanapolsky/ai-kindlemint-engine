import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "word_search_generator.py"


@pytest.mark.parametrize("count", [1, 3])
def test_word_search_generator_creates_files(tmp_path, count):
    """Test Word Search Generator Creates Files"""
    output_dir = tmp_path / "output"
    # Run the generator script
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--output",
        str(output_dir),
        "--count",
        str(count),
        "--grid-size",
        "10",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Ensure it ran successfully
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    # Check directories exist
    puzzles_dir = output_dir / "puzzles"
    metadata_dir = output_dir / "metadata"
    assert puzzles_dir.exists() and puzzles_dir.is_dir(), "Puzzles directory missing"
    assert metadata_dir.exists() and metadata_dir.is_dir(), "Metadata directory missing"
    # Check puzzle images and metadata files
    png_files = sorted(puzzles_dir.glob("*.png"))
    json_files = sorted(metadata_dir.glob("word_search_puzzle_*.json"))
    assert len(png_files) == count, f"Expected {count} PNGs, found {len(png_files)}"
    assert (
        len(json_files) == count
    ), f"Expected {count} metadata JSONs, found {len(json_files)}"
    # Check collection metadata
    coll_file = metadata_dir / "word_search_collection.json"
    assert coll_file.exists(), "Collection metadata JSON missing"
    # Validate JSON structure
    import json

    coll = json.loads(coll_file.read_text())
    assert coll.get("puzzle_count") == count
    assert "words" in coll and isinstance(coll["words"], list)


    """Test Words File Option"""
def test_words_file_option(tmp_path):
    # Create a custom words file
    words = ["TEST", "PYTEST", "KINDLE"]
    words_file = tmp_path / "words.txt"
    words_file.write_text("\n".join(words))
    output_dir = tmp_path / "out2"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--output",
        str(output_dir),
        "--count",
        "2",
        "--words-file",
        str(words_file),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Script failed with custom words: {result.stderr}"
    # Check that metadata contains the custom words list
    coll_file = output_dir / "metadata" / "word_search_collection.json"
    import json

    coll = json.loads(coll_file.read_text())
    assert coll.get("words") == [w.upper() for w_var in words]
