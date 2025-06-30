#!/usr/bin/env python3
"""
CLI entrypoint for KindleMint Engine.
"""
from pathlib import Path

import click

from scripts.book_layout_bot import BookLayoutFormatter

# Import formatter classes
from scripts.create_professional_crossword_pdf import ProfessionalCrosswordFormatter
from scripts.create_real_crossword_book import RealCrosswordFormatter
from scripts.daily_tasks import run_daily_tasks
from scripts.enhanced_epub_generator import EnhancedEpubFormatter

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
    click.echo("")
    click.echo("Use 'kindlemint publish --metadata <file>' to upload to KDP")


@cli.command("daily-tasks")
def daily_tasks():  # noqa: D103
    """
    Run the daily AI publishing task scheduler.
    """
    run_daily_tasks()


if __name__ == "__main__":
    cli()
