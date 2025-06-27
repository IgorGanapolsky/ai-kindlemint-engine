"""
Vibecode CLI Interface for KindleMint

Command-line interface for testing and demonstrating the vibecoding system.
Allows users to interact with the conversational book creation system via text input.
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from ..agents.vibecode_agent import VibecodeAgent
from ..agents.task_system import Task
from ..context.voice_processing import VoiceInputProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for beautiful output
console = Console()

class VibecodeCliSession:
    """Manages a CLI vibecode session"""
    
    def __init__(self):
        self.vibecode_agent = None
        self.voice_processor = VoiceInputProcessor()
        self.session_id = None
        self.user_id = "cli_user"
        self.session_active = False
        
    async def initialize(self):
        """Initialize the vibecode agent"""
        console.print("[bold blue]Initializing KindleMint Vibecode System...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Starting AI agents...", total=None)
            
            try:
                self.vibecode_agent = VibecodeAgent()
                await self.vibecode_agent.start()
                progress.update(task, description="✅ Vibecode system ready!")
                await asyncio.sleep(0.5)  # Brief pause for effect
                
            except Exception as e:
                progress.update(task, description="❌ Failed to initialize")
                console.print(f"[red]Error: {e}[/red]")
                raise
    
    async def start_session(self):
        """Start a new vibecode session"""
        console.print("\n" + "="*60)
        console.print("[bold cyan]🎤 KindleMint Vibecode - Conversational Book Creation[/bold cyan]")
        console.print("="*60)
        
        # Create new session
        task = Task(
            task_type="START_VIBECODE_SESSION",
            name="Start CLI Session",
            input_data={"user_id": self.user_id}
        )
        
        success = await self.vibecode_agent.assign_task(task)
        if not success:
            console.print("[red]Failed to start session[/red]")
            return False
        
        # Wait for completion
        await self._wait_for_task_completion(task, "Starting your creative session...")
        
        if task.result and task.result.success:
            self.session_id = task.result.output_data["session_id"]
            greeting = task.result.output_data["greeting"]
            
            # Display greeting in a beautiful panel
            greeting_panel = Panel(
                Text(greeting, style="bold green"),
                title="[bold blue]AI Writing Assistant[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            )
            console.print(greeting_panel)
            
            self.session_active = True
            console.print("\n[dim]💡 Tip: Type 'help' for commands, 'quit' to exit[/dim]\n")
            return True
        else:
            console.print("[red]Failed to create session[/red]")
            return False
    
    async def run_conversation_loop(self):
        """Run the main conversation loop"""
        while self.session_active:
            try:
                # Get user input
                user_input = Prompt.ask(
                    "\n[bold cyan]You[/bold cyan]",
                    default="",
                    show_default=False
                )
                
                if not user_input.strip():
                    continue
                    
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    await self._handle_quit()
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'status':
                    await self._show_status()
                    continue
                elif user_input.lower().startswith('export'):
                    await self._handle_export(user_input)
                    continue
                
                # Process the input as voice/text
                await self._process_user_input(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted by user[/yellow]")
                await self._handle_quit()
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.error(f"Error in conversation loop: {e}")
    
    async def _process_user_input(self, text: str):
        """Process user text input"""
        
        # Show processing indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_progress = progress.add_task("🧠 Processing your input...", total=None)
            
            try:
                # Process as voice input (using text mode)
                voice_input = await self.voice_processor.process_text_input(text, self.session_id)
                
                # Create task for processing
                task = Task(
                    task_type="PROCESS_VOICE_INPUT",
                    name="Process User Input",
                    input_data={
                        "session_id": self.session_id,
                        "audio_data": text.encode('utf-8'),
                        "audio_format": "text",
                        "text_override": text
                    }
                )
                
                progress.update(task_progress, description="🤖 AI is thinking...")
                
                # Execute task
                success = await self.vibecode_agent.assign_task(task)
                if not success:
                    progress.update(task_progress, description="❌ Failed to process")
                    console.print("[red]Failed to process input[/red]")
                    return
                
                # Wait for completion
                await self._wait_for_task_completion(task, None, progress, task_progress)
                
                if task.result and task.result.success:
                    await self._display_ai_response(task.result.output_data)
                else:
                    console.print("[red]Failed to generate response[/red]")
                    
            except Exception as e:
                progress.update(task_progress, description="❌ Error occurred")
                console.print(f"[red]Error processing input: {e}[/red]")
    
    async def _display_ai_response(self, output_data: dict):
        """Display AI response in a beautiful format"""
        
        response_data = output_data.get("response", {})
        text_response = response_data.get("text_response", "I'm sorry, I didn't understand that.")
        suggestions = response_data.get("suggestions", [])
        generated_content = response_data.get("generated_content")
        next_steps = response_data.get("next_steps", [])
        
        # Main response
        response_panel = Panel(
            Text(text_response, style="green"),
            title="[bold magenta]AI Assistant[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        )
        console.print(response_panel)
        
        # Show generated content if available
        if generated_content:
            content_text = generated_content.get("generated_content", "")
            if content_text:
                content_panel = Panel(
                    Markdown(f"```\n{content_text}\n```"),
                    title="[bold yellow]✨ Generated Content[/bold yellow]",
                    border_style="yellow",
                    padding=(1, 2)
                )
                console.print(content_panel)
                
                # Show content stats
                word_count = generated_content.get("word_count", 0)
                content_type = generated_content.get("content_type", "content")
                console.print(f"[dim]📝 {word_count} words • {content_type}[/dim]")
        
        # Show suggestions
        if suggestions:
            console.print("\n[bold blue]💡 Suggestions:[/bold blue]")
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"  [cyan]{i}.[/cyan] {suggestion}")
        
        # Show next steps
        if next_steps:
            console.print("\n[bold green]➡️  Next Steps:[/bold green]")
            for step in next_steps:
                console.print(f"  • {step}")
    
    async def _wait_for_task_completion(self, task: Task, description: Optional[str] = None, 
                                      progress: Optional[Progress] = None, 
                                      task_id: Optional[any] = None):
        """Wait for task completion with progress indicator"""
        
        timeout_seconds = 30
        for _ in range(timeout_seconds * 10):  # Check every 100ms
            if task.status.value in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
            
            if progress and task_id and description:
                progress.update(task_id, description=description)
    
    def _show_help(self):
        """Show help information"""
        help_text = """
