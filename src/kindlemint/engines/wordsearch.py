#!/usr/bin/env python3
"""
Word Search Generator - Command Line Interface
Generates Word Search puzzles for KindleMint Engine
"""
import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class WordSearchGenerator:
    """Generate Word Search puzzles with a simple random grid and a word list."""

    def __init__(self, output_dir, puzzle_count=50, grid_size=15, words_file=None):
        self.grid_size = grid_size
        self.puzzle_count = puzzle_count
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Prepare subdirectories
        self.puzzles_dir = self.output_dir / "puzzles"
        self.puzzles_dir.mkdir(exist_ok=True)
        self.metadata_dir = self.output_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        # Load word list
        if words_file:
            wf = Path(words_file)
            if not wf.exists():
                raise FileNotFoundError(f"Words file not found: {wf}")
            # Expect one word per line
            self.words = [
                w.strip().upper() for w in wf.read_text().splitlines() if w.strip()
            ]
        else:
            # Default sample words
            self.words = ["PUZZLE", "KINDLE", "BOOK", "ENGINE", "SOLUTION"]

    """ Generate Grid"""


def _generate_grid(self):
    # Fill grid with random uppercase letters
    return [
        [random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
         for __var in range(self.grid_size)]
        for __var in range(self.grid_size)
    ]

    """ Create Image"""


def _create_image(self, grid, puzzle_id):
    cell_size = 40
    margin = 20
    img_size = self.grid_size * cell_size + 2 * margin
    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)
    # Load font or default
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    # Draw grid and letters
    for i in range(self.grid_size + 1):
        lw = 2
        # vertical
        draw.line(
            [
                (margin + i * cell_size, margin),
                (margin + i * cell_size, img_size - margin),
            ],
            fill="black",
            width=lw,
        )
        # horizontal
        draw.line(
            [
                (margin, margin + i * cell_size),
                (img_size - margin, margin + i * cell_size),
            ],
            fill="black",
            width=lw,
        )
    for r in range(self.grid_size):
        for c in range(self.grid_size):
            letter = grid[r][c]
            # Compute text size
            try:
                w, h = font.getsize(letter)
            except AttributeError:
                # Fallback to textbbox if getsize is unavailable
                bbox = draw.textbbox((0, 0), letter, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = margin + c * cell_size + (cell_size - w) / 2
            y = margin + r * cell_size + (cell_size - h) / 2
            draw.text((x, y), letter, fill="black", font=font)
    # Save image
    img_path = self.puzzles_dir / f"word_search_puzzle_{puzzle_id:02d}.png"
    img.save(img_path, "PNG")
    return img_path

    """Generate Puzzles"""


def generate_puzzles(self):
    print(f"📝 WORD SEARCH - Generating {self.puzzle_count} puzzles")
    puzzles = []
    for i in range(1, self.puzzle_count + 1):
        grid = self._generate_grid()
        img_path = self._create_image(grid, i)
        data = {
            "id": i,
            "words": self.words,
            "grid_size": self.grid_size,
            "grid": grid,
            "grid_path": str(img_path),
        }
        # save metadata
        meta_file = self.metadata_dir / f"word_search_puzzle_{i:02d}.json"
        with open(meta_file, "w") as mf:
            json.dump(data, mf, indent=2)
        puzzles.append(data)
    # Save collection metadata
    collection = {
        "puzzle_count": self.puzzle_count,
        "grid_size": self.grid_size,
        "generation_date": datetime.now().isoformat(),
        "words": self.words,
    }
    coll_file = self.metadata_dir / "word_search_collection.json"
    with open(coll_file, "w") as cf:
        json.dump(collection, cf, indent=2)
    print(f"✅ Generated {self.puzzle_count} Word Search puzzles")
    return puzzles


# Export the main class
__all__ = ["WordSearchGenerator"]

"""Main"""


def main():
    parser = argparse.ArgumentParser(
        description="Word Search Generator - Generate puzzles for KindleMint Engine"
    )
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument(
        "--count", type=int, default=50, help="Number of puzzles to generate"
    )
    parser.add_argument(
        "--grid-size", type=int, default=15, help="Grid dimension (NxN)"
    )
    parser.add_argument(
        "--words-file", help="Path to newline-separated words file")
    args = parser.parse_args()
    try:
        gen = WordSearchGenerator(
            output_dir=args.output,
            puzzle_count=args.count,
            grid_size=args.grid_size,
            words_file=args.words_file,
        )
        gen.generate_puzzles()
        return 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
