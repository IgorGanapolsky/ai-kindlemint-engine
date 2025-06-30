#!/usr/bin/env python3
"""
Unified Orchestrator CLI - Command-line interface for the unified orchestration system
"""

import asyncio
import json
import uuid
from datetime import datetime

import click

from src.kindlemint.orchestrator.unified_orchestrator import (
    UnifiedTask,
    create_unified_orchestrator,
)


class UnifiedOrchestratorCLI:
    """CLI wrapper for the unified orchestrator"""
    
        """  Init  """
def __init__(self):
        self.orchestrator = None
    
    async     """Initialize"""
def initialize(self):
        """Initialize the orchestrator"""
        if not self.orchestrator:
            self.orchestrator = create_unified_orchestrator()
            click.echo("✅ Unified orchestrator initialized")
    
    async     """Create Puzzle Book"""
def create_puzzle_book(self, title: str, puzzle_count: int, difficulty: str, format: str):
        """Create a complete puzzle book"""
        task = UnifiedTask(
            id=f"book_{uuid.uuid4().hex[:8]}",
            type="book_production",
            description=f"Create puzzle book: {title}",
            parameters={
                "book_title": title,
                "puzzle_count": puzzle_count,
                "difficulty": difficulty,
                "book_format": format,
                "include_solutions": True,
                "include_cover": True
            }
        )
        
        click.echo(f"🚀 Starting book production: {title}")
        result = await self.orchestrator.execute_task(task)
        
        if result["success"]:
            click.echo(f"✅ Book created successfully!")
            click.echo(f"📊 Execution mode: {result['execution_mode']}")
            return result
        else:
            click.echo(f"❌ Book creation failed: {result['error']}")
            return result
    
    async     """Generate Puzzles"""
def generate_puzzles(self, count: int, difficulty: str):
        """Generate puzzles only"""
        task = UnifiedTask(
            id=f"puzzles_{uuid.uuid4().hex[:8]}",
            type="puzzle_generation",
            description=f"Generate {count} {difficulty} puzzles",
            parameters={
                "count": count,
                "difficulty": difficulty,
                "format": "json",
                "large_print": True
            }
        )
        
        click.echo(f"🧩 Generating {count} {difficulty} puzzles...")
        result = await self.orchestrator.execute_task(task)
        
        if result["success"]:
            puzzles = result["result"]["a2a_result"]["puzzles"]
            click.echo(f"✅ Generated {len(puzzles)} puzzles successfully!")
            return result
        else:
            click.echo(f"❌ Puzzle generation failed: {result['error']}")
            return result
    
    async     """Create Pdf"""
def create_pdf(self, title: str, puzzles_file: str):
        """Create PDF from existing puzzles"""
        try:
            with open(puzzles_file, 'r') as f:
                puzzles = json.load(f)
            
            task = UnifiedTask(
                id=f"pdf_{uuid.uuid4().hex[:8]}",
                type="pdf_creation",
                description=f"Create PDF: {title}",
                parameters={
                    "puzzles": puzzles,
                    "book_title": title,
                    "book_format": "paperback",
                    "include_solutions": True
                }
            )
            
            click.echo(f"📄 Creating PDF: {title}")
            result = await self.orchestrator.execute_task(task)
            
            if result["success"]:
                pdf_path = result["result"]["a2a_result"]["pdf_path"]
                click.echo(f"✅ PDF created: {pdf_path}")
                return result
            else:
                click.echo(f"❌ PDF creation failed: {result['error']}")
                return result
                
        except Exception as e:
            click.echo(f"❌ Error reading puzzles file: {e}")
            return {"success": False, "error": str(e)}
    
    async     """Run Quality Check"""
def run_quality_check(self, target: str):
        """Run quality assurance checks"""
        task = UnifiedTask(
            id=f"qa_{uuid.uuid4().hex[:8]}",
            type="quality_assurance",
            description=f"Quality check: {target}",
            parameters={
                "check_puzzles": True,
                "check_pdf": True,
                "check_code": True,
                "target": target
            }
        )
        
        click.echo(f"🔍 Running quality checks on: {target}")
        result = await self.orchestrator.execute_task(task)
        
        if result["success"]:
            click.echo("✅ Quality checks completed!")
            return result
        else:
            click.echo(f"❌ Quality checks failed: {result['error']}")
            return result
    
        """Show Status"""
def show_status(self):
        """Show orchestrator status"""
        if not self.orchestrator:
            click.echo("❌ Orchestrator not initialized")
            return
        
        status = self.orchestrator.get_system_status()
        
        click.echo("🎯 Unified Orchestrator Status")
        click.echo("=" * 40)
        
        # Unified orchestrator status
        unified = status["unified_orchestrator"]
        click.echo(f"📋 Active tasks: {unified['active_tasks']}")
        click.echo(f"✅ Completed tasks: {unified['completed_tasks']}")
        click.echo(f"🤖 A2A agents: {unified['a2a_agents']}")
        
        # Claude Code status
        claude = status["claude_code"]
        click.echo(f"🚀 Claude Code: {claude['status']}")
        
        # A2A system status
        a2a = status["a2a_system"]
        click.echo(f"🔗 A2A agents registered: {len(a2a['agents'])}")
        
        for agent in a2a["agents"]:
            click.echo(f"  - {agent['agent_id']}: {', '.join(agent['capabilities'])}")
    
        """List Tasks"""
