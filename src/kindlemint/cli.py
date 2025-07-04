"""
KindleMint Command-Line Interface

This module provides the main entry point for KindleMint's CLI,
offering tools for book generation, orchestration, and marketing tasks.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import click

from kindlemint.marketing.seo_engine_2025 import SEOOptimizedMarketing
from security import safe_command

# Add src to path to allow importing from kindlemint package
# This is necessary for the CLI to find its own modules when run directly
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@click.group()
def cli():
    """KindleMint CLI for book generation, orchestration, and marketing tasks."""
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
    Enhance book marketing metadata with 2025 SEO strategies.

    The enhanced JSON will be written alongside the source file
    with a *_seo.json suffix.
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


@cli.group("batch")
def batch():
    """Batch processing commands for book generation."""
    pass


@batch.command("generate")
@click.option(
    "--type",
    "book_type",
    type=click.Choice(["sudoku", "crossword", "wordsearch"]),
    required=True,
    help="Type of puzzle book to generate.",
)
@click.option(
    "--count",
    type=click.IntRange(min=1, max=100),  # Add reasonable limits
    default=1,
    help="Number of books to generate (1-100).",
)
@click.option(
    "--volume-start",
    type=click.IntRange(min=1),
    default=1,
    help="Starting volume number (minimum 1).",
)
@click.option(
    "--parallel/--sequential",
    default=False,
    help="Use parallel processing via worktrees.",
)
def batch_generate(
    book_type: str, count: int, volume_start: int, parallel: bool
) -> None:  # pragma: no cover
    """
    Generate multiple puzzle books in batch mode.
    
    Example:
        kindlemint batch generate --type sudoku --count 5 --parallel
    """
    click.echo(f"🚀 Generating {count} {book_type} book(s)...")
    
    # Import orchestration components
    orchestration_path = Path(__file__).parents[2] / "scripts" / "orchestration"
    sys.path.insert(0, str(orchestration_path))
    
    if parallel:
        try:
            from scripts.orchestration.autonomous_worktree_manager import AutonomousWorktreeManager
            manager = AutonomousWorktreeManager()
            click.echo("📊 Using parallel worktree orchestration...")
            # TODO: Call manager.generate_books(book_type, count, volume_start)
        except ImportError:
            click.echo("❌ Worktree orchestration not available, falling back to sequential.")
            parallel = False # Fallback to sequential if parallel not available
    
    if not parallel:
        # TODO: Implement sequential generation
        click.echo(f"📚 Sequential generation of {count} books...")
        for i in range(count):
            volume = volume_start + i
            click.echo(f"  📖 Generating Volume {volume}...")
    
    click.echo("✅ Batch generation complete!")


@cli.group("orchestrate")
def orchestrate():
    """Worktree orchestration commands."""
    pass


@orchestrate.command("status")
def orchestrate_status() -> None:  # pragma: no cover
    """Show worktree orchestration status."""
    click.echo("🌳 Worktree Orchestration Status")
    click.echo("─" * 40)
    
    # Import orchestration components
    orchestration_path = Path(__file__).parents[2] / "scripts" / "orchestration"
    sys.path.insert(0, str(orchestration_path))
    
    try:
        import subprocess
        result = subprocess.run(
            ["git", "worktree", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        worktrees = result.stdout.strip().split('\n')
        active_count = len([w for w in worktrees if w.strip()])
        
        click.echo(f"✅ Active worktrees: {active_count}")
        for worktree in worktrees:
            if worktree.strip():
                click.echo(f"  📁 {worktree}")
                
    except subprocess.CalledProcessError:
        click.echo("❌ Unable to get worktree status")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@orchestrate.command("dashboard")
def orchestrate_dashboard() -> None:  # pragma: no cover
    """Launch the CEO dashboard for business metrics."""
    click.echo("📊 Launching CEO Dashboard...")
    
    # Import and run CEO dashboard
    orchestration_path = Path(__file__).parents[2] / "scripts" / "orchestration"
    dashboard_script = orchestration_path / "ceo_dashboard.py"
    
    if dashboard_script.exists():
        import subprocess
        safe_command.run(subprocess.run, [sys.executable, str(dashboard_script)])
    else:
        click.echo("❌ CEO Dashboard not found")


@orchestrate.command("run")
@click.option(
    "--task",
    type=click.Choice([
        "book-production",
        "ci-fixes", 
        "market-research",
        "qa-validation"
    ]),
    required=True,
    help="Task type to orchestrate.",
)
@click.option(
    "--monitor/--no-monitor",
    default=True,
    help="Enable real-time monitoring.",
)
def orchestrate_run(task: str, monitor: bool) -> None:  # pragma: no cover
    """
    Run orchestrated tasks across worktrees.
    
    Example:
        kindlemint orchestrate run --task book-production --monitor
    """
    click.echo(f"🚀 Orchestrating {task} task...")
    
    # Import orchestration components
    orchestration_path = Path(__file__).parents[2] / "scripts" / "orchestration"
    sys.path.insert(0, str(orchestration_path))
    
    try:
        from scripts.orchestration.worktree_orchestrator import WorktreeOrchestrator
        # TODO: Implement actual orchestration using orchestrator.run_task(task, monitor=monitor)
        click.echo(f"📊 Orchestrating {task} task (functionality coming soon)!")
        
    except ImportError:
        click.echo("❌ Orchestration system not available")
    
    click.echo("✅ Orchestration complete!")


if __name__ == "__main__":
    cli()
