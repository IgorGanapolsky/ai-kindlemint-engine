#!/usr/bin/env python3
"""
Code Hygiene Orchestrator Agent
Maintains project cleanliness, organizes files, and manages git hygiene
"""

import json
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set


class FileCategory(Enum):
    """Categories for file organization"""

    TEST = "test"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    SOURCE = "source"
    DATA = "data"
    TEMPORARY = "temporary"
    BUILD = "build"
    LOG = "log"
    SCRIPT = "script"
    GENERATED = "generated"
    UNKNOWN = "unknown"


class CodeHygieneOrchestrator:
    """Orchestrates code hygiene tasks across the codebase"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.git_ignore_patterns = self._load_gitignore()
        self.hygiene_report = {
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "suggestions": [],
            "metrics": {},
        }

    def _load_gitignore(self) -> Set[str]:
        """Load gitignore patterns"""
        gitignore_path = self.project_root / ".gitignore"
        patterns = set()

        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)

        return patterns

    def analyze_project_hygiene(self) -> Dict:
        """Comprehensive project hygiene analysis"""
        print("🔍 Analyzing project hygiene...")

        # Get all untracked files
        untracked = self._get_untracked_files()

        # Categorize files
        categorized = self._categorize_files(untracked)

        # Find problematic patterns
        issues = self._find_hygiene_issues(categorized)

        # Generate suggestions
        suggestions = self._generate_cleanup_suggestions(categorized, issues)

        # Calculate metrics
        metrics = self._calculate_hygiene_metrics(untracked, categorized, issues)

        self.hygiene_report.update(
            {
                "untracked_files": len(untracked),
                "categorized_files": {k.value: len(v) for k, v in categorized.items()},
                "issues": issues,
                "suggestions": suggestions,
                "metrics": metrics,
            }
        )

        return self.hygiene_report

    def _get_untracked_files(self) -> List[Path]:
        """Get all untracked files from git"""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                files = [Path(f) for f in result.stdout.strip().split("\n") if f]
                return files
            return []

        except Exception as e:
            print(f"Error getting untracked files: {e}")
            return []

    def _categorize_files(self, files: List[Path]) -> Dict[FileCategory, List[Path]]:
        """Categorize files by type"""
        categories = defaultdict(list)

        for file in files:
            category = self._determine_file_category(file)
            categories[category].append(file)

        return dict(categories)

    def _determine_file_category(self, file: Path) -> FileCategory:
        """Determine the category of a file"""
        name = file.name.lower()
        path_str = str(file).lower()

        # Test files
        if "test" in path_str or name.startswith("test_") or name.endswith("_test.py"):
            return FileCategory.TEST

        # Config files
        if name.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".cfg")):
            return FileCategory.CONFIG

        # Documentation
        if name.endswith((".md", ".rst", ".txt")) and "readme" in name:
            return FileCategory.DOCUMENTATION

        # Temporary files
        if (
            name.startswith(".")
            or name.endswith("~")
            or "__pycache__" in path_str
            or ".pyc" in name
        ):
            return FileCategory.TEMPORARY

        # Log files
        if name.endswith(".log") or "logs" in path_str:
            return FileCategory.LOG

        # Build artifacts
        if "dist" in path_str or "build" in path_str or name.endswith(".whl"):
            return FileCategory.BUILD

        # Scripts
        if name.endswith(".sh") or name.endswith(".py") and "scripts" in path_str:
            return FileCategory.SCRIPT

        # Source code
        if name.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
            return FileCategory.SOURCE

        # Data files
        if name.endswith((".csv", ".json", ".xml")) or "data" in path_str:
            return FileCategory.DATA

        return FileCategory.UNKNOWN

    def _find_hygiene_issues(
        self, categorized: Dict[FileCategory, List[Path]]
    ) -> List[Dict]:
        """Identify hygiene issues"""
        issues = []

        # Check for temporary files
        if FileCategory.TEMPORARY in categorized:
            issues.append(
                {
                    "type": "temporary_files",
                    "severity": "high",
                    "count": len(categorized[FileCategory.TEMPORARY]),
                    "message": "Temporary files should not be tracked",
                    "files": [str(f) for f in categorized[FileCategory.TEMPORARY][:10]],
                }
            )

        # Check for build artifacts
        if FileCategory.BUILD in categorized:
            issues.append(
                {
                    "type": "build_artifacts",
                    "severity": "high",
                    "count": len(categorized[FileCategory.BUILD]),
                    "message": "Build artifacts should be gitignored",
                }
            )

        # Check for excessive untracked files
        total_untracked = sum(len(files) for files in categorized.values())
        if total_untracked > 50:
            issues.append(
                {
                    "type": "excessive_untracked",
                    "severity": "high",
                    "count": total_untracked,
                    "message": f"Too many untracked files ({total_untracked})",
                }
            )

        # Check for missing gitignore entries
        missing_gitignore = self._find_missing_gitignore_patterns(categorized)
        if missing_gitignore:
            issues.append(
                {
                    "type": "missing_gitignore",
                    "severity": "medium",
                    "patterns": list(missing_gitignore),
                    "message": "Patterns that should be in .gitignore",
                }
            )

        return issues

    def _find_missing_gitignore_patterns(
        self, categorized: Dict[FileCategory, List[Path]]
    ) -> Set[str]:
        """Find patterns that should be in gitignore"""
        patterns = set()

        # Common patterns that should be ignored
        if FileCategory.TEMPORARY in categorized:
            patterns.add("__pycache__/")
            patterns.add("*.pyc")
            patterns.add(".DS_Store")
            patterns.add("*.swp")

        if FileCategory.BUILD in categorized:
            patterns.add("dist/")
            patterns.add("build/")
            patterns.add("*.egg-info/")

        if FileCategory.LOG in categorized:
            patterns.add("*.log")
            patterns.add("logs/")

        # Remove patterns already in gitignore
        patterns -= self.git_ignore_patterns

        return patterns

    def _generate_cleanup_suggestions(
        self, categorized: Dict[FileCategory, List[Path]], issues: List[Dict]
    ) -> List[Dict]:
        """Generate cleanup suggestions"""
        suggestions = []

        # Suggest gitignore updates
        missing_patterns = set()
        for issue in issues:
            if issue["type"] == "missing_gitignore":
                missing_patterns.update(issue["patterns"])

        if missing_patterns:
            suggestions.append(
                {
                    "action": "update_gitignore",
                    "priority": "high",
                    "patterns": list(missing_patterns),
                    "command": f"echo '{chr(10).join(missing_patterns)}' >> .gitignore",
                }
            )

        # Suggest file organization
        if (
            FileCategory.UNKNOWN in categorized
            and len(categorized[FileCategory.UNKNOWN]) > 10
        ):
            suggestions.append(
                {
                    "action": "organize_files",
                    "priority": "medium",
                    "message": "Many uncategorized files need organization",
                }
            )

        # Suggest cleanup commands
        if FileCategory.TEMPORARY in categorized:
            suggestions.append(
                {
                    "action": "clean_temporary",
                    "priority": "high",
                    "command": "find . -type f -name '*.pyc' -delete && find . -type d -name '__pycache__' -exec rm -rf {} +",
                }
            )

        # Suggest commit strategy
        if sum(len(files) for files in categorized.values()) > 20:
            suggestions.append(
                {
                    "action": "staged_commits",
                    "priority": "medium",
                    "message": "Use staged commits to organize changes logically",
                }
            )

        return suggestions

    def _calculate_hygiene_metrics(
        self,
        untracked: List[Path],
        categorized: Dict[FileCategory, List[Path]],
        issues: List[Dict],
    ) -> Dict:
        """Calculate hygiene metrics"""
        total_files = len(untracked)

        return {
            "hygiene_score": self._calculate_hygiene_score(issues, total_files),
            "untracked_files": total_files,
            "temporary_files": len(categorized.get(FileCategory.TEMPORARY, [])),
            "organization_score": self._calculate_organization_score(categorized),
            "issues_count": len(issues),
            "critical_issues": sum(1 for i in issues if i.get("severity") == "high"),
        }

    def _calculate_hygiene_score(self, issues: List[Dict], total_files: int) -> float:
        """Calculate overall hygiene score (0-100)"""
        score = 100.0

        # Deduct for issues
        for issue in issues:
            if issue.get("severity") == "high":
                score -= 10
            elif issue.get("severity") == "medium":
                score -= 5
            else:
                score -= 2

        # Deduct for excessive files
        if total_files > 100:
            score -= 20
        elif total_files > 50:
            score -= 10
        elif total_files > 20:
            score -= 5

        return max(0, score)

    def _calculate_organization_score(
        self, categorized: Dict[FileCategory, List[Path]]
    ) -> float:
        """Calculate organization score"""
        total = sum(len(files) for files in categorized.values())
        if total == 0:
            return 100.0

        unknown = len(categorized.get(FileCategory.UNKNOWN, []))
        organized = total - unknown

        return (organized / total) * 100

    def execute_cleanup(self, auto_confirm: bool = False) -> Dict:
        """Execute cleanup operations"""
        results = {"operations": [], "success": True, "errors": []}

        # First analyze
        report = self.analyze_project_hygiene()

        for suggestion in report["suggestions"]:
            if suggestion["priority"] == "high":
                if auto_confirm or self._confirm_action(suggestion):
                    result = self._execute_suggestion(suggestion)
                    results["operations"].append(result)

        return results

    def _confirm_action(self, suggestion: Dict) -> bool:
        """Confirm action with user"""
        print(f"\n🤔 Suggested action: {suggestion.get('action')}")
        if "message" in suggestion:
            print(f"   {suggestion['message']}")
        if "command" in suggestion:
            print(f"   Command: {suggestion['command']}")

        response = input("Execute? (y/n): ")
        return response.lower() == "y"

    def _execute_suggestion(self, suggestion: Dict) -> Dict:
        """Execute a cleanup suggestion"""
        action = suggestion.get("action")

        if action == "update_gitignore":
            return self._update_gitignore(suggestion["patterns"])
        elif action == "clean_temporary":
            return self._clean_temporary_files()
        elif action == "organize_files":
            return self._organize_files()

        return {"action": action, "status": "skipped"}

    def _update_gitignore(self, patterns: List[str]) -> Dict:
        """Update gitignore file"""
        try:
            gitignore_path = self.project_root / ".gitignore"

            with open(gitignore_path, "a") as f:
                f.write("\n# Added by Code Hygiene Orchestrator\n")
                for pattern in patterns:
                    f.write(f"{pattern}\n")

            return {
                "action": "update_gitignore",
                "status": "success",
                "patterns_added": patterns,
            }
        except Exception as e:
            return {"action": "update_gitignore", "status": "error", "error": str(e)}

    def _clean_temporary_files(self) -> Dict:
        """Clean temporary files"""
        cleaned = []
        errors = []

        patterns = ["__pycache__", ".pyc", ".pyo", ".DS_Store", ".swp"]

        for pattern in patterns:
            try:
                if pattern == "__pycache__":
                    # Remove __pycache__ directories
                    for pycache in self.project_root.rglob("__pycache__"):
                        shutil.rmtree(pycache)
                        cleaned.append(str(pycache))
                else:
                    # Remove files matching pattern
                    for file in self.project_root.rglob(f"*{pattern}"):
                        file.unlink()
                        cleaned.append(str(file))

            except Exception as e:
                errors.append(f"Error cleaning {pattern}: {e}")

        return {
            "action": "clean_temporary",
            "status": "success" if not errors else "partial",
            "cleaned": len(cleaned),
            "errors": errors,
        }

    def _organize_files(self) -> Dict:
        """Organize files into appropriate directories"""
        # This is a placeholder for more complex organization logic
        return {
            "action": "organize_files",
            "status": "manual_required",
            "message": "File organization requires manual review",
        }

    def generate_commit_plan(self) -> List[Dict]:
        """Generate a plan for committing files in logical groups"""
        self.analyze_project_hygiene()
        categorized = self._categorize_files(self._get_untracked_files())

        commit_groups = []

        # Group 1: Documentation
        if FileCategory.DOCUMENTATION in categorized:
            commit_groups.append(
                {
                    "message": "docs: Add documentation files",
                    "files": [str(f) for f in categorized[FileCategory.DOCUMENTATION]],
                    "priority": 1,
                }
            )

        # Group 2: Configuration
        if FileCategory.CONFIG in categorized:
            commit_groups.append(
                {
                    "message": "config: Add configuration files",
                    "files": [str(f) for f in categorized[FileCategory.CONFIG]],
                    "priority": 2,
                }
            )

        # Group 3: Tests
        if FileCategory.TEST in categorized:
            commit_groups.append(
                {
                    "message": "test: Add test files",
                    "files": [str(f) for f in categorized[FileCategory.TEST]],
                    "priority": 3,
                }
            )

        # Group 4: Source code by module
        if FileCategory.SOURCE in categorized:
            # Group by directory
            by_module = defaultdict(list)
            for file in categorized[FileCategory.SOURCE]:
                module = file.parts[0] if len(file.parts) > 1 else "root"
                by_module[module].append(file)

            for module, files in by_module.items():
                commit_groups.append(
                    {
                        "message": f"feat: Add {module} module",
                        "files": [str(f) for f in files],
                        "priority": 4,
                    }
                )

        return sorted(commit_groups, key=lambda x: x["priority"])

    def save_report(self, output_path: Path = None) -> Path:
        """Save hygiene report to file"""
        if output_path is None:
            output_path = (
                self.project_root
                / f"hygiene_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        with open(output_path, "w") as f:
            json.dump(self.hygiene_report, f, indent=2)

        return output_path


if __name__ == "__main__":
    # Run hygiene analysis
    orchestrator = CodeHygieneOrchestrator()

    print("🧹 Code Hygiene Orchestrator")
    print("=" * 50)

    # Analyze project
    report = orchestrator.analyze_project_hygiene()

    print(f"\n📊 Hygiene Score: {report['metrics']['hygiene_score']:.1f}/100")
    print(f"📁 Untracked Files: {report['untracked_files']}")
    print(f"⚠️  Issues Found: {report['metrics']['issues_count']}")

    # Show categorized files
    print("\n📂 File Categories:")
    for category, count in report["categorized_files"].items():
        if count > 0:
            print(f"   {category}: {count} files")

    # Show issues
    if report["issues"]:
        print("\n🚨 Issues:")
        for issue in report["issues"]:
            print(f"   - {issue['message']} (severity: {issue['severity']})")

    # Show suggestions
    if report["suggestions"]:
        print("\n💡 Suggestions:")
        for suggestion in report["suggestions"]:
            print(f"   - {suggestion.get('message', suggestion['action'])}")

    # Save report
    report_path = orchestrator.save_report()
    print(f"\n📄 Full report saved to: {report_path}")

    # Offer to execute cleanup
    if input("\n🤔 Execute automatic cleanup? (y/n): ").lower() == "y":
        results = orchestrator.execute_cleanup()
        print(f"\n✅ Cleanup completed: {len(results['operations'])} operations")