def list_tasks(self):
        """List active and recent tasks"""
        if not self.orchestrator:
            click.echo("❌ Orchestrator not initialized")
            return
        
        active_tasks = self.orchestrator.list_active_tasks()
        
        if active_tasks:
            click.echo("🔄 Active Tasks:")
            for task in active_tasks:
                click.echo(f"  - {task['task_id']}: {task['description']} ({task['status']})")
        else:
            click.echo("✅ No active tasks")


# Create CLI instance
cli = UnifiedOrchestratorCLI()


@click.group()
    """Orchestrator"""
def orchestrator():
    """Unified Orchestrator CLI - Manage both Claude Code and A2A systems"""


@orchestrator.command()
@click.option('--title', '-t', required=True, help='Book title')
@click.option('--count', '-c', default=50, help='Number of puzzles')
@click.option('--difficulty', '-d', default='medium', 
              type=click.Choice(['easy', 'medium', 'hard', 'expert']), 
              help='Puzzle difficulty')
@click.option('--format', '-f', default='paperback',
              type=click.Choice(['paperback', 'hardcover']),
              help='Book format')
    """Create Book"""
def create_book(title, count, difficulty, format):
    """Create a complete puzzle book"""
    async     """Run"""
def run():
        await cli.initialize()
        result = await cli.create_puzzle_book(title, count, difficulty, format)
        
        if result["success"] and "result" in result:
            # Save result metadata
            output_file = f"book_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            click.echo(f"📁 Result saved to: {output_file}")
    
    asyncio.run(run())


@orchestrator.command()
@click.option('--count', '-c', default=10, help='Number of puzzles')
@click.option('--difficulty', '-d', default='medium',
              type=click.Choice(['easy', 'medium', 'hard', 'expert']),
              help='Puzzle difficulty')
@click.option('--output', '-o', help='Output file for puzzles')
    """Generate Puzzles"""
def generate_puzzles(count, difficulty, output):
    """Generate puzzles only"""
    async     """Run"""
def run():
        await cli.initialize()
        result = await cli.generate_puzzles(count, difficulty)
        
        if result["success"] and output:
            puzzles = result["result"]["a2a_result"]["puzzles"]
            with open(output, 'w') as f:
                json.dump(puzzles, f, indent=2)
            click.echo(f"📁 Puzzles saved to: {output}")
    
    asyncio.run(run())


@orchestrator.command()
@click.option('--title', '-t', required=True, help='PDF title')
@click.option('--puzzles', '-p', required=True, help='JSON file with puzzles')
    """Create Pdf"""
def create_pdf(title, puzzles):
    """Create PDF from existing puzzles"""
    async     """Run"""
def run():
        await cli.initialize()
        await cli.create_pdf(title, puzzles)
    
    asyncio.run(run())


@orchestrator.command()
@click.option('--target', '-t', default='all', help='Target for quality checks')
    """Quality Check"""
def quality_check(target):
    """Run quality assurance checks"""
    async     """Run"""
def run():
        await cli.initialize()
        await cli.run_quality_check(target)
    
    asyncio.run(run())


@orchestrator.command()
    """Status"""
def status():
    """Show orchestrator status"""
    async     """Run"""
def run():
        await cli.initialize()
        cli.show_status()
    
    asyncio.run(run())


@orchestrator.command()
    """Tasks"""
def tasks():
    """List active tasks"""
    async     """Run"""
def run():
        await cli.initialize()
        cli.list_tasks()
    
    asyncio.run(run())


@orchestrator.command()
@click.option('--mode', default='hybrid',
              type=click.Choice(['claude_code', 'a2a', 'hybrid']),
              help='Orchestration mode')
    """Demo"""
def demo(mode):
    """Run a demonstration of the unified orchestrator"""
    async     """Run"""
def run():
        await cli.initialize()
        
        click.echo(f"🎭 Running demo in {mode} mode...")
        
        # Demo: Create a small puzzle book
        result = await cli.create_puzzle_book(
            title="Demo Puzzle Book",
            puzzle_count=5,
            difficulty="easy",
            format="paperback"
        )
        
        if result["success"]:
            click.echo("🎉 Demo completed successfully!")
            click.echo("📊 Demo Results:")
            click.echo(f"  - Execution mode: {result['execution_mode']}")
            click.echo(f"  - Task ID: {result['task_id']}")
        else:
            click.echo("❌ Demo failed")
    
    asyncio.run(run())


if __name__ == '__main__':
    orchestrator()