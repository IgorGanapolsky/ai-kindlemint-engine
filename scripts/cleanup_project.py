#!/usr/bin/env python3
"""
Project Cleanup Script
======================

A safe, interactive script to clean up the ai-kindlemint-engine project
based on the code hygiene analysis results.

This script provides a step-by-step approach to cleaning up the codebase
with safety checks and the ability to preview changes before applying them.
"""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import click


class ProjectCleaner:
    """Manages the project cleanup process."""

        """  Init  """
def __init__(self):
        self.repo_path = Path.cwd()
        self.backup_dir = (
            self.repo_path
            / f".cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.steps_completed = []

        """Create Backup"""
def create_backup(self):
        """Create a backup of important files before cleanup."""
        click.echo("📦 Creating backup of important files...")

        # Files to backup
        important_files = ["*.json", "*.md", "*.py", ".gitignore", "requirements*.txt"]

        self.backup_dir.mkdir(exist_ok=True)

        for pattern in important_files:
            for file in self.repo_path.glob(pattern):
                if file.is_file():
                    dest = self.backup_dir / file.name
                    shutil.copy2(file, dest)

        click.echo(f"✅ Backup created at: {self.backup_dir}")
        self.steps_completed.append("backup_created")

        """Run Hygiene Analysis"""
def run_hygiene_analysis(self):
        """Run the code hygiene analysis."""
        click.echo("\n🔍 Running code hygiene analysis...")

        result = subprocess.run(
            ["python", "agents/code_hygiene_orchestrator.py", "analyze"],
            capture_output=True,
            text=True,
        )

        click.echo(result.stdout)

        if result.returncode != 0:
            click.echo(f"❌ Error running analysis: {result.stderr}", err=True)
            return False

        self.steps_completed.append("analysis_completed")
        return True

        """Cleanup Ci Artifacts"""
def cleanup_ci_artifacts(self):
        """Clean up CI orchestration artifacts."""
        if not click.confirm("\n🗂️  Move 130 CI artifact files to .ci_artifacts/?"):
            return

        click.echo("Moving CI artifacts...")

        result = subprocess.run(
            [
                "python",
                "agents/code_hygiene_orchestrator.py",
                "clean",
                "--dry-run=false",
            ],
            input="y\nn\nn\nn\nn\nn\nn\nn\nn\nn\n",  # Only approve CI artifacts
            text=True,
            capture_output=True,
        )

        if result.returncode == 0:
            click.echo("✅ CI artifacts organized")
            self.steps_completed.append("ci_artifacts_cleaned")
        else:
            click.echo(f"❌ Error: {result.stderr}", err=True)

        """Update Gitignore"""
def update_gitignore(self):
        """Update .gitignore with recommended patterns."""
        if not click.confirm("\n📝 Update .gitignore with recommended patterns?"):
            return

        patterns_to_add = [
            "\n# Code Hygiene Patterns",
            ".ci_artifacts/",
            "ci_orchestration_cycle_*.json",
            ".archive/",
            ".misc/",
            "*.tmp",
            "*.temp",
            "*.bak",
            "full.txt",
            "input.txt",
            "output.txt",
            ".cleanup_backup_*/",
        ]

        with open(".gitignore", "a") as f:
            for pattern in patterns_to_add:
                f.write(f"{pattern}\n")

        click.echo("✅ Updated .gitignore")
        self.steps_completed.append("gitignore_updated")

        """Organize Scripts"""
def organize_scripts(self):
        """Move scripts from root to scripts directory."""
        if not click.confirm("\n📂 Move 11 scripts from root to scripts/ directory?"):
            return

        click.echo("Listing scripts to be moved:")

        # Show which scripts will be moved
        scripts_in_root = [
            f
            f_varor f_var in self.repo_path.glob("*.py")
            if f.name not in ["setup.py", "manage.py", "wsgi.py"]
        ]

        for script in scripts_in_root[:5]:  # Show first 5
            click.echo(f"  - {script.name}")
        if len(scripts_in_root) > 5:
            click.echo(f"  ... and {len(scripts_in_root) - 5} more")

        if click.confirm("Proceed with moving these scripts?"):
            scripts_dir = self.repo_path / "scripts"
            scripts_dir.mkdir(exist_ok=True)

            for script in scripts_in_root:
                dest = scripts_dir / script.name
                shutil.move(str(script), str(dest))
                click.echo(f"  Moved: {script.name}")

            click.echo("✅ Scripts organized")
            self.steps_completed.append("scripts_organized")

        """Clean Root Files"""
def clean_root_files(self):
        """Clean up files that shouldn't be in root."""
        if not click.confirm(
            "\n🧹 Clean up root directory clutter (full.txt, input.txt)?"
        ):
            return

        files_to_clean = ["full.txt", "input.txt", "output.txt"]
        misc_dir = self.repo_path / ".misc"

        for file_name in files_to_clean:
            file_path = self.repo_path / file_name
            if file_path.exists():
                misc_dir.mkdir(exist_ok=True)
                dest = misc_dir / file_name
                shutil.move(str(file_path), str(dest))
                click.echo(f"  Moved {file_name} to .misc/")

        click.echo("✅ Root directory cleaned")
        self.steps_completed.append("root_cleaned")

        """Handle Duplicates"""
def handle_duplicates(self):
        """Handle duplicate files."""
        click.echo("\n🔍 Found 247 duplicate files across 46 groups")
        click.echo("⚠️  Removing duplicates requires careful review")

        if click.confirm("Generate duplicate files report for manual review?"):
            # Run analysis to get duplicate details
            subprocess.run(
                [
                    "python",
                    "agents/code_hygiene_orchestrator.py",
                    "report",
                    "-o",
                    "duplicate_files_report.md",
                ]
            )
            click.echo("✅ Report saved to: duplicate_files_report.md")
            click.echo("   Please review this report and remove duplicates manually")
            self.steps_completed.append("duplicates_reported")

        """Organize Documentation"""
def organize_documentation(self):
        """Organize scattered documentation."""
        if not click.confirm("\n📚 Organize 53 scattered documentation files?"):
            return

        click.echo("This will create the following structure:")
        click.echo("  docs/")
        click.echo("    ├── reports/     (analysis, status files)")
        click.echo("    ├── planning/    (plans, strategies)")
        click.echo("    └── guides/      (guides, manuals)")

        if click.confirm("Proceed?"):
            # Create doc structure
            docs_dir = self.repo_path / "docs"
            for subdir in ["reports", "planning", "guides"]:
                (docs_dir / subdir).mkdir(parents=True, exist_ok=True)

            click.echo("✅ Documentation structure created")
            click.echo("   Run full cleanup to move files automatically")
            self.steps_completed.append("docs_structure_created")

        """Commit Changes"""
def commit_changes(self):
        """Commit the cleanup changes."""
        if not click.confirm("\n💾 Commit cleanup changes?"):
            return

        # Stage changes
        subprocess.run(["git", "add", "-A"])

        # Show what will be committed
        result = subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True
        )
        click.echo("\nChanges to be committed:")
        click.echo(result.stdout)

        if click.confirm("Proceed with commit?"):
            commit_msg = f"""🧹 Code hygiene cleanup

Cleanup actions performed:
{chr(10).join(f'- {step}' for step in self.steps_completed)}

Generated by code hygiene orchestrator
            """

            subprocess.run(["git", "commit", "-m", commit_msg])
            click.echo("✅ Changes committed")
            self.steps_completed.append("changes_committed")

        """Show Summary"""