[bold blue]KindleMint Vibecode Commands:[/bold blue]

[green]Basic Commands:[/green]
• Simply type what you want to create or discuss
• "I want to write a mystery novel"
• "Create a romantic story set in Paris"
• "Help me develop my main character"

[cyan]Special Commands:[/cyan]
• [bold]help[/bold] - Show this help message
• [bold]status[/bold] - Show current session status
• [bold]export pdf[/bold] - Export your book as PDF
• [bold]export epub[/bold] - Export your book as EPUB
• [bold]quit[/bold] - End the session

[yellow]Tips:[/yellow]
• Be conversational and natural
• Describe what you want to create
• Ask for feedback and suggestions
• Request specific changes or refinements

[magenta]Examples:[/magenta]
• "I'm feeling inspired to write something mysterious"
• "Make the dialogue more natural"
• "Add more description to the opening scene"
• "What genre would work best for my idea?"
        """
        
        help_panel = Panel(
            help_text,
            title="[bold blue]📖 Help & Commands[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(help_panel)
    
    async def _show_status(self):
        """Show current session status"""
        if not self.session_id:
            console.print("[red]No active session[/red]")
            return
        
        # Get session from agent
        session = self.vibecode_agent.active_sessions.get(self.session_id)
        conversation_state = self.vibecode_agent.conversation_states.get(self.session_id)
        
        if session and conversation_state:
            status_text = f"""
[bold green]Session Status:[/bold green]

📊 **Session ID:** {self.session_id[:8]}...
⏱️  **Duration:** {session.session_duration:.1f} minutes
🔄 **Phase:** {conversation_state.current_phase}
📝 **Words:** {session.total_input_words}
💬 **Inputs:** {len(session.voice_inputs)}
🎯 **Status:** {session.session_status}
            """
            
            status_panel = Panel(
                status_text,
                title="[bold cyan]📈 Session Information[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(status_panel)
        else:
            console.print("[red]Could not retrieve session status[/red]")
    
    async def _handle_export(self, command: str):
        """Handle export commands"""
        parts = command.split()
        export_format = "pdf"  # default
        
        if len(parts) > 1:
            export_format = parts[1].lower()
        
        if export_format not in ["pdf", "epub", "docx", "txt"]:
            console.print("[red]Unsupported format. Use: pdf, epub, docx, or txt[/red]")
            return
        
        console.print(f"[blue]Exporting your book as {export_format.upper()}...[/blue]")
        
        # Create export task
        task = Task(
            task_type="EXPORT_BOOK",
            name="Export Book",
            input_data={
                "session_id": self.session_id,
                "format": export_format
            }
        )
        
        success = await self.vibecode_agent.assign_task(task)
        if not success:
            console.print("[red]Failed to start export[/red]")
            return
        
        # Wait for completion with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            export_task = progress.add_task(f"📤 Exporting {export_format.upper()}...", total=None)
            
            await self._wait_for_task_completion(task, None, progress, export_task)
            
            if task.result and task.result.success:
                export_path = task.result.output_data.get("export_path", "unknown")
                word_count = task.result.output_data.get("word_count", 0)
                
                success_text = f"""
