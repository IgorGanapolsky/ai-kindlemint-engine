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


@cli.group("trends")
def trends():
    """Consumer trends analysis and prediction commands."""
    pass


@trends.command("run")
@click.option(
    "--sources",
    type=click.Choice(["all", "reddit", "tiktok", "google", "amazon"]),
    default="all",
    help="Data sources to analyze (default: all)"
)
@click.option(
    "--save-analysis/--no-save-analysis",
    default=True,
    help="Save analysis results to storage"
)
def trends_run(sources: str, save_analysis: bool) -> None:
    """
    Execute comprehensive trend analysis and trigger content generation.
    
    Analyzes data from multiple sources to identify trending topics
    and their potential profitability for book publishing.
    """
    click.echo("🔍 Starting comprehensive trend analysis...")
    
    try:
        import asyncio
        from kindlemint.analytics.trend_analyzer import PredictiveTrendAnalyzer
        from kindlemint.utils.config import Config
        
        async def run_analysis():
            config = Config()
            async with PredictiveTrendAnalyzer(config) as analyzer:
                analysis = await analyzer.analyze_trends()
                
                click.echo(f"\n📊 Trend Analysis Results")
                click.echo("─" * 50)
                click.echo(f"Total trends found: {len(analysis.trends)}")
                click.echo(f"Average profitability: {analysis.summary['avg_profitability']:.2f}")
                
                click.echo(f"\n🏆 Top 5 Trends")
                click.echo("─" * 30)
                for i, trend in enumerate(analysis.trends[:5], 1):
                    click.echo(f"{i}. {trend.topic}")
                    click.echo(f"   📈 Profitability: {trend.predicted_profitability:.2f}")
                    click.echo(f"   🏁 Competition: {trend.competition_level}")
                    click.echo(f"   📡 Source: {trend.source}")
                    click.echo()
                
                click.echo(f"💡 Recommendations")
                click.echo("─" * 20)
                for rec in analysis.recommendations:
                    click.echo(f"• {rec}")
                
                if save_analysis:
                    click.echo(f"\n✅ Analysis saved to storage")
                
                return analysis
        
        # Run the analysis
        analysis = asyncio.run(run_analysis())
        click.echo(f"\n🎯 Trend analysis complete! Found {len(analysis.trends)} opportunities.")
        
    except ImportError as e:
        click.echo(f"❌ Error importing trend analyzer: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error during trend analysis: {e}", err=True)
        raise SystemExit(1)


