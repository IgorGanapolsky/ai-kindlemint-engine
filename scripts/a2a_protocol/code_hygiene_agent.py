#!/usr/bin/env python3
"""
Code Hygiene Orchestrator Agent - A2A implementation for cleaning up project structure
"""

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_agent import A2AAgent, A2AMessage, AgentCapability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FileAnalysis:
    """Analysis result for a file"""

    path: Path
    category: str  # 'source', 'test', 'config', 'docs', 'temp', 'duplicate'
    purpose: str
    issues: List[str]
    suggested_action: str
    suggested_location: Optional[Path] = None


class CodeHygieneAgent(A2AAgent):
    """A2A Agent for analyzing and cleaning up code structure"""

    def __init__(self, project_root: Optional[Path] = None):
        super().__init__(
            agent_id="code-hygiene-001",
            agent_type="orchestrator",
            name="Code Hygiene Orchestrator",
            description="Analyzes and cleans up project structure for better organization",
            version="1.0.0",
        )
        self.project_root = project_root or Path.cwd()

        # File patterns to identify different types
        self.patterns = {
            "test": [
                r"test_.*\.py$",
                r".*_test\.py$",
                r".*tests.*\.py$",
                r".*spec\.py$",
                r".*_spec\.py$",
            ],
            "config": [
                r"requirements.*\.txt$",
                r".*\.yml$",
                r".*\.yaml$",
                r".*\.json$",
                r".*\.toml$",
                r"\..*rc$",
                r".*config.*",
            ],
            "temp": [
                r"debug_.*",
                r".*\.pyc$",
                r".*\.pyo$",
                r".*__pycache__.*",
                r".*\.tmp$",
                r".*\.temp$",
                r".*\.bak$",
                r".*~$",
            ],
            "docs": [r".*\.md$", r".*\.rst$", r".*\.txt$", r"README.*", r"LICENSE.*"],
            "orchestration": [
                r".*orchestrat.*\.py$",
                r".*_agent\.py$",
                r".*badge.*\.py$",
            ],
            "scripts": [r"setup\.py$", r".*\.sh$", r"deploy.*", r"install.*"],
        }

        # Suggested directory structure
        self.ideal_structure = {
            "src": ["source code", "main application"],
            "tests": ["unit tests", "integration tests", "test fixtures"],
            "scripts": ["utility scripts", "deployment scripts", "automation"],
            "config": ["configuration files", "environment settings"],
            "docs": ["documentation", "README files", "guides"],
            "agents": ["A2A agents", "orchestrators", "AI components"],
            "data": ["data files", "datasets", "examples"],
            "infrastructure": ["Docker", "CI/CD", "deployment configs"],
            ".github": ["GitHub workflows", "issue templates"],
            "notebooks": ["Jupyter notebooks", "analysis"],
        }

    def _define_capabilities(self) -> List[AgentCapability]:
        """Define agent capabilities"""
        return [
            AgentCapability(
                name="analyze_structure",
                description="Analyze project structure and identify issues",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Project path"},
                        "deep_scan": {"type": "boolean", "default": True},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "total_files": {"type": "integer"},
                        "issues_found": {"type": "integer"},
                        "analysis": {"type": "array"},
                        "recommendations": {"type": "array"},
                    },
                },
            ),
            AgentCapability(
                name="generate_cleanup_plan",
                description="Generate a cleanup plan for the project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "analysis": {"type": "object"},
                        "auto_fix": {"type": "boolean", "default": False},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "actions": {"type": "array"},
                        "estimated_impact": {"type": "object"},
                    },
                },
            ),
            AgentCapability(
                name="execute_cleanup",
                description="Execute the cleanup plan",
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan": {"type": "object"},
                        "dry_run": {"type": "boolean", "default": True},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "executed_actions": {"type": "array"},
                        "status": {"type": "string"},
                    },
                },
            ),
            AgentCapability(
                name="find_duplicates",
                description="Find duplicate and similar files",
                input_schema={
                    "type": "object",
                    "properties": {
                        "similarity_threshold": {"type": "number", "default": 0.9}
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "duplicate_groups": {"type": "array"},
                        "total_duplicates": {"type": "integer"},
                    },
                },
            ),
        ]

    def _register_handlers(self) -> Dict[str, Any]:
        """Register message handlers"""
        return {
            "analyze_structure": self._handle_analyze_structure,
            "generate_cleanup_plan": self._handle_generate_cleanup_plan,
            "execute_cleanup": self._handle_execute_cleanup,
            "find_duplicates": self._handle_find_duplicates,
        }

    def _categorize_file(self, file_path: Path) -> Tuple[str, List[str]]:
        """Categorize a file and identify issues"""
        relative_path = str(file_path.relative_to(self.project_root))
        issues = []

        # Check against patterns
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.match(pattern, relative_path, re.IGNORECASE):
                    # Check if file is in wrong location
                    if category == "test" and "tests" not in str(file_path.parent):
                        issues.append("Test file not in tests directory")
                    elif category == "config" and file_path.parent == self.project_root:
                        issues.append("Config file in project root")
                    elif category == "temp":
                        issues.append("Temporary file should be removed")

                    return category, issues

        # Default to source if no pattern matches
        if file_path.suffix == ".py":
            return "source", issues

        return "other", issues

    def _analyze_project_structure(self, deep_scan: bool = True) -> Dict[str, Any]:
        """Analyze the entire project structure"""
        analysis_results = []
        file_categories = defaultdict(list)
        total_issues = 0

        # Scan all files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not str(file_path).startswith(".git"):
                category, issues = self._categorize_file(file_path)
                file_categories[category].append(file_path)

                if issues or self._needs_reorganization(file_path, category):
                    total_issues += 1
                    analysis = FileAnalysis(
                        path=file_path,
                        category=category,
                        purpose=self._determine_purpose(file_path),
                        issues=issues,
                        suggested_action=self._suggest_action(
                            file_path, category, issues
                        ),
                        suggested_location=self._suggest_location(file_path, category),
                    )
                    analysis_results.append(analysis)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            file_categories, analysis_results
        )

        return {
            "total_files": sum(len(files) for files in file_categories.values()),
            "issues_found": total_issues,
            "file_categories": {k: len(v) for k, v in file_categories.items()},
            "analysis": [
                self._analysis_to_dict(a) for a in analysis_results[:50]
            ],  # Limit to 50
            "recommendations": recommendations,
        }

    def _needs_reorganization(self, file_path: Path, category: str) -> bool:
        """Check if file needs reorganization"""
        # Root level files (except standard ones) need organization
        if file_path.parent == self.project_root:
            allowed_root_files = {
                "README.md",
                "LICENSE",
                "setup.py",
                ".gitignore",
                "requirements.txt",
                "pyproject.toml",
                "Makefile",
            }
            return file_path.name not in allowed_root_files

        # Check if file is in appropriate directory
        if category == "test" and "tests" not in str(file_path):
            return True
        if category == "config" and "config" not in str(file_path):
            return True
        if category == "orchestration" and "agents" not in str(file_path):
            return True

        return False

    def _determine_purpose(self, file_path: Path) -> str:
        """Determine the purpose of a file"""
        name = file_path.name.lower()

        if "test" in name:
            return "Testing"
        elif "config" in name or name.endswith((".yml", ".yaml", ".json")):
            return "Configuration"
        elif "requirements" in name:
            return "Dependencies"
        elif name.endswith("_agent.py"):
            return "AI Agent"
        elif "orchestrat" in name:
            return "Orchestration"
        elif "debug" in name:
            return "Debugging (temporary)"
        elif name.endswith(".md"):
            return "Documentation"
        else:
            return "Application code"

    def _suggest_action(self, file_path: Path, category: str, issues: List[str]) -> str:
        """Suggest action for a file"""
        if category == "temp":
            return "Delete temporary file"
        elif category == "test" and "tests" not in str(file_path):
            return "Move to tests directory"
        elif category == "config" and file_path.parent == self.project_root:
            return "Move to config directory"
        elif "duplicate" in " ".join(issues):
            return "Remove duplicate or consolidate"
        elif file_path.parent == self.project_root and file_path.suffix == ".py":
            return "Move to appropriate module directory"
        else:
            return "Review and organize"

    def _suggest_location(self, file_path: Path, category: str) -> Optional[Path]:
        """Suggest new location for a file"""
        if category == "test":
            return self.project_root / "tests" / file_path.name
        elif category == "config":
            return self.project_root / "config" / file_path.name
        elif category == "orchestration":
            return self.project_root / "agents" / file_path.name
        elif category == "scripts":
            return self.project_root / "scripts" / file_path.name
        elif category == "docs":
            return self.project_root / "docs" / file_path.name
        elif file_path.parent == self.project_root and file_path.suffix == ".py":
            # Analyze imports to determine module
            return self.project_root / "src" / file_path.name

        return None

    def _analysis_to_dict(self, analysis: FileAnalysis) -> Dict[str, Any]:
        """Convert FileAnalysis to dictionary"""
        return {
            "path": str(analysis.path.relative_to(self.project_root)),
            "category": analysis.category,
            "purpose": analysis.purpose,
            "issues": analysis.issues,
            "suggested_action": analysis.suggested_action,
            "suggested_location": (
                str(analysis.suggested_location.relative_to(self.project_root))
                if analysis.suggested_location
                else None
            ),
        }

    def _generate_recommendations(
        self,
        file_categories: Dict[str, List[Path]],
        analysis_results: List[FileAnalysis],
    ) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []

        # Check for missing directories
        for dir_name, purpose in self.ideal_structure.items():
            dir_path = self.project_root / dir_name
            if not dir_path.exists() and file_categories.get(dir_name.rstrip("s"), []):
                recommendations.append(
                    f"Create '{dir_name}' directory for {purpose[0]}"
                )

        # Check for too many root files
        root_files = [f for f in self.project_root.iterdir() if f.is_file()]
        if len(root_files) > 10:
            recommendations.append(
                f"Too many files in root ({len(root_files)}), organize into subdirectories"
            )

        # Check for test organization
        if file_categories["test"] and not (self.project_root / "tests").exists():
            recommendations.append(
                "Create dedicated 'tests' directory and organize test files"
            )

        # Check for duplicate requirements files
        req_files = [f for f in self.project_root.rglob("requirements*.txt")]
        if len(req_files) > 2:
            recommendations.append(
                f"Found {len(req_files)} requirements files, consider consolidating"
            )

        # Check for temporary files
        if file_categories["temp"]:
            recommendations.append(
                f"Remove {len(file_categories['temp'])} temporary files"
            )

        return recommendations

    def _find_duplicate_files(
        self, similarity_threshold: float = 0.9
    ) -> Dict[str, Any]:
        """Find duplicate files based on content similarity"""
        from hashlib import md5

        file_hashes = defaultdict(list)

        # Calculate hashes for all files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not str(file_path).startswith(".git"):
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                        file_hash = md5(content).hexdigest()
                        file_hashes[file_hash].append(file_path)
                except Exception:
                    continue

        # Find duplicates
        duplicate_groups = []
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                duplicate_groups.append(
                    {
                        "hash": file_hash,
                        "files": [str(f.relative_to(self.project_root)) for f in files],
                        "count": len(files),
                        "size": files[0].stat().st_size if files else 0,
                    }
                )

        return {
            "duplicate_groups": duplicate_groups,
            "total_duplicates": sum(g["count"] - 1 for g in duplicate_groups),
            "space_wasted": sum(g["size"] * (g["count"] - 1) for g in duplicate_groups),
        }

    def _handle_analyze_structure(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle structure analysis request"""
        try:
            deep_scan = payload.get("deep_scan", True)
            analysis = self._analyze_project_structure(deep_scan)

            return {"status": "success", **analysis}
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    def _handle_generate_cleanup_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cleanup plan based on analysis"""
        try:
            analysis = payload.get("analysis", {})
            auto_fix = payload.get("auto_fix", False)

            actions = []

            # Plan actions based on analysis
            if "analysis" in analysis:
                for item in analysis["analysis"]:
                    action = {
                        "type": item["suggested_action"],
                        "file": item["path"],
                        "reason": ", ".join(item["issues"]),
                        "target": item["suggested_location"],
                    }
                    actions.append(action)

            # Estimate impact
            impact = {
                "files_to_move": len([a for a in actions if "Move" in a["type"]]),
                "files_to_delete": len([a for a in actions if "Delete" in a["type"]]),
                "directories_to_create": len(
                    set(a["target"] for a in actions if a["target"])
                ),
            }

            return {
                "status": "success",
                "actions": actions,
                "estimated_impact": impact,
                "auto_fix_available": auto_fix,
            }
        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            return {"status": "error", "error": str(e)}

    def _handle_execute_cleanup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cleanup plan"""
        try:
            plan = payload.get("plan", {})
            dry_run = payload.get("dry_run", True)

            executed_actions = []

            if not dry_run:
                logger.warning("Actual cleanup execution not implemented for safety")

            # Simulate execution
            for action in plan.get("actions", []):
                executed_actions.append(
                    {
                        "action": action,
                        "status": "dry_run" if dry_run else "would_execute",
                        "message": f"Would {action['type']} {action['file']}",
                    }
                )

            return {
                "status": "success",
                "executed_actions": executed_actions,
                "dry_run": dry_run,
            }
        except Exception as e:
            logger.error(f"Cleanup execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def _handle_find_duplicates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle duplicate file detection"""
        try:
            threshold = payload.get("similarity_threshold", 0.9)
            duplicates = self._find_duplicate_files(threshold)

            return {"status": "success", **duplicates}
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    # Test the agent
    import asyncio

    async def test_hygiene_agent():
        agent = CodeHygieneAgent()

        # Test analysis
        msg = A2AMessage.create_request(
            sender_id="test",
            receiver_id="code-hygiene-001",
            action="analyze_structure",
            payload={"deep_scan": True},
        )

        response = agent.process_message(msg)
        print(json.dumps(response.payload, indent=2))

    asyncio.run(test_hygiene_agent())