✅ **Export Complete!**

📁 **File:** {export_path}
📄 **Format:** {export_format.upper()}
📝 **Words:** {word_count}
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                success_panel = Panel(
                    success_text,
                    title="[bold green]📤 Export Successful[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                )
                console.print(success_panel)
            else:
                console.print("[red]Export failed[/red]")
    
    async def _handle_quit(self):
        """Handle session quit"""
        console.print("\n[yellow]Ending your vibecode session...[/yellow]")
        
        if self.session_id:
            # Get final session stats
            session = self.vibecode_agent.active_sessions.get(self.session_id)
            if session:
                farewell_text = f"""
🎉 **Great session!**

📝 You created **{session.total_input_words}** words
⏱️  Session lasted **{session.session_duration:.1f}** minutes  
💬 We had **{len(session.voice_inputs)}** interactions
✨ Your creativity brought ideas to life!

Thank you for using KindleMint Vibecode. 
Your book awaits! 📚
                """
                
                farewell_panel = Panel(
                    farewell_text,
                    title="[bold magenta]👋 Session Complete[/bold magenta]",
                    border_style="magenta",
                    padding=(1, 2)
                )
                console.print(farewell_panel)
        
        self.session_active = False
        
        # Cleanup
        if self.vibecode_agent:
            await self.vibecode_agent.stop()

@click.group()
def cli():
    """KindleMint Vibecode CLI - Conversational Book Creation"""
    pass

@cli.command()
@click.option('--user-id', default='cli_user', help='User ID for the session')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def vibecode(user_id: str, debug: bool):
    """Start an interactive vibecode session"""
    
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
            logger.error(f"Session error: {e}")
        finally:
            if session.vibecode_agent:
                await session.vibecode_agent.stop()
    
    # Run the async session
    try:
        asyncio.run(run_session())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")

@cli.command()
def demo():
    """Run a quick demo of the vibecode system"""
    
    demo_text = """
[bold blue]🎤 KindleMint Vibecode Demo[/bold blue]

Vibecode enables conversational book creation through natural language.
Instead of filling out forms, you simply talk to AI about your story ideas.

[green]Example conversation:[/green]

[cyan]You:[/cyan] "I want to write a cozy mystery set in a small bookshop"

[magenta]AI:[/magenta] "I love that idea! Bookshops make perfect settings for mysteries. 
Tell me about your amateur sleuth - are they the bookshop owner, 
a regular customer, or perhaps someone new to town?"

[cyan]You:[/cyan] "The owner, and she's really good at reading people"

[magenta]AI:[/magenta] "Perfect! Let me create an opening scene..."

[yellow]✨ Generated Content:[/yellow]
*Opening paragraph appears with atmospheric description 
of the bookshop and mysterious customer*

[bold green]Ready to try it yourself?[/bold green]
Run: [bold]kindlemint vibecode[/bold]
    """
    
    demo_panel = Panel(
        demo_text,
        title="[bold cyan]📖 Vibecode Demo[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(demo_panel)

@cli.command()
def info():
    """Show information about the vibecode system"""
    
    info_text = """
[bold blue]About KindleMint Vibecode[/bold blue]

Vibecode revolutionizes book creation by enabling natural conversation
with AI instead of traditional form-based interfaces.

[green]Key Features:[/green]
• 🎤 **Voice-first interaction** - Speak your ideas naturally
• 🧠 **Context-aware AI** - Learns your style and preferences  
• ✨ **Real-time generation** - Content appears as you create
• 🔄 **Conversational refinement** - Iterate through dialogue
• 📚 **Multi-format export** - PDF, EPUB, DOCX, TXT

[yellow]Technology:[/yellow]
• Advanced speech processing with emotion detection
• Multi-layer context synthesis (author, market, creative, publishing)
• Specialized AI agents for different aspects of creation
• Real-time feedback processing and adaptation

[cyan]Perfect for:[/cyan]
• Writers who prefer speaking to typing
• Creative brainstorming and ideation
• Rapid prototyping of story concepts
• Collaborative creation with AI assistance

[magenta]Getting Started:[/magenta]
1. Run [bold]kindlemint vibecode[/bold]
2. Start talking about your book idea
3. Let the AI guide you through creation
4. Export your finished work
    """
    
    info_panel = Panel(
        info_text,
        title="[bold magenta]ℹ️  System Information[/bold magenta]",
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(info_panel)

if __name__ == "__main__":
    cli()