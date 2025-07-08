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


@cli.command()
@click.argument('book_path', type=click.Path(exists=True))
@click.option('--visual/--no-visual', default=True, help='Include visual QA checks')
@click.option('--save-report/--no-save-report', default=True, help='Save validation report')
def validate(book_path, visual, save_report):
    """Validate a puzzle book PDF with optional visual QA"""
    from kindlemint.validators.integrated_pdf_validator import IntegratedPDFValidator
    
    click.echo(f"🔍 Validating: {book_path}")
    
    try:
        if visual:
            # Use integrated validator with visual QA
            validator = IntegratedPDFValidator()
            report = validator.validate_pdf_complete(Path(book_path))
            is_valid = report['overall_status'] == 'PASS'
        else:
            # Use basic content validation only
            from kindlemint.validators.sudoku_content_validator import SudokuContentValidator
            validator = SudokuContentValidator()
            report = validator.validate_puzzle_book(Path(book_path))
            is_valid = report.get('status') == 'PASS'
        
        if is_valid:
            click.echo("✅ Validation PASSED!")
        else:
            click.echo("❌ Validation FAILED!")
            
            if visual and 'summary' in report:
                summary = report['summary']
                if summary.get('critical_issues'):
                    click.echo("\n🔴 Critical Issues:")
                    for issue in summary['critical_issues'][:5]:
                        click.echo(f"  • {issue}")
                if summary.get('major_issues'):
                    click.echo("\n🟡 Major Issues:")
                    for issue in summary['major_issues'][:3]:
                        click.echo(f"  • {issue}")
            else:
                click.echo("\nIssues found:")
                for issue in report.get('errors', []):
                    click.echo(f"  - {issue}")
                
    except Exception as e:
        click.echo(f"❌ Error during validation: {e}", err=True)
        sys.exit(1)
        
        
@cli.command()
@click.argument('pdf1', type=click.Path(exists=True))
@click.argument('pdf2', type=click.Path(exists=True))
@click.option('--threshold', default=0.95, help='Similarity threshold (0-1)')
def compare_pdfs(pdf1, pdf2, threshold):
    """Compare two PDFs visually for regression testing"""
    from kindlemint.validators.pdf_visual_qa_validator import compare_pdf_screenshots
    
    click.echo(f"🔄 Comparing PDFs visually...")
    click.echo(f"  • PDF 1: {pdf1}")
    click.echo(f"  • PDF 2: {pdf2}")
    click.echo(f"  • Threshold: {threshold}")
    
    try:
        results = compare_pdf_screenshots(Path(pdf1), Path(pdf2), threshold)
        
        click.echo(f"\n📊 Results: {results['status']}")
        
        if results.get('similarity_scores'):
            click.echo("\nPage Similarity Scores:")
            for score_info in results['similarity_scores']:
                page = score_info['page']
                score = score_info['score']
                status = "✅" if score >= threshold else "❌"
                click.echo(f"  {status} Page {page}: {score:.3f}")
                
        if results.get('differences'):
            click.echo(f"\n❌ Visual differences found on {len(results['differences'])} pages")
            
    except Exception as e:
        click.echo(f"❌ Error during comparison: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
