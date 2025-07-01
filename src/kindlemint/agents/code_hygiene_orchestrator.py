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
        """REAL comprehensive project hygiene analysis"""
        print("🔍 Analyzing REAL project hygiene...")

        # Get ALL repository files, not just untracked
        all_files = self._get_all_repository_files()

        # Analyze root directory clutter
        root_files = self._get_root_files()

        # Find hygiene issues in repository structure
        issues = self._find_real_hygiene_issues(root_files, all_files)

        # Generate real cleanup suggestions
        suggestions = self._generate_real_cleanup_suggestions(
            issues, root_files)

        # Calculate REAL hygiene metrics
        metrics = self._calculate_real_hygiene_metrics(
            root_files, issues, all_files)

        self.hygiene_report.update(
            {
                "total_files": len(all_files),
                "root_files": len(root_files),
                "root_file_list": [f.name for f in root_files],
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
                files = [Path(f)
                         for f in result.stdout.strip().split("\n") if f]
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

    def _get_all_repository_files(self) -> List[Path]:
        """Get all files in the repository"""
        all_files = []
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                # Skip .git directory and other hidden system files
                if not any(part.startswith(".git") for part in file_path.parts):
                    all_files.append(file_path)
        return all_files

    def _get_root_files(self) -> List[Path]:
        """Get all files in the root directory"""
        root_files = []
        for item in self.project_root.iterdir():
            if item.is_file():
                root_files.append(item)
        return root_files

    def _find_real_hygiene_issues(
        self, root_files: List[Path], all_files: List[Path]
    ) -> List[Dict]:
        """Find REAL hygiene issues in repository structure"""
        issues = []

        # Check for excessive root clutter
        if len(root_files) > 25:
            issues.append(
                {
                    "type": "root_clutter_critical",
                    "severity": "high",
                    "count": len(root_files),
                    "message": f"Too many files in root directory ({len(root_files)}). Should be < 20.",
                    "suggestion": "Move files to appropriate subdirectories",
                }
            )
        elif len(root_files) > 15:
            issues.append(
                {
                    "type": "root_clutter_moderate",
                    "severity": "medium",
                    "count": len(root_files),
                    "message": f"Moderate root clutter ({len(root_files)} files). Consider organizing.",
                    "suggestion": "Move non-essential files to subdirectories",
                }
            )

        # Check for specific problematic patterns in root
        root_md_files = [
            f for f in root_files if f.suffix == ".md" and f.name != "README.md"
        ]
        if len(root_md_files) > 3:
            issues.append(
                {
                    "type": "documentation_clutter",
                    "severity": "high",
                    "count": len(root_md_files),
                    "message": f"{len(root_md_files)} .md files in root (should be in docs/)",
                    "files": [f.name for f in root_md_files[:5]],
                }
            )

        # Check for log files in root
        root_log_files = [
            f
            for f in root_files
            if f.suffix in [".log", ".txt"] and "output" in f.name.lower()
        ]
        if root_log_files:
            issues.append(
                {
                    "type": "log_file_clutter",
                    "severity": "medium",
                    "count": len(root_log_files),
                    "message": f"{len(root_log_files)} log/output files in root (should be in logs/)",
                    "files": [f.name for f in root_log_files],
                }
            )

        # Check for script files in root
        root_script_files = [
            f for f in root_files if f.suffix == ".py" and f.name not in ["setup.py"]
        ]
        if root_script_files:
            issues.append(
                {
                    "type": "script_clutter",
                    "severity": "medium",
                    "count": len(root_script_files),
                    "message": f"{len(root_script_files)} Python scripts in root (should be in scripts/)",
                    "files": [f.name for f in root_script_files],
                }
            )

        return issues

    def _generate_real_cleanup_suggestions(
        self, issues: List[Dict], root_files: List[Path]
    ) -> List[Dict]:
        """Generate REAL cleanup suggestions based on actual issues"""
        suggestions = []

        for issue in issues:
            if issue["type"] == "root_clutter_critical":
                suggestions.append(
                    {
                        "action": "aggressive_root_cleanup",
                        "priority": "high",
                        "message": f"Move {issue['count']} files from root to appropriate directories",
                        "command": "python scripts/aggressive_repository_cleanup.py",
                    }
                )
            elif issue["type"] == "documentation_clutter":
                suggestions.append(
                    {
                        "action": "move_docs_to_docs_dir",
                        "priority": "high",
                        "message": f"Move {issue['count']} .md files to docs/ directory",
                        "files": issue.get("files", []),
                    }
                )
            elif issue["type"] == "log_file_clutter":
                suggestions.append(
                    {
                        "action": "move_logs_to_logs_dir",
                        "priority": "medium",
                        "message": f"Move {issue['count']} log files to logs/ directory",
                        "files": issue.get("files", []),
                    }
                )
            elif issue["type"] == "script_clutter":
                suggestions.append(
                    {
                        "action": "move_scripts_to_scripts_dir",
                        "priority": "medium",
                        "message": f"Move {issue['count']} Python scripts to scripts/ directory",
                        "files": issue.get("files", []),
                    }
                )

        return suggestions

    def _calculate_real_hygiene_metrics(
        self, root_files: List[Path], issues: List[Dict], all_files: List[Path]
    ) -> Dict:
        """Calculate REAL hygiene metrics based on repository organization"""
        # Base score starts at 100
        hygiene_score = 100.0

        # Deduct points for root clutter
        root_file_count = len(root_files)
        if root_file_count > 30:
            hygiene_score -= 30
        elif root_file_count > 25:
            hygiene_score -= 20
        elif root_file_count > 20:
            hygiene_score -= 15
        elif root_file_count > 15:
            hygiene_score -= 10
        elif root_file_count > 10:
            hygiene_score -= 5

        # Deduct points for specific issues
        for issue in issues:
            if issue["severity"] == "high":
                hygiene_score -= 15
            elif issue["severity"] == "medium":
                hygiene_score -= 10
            else:
                hygiene_score -= 5

        # Ensure score doesn't go below 0
        hygiene_score = max(0, hygiene_score)

        return {
            "hygiene_score": hygiene_score,
            "root_files": root_file_count,
            "total_files": len(all_files),
            "issues_count": len(issues),
            "critical_issues": sum(1 for i in issues if i.get("severity") == "high"),
            "organization_score": self._calculate_organization_score_real(
                root_files, all_files
            ),
        }

    def _calculate_organization_score_real(
        self, root_files: List[Path], all_files: List[Path]
    ) -> float:
        """Calculate organization score based on file distribution"""
        if len(all_files) == 0:
            return 100.0

        # Calculate what percentage of files are properly organized (not in root)
        non_root_files = len(all_files) - len(root_files)
        organization_score = (non_root_files / len(all_files)) * 100

        # Bonus points for having standard directories
        standard_dirs = ["src", "scripts", "docs", "tests", "config"]
        existing_dirs = [
            d.name for d in self.project_root.iterdir() if d.is_dir()]
        dir_bonus = sum(5 for d in standard_dirs if d in existing_dirs)

        return min(100.0, organization_score + dir_bonus)

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

    print(
        f"\n📊 REAL Hygiene Score: {report['metrics']['hygiene_score']:.1f}/100")
    print(f"📁 Root Files: {report['root_files']}")
    print(f"📁 Total Files: {report['total_files']}")
    print(f"⚠️  Issues Found: {report['metrics']['issues_count']}")

    # Show root files
    print(f"\n📂 Root Directory Files ({len(report['root_file_list'])}):")
    for i, filename in enumerate(report["root_file_list"][:10]):
        print(f"   {filename}")
    if len(report["root_file_list"]) > 10:
        print(f"   ... and {len(report['root_file_list']) - 10} more")

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
        print(
            f"\n✅ Cleanup completed: {len(results['operations'])} operations")
