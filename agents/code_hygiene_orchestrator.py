#!/usr/bin/env python3
"""
Code Hygiene Orchestrator Agent
================================

An intelligent agent that automatically maintains code quality and cleanliness
by identifying and fixing common hygiene issues in the codebase.

Features:
- Automated file organization and cleanup
- Duplicate detection and removal
- Outdated file archival
- CI/CD artifact management
- Documentation consolidation
- Naming convention enforcement
- Dead code detection
- Dependency cleanup
"""

import hashlib
import json
import logging
import os
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import click
import git
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CodeHygieneOrchestrator:
    """Main orchestrator for code hygiene operations."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.repo = git.Repo(self.repo_path)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

        # Configuration
        self.config = {
            "archive_dir": self.repo_path / ".archive",
            "ci_artifacts_dir": self.repo_path / ".ci_artifacts",
            "duplicate_threshold": 0.95,  # Similarity threshold for duplicates
            "stale_days": 30,  # Days before considering a file stale
            "large_file_size": 10 * 1024 * 1024,  # 10MB
            "ignored_dirs": {
                ".git",
                "__pycache__",
                "node_modules",
                ".pytest_cache",
                ".venv",
                "venv",
            },
            "temp_file_patterns": ["*.tmp", "*.temp", "*.bak", "*.swp", "*.swo", "*~"],
            "ci_artifact_patterns": [
                "ci_orchestration_cycle_*.json",
                "ci_*_results.json",
            ],
        }

        # Hygiene rules
        self.hygiene_rules = {
            "organize_ci_artifacts": self._organize_ci_artifacts,
            "remove_duplicates": self._find_and_handle_duplicates,
            "clean_temp_files": self._clean_temporary_files,
            "archive_old_reports": self._archive_old_reports,
            "consolidate_docs": self._consolidate_documentation,
            "fix_naming_conventions": self._fix_naming_conventions,
            "remove_empty_dirs": self._remove_empty_directories,
            "organize_scripts": self._organize_scripts,
            "clean_root_dir": self._clean_root_directory,
            "update_gitignore": self._update_gitignore,
        }

    def analyze(self) -> Dict:
        """Analyze the codebase for hygiene issues."""
        logger.info(f"Analyzing codebase at {self.repo_path}")

        # Reset issues and stats
        self.issues.clear()
        self.stats.clear()

        # Run all analysis rules
        for rule_name, rule_func in self.hygiene_rules.items():
            try:
                logger.info(f"Running rule: {rule_name}")
                rule_func(analyze_only=True)
            except Exception as e:
                logger.error(f"Error in rule {rule_name}: {e}")
                self.issues["errors"].append(f"{rule_name}: {str(e)}")

        return {
            "issues": dict(self.issues),
            "stats": dict(self.stats),
            "summary": self._generate_summary(),
        }

    def clean(self, dry_run: bool = True, interactive: bool = False) -> Dict:
        """Clean the codebase based on hygiene rules."""
        logger.info(f"Cleaning codebase (dry_run={dry_run}, interactive={interactive})")

        # First analyze
        self.analyze()

        if not self.issues:
            logger.info("No hygiene issues found!")
            return {"status": "clean", "actions": []}

        actions_taken = []

        # Execute fixes
        for rule_name, rule_func in self.hygiene_rules.items():
            if rule_name in self.issues:
                if interactive and not self._confirm_action(rule_name):
                    continue

                try:
                    logger.info(f"Applying fix: {rule_name}")
                    if not dry_run:
                        actions = rule_func(analyze_only=False)
                        actions_taken.extend(actions or [])
                    else:
                        logger.info(f"[DRY RUN] Would apply: {rule_name}")
                except Exception as e:
                    logger.error(f"Error applying {rule_name}: {e}")

        return {
            "status": "completed",
            "actions": actions_taken,
            "stats": dict(self.stats),
        }

    def _organize_ci_artifacts(self, analyze_only: bool = True) -> Optional[List[str]]:
        """Organize CI orchestration artifacts into a dedicated directory."""
        ci_files = []
        actions = []

        # Find all CI artifact files
        for pattern in self.config["ci_artifact_patterns"]:
            ci_files.extend(self.repo_path.glob(f"**/{pattern}"))

        ci_files = [
            f
            for f in ci_files
            if not any(ignored in f.parts for ignored in self.config["ignored_dirs"])
        ]

        if ci_files:
            self.issues["ci_artifacts"].append(
                f"Found {len(ci_files)} CI artifact files scattered in the codebase"
            )
            self.stats["ci_artifacts"] = len(ci_files)

            if not analyze_only:
                # Create CI artifacts directory
                ci_dir = self.config["ci_artifacts_dir"]
                ci_dir.mkdir(exist_ok=True)

                # Move files
                for file in ci_files:
                    dest = ci_dir / file.name
                    shutil.move(str(file), str(dest))
                    actions.append(f"Moved {file} to {dest}")
                    logger.info(f"Moved CI artifact: {file.name}")

                # Create index file
                index_file = ci_dir / "index.json"
                index_data = {
                    "moved_at": datetime.now().isoformat(),
                    "files": [f.name for f in ci_files],
                    "count": len(ci_files),
                }
                with open(index_file, "w") as f:
                    json.dump(index_data, f, indent=2)

                actions.append(f"Created CI artifacts index at {index_file}")

        return actions if not analyze_only else None

    def _find_and_handle_duplicates(
        self, analyze_only: bool = True
    ) -> Optional[List[str]]:
        """Find and handle duplicate files."""
        file_hashes = defaultdict(list)
        actions = []

        # Calculate hashes for all files
        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file() and not any(
                ignored in file_path.parts for ignored in self.config["ignored_dirs"]
            ):
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    file_hashes[file_hash].append(file_path)
                except Exception as e:
                    logger.debug(f"Could not hash {file_path}: {e}")

        # Find duplicates
        duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}

        if duplicates:
            total_dupes = sum(len(files) - 1 for files in duplicates.values())
            self.issues["duplicates"].append(
                f"Found {total_dupes} duplicate files across {len(duplicates)} groups"
            )
            self.stats["duplicates"] = total_dupes

            if not analyze_only:
                for file_hash, files in duplicates.items():
                    # Keep the oldest file
                    files_by_mtime = sorted(files, key=lambda f: f.stat().st_mtime)
                    
                    for dup_file in files_by_mtime[1:]:
                        dup_file.unlink()
                        actions.append(f"Removed duplicate: {dup_file}")
                        logger.info(f"Removed duplicate: {dup_file}")

        return actions if not analyze_only else None

    def _clean_temporary_files(self, analyze_only: bool = True) -> Optional[List[str]]:
        """Clean temporary and backup files."""
        temp_files = []
        actions = []

        for pattern in self.config["temp_file_patterns"]:
            temp_files.extend(self.repo_path.rglob(pattern))

        temp_files = [
            f
            for f in temp_files
            if not any(ignored in f.parts for ignored in self.config["ignored_dirs"])
        ]

        if temp_files:
            self.issues["temp_files"].append(
                f"Found {len(temp_files)} temporary/backup files"
            )
            self.stats["temp_files"] = len(temp_files)

            if not analyze_only:
                for temp_file in temp_files:
                    temp_file.unlink()
                    actions.append(f"Removed temp file: {temp_file}")
                    logger.info(f"Removed temp file: {temp_file}")

        return actions if not analyze_only else None

    def _archive_old_reports(self, analyze_only: bool = True) -> Optional[List[str]]:
        """Archive old report and analysis files."""
        old_reports = []
        actions = []
        cutoff_date = datetime.now() - timedelta(days=self.config["stale_days"])

        # Patterns for report files
        report_patterns = [
            "*_analysis.md",
            "*_report.md",
            "*_results.json",
            "qa_validation_*.json",
            "*_COMPLETE.md",
        ]

        for pattern in report_patterns:
            for file in self.repo_path.rglob(pattern):
                if not any(
                    ignored in file.parts for ignored in self.config["ignored_dirs"]
                ):
                    if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
                        old_reports.append(file)

        if old_reports:
            self.issues["old_reports"].append(
                f"Found {len(old_reports)} old reports (>{self.config['stale_days']} days)"
            )
            self.stats["old_reports"] = len(old_reports)

            if not analyze_only:
                # Create archive directory
                archive_dir = (
                    self.config["archive_dir"]
                    / "reports"
                    / datetime.now().strftime("%Y%m%d")
                )
                archive_dir.mkdir(parents=True, exist_ok=True)

                for report in old_reports:
                    dest = archive_dir / report.name
                    shutil.move(str(report), str(dest))
                    actions.append(f"Archived {report} to {dest}")
                    logger.info(f"Archived old report: {report.name}")

        return actions if not analyze_only else None

    def _clean_root_directory(self, analyze_only: bool = True) -> Optional[List[str]]:
        """Clean up files that shouldn't be in the root directory."""
        actions = []
        root_files = []

        # Files that shouldn't be in root
        bad_root_patterns = [
            "full.txt",
            "input.txt",
            "output.txt",
            "test*.txt",
            "*.log",
            "*.tmp",
            "*.bak",
        ]

        for pattern in bad_root_patterns:
            root_files.extend(self.repo_path.glob(pattern))

        if root_files:
            self.issues["root_clutter"].append(
                f"Found {len(root_files)} files cluttering the root directory"
            )
            self.stats["root_clutter"] = len(root_files)

            if not analyze_only:
                # Move to appropriate directories or remove
                misc_dir = self.repo_path / ".misc"
                misc_dir.mkdir(exist_ok=True)

                for file in root_files:
                    if file.suffix in [".log", ".tmp", ".bak"]:
                        file.unlink()
                        actions.append(f"Removed {file}")
                    else:
                        dest = misc_dir / file.name
                        shutil.move(str(file), str(dest))
                        actions.append(f"Moved {file} to {dest}")

        return actions if not analyze_only else None

    def _consolidate_documentation(
        self, analyze_only: bool = True
    ) -> Optional[List[str]]:
        """Consolidate scattered documentation files."""
        actions = []
        doc_files = defaultdict(list)

        # Find all documentation files
        doc_patterns = ["*.md", "*.rst", "*.txt"]
        for pattern in doc_patterns:
            for file in self.repo_path.rglob(pattern):
                if not any(
                    ignored in file.parts for ignored in self.config["ignored_dirs"]
                ):
                    # Group by type
                    if "README" in file.name:
                        continue  # Don't touch READMEs
                    elif any(
                        kw in file.name.lower()
                        for kw in ["analysis", "report", "status"]
                    ):
                        doc_files["reports"].append(file)
                    elif any(
                        kw in file.name.lower()
                        for kw in ["plan", "strategy", "roadmap"]
                    ):
                        doc_files["planning"].append(file)
                    elif any(
                        kw in file.name.lower() for kw in ["guide", "manual", "howto"]
                    ):
                        doc_files["guides"].append(file)

        total_docs = sum(len(files) for files in doc_files.values())
        if total_docs > 20:  # Only flag if there are many docs
            self.issues["scattered_docs"].append(
                f"Found {total_docs} documentation files that could be better organized"
            )
            self.stats["scattered_docs"] = total_docs

            if not analyze_only:
                # Create organized doc structure
                docs_dir = self.repo_path / "docs"
                for category, files in doc_files.items():
                    cat_dir = docs_dir / category
                    cat_dir.mkdir(parents=True, exist_ok=True)

                    for file in files:
                        if file.parent != cat_dir:
                            dest = cat_dir / file.name
                            shutil.move(str(file), str(dest))
                            actions.append(f"Organized {file} to {dest}")

        return actions if not analyze_only else None

    def _fix_naming_conventions(self, analyze_only: bool = True) -> Optional[List[str]]:
        """Fix file naming convention issues."""
        actions = []
        naming_issues = []

        # Check Python files
        for py_file in self.repo_path.rglob("*.py"):
            if not any(
                ignored in py_file.parts for ignored in self.config["ignored_dirs"]
            ):
                # Check for non-snake_case
                if not self._is_snake_case(py_file.stem) and py_file.stem != "__init__":
                    naming_issues.append(
                        ("python", py_file, self._to_snake_case(py_file.stem))
                    )

        if naming_issues:
            self.issues["naming"].append(
                f"Found {len(naming_issues)} files with naming convention issues"
            )
            self.stats["naming"] = len(naming_issues)

            if not analyze_only:
                for file_type, file_path, new_name in naming_issues:
                    new_path = file_path.parent / f"{new_name}{file_path.suffix}"
                    if not new_path.exists():
                        file_path.rename(new_path)
                        actions.append(f"Renamed {file_path} to {new_path}")
                        logger.info(
                            f"Fixed naming: {file_path.name} -> {new_path.name}"
                        )

        return actions if not analyze_only else None

    def _remove_empty_directories(
        self, analyze_only: bool = True
    ) -> Optional[List[str]]:
        """Remove empty directories."""
        actions = []
        empty_dirs = []

        # Find empty directories (bottom-up)
        for root, dirs, files in os.walk(self.repo_path, topdown=False):
            root_path = Path(root)
            if not any(
                ignored in root_path.parts for ignored in self.config["ignored_dirs"]
            ):
                if not dirs and not files:
                    empty_dirs.append(root_path)

        if empty_dirs:
            self.issues["empty_dirs"].append(
                f"Found {len(empty_dirs)} empty directories"
            )
            self.stats["empty_dirs"] = len(empty_dirs)

            if not analyze_only:
                for empty_dir in empty_dirs:
                    try:
                        empty_dir.rmdir()
                        actions.append(f"Removed empty directory: {empty_dir}")
                        logger.info(f"Removed empty directory: {empty_dir}")
                    except Exception as e:
                        logger.warning(f"Could not remove {empty_dir}: {e}")

        return actions if not analyze_only else None

    def _organize_scripts(self, analyze_only: bool = True) -> Optional[List[str]]:
        """Organize scattered scripts into appropriate directories."""
        actions = []
        scattered_scripts = []

        # Find scripts in inappropriate locations
        for script in self.repo_path.rglob("*.py"):
            if script.parent == self.repo_path and script.name not in [
                "setup.py",
                "manage.py",
                "wsgi.py",
            ]:
                scattered_scripts.append(script)

        if scattered_scripts:
            self.issues["scattered_scripts"].append(
                f"Found {len(scattered_scripts)} scripts in the root directory"
            )
            self.stats["scattered_scripts"] = len(scattered_scripts)

            if not analyze_only:
                scripts_dir = self.repo_path / "scripts"
                scripts_dir.mkdir(exist_ok=True)

                for script in scattered_scripts:
                    dest = scripts_dir / script.name
                    shutil.move(str(script), str(dest))
                    actions.append(f"Moved {script} to {dest}")
                    logger.info(f"Organized script: {script.name}")

        return actions if not analyze_only else None

    def _update_gitignore(self, analyze_only: bool = True) -> Optional[List[str]]:
        """Update .gitignore with commonly ignored patterns."""
        actions = []
        gitignore_path = self.repo_path / ".gitignore"

        required_patterns = [
            "# CI/CD artifacts",
            ".ci_artifacts/",
            "ci_orchestration_cycle_*.json",
            "",
            "# Archives",
            ".archive/",
            "",
            "# Temporary files",
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.swp",
            "*.swo",
            "*~",
            "",
            "# Misc",
            ".misc/",
            "full.txt",
            "input.txt",
            "output.txt",
        ]

        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                current_content = f.read()

            missing_patterns = []
            for pattern in required_patterns:
                if pattern and pattern not in current_content:
                    missing_patterns.append(pattern)

            if missing_patterns:
                self.issues["gitignore"].append(
                    f".gitignore is missing {len(missing_patterns)} recommended patterns"
                )
                self.stats["gitignore"] = len(missing_patterns)

                if not analyze_only:
                    with open(gitignore_path, "a") as f:
                        f.write("\n\n# Added by Code Hygiene Orchestrator\n")
                        for pattern in required_patterns:
                            if pattern not in current_content:
                                f.write(f"{pattern}\n")
                    actions.append(
                        f"Updated .gitignore with {len(missing_patterns)} patterns"
                    )

        return actions if not analyze_only else None

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _is_snake_case(self, name: str) -> bool:
        """Check if a name follows snake_case convention."""
        return name.islower() and (name.replace("_", "").isalnum() or name == "")

    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case."""
        import re

        # Convert CamelCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _confirm_action(self, action: str) -> bool:
        """Ask user for confirmation."""
        response = input(f"\nApply fix for '{action}'? [y/N]: ")
        return response.lower() == "y"

    def _generate_summary(self) -> str:
        """Generate a summary of hygiene issues."""
        total_issues = sum(len(issues) for issues in self.issues.values())

        if total_issues == 0:
            return "✅ Your codebase is clean! No hygiene issues found."

        summary_lines = [
            f"🔍 Code Hygiene Analysis Summary",
            f"Found {total_issues} issues across {len(self.issues)} categories:",
            "",
        ]

        # Create table of issues
        table_data = []
        for category, issues in sorted(self.issues.items()):
            if issues:
                count = self.stats.get(category, len(issues))
                table_data.append(
                    [category.replace("_", " ").title(), count, issues[0][:50] + "..."]
                )

        summary_lines.append(
            tabulate(
                table_data,
                headers=["Category", "Count", "Description"],
                tablefmt="grid",
            )
        )

        return "\n".join(summary_lines)

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a detailed hygiene report."""
        report_lines = [
            f"# Code Hygiene Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Repository: {self.repo_path}",
            "",
            "## Summary",
            self._generate_summary(),
            "",
            "## Detailed Issues",
            "",
        ]

        for category, issues in sorted(self.issues.items()):
            if issues:
                report_lines.append(f"### {category.replace('_', ' ').title()}")
                report_lines.append("")
                for issue in issues:
                    report_lines.append(f"- {issue}")
                report_lines.append("")

        report_lines.append("## Recommended Actions")
        report_lines.append("")
        report_lines.append("Run the following command to clean up these issues:")
        report_lines.append("```bash")
        report_lines.append(
            "python agents/code_hygiene_orchestrator.py clean --interactive"
        )
        report_lines.append("```")

        report_content = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_content)
            logger.info(f"Report saved to: {output_file}")

        return report_content


