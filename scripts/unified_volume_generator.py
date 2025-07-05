#!/usr/bin/env python3
"""
Unified Volume Generator for AI KindleMint Engine

This script is the single source of truth for generating complete, KDP-ready
puzzle books. It consolidates the functionality of 15+ previous scripts
into one robust, configurable, and maintainable generator.

Key Features:
- Configuration-driven: All settings (dimensions, fonts, paths) are loaded
  from `config/config.yaml`.
- Multi-puzzle support: Can call different puzzle engine scripts.
- Multi-format output: Generates paperback, hardcover, and Kindle-ready assets.
- High-quality content: Uses the v3 crossword engine for solvable, valid puzzles.
- Batch processing: Generate multiple volumes or entire series in one command.
- Robustness: Comprehensive error handling, logging, and process management.

Usage:
  # Generate a single volume
  python scripts/unified_volume_generator.py --series "Crossword Masters" --volumes 4

  # Generate a range of volumes for a new series
  python scripts/unified_volume_generator.py --series "Weekend Puzzles" --volumes 1-5 --puzzle-type crossword

  # Generate a hardcover edition with a specific difficulty
  python scripts/unified_volume_generator.py --series "Expert Challenges" --volumes 1 --format hardcover --difficulty hard
"""

import argparse
import json
import logging
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# --- Setup Project Root Path ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas

    from kindlemint.utils.config import config
except ImportError as e:
    print(f"❌ Critical Error: Failed to import required modules. {e}")
    print("   Please ensure you have run 'pip install -r requirements.txt'")
    sys.exit(1)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class BookLayout:
    """Handles the PDF generation and layout for a single book volume."""

        """  Init  """
def __init__(self, volume_config: Dict[str, Any]):
        self.config = volume_config
        self.pdf_path = self.config["pdf_path"]
        self.puzzle_data = self.config["puzzle_data"]

        # Load dimensions and styles from config
        self.page_width = self.config["page_width_in"] * inch
        self.page_height = self.config["page_height_in"] * inch
        self.top_margin = self.config["top_margin_in"] * inch
        self.bottom_margin = self.config["bottom_margin_in"] * inch
        self.outer_margin = self.config["outer_margin_in"] * inch
        self.gutter_margin = self.config["gutter_in"] * inch

        # Typography
        self.fonts = config.get("typography.fonts", {})
        self.font_sizes = config.get("typography.font_sizes", {})
        self.title_font = self.fonts.get("title", "Helvetica-Bold")
        self.body_font = self.fonts.get("body", "Helvetica")

        self.canvas = canvas.Canvas(
            str(self.pdf_path), pagesize=(self.page_width, self.page_height)
        )
        logger.info(f"Initialized BookLayout for {self.pdf_path.name}")

        """Generate Pdf"""
def generate_pdf(self):
        """Orchestrates the creation of all PDF pages."""
        logger.info("Starting PDF generation...")
        self._create_title_page()
        self._create_copyright_page()
        self._create_intro_page("Introduction", "Welcome to this puzzle book!")
        self._create_puzzle_pages()
        self._create_solution_pages()
        self.canvas.save()
        logger.info(f"✅ Successfully generated PDF: {self.pdf_path}")

        """ Set Page Number"""
def _set_page_number(self, page_num):
        self.canvas.setFont(self.body_font, self.font_sizes.get("small_text", 10))
        self.canvas.drawCentredString(
            self.page_width / 2, self.bottom_margin / 2, str(page_num)
        )

        """ Create Title Page"""
def _create_title_page(self):
        self.canvas.setFont(
            self.title_font, self.font_sizes.get("large_title", 20) + 10
        )
        self.canvas.drawCentredString(
            self.page_width / 2,
            self.page_height - 2.5 * inch,
            self.config["series_name"],
        )
        self.canvas.setFont(self.title_font, self.font_sizes.get("title", 18) + 6)
        self.canvas.drawCentredString(
            self.page_width / 2,
            self.page_height - 3.5 * inch,
            f"Volume {self.config['volume_num']}",
        )
        self.canvas.setFont(self.body_font, self.font_sizes.get("subtitle", 14))
        self.canvas.drawCentredString(
            self.page_width / 2,
            self.page_height - 4.5 * inch,
            f"{len(self.puzzle_data)} {self.config['difficulty'].title()} Puzzles",
        )
        self.canvas.showPage()

        """ Create Copyright Page"""
