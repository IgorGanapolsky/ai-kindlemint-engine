"""
KindleMint Command-Line Interface

This module provides the main entry point for KindleMint's CLI,
offering tools for enhancing book metadata and other utilities.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import click

from kindlemint.marketing.seo_engine_2025 import SEOOptimizedMarketing

# Add src to path to allow importing from kindlemint package
# This is necessary for the CLI to find its own modules when run directly
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@click.group()
def cli():
    """
    Main command group for the KindleMint CLI, providing access to book generation and marketing commands.
    """
    pass


@cli.command("enhance-seo")
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, dir_okay=False,
                    readable=True, resolve_path=True),
    required=True,
    help="Path to the book metadata JSON file to enhance.",
)
def enhance_seo(input_path: str) -> None:  # pragma: no cover
    """
    Enhance book metadata with SEO-optimized marketing strategies and save the result as a new JSON file.
    
    Parameters:
        input_path (str): Path to the input JSON file containing book metadata.
    
    The enhanced metadata is written to a new file in the same directory, with a `_seo.json` suffix added to the original filename. Exits with status 1 if the input file is not valid JSON.
    """
    input_file = Path(input_path)
    with input_file.open("r", encoding="utf-8") as fp:
        try:
            book_data: Dict[str, Any] = json.load(fp)
        except json.JSONDecodeError as exc:  # pragma: no cover
            click.echo(f"❌ Failed to parse JSON: {exc}", err=True)
            raise SystemExit(1) from exc

    engine = SEOOptimizedMarketing()
    enhanced_data = engine.enhance_book_marketing(book_data)

    output_file = input_file.with_name(f"{input_file.stem}_seo.json")
    with output_file.open("w", encoding="utf-8") as fp:
        json.dump(enhanced_data, fp, ensure_ascii=False, indent=2)

    click.echo(f"✅ Enhanced metadata written to {output_file}")


if __name__ == "__main__":
    cli()