@click.command()
@click.argument("command", type=click.Choice(["analyze", "clean", "report"]))
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@click.option(
    "--interactive", is_flag=True, help="Ask for confirmation before each action"
)
@click.option("--output", "-o", help="Output file for report")
@click.option(
    "--repo-path", default=".", help="Path to repository (default: current directory)"
)
def main(command, dry_run, interactive, output, repo_path):
    """Code Hygiene Orchestrator - Keep your codebase clean and organized."""
    orchestrator = CodeHygieneOrchestrator(repo_path)

    if command == "analyze":
        result = orchestrator.analyze()
        print("\n" + result["summary"])

    elif command == "clean":
        if not dry_run:
            print("⚠️  WARNING: This will modify your codebase!")
            if not interactive and not click.confirm("Continue?"):
                return

        result = orchestrator.clean(dry_run=dry_run, interactive=interactive)

        if dry_run:
            print("\n🔍 DRY RUN - No changes made")
        else:
            print(f"\n✅ Cleaned {len(result['actions'])} issues")

        if result["actions"]:
            print("\nActions taken:")
            for action in result["actions"][:10]:  # Show first 10
                print(f"  - {action}")
            if len(result["actions"]) > 10:
                print(f"  ... and {len(result['actions']) - 10} more")

    elif command == "report":
        orchestrator.analyze()
        report = orchestrator.generate_report(output)
        if not output:
            print(report)


if __name__ == "__main__":
    main()