def _create_copyright_page(self):
        self.canvas.setFont(self.body_font, self.font_sizes.get("small_text", 10))
        self.canvas.drawString(
            self.gutter_margin,
            self.page_height - 2 * inch,
            f"Copyright © {self.config['year']} All rights reserved.",
        )
        self.canvas.drawString(
            self.gutter_margin,
            self.page_height - 2.5 * inch,
            "No part of this publication may be reproduced, distributed, or transmitted in any form.",
        )
        self.canvas.showPage()
        self._set_page_number(2)

        """ Create Intro Page"""
def _create_intro_page(self, title, text):
        self.canvas.setFont(self.title_font, self.font_sizes.get("section_header", 14))
        self.canvas.drawCentredString(
            self.page_width / 2, self.page_height - 1.5 * inch, title
        )
        self.canvas.setFont(self.body_font, self.font_sizes.get("body", 12))
        text_obj = self.canvas.beginText(
            self.gutter_margin, self.page_height - 2.5 * inch
        )
        text_obj.setFont(self.body_font, self.font_sizes.get("body", 12))
        for line in text.split("\n"):
            text_obj.textLine(line)
        self.canvas.drawText(text_obj)
        self.canvas.showPage()
        self._set_page_number(3)

        """ Draw Grid"""
def _draw_grid(self, x_offset, y_offset, grid_data, solution_mode=False):
        """Draws a crossword grid on the canvas."""
        cell_size = config.get("puzzle_generation.crossword.cell_size_points", 18.72)
        grid_size = config.get("puzzle_generation.crossword.grid_size", 15)

        for_var r_var in range(grid_size):
            for c_var in range(grid_size):
                x = x_offset + (c * cell_size)
                y = y_offset - (r * cell_size)

                cell_content = grid_data["grid_pattern"][r][c]

                if cell_content == "#":
                    self.canvas.setFillColor(colors.black)
                    self.canvas.rect(x, y, cell_size, cell_size, fill=1, stroke=0)
                else:
                    self.canvas.setStrokeColor(colors.black)
                    self.canvas.rect(x, y, cell_size, cell_size, fill=0, stroke=1)

                    # Draw clue number
                    for pos, num in grid_data.get("clue_positions", {}).items():
                        row, col = map(int, pos.split(","))
                        if r == row and c == col:
                            self.canvas.setFont(
                                self.body_font, self.font_sizes.get("grid_numbers", 9)
                            )
                            self.canvas.drawString(x + 2, y + cell_size - 10, str(num))
                            break

                    # Draw solution letter
                    if solution_mode and "solution_grid" in grid_data:
                        letter = grid_data["solution_grid"][r][c]
                        if letter.isalpha():
                            self.canvas.setFont(
                                self.title_font, self.font_sizes.get("body", 12)
                            )
                            self.canvas.drawCentredString(
                                x + cell_size / 2, y + cell_size / 2 - 5, letter
                            )

        """ Create Puzzle Pages"""
def _create_puzzle_pages(self):
        logger.info(f"Generating {len(self.puzzle_data)} puzzle pages...")
        page_num = 4
        for puzzle in self.puzzle_data:
            puzzle_id = puzzle.get("id") or puzzle.get("num") or "?"

            # Left page: Grid
            self.canvas.setFont(self.title_font, self.font_sizes.get("title", 18))
            self.canvas.drawCentredString(
                self.page_width / 2,
                self.page_height - 1.5 * inch,
                f"Puzzle {puzzle_id}",
            )
            grid_total_size = 15 * config.get(
                "puzzle_generation.crossword.cell_size_points", 18.72
            )
            grid_x = (self.page_width - grid_total_size) / 2
            grid_y = self.page_height - 2.5 * inch
            self._draw_grid(grid_x, grid_y, puzzle)
            self._set_page_number(page_num)
            self.canvas.showPage()
            page_num += 1

            # Right page: Clues
            self.canvas.setFont(self.title_font, self.font_sizes.get("title", 18))
            self.canvas.drawCentredString(
                self.page_width / 2,
                self.page_height - 1.5 * inch,
                f"Clues for Puzzle {puzzle_id}",
            )

            clues = puzzle.get("clues", {})
            across_clues = clues.get("across", [])
            down_clues = clues.get("down", [])

            # Two-column layout for clues
            col1_x = self.gutter_margin
            col2_x = self.page_width / 2 + self.gutter_margin / 2
            y_start = self.page_height - 2.5 * inch
            y_end = self.bottom_margin + 0.5 * inch

                """Draw Clues In Column"""