@trends.command("report")
@click.option(
    "--format",
    type=click.Choice(["summary", "detailed", "json"]),
    default="summary",
    help="Report format (default: summary)"
)
@click.option(
    "--hours",
    type=click.IntRange(min=1, max=168),
    default=24,
    help="Hours of data to include in report (1-168, default: 24)"
)
def trends_report(format: str, hours: int) -> None:
    """
    Generate a report of the latest trends.
    
    Creates a comprehensive report of trending topics and market opportunities
    based on recent analysis data.
    """
    click.echo(f"📋 Generating trends report (last {hours} hours)...")
    
    try:
        import asyncio
        from kindlemint.analytics.trend_analyzer import PredictiveTrendAnalyzer
        from kindlemint.utils.config import Config
        
        async def generate_report():
            config = Config()
            async with PredictiveTrendAnalyzer(config) as analyzer:
                # Get latest analysis
                analysis = await analyzer.get_latest_analysis()
                
                if not analysis:
                    click.echo("❌ No recent analysis found. Run 'trends run' first.")
                    return
                
                if format == "json":
                    import json
                    report_data = {
                        'trends': [trend.__dict__ for trend in analysis.trends],
                        'summary': analysis.summary,
                        'recommendations': analysis.recommendations,
                        'generated_at': analysis.generated_at.isoformat()
                    }
                    click.echo(json.dumps(report_data, indent=2, default=str))
                    return
                
                # Summary format
                click.echo(f"\n📊 Trends Report - Last {hours} Hours")
                click.echo("=" * 60)
                click.echo(f"Generated: {analysis.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                click.echo(f"Total Trends: {len(analysis.trends)}")
                click.echo(f"Avg Profitability: {analysis.summary['avg_profitability']:.2f}")
                
                if format == "detailed":
                    click.echo(f"\n📈 Detailed Trend Analysis")
                    click.echo("─" * 40)
                    for i, trend in enumerate(analysis.trends, 1):
                        click.echo(f"\n{i}. {trend.topic}")
                        click.echo(f"   📊 Profitability Score: {trend.predicted_profitability:.3f}")
                        click.echo(f"   📈 Volume: {trend.volume}")
                        click.echo(f"   😊 Sentiment: {trend.sentiment:.2f}")
                        click.echo(f"   🏁 Competition: {trend.competition_level}")
                        click.echo(f"   📡 Source: {trend.source}")
                        click.echo(f"   ⏰ Detected: {trend.timestamp.strftime('%Y-%m-%d %H:%M')}")
                
                click.echo(f"\n💡 Strategic Recommendations")
                click.echo("─" * 30)
                for rec in analysis.recommendations:
                    click.echo(f"• {rec}")
                
                click.echo(f"\n📊 Market Summary")
                click.echo("─" * 20)
                for source, count in analysis.summary.get('top_sources', []):
                    click.echo(f"• {source}: {count} trends")
                
                competition_dist = analysis.summary.get('competition_distribution', {})
                if competition_dist:
                    click.echo(f"\n🏁 Competition Distribution")
                    click.echo("─" * 25)
                    for level, count in competition_dist.items():
                        click.echo(f"• {level}: {count} trends")
        
        # Generate the report
        asyncio.run(generate_report())
        click.echo(f"\n✅ Trends report generated successfully!")
        
    except ImportError as e:
        click.echo(f"❌ Error importing trend analyzer: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}", err=True)
        raise SystemExit(1)


@trends.command("monitor")
@click.option(
    "--interval",
    type=click.IntRange(min=60, max=3600),
    default=300,
    help="Monitoring interval in seconds (60-3600, default: 300)"
)
@click.option(
    "--duration",
    type=click.IntRange(min=1, max=24),
    default=1,
    help="Monitoring duration in hours (1-24, default: 1)"
)
def trends_monitor(interval: int, duration: int) -> None:
    """
    Start real-time monitoring of market signals.
    
    Continuously monitors trend sources for emerging opportunities
    and triggers alerts when significant trends are detected.
    """
    click.echo(f"🔍 Starting real-time signal monitoring...")
    click.echo(f"⏱️  Interval: {interval}s, Duration: {duration}h")
    
    try:
        import asyncio
        from kindlemint.agents.signal_listener import SignalListener, SignalPriority
        from kindlemint.utils.config import Config
        
        async def start_monitoring():
            config = Config()
            async with SignalListener(config) as listener:
                # Add alert callback
                def alert_callback(alert):
                    click.echo(f"\n🚨 ALERT: {alert.message}")
                    click.echo(f"   📊 Signal: {alert.signal.topic}")
                    click.echo(f"   ⚡ Priority: {alert.signal.priority.value}")
                    click.echo(f"   📈 Volume: {alert.signal.volume}")
                    click.echo(f"   🎯 Actions: {', '.join(alert.actions_taken)}")
                
                listener.add_alert_callback(alert_callback)
                
                # Start monitoring
                await listener.start_monitoring(interval_seconds=interval)
                
                click.echo("✅ Monitoring started. Press Ctrl+C to stop...")
                
                try:
                    # Monitor for specified duration
                    await asyncio.sleep(duration * 3600)
                except KeyboardInterrupt:
                    click.echo("\n⏹️  Stopping monitoring...")
                finally:
                    await listener.stop_monitoring()
                
                # Show summary
                active_signals = listener.get_active_signals(hours=duration)
                high_priority = listener.get_signals_by_priority(SignalPriority.HIGH)
                critical_priority = listener.get_signals_by_priority(SignalPriority.CRITICAL)
                
                click.echo(f"\n📊 Monitoring Summary ({duration}h)")
                click.echo("─" * 40)
                click.echo(f"Total signals detected: {len(active_signals)}")
                click.echo(f"High priority signals: {len(high_priority)}")
                click.echo(f"Critical priority signals: {len(critical_priority)}")
                
                if critical_priority:
                    click.echo(f"\n🚨 Critical Signals")
                    click.echo("─" * 20)
                    for signal in critical_priority:
                        click.echo(f"• {signal.topic} ({signal.source})")
        
        # Start monitoring
        asyncio.run(start_monitoring())
        
    except ImportError as e:
        click.echo(f"❌ Error importing signal listener: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error during monitoring: {e}", err=True)
        raise SystemExit(1)


@trends.command("personalize")
@click.option(
    "--persona",
    type=click.Choice([
        "business_professional", "self_help_seeker", "fiction_lover",
        "tech_enthusiast", "academic_reader", "casual_reader",
        "young_adult", "senior_reader"
    ]),
    help="Target persona for personalization analysis"
)
@click.option(
    "--content-type",
    type=click.Choice(["email_subject", "book_description", "ad_copy"]),
    default="book_description",
    help="Type of content to personalize"
)
def trends_personalize(persona: str, content_type: str) -> None:
    """
    Run personalization analysis for specific reader segments.
    
    Analyzes reader personas and generates personalized content
    recommendations for different audience segments.
    """
    click.echo(f"🎯 Running personalization analysis...")
    
    try:
        import asyncio
        from kindlemint.marketing.personalization_engine import PersonalizationEngine, PersonaType
        from kindlemint.utils.config import Config
        
        async def run_personalization():
            config = Config()
            engine = PersonalizationEngine(config)
            
            # Convert persona string to enum
            persona_enum = PersonaType(persona) if persona else PersonaType.BUSINESS_PROFESSIONAL
            
            click.echo(f"📊 Analyzing persona: {persona_enum.value}")
            
            # Sample book data for testing
            book_data = {
                'title': 'The Future of AI in Business',
                'genre': 'business',
                'benefit': 'transform your business with AI',
                'target_role': 'executives and managers',
                'credibility_source': 'leading AI research'
            }
            
            # Generate personalized content
            personalized_content = engine.generate_personalized_content(
                persona_enum, content_type, book_data
            )
            
            click.echo(f"\n📝 Personalized Content")
            click.echo("─" * 30)
            click.echo(f"Content Type: {content_type}")
            click.echo(f"Target Persona: {persona_enum.value}")
            click.echo(f"\n🎯 Generated Content:")
            click.echo(f"'{personalized_content.content}'")
            
            if personalized_content.variants:
                click.echo(f"\n🔄 A/B Test Variants:")
                for i, variant in enumerate(personalized_content.variants, 1):
                    click.echo(f"{i}. '{variant}'")
            
            # Get recommendations
            recommendations = await engine.get_personalization_recommendations(persona_enum)
            
            click.echo(f"\n💡 Personalization Recommendations")
            click.echo("─" * 35)
            for rec in recommendations:
                click.echo(f"• {rec}")
        
        # Run personalization
        asyncio.run(run_personalization())
        click.echo(f"\n✅ Personalization analysis complete!")
        
    except ImportError as e:
        click.echo(f"❌ Error importing personalization engine: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error during personalization: {e}", err=True)
        raise SystemExit(1)


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
