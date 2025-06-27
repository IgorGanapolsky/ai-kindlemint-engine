#!/usr/bin/env python3
"""
CLI entrypoint for KindleMint Engine.
"""
import click
from pathlib import Path

# Import formatter classes
from scripts.create_professional_crossword_pdf import ProfessionalCrosswordFormatter
from scripts.create_real_crossword_book import RealCrosswordFormatter
from scripts.enhanced_epub_generator import EnhancedEpubFormatter
from scripts.book_layout_bot import BookLayoutFormatter

# Registry of available formatters
FORMATTERS = {
    "professional-crossword": ProfessionalCrosswordFormatter,
    "real-crossword": RealCrosswordFormatter,
    "enhanced-epub": EnhancedEpubFormatter,
    "book-layout": BookLayoutFormatter,
}


@click.group()
def cli():
    """KindleMint Engine CLI"""
    pass


@cli.command("generate")
@click.option(
    "--formatter",
    type=click.Choice(FORMATTERS.keys()),
    required=True,
    help="Formatter to use for generation",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Optional output path for the generated file",
)
def generate(formatter, output):  # noqa: D103
    """
    Generate a book using the specified formatter.
    """
    fmt_class = FORMATTERS[formatter]
    if output:
        fmt = fmt_class(Path(output))
    else:
        fmt = fmt_class()
    result_path = fmt.create_pdf()
    click.echo(f"Generated: {result_path}")


@cli.command("list")
def list_formatters():  # noqa: D103
    """
    List available formatters.
    """
    click.echo("Available formatters:")
    for name in FORMATTERS:
        click.echo(f"  - {name}")


if __name__ == "__main__":
    cli()