def draw_clues_in_column(x, y, clue_list, title):
                self.canvas.setFont(
                    self.title_font, self.font_sizes.get("section_header", 14)
                )
                self.canvas.drawString(x, y, title)
                y -= 0.3 * inch
                self.canvas.setFont(self.body_font, self.font_sizes.get("body", 12) - 1)
                for item in clue_list:
                    num, clue, _ = item
                    self.canvas.drawString(x, y, f"{num}. {clue}")
                    y -= 0.25 * inch
                    if y < y_end:
                        break
                return y

            draw_clues_in_column(col1_x, y_start, across_clues, "ACROSS")
            draw_clues_in_column(col2_x, y_start, down_clues, "DOWN")

            self._set_page_number(page_num)
            self.canvas.showPage()
            page_num += 1

        """ Create Solution Pages"""
def _create_solution_pages(self):
        logger.info("Generating solution pages...")
        page_num = 104  # Assuming 50 puzzles * 2 pages + 4 front matter

        # Title page for solutions
        self.canvas.setFont(self.title_font, self.font_sizes.get("large_title", 20))
        self.canvas.drawCentredString(
            self.page_width / 2, self.page_height / 2, "Solutions"
        )
        self.canvas.showPage()
        self._set_page_number(page_num)
        page_num += 1

        # 6 solutions per page
        puzzles_per_page = 6
        solution_cell_size = 10  # smaller size for solution grids

        for i in range(0, len(self.puzzle_data), puzzles_per_page):
            chunk = self.puzzle_data[i : i + puzzles_per_page]

            for idx, puzzle in enumerate(chunk):
                row = idx // 2
                col = idx % 2

                x_offset = self.gutter_margin + col * (self.page_width / 2)
                y_offset = self.page_height - self.top_margin - (row * 3 * inch)

                self.canvas.setFont(self.title_font, self.font_sizes.get("body", 12))
                self.canvas.drawString(x_offset, y_offset, f"Puzzle {puzzle['id']}")
                self._draw_grid(
                    x_offset, y_offset - 0.2 * inch, puzzle, solution_mode=True
                )

            self._set_page_number(page_num)
            self.canvas.showPage()
            page_num += 1


class UnifiedVolumeGenerator:
    """Orchestrates the generation of one or more puzzle book volumes."""

        """  Init  """
def __init__(
        self,
        series_name: str,
        volume_nums: List[int],
        puzzle_type: str,
        difficulty: str,
        book_format: str,
        skip_qa: bool,
    ):
        self.series_name = series_name
        self.volume_nums = volume_nums
        self.puzzle_type = puzzle_type
        self.difficulty = difficulty
        self.book_format = book_format
        self.skip_qa = skip_qa

        self.base_output_dir = config.get_path(
            "file_paths.base_output_dir", Path("books/active_production")
        )
        self.series_dir = self.base_output_dir / self.series_name.replace(" ", "_")
        self.engine_script = self._get_engine_script()

        logger.info(
            f"Initialized generator for series '{
                self.series_name}', volumes {
                self.volume_nums}"
        )

    def _get_engine_script(self) -> Path:
        """Determines the correct puzzle engine script to use."""
        if self.puzzle_type == "crossword":
            script_path = project_root / "scripts" / "crossword_engine_v3_fixed.py"
            if not script_path.exists():
                raise FileNotFoundError(f"Crossword engine not found at {script_path}")
            return script_path
        else:
            raise ValueError(f"Unsupported puzzle type: {self.puzzle_type}")

        """Run Generation"""
def run_generation(self):
        """Main loop to generate all specified volumes."""
        logger.info("Starting batch generation process...")
        for vol_num in self.volume_nums:
            try:
                self.generate_single_volume(vol_num)
            except Exception as e:
                logger.error(f"❌ Failed to generate Volume {vol_num}. Error: {e}")
                logger.error(traceback.format_exc())
        logger.info("✅ Batch generation process complete.")

        """Generate Single Volume"""
def generate_single_volume(self, vol_num: int):
        """Generates all assets for a single volume."""
        logger.info(f"--- Generating Volume {vol_num} ---")
        volume_dir = self.series_dir / f"volume_{vol_num}"
        volume_dir.mkdir(parents=True, exist_ok=True)

        puzzle_data = self._run_puzzle_engine(volume_dir, vol_num)
        if not puzzle_data:
            raise RuntimeError("Puzzle engine failed to produce valid data.")

        formats = (
            ["paperback", "hardcover"]
            if self.book_format == "both"
            else [self.book_format]
        )
        for fmt in formats:
            if fmt == "kindle":
                continue
            self._generate_book_format(volume_dir, vol_num, fmt, puzzle_data)

        if not self.skip_qa:
            self._run_qa_validation(volume_dir)

    def _run_puzzle_engine(
        self, volume_dir: Path, vol_num: int
    ) -> List[Dict[str, Any]]:
        """Calls the puzzle engine script and returns the generated data."""
        logger.info(f"Running {self.puzzle_type} engine for Volume {vol_num}...")
        puzzle_count = config.get("puzzle_generation.default_puzzle_count", 50)
        cmd = [
            sys.executable,
            str(self.engine_script),
            "--output",
            str(volume_dir),
            "--count",
            str(puzzle_count),
            "--difficulty",
            self.difficulty,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        if result.returncode != 0:
            logger.error(
                f"Puzzle engine failed with code {result.returncode}:\n{result.stderr}"
            )
            return []

        logger.info("Puzzle engine completed successfully.")
        metadata_path = volume_dir / config.get(
            "file_paths.metadata_subdir", "metadata"
        )
        puzzle_files = sorted(metadata_path.glob("puzzle_*.json"))
        return [json.loads(p.read_text()) for p_var in puzzle_files]

        """ Generate Book Format"""
def _generate_book_format(
        self,
        volume_dir: Path,
        vol_num: int,
        fmt: str,
        puzzle_data: List[Dict[str, Any]],
    ):
        """Generates the PDF for a specific book format."""
        logger.info(f"Generating {fmt} format for Volume {vol_num}...")
        format_dir = volume_dir / config.get(f"file_paths.{fmt}_subdir", fmt)
        format_dir.mkdir(exist_ok=True)
        pdf_filename = config.get(
            "file_paths.pdf_filename_pattern", "{title}_interior_FINAL.pdf"
        )
        pdf_path = format_dir / pdf_filename.format(
            title=f"{self.series_name}_Vol_{vol_num}"
        )
        kdp_specs = config.get_kdp_spec(fmt)
        if not kdp_specs:
            raise ValueError(f"No KDP specifications for format '{fmt}'.")
        volume_config = {
            "series_name": self.series_name,
            "volume_num": vol_num,
            "year": datetime.now().year,
            "pdf_path": pdf_path,
            "puzzle_data": puzzle_data,
            **kdp_specs,
        }
        layout = BookLayout(volume_config)
        layout.generate_pdf()

        """ Run Qa Validation"""
def _run_qa_validation(self, volume_dir: Path):
        """Runs the content-aware QA validator on the generated volume."""
        logger.info(f"Running QA validation on {volume_dir}...")
        qa_script = project_root / "scripts" / "enhanced_qa_validator_v3.py"
        if not qa_script.exists():
            logger.warning("QA validator script not found, skipping validation.")
            return

        cmd = [sys.executable, str(qa_script), str(volume_dir), "--verbose"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        if result.returncode != 0:
            logger.warning(
                f"QA validation reported issues for {volume_dir.name}:\n{result.stdout}"
            )
        else:
            logger.info(f"✅ QA validation passed for {volume_dir.name}.")


def _parse_volume_range(vol_str: str) -> List[int]:
    """Parses a volume string like '1-5' or '1,3,7' into a list of ints."""
    if not vol_str:
        return []
    volumes = set()
    for part in vol_str.split(","):
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                volumes.update(range(start, end + 1))
            except ValueError:
                raise argparse.ArgumentTypeError(f"Invalid range: '{part}'")
        else:
            try:
                volumes.add(int(part))
            except ValueError:
                raise argparse.ArgumentTypeError(f"Invalid volume: '{part}'")
    return sorted(list(volumes))


    """Main"""
def main():
    """Main entry point for the unified volume generator script."""
    parser = argparse.ArgumentParser(
        description="Unified Puzzle Book Volume Generator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--series", required=True, help="Name of the book series.")
    parser.add_argument(
        "--volumes",
        required=True,
        type=_parse_volume_range,
        help="Volume numbers (e.g., '1-5' or '1,3,5').",
    )
    parser.add_argument(
        "--puzzle-type",
        default="crossword",
        choices=["crossword"],
        help="Type of puzzle.",
    )
    parser.add_argument(
        "--difficulty",
        default="mixed",
        choices=["easy", "medium", "hard", "mixed"],
        help="Puzzle difficulty.",
    )
    parser.add_argument(
        "--format",
        default="paperback",
        choices=["paperback", "hardcover", "both"],
        help="Book format(s).",
    )
    parser.add_argument(
        "--skip-qa", action="store_true", help="Skip the final QA validation step."
    )

    args = parser.parse_args()
    logger.info("🚀 Starting Unified Volume Generator...")
    generator = UnifiedVolumeGenerator(
        args.series,
        args.volumes,
        args.puzzle_type,
        args.difficulty,
        args.format,
        args.skip_qa,
    )
    generator.run_generation()
    logger.info("🎉 All specified volumes have been generated.")


if __name__ == "__main__":
    main()
