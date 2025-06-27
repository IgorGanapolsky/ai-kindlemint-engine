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
from scripts.daily_tasks import run_daily_tasks

# Import vibecode CLI
try:
    from src.kindlemint.cli.vibecode_cli import cli as vibecode_cli
    VIBECODE_AVAILABLE = True
except ImportError:
    VIBECODE_AVAILABLE = False

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
    click.echo("")
    click.echo("Use 'kindlemint publish --metadata <file>' to upload to KDP")

@cli.command("daily-tasks")
def daily_tasks():  # noqa: D103
    """
    Run the daily AI publishing task scheduler.
    """
    run_daily_tasks()


# Add vibecode commands if available
if VIBECODE_AVAILABLE:
    @cli.command("vibecode")
    @click.option('--user-id', default='cli_user', help='User ID for the session')
    @click.option('--debug', is_flag=True, help='Enable debug logging')
    def vibecode_session(user_id: str, debug: bool):
        """Start an interactive vibecode session for conversational book creation"""
        from src.kindlemint.cli.vibecode_cli import VibecodeCliSession
        import asyncio
        from rich.console import Console
        import logging
        
        console = Console()
        
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        async def run_session():
            session = VibecodeCliSession()
            session.user_id = user_id
            
            try:
                await session.initialize()
                
                if await session.start_session():
                    await session.run_conversation_loop()
                else:
                    console.print("[red]Failed to start session[/red]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted by user[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
            finally:
                if session.vibecode_agent:
                    await session.vibecode_agent.stop()
        
        try:
            asyncio.run(run_session())
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
    
    @cli.command("vibecode-demo")
    def vibecode_demo():
        """Show a demo of the vibecode conversational interface"""
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        demo_text = """
[bold blue]🎤 KindleMint Vibecode - Conversational Book Creation[/bold blue]

Transform your ideas into books through natural conversation with AI.

[green]Example:[/green]
[cyan]You:[/cyan] "I want to write a mystery novel"
[magenta]AI:[/magenta] "Exciting! Tell me about the setting and main character..."

[yellow]Features:[/yellow]
• 🎤 Voice-first interaction
• 🧠 Context-aware AI that learns your style  
• ✨ Real-time content generation
• 🔄 Conversational refinement
• 📚 Multi-format export

[bold green]Try it now:[/bold green]
kindlemint vibecode
        """
        
        demo_panel = Panel(
            demo_text,
            title="[bold cyan]📖 Vibecode Demo[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(demo_panel)

    @cli.command("vibecode-info")
    def vibecode_info():
        """Show detailed information about the vibecode system"""
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        info_text = """
[bold blue]KindleMint Vibecode System[/bold blue]

Revolutionary conversational interface for book creation that replaces
traditional forms with natural AI conversation.

[green]Core Capabilities:[/green]
• **Voice Processing**: Advanced speech-to-text with emotion detection
• **Context Synthesis**: Multi-layer context engine (author, market, creative, publishing)
• **Agent Orchestration**: Specialized AI agents working together
• **Real-time Generation**: Content appears as you speak/type
• **Style Adaptation**: AI learns and matches your writing style

[yellow]Technical Innovation:[/yellow]
• Context-aware conversation management
• Vibe interpretation and mood translation
• Multi-agent coordination for complex tasks
• Real-time feedback processing and adaptation

[cyan]Integration:[/cyan]
• REST API for frontend applications
• WebSocket support for real-time communication
• CLI interface for testing and development
• Compatible with existing KindleMint publishing pipeline

[magenta]Commands:[/magenta]
• [bold]kindlemint vibecode[/bold] - Start interactive session
• [bold]kindlemint vibecode-demo[/bold] - See demo and examples
• [bold]kindlemint vibecode-info[/bold] - This information
        """
        
        info_panel = Panel(
            info_text,
            title="[bold magenta]ℹ️  Vibecode System Information[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        )
        console.print(info_panel)


# Update help text to include vibecode
@cli.command("about")
def about():
    """Show information about KindleMint Engine"""
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    features = [
        "📚 Traditional formatters (crossword, epub, layout)",
        "🤖 Daily AI publishing automation",
        "📊 Market research and optimization"
    ]
    
    if VIBECODE_AVAILABLE:
        features.insert(0, "🎤 Vibecode conversational book creation")
    
    about_text = f"""
[bold blue]KindleMint Engine[/bold blue]
AI-powered book creation and publishing automation

[green]Features:[/green]
{chr(10).join(f"• {feature}" for feature in features)}

[yellow]Getting Started:[/yellow]
• [bold]kindlemint list[/bold] - See available formatters
• [bold]kindlemint generate[/bold] - Create books with traditional formatters
• [bold]kindlemint daily-tasks[/bold] - Run automation tasks
{"• [bold]kindlemint vibecode[/bold] - Try conversational creation" if VIBECODE_AVAILABLE else ""}

[cyan]Documentation:[/cyan]
See docs/ directory for detailed guides and examples
    """
    
    about_panel = Panel(
        about_text,
        title="[bold cyan]📖 About KindleMint[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(about_panel)


if __name__ == "__main__":
    cli()