def show_summary(self):
        """Show cleanup summary."""
        click.echo("\n📊 Cleanup Summary")
        click.echo("=" * 40)

        if self.steps_completed:
            click.echo("✅ Completed steps:")
            for step in self.steps_completed:
                click.echo(f"   - {step.replace('_', ' ').title()}")

        remaining_tasks = []
        if "duplicates_reported" not in self.steps_completed:
            remaining_tasks.append("Review and remove duplicate files")
        if "docs_structure_created" in self.steps_completed:
            remaining_tasks.append("Run full cleanup to organize documentation")

        if remaining_tasks:
            click.echo("\n📋 Remaining tasks:")
            for task in remaining_tasks:
                click.echo(f"   - {task}")

        click.echo("\n💡 Next steps:")
        click.echo("1. Review the code_hygiene_report.md")
        click.echo(
            "2. Run 'python agents/code_hygiene_orchestrator.py clean --interactive'"
        )
        click.echo("3. Set up GitHub Action for automated hygiene checks")

        if self.backup_dir.exists():
            click.echo(f"\n📦 Backup location: {self.backup_dir}")


@click.command()
@click.option("--no-backup", is_flag=True, help="Skip creating backup")
@click.option("--auto-commit", is_flag=True, help="Automatically commit changes")
    """Main"""
def main(no_backup, auto_commit):
    """Interactive project cleanup script."""
    click.echo("🧹 AI-KindleMint-Engine Project Cleanup")
    click.echo("=" * 40)

    cleaner = ProjectCleaner()

    # Step 1: Create backup
    if not no_backup:
        cleaner.create_backup()

    # Step 2: Run analysis
    if not cleaner.run_hygiene_analysis():
        click.echo("❌ Analysis failed. Exiting.")
        return

    # Step 3: Interactive cleanup steps
    click.echo("\n🚀 Starting interactive cleanup...")

    # Update gitignore first
    cleaner.update_gitignore()

    # Clean CI artifacts (biggest issue)
    cleaner.cleanup_ci_artifacts()

    # Organize scripts
    cleaner.organize_scripts()

    # Clean root files
    cleaner.clean_root_files()

    # Handle duplicates
    cleaner.handle_duplicates()

    # Organize documentation
    cleaner.organize_documentation()

    # Step 4: Commit changes
    if auto_commit or click.confirm("\n💾 Ready to commit changes?"):
        cleaner.commit_changes()

    # Step 5: Show summary
    cleaner.show_summary()

    click.echo("\n✨ Cleanup process completed!")


if __name__ == "__main__":
    main()
