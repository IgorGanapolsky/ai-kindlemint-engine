#!/usr/bin/env python3
"""
Configuration Usage Examples
This script demonstrates best practices for using the centralized configuration
system in the AI KindleMint Engine.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config_loader import config


def example_1_basic_usage():
    """Example 1: Basic configuration value access"""
    print("=== Example 1: Basic Configuration Access ===\n")

    # Get simple values with defaults
    page_width = config.get("kdp_specifications.paperback.page_width_in", 8.5)
    print(f"Page width: {page_width} inches")

    # Get nested values
    grid_size = config.get("puzzle_generation.crossword.grid_size")
    print(f"Crossword grid size: {grid_size}x{grid_size}")

    # Get with type conversion (config returns floats/ints as needed)
    dpi = config.get("kdp_specifications.dpi")
    pixels_width = int(page_width * dpi)
    print(f"Page width in pixels at {dpi} DPI: {pixels_width}")


def example_2_path_handling():
    """Example 2: Working with file paths"""
    print("\n=== Example 2: Path Handling ===\n")

    # Get base output directory as a Path object
    base_dir = Path(config.get_path("file_paths.base_output_dir"))
    print(f"Base output directory: {base_dir}")

    # Build a complete book path
    series_name = config.get("series_defaults.default_series_name")
    volume = 5  # Dynamic volume number
    book_dir = base_dir / series_name / f"volume_{volume}"
    paperback_dir = book_dir / config.get("file_paths.paperback_subdir")

    print(f"Volume 5 paperback directory: {paperback_dir}")

    # Use filename patterns
    pdf_pattern = config.get("file_paths.pdf_filename_pattern")
    pdf_filename = pdf_pattern.format(title=f"{series_name}_Volume_{volume}")
    pdf_path = paperback_dir / pdf_filename

    print(f"PDF path: {pdf_path}")


def example_3_typography_settings():
    """Example 3: Using typography configuration"""
    print("\n=== Example 3: Typography Configuration ===\n")

    # Get font settings
    title_font = config.get("typography.fonts.title")
    title_size = config.get("typography.font_sizes.title")

    print(f"Title font: {title_font} at {title_size}pt")

    # Get all font sizes as a dictionary
    font_sizes = {
        "title": config.get("typography.font_sizes.title"),
        "subtitle": config.get("typography.font_sizes.subtitle"),
        "body": config.get("typography.font_sizes.body"),
        "small": config.get("typography.font_sizes.small_text"),
    }

    print("Font size hierarchy:")
    for name, size in font_sizes.items():
        print(f"  {name}: {size}pt")


def example_4_reportlab_integration():
    """Example 4: Using config with ReportLab"""
    print("\n=== Example 4: ReportLab Integration ===\n")

    from reportlab.lib.units import inch

    # Convert inches to points (72 points = 1 inch)
    gutter = config.get("kdp_specifications.paperback.gutter_in") * inch
    outer_margin = config.get("kdp_specifications.paperback.outer_margin_in") * inch
    top_margin = config.get("kdp_specifications.paperback.top_margin_in") * inch

    print(f"Margins in points:")
    print(f"  Gutter: {gutter:.1f}pt ({gutter/inch:.3f} inches)")
    print(f"  Outer: {outer_margin:.1f}pt ({outer_margin/inch:.3f} inches)")
    print(f"  Top: {top_margin:.1f}pt ({top_margin/inch:.3f} inches)")

    # Cell size for crossword grids
    cell_size = config.get("puzzle_generation.crossword.cell_size_points")
    print(f"\nCrossword cell size: {cell_size}pt")


def example_5_environment_overrides():
    """Example 5: Environment variable overrides"""
    print("\n=== Example 5: Environment Variable Overrides ===\n")

    # You can override any config value with environment variables
    # Format: KINDLEMINT_<SECTION>__<SUBSECTION>__<KEY>

    import os

    # Example: Override the base output directory
    os.environ["KINDLEMINT_FILE_PATHS__BASE_OUTPUT_DIR"] = "custom/output/path"

    # The config loader will automatically use the environment variable
    base_dir = config.get("file_paths.base_output_dir")
    print(f"Base output dir (after env override): {base_dir}")

    # Clean up
    del os.environ["KINDLEMINT_FILE_PATHS__BASE_OUTPUT_DIR"]


def example_6_validation_thresholds():
    """Example 6: Using QA validation thresholds"""
    print("\n=== Example 6: QA Validation Configuration ===\n")

    # Get validation thresholds
    min_score = config.get("qa_validation.minimum_score")
    critical_penalty = config.get("qa_validation.critical_issue_penalty")

    print(f"Minimum passing score: {min_score}")
    print(f"Critical issue penalty: {critical_penalty} points")

    # Get puzzle constraints
    max_black_squares = config.get("puzzle_generation.crossword.max_black_square_ratio")
    print(f"\nMax black square ratio: {max_black_squares:.0%}")

    # Expected page count with tolerance
    expected_pages = config.get("kdp_specifications.expected_page_count")
    tolerance = config.get("qa_validation.page_count_tolerance")

    print(f"Expected pages: {expected_pages} ± {tolerance}")


def example_7_api_configuration():
    """Example 7: API settings (without exposing keys)"""
    print("\n=== Example 7: API Configuration ===\n")

    # Get API settings
    openai_model = config.get("api_settings.openai.gpt_model")
    dalle_model = config.get("api_settings.openai.dalle_model")

    print(f"OpenAI GPT model: {openai_model}")
    print(f"DALL-E model: {dalle_model}")

    # Get rate limits
    serpapi_rpm = config.get("api_settings.serpapi.requests_per_minute", 60)
    print(f"SerpAPI rate limit: {serpapi_rpm} requests/minute")

    # Note: API keys should come from environment variables, not config.yaml
    print("\nNote: API keys should be set via environment variables:")
    print("  - OPENAI_API_KEY")
    print("  - SENTRY_DSN")
    print("  - SLACK_WEBHOOK_URL")


def main():
    """Run all examples"""
    print("AI KindleMint Engine - Configuration Usage Examples")
    print("=" * 60)

    example_1_basic_usage()
    example_2_path_handling()
    example_3_typography_settings()
    example_4_reportlab_integration()
    example_5_environment_overrides()
    example_6_validation_thresholds()
    example_7_api_configuration()

    print("\n" + "=" * 60)
    print("For more information, see scripts/config_loader.py")


if __name__ == "__main__":
    main()
