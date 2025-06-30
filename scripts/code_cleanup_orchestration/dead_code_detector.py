#!/usr/bin/env python3
"""
Dead Code Detection Agent for AI-KindleMint Engine

This module provides comprehensive dead code detection capabilities including:
- Import analysis and unused import detection
- Function/class usage analysis across the codebase
- File dependency mapping and orphaned file identification
- Archive validation for obsolete code
- Entry point analysis for unreachable code
- Test coverage correlation for unused code paths
"""

import ast
import json
import logging
import os
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


@dataclass
class DeadCodeCandidate:
    """Represents a potential dead code item"""

    type: str  # 'import', 'function', 'class', 'file', 'variable'
    name: str
    file_path: str
    line_number: int
    confidence: float  # 0.0 to 1.0
    reasons: List[str]
    dependencies: List[str]
    last_modified: str
    size_impact: int  # lines of code


@dataclass
class DependencyGraph:
    """Represents the dependency relationships in the codebase"""

    nodes: Set[str]
    edges: Dict[str, Set[str]]
    entry_points: Set[str]
    orphaned_files: Set[str]


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python code structure"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports: Dict[str, int] = {}
        self.function_definitions: Dict[str, int] = {}
        self.class_definitions: Dict[str, int] = {}
        self.function_calls: Dict[str, List[int]] = defaultdict(list)
        self.attribute_accesses: Dict[str, List[int]] = defaultdict(list)
        self.variables: Dict[str, int] = {}

    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.name] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                import_name = f"{node.module}.{alias.name}"
                self.imports[import_name] = node.lineno
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.function_definitions[node.name] = node.lineno
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.function_definitions[node.name] = node.lineno
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.class_definitions[node.name] = node.lineno
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls[node.func.id].append(node.lineno)
        elif isinstance(node.func, ast.Attribute):
            self.attribute_accesses[node.func.attr].append(node.lineno)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.variables[node.id] = node.lineno
        self.generic_visit(node)


class DeadCodeDetector:
    """Main dead code detection engine"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.project_root = Path(self.config.get("project_root", os.getcwd()))
        self.exclude_patterns = self.config.get("exclude_patterns", [])
        self.entry_points = self.config.get("entry_points", [])
        self.archive_dirs = self.config.get(
            "archive_dirs", ["archive", "backup"])

        # Analysis results
        self.file_ast_data: Dict[str, ASTAnalyzer] = {}
        self.dependency_graph = DependencyGraph(set(), {}, set(), set())
        self.candidates: List[DeadCodeCandidate] = []

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = Path(__file__).parent / \
                "config" / "cleanup_config.yaml"

        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(
                f"Config file not found: {config_path}. Using defaults."
            )
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "project_root": os.getcwd(),
            "exclude_patterns": [
                "*/venv/*",
                "*/node_modules/*",
                "*/.git/*",
                "*/__pycache__/*",
                "*/tests/*",
                "*/test_*",
                "*conftest.py",
            ],
            "entry_points": ["main.py", "cli.py", "app.py", "manage.py"],
            "archive_dirs": ["archive", "backup", "old", "deprecated"],
            "min_confidence_threshold": 0.7,
            "coverage_threshold": 0.8,
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("dead_code_detector")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    Path(root, d).match(pattern) for pattern in self.exclude_patterns
                )
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    if not any(
                        file_path.match(pattern) for pattern in self.exclude_patterns
                    ):
                        python_files.append(file_path)

        return python_files

    def analyze_file(self, file_path: Path) -> ASTAnalyzer:
        """Analyze a single Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            analyzer = ASTAnalyzer(str(file_path))
            analyzer.visit(tree)

            return analyzer
        except (SyntaxError, UnicodeDecodeError) as e:
            self.logger.warning(f"Failed to parse {file_path}: {e}")
            return ASTAnalyzer(str(file_path))

    def build_dependency_graph(self) -> DependencyGraph:
        """Build dependency graph of the entire codebase"""
        self.logger.info("Building dependency graph...")

        nodes = set()
        edges = defaultdict(set)

        for file_path, analyzer in self.file_ast_data.items():
            nodes.add(file_path)

            # Add edges for imports
            for import_name in analyzer.imports:
                # Try to resolve import to actual file
                resolved_file = self._resolve_import(import_name, file_path)
                if resolved_file and resolved_file in self.file_ast_data:
                    edges[file_path].add(resolved_file)

        # Identify entry points
        entry_points = set()
        for file_path in nodes:
            file_name = Path(file_path).name
            if any(
                file_name == ep or file_name.startswith("main")
                for ep in self.entry_points
            ):
                entry_points.add(file_path)

        # Find orphaned files (not reachable from entry points)
        reachable = self._find_reachable_files(entry_points, edges)
        orphaned_files = nodes - reachable

        return DependencyGraph(nodes, dict(edges), entry_points, orphaned_files)

    def _resolve_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Attempt to resolve an import to an actual file path"""
        try:
            # Handle relative imports
            if import_name.startswith("."):
                current_dir = Path(current_file).parent
                # Simplified relative import resolution
                import_parts = import_name.lstrip(".").split(".")
                potential_path = current_dir
                for part in import_parts:
                    potential_path = potential_path / part

                py_file = potential_path.with_suffix(".py")
                if py_file.exists():
                    return str(py_file)

                init_file = potential_path / "__init__.py"
                if init_file.exists():
                    return str(init_file)

            # Handle absolute imports within project
            import_parts = import_name.split(".")
            potential_path = self.project_root
            for part in import_parts:
                potential_path = potential_path / part

            py_file = potential_path.with_suffix(".py")
            if py_file.exists():
                return str(py_file)

            init_file = potential_path / "__init__.py"
            if init_file.exists():
                return str(init_file)

        except Exception:
            pass

        return None

    def _find_reachable_files(
        self, entry_points: Set[str], edges: Dict[str, Set[str]]
    ) -> Set[str]:
        """Find all files reachable from entry points using BFS"""
        reachable = set()
        queue = deque(entry_points)

        while queue:
            current = queue.popleft()
            if current in reachable:
                continue

            reachable.add(current)
            for neighbor in edges.get(current, set()):
                if neighbor not in reachable:
                    queue.append(neighbor)

        return reachable

    def detect_unused_imports(self) -> List[DeadCodeCandidate]:
        """Detect unused imports across all files"""
        candidates = []

        for file_path, analyzer in self.file_ast_data.items():
            for import_name, line_number in analyzer.imports.items():
                # Check if import is used in the file
                is_used = self._is_import_used(import_name, analyzer)

                if not is_used:
                    confidence = 0.9  # High confidence for unused imports

                    # Check if it's in archive directory (lower priority)
                    if any(
                        archive_dir in file_path for archive_dir in self.archive_dirs
                    ):
                        confidence = 0.95

                    candidate = DeadCodeCandidate(
                        type="import",
                        name=import_name,
                        file_path=file_path,
                        line_number=line_number,
                        confidence=confidence,
                        reasons=["Import not used in file"],
                        dependencies=[],
                        last_modified=self._get_file_modified_time(file_path),
                        size_impact=1,
                    )
                    candidates.append(candidate)

        return candidates

    def _is_import_used(self, import_name: str, analyzer: ASTAnalyzer) -> bool:
        """Check if an import is used within the file"""
        # Simple heuristic: check if import name appears in function calls or attributes
        import_parts = import_name.split(".")
        base_name = import_parts[-1]

        # Check function calls and attribute accesses
        if (
            base_name in analyzer.function_calls
            or base_name in analyzer.attribute_accesses
        ):
            return True

        # Check if used in variable assignments or other contexts
        # This is a simplified check - could be enhanced with more sophisticated
        # analysis
        try:
            with open(analyzer.file_path, "r") as f:
                content = f.read()
                return base_name in content.replace(f"import {import_name}", "")
        except Exception:
            return True  # Conservative approach if we can't read the file

    def detect_unused_functions(self) -> List[DeadCodeCandidate]:
        """Detect unused functions across the codebase"""
        candidates = []

        # Build a map of all function calls across all files
        all_function_calls = set()
        for analyzer in self.file_ast_data.values():
            all_function_calls.update(analyzer.function_calls.keys())

        for file_path, analyzer in self.file_ast_data.items():
            for func_name, line_number in analyzer.function_definitions.items():
                # Skip special methods and private functions with low confidence
                if func_name.startswith("__") and func_name.endswith("__"):
                    continue

                is_used = func_name in all_function_calls
                confidence = 0.8 if not is_used else 0.0

                # Higher confidence for archive directories
                if any(archive_dir in file_path for archive_dir in self.archive_dirs):
                    confidence = min(confidence + 0.1, 1.0)

                # Check if it's a main function or entry point
                if (
                    func_name in ["main", "run", "execute"]
                    or file_path in self.dependency_graph.entry_points
                ):
                    confidence = max(confidence - 0.3, 0.0)

                if confidence > self.config.get("min_confidence_threshold", 0.7):
                    candidate = DeadCodeCandidate(
                        type="function",
                        name=func_name,
                        file_path=file_path,
                        line_number=line_number,
                        confidence=confidence,
                        reasons=["Function not called anywhere in codebase"],
                        dependencies=[],
                        last_modified=self._get_file_modified_time(file_path),
                        size_impact=self._estimate_function_size(
                            file_path, line_number
                        ),
                    )
                    candidates.append(candidate)

        return candidates

    def detect_unused_classes(self) -> List[DeadCodeCandidate]:
        """Detect unused classes across the codebase"""
        candidates = []

        # Build a map of all class instantiations and references
        all_class_references = set()
        for analyzer in self.file_ast_data.values():
            all_class_references.update(
                analyzer.function_calls.keys())  # Class() calls
            all_class_references.update(
                analyzer.attribute_accesses.keys()
            )  # Class.method calls

        for file_path, analyzer in self.file_ast_data.items():
            for class_name, line_number in analyzer.class_definitions.items():
                is_used = class_name in all_class_references
                confidence = 0.7 if not is_used else 0.0

                # Higher confidence for archive directories
                if any(archive_dir in file_path for archive_dir in self.archive_dirs):
                    confidence = min(confidence + 0.2, 1.0)

                if confidence > self.config.get("min_confidence_threshold", 0.7):
                    candidate = DeadCodeCandidate(
                        type="class",
                        name=class_name,
                        file_path=file_path,
                        line_number=line_number,
                        confidence=confidence,
                        reasons=[
                            "Class not instantiated or referenced anywhere"],
                        dependencies=[],
                        last_modified=self._get_file_modified_time(file_path),
                        size_impact=self._estimate_class_size(
                            file_path, line_number),
                    )
                    candidates.append(candidate)

        return candidates

    def detect_orphaned_files(self) -> List[DeadCodeCandidate]:
        """Detect files that are not reachable from entry points"""
        candidates = []

        for file_path in self.dependency_graph.orphaned_files:
            # Skip test files and configuration files
            if any(pattern in file_path for pattern in ["test_", "conftest", "config"]):
                continue

            confidence = 0.6
            reasons = ["File not reachable from any entry point"]

            # Higher confidence for archive directories
            if any(archive_dir in file_path for archive_dir in self.archive_dirs):
                confidence = 0.9
                reasons.append("File in archive directory")

            # Check file age
            age_days = self._get_file_age_days(file_path)
            if age_days > 90:
                confidence = min(confidence + 0.1, 1.0)
                reasons.append(f"File not modified for {age_days} days")

            if confidence > self.config.get("min_confidence_threshold", 0.7):
                candidate = DeadCodeCandidate(
                    type="file",
                    name=Path(file_path).name,
                    file_path=file_path,
                    line_number=0,
                    confidence=confidence,
                    reasons=reasons,
                    dependencies=list(
                        self.dependency_graph.edges.get(file_path, set())
                    ),
                    last_modified=self._get_file_modified_time(file_path),
                    size_impact=self._get_file_line_count(file_path),
                )
                candidates.append(candidate)

        return candidates

    def correlate_with_coverage(
        self, coverage_file: Optional[str] = None
    ) -> List[DeadCodeCandidate]:
        """Correlate dead code detection with test coverage data"""
        if not coverage_file:
            # Try to find coverage file
            potential_files = [".coverage", "coverage.xml", "coverage.json"]
            for f in potential_files:
                if Path(f).exists():
                    coverage_file = f
                    break

        if not coverage_file:
            self.logger.warning(
                "No coverage file found. Skipping coverage correlation."
            )
            return []

        # This would integrate with coverage.py data
        # Implementation depends on coverage file format
        candidates = []

        # Placeholder for coverage correlation logic
        self.logger.info(
            f"Coverage correlation with {coverage_file} not yet implemented"
        )

        return candidates

    def _get_file_modified_time(self, file_path: str) -> str:
        """Get file last modified time"""
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).isoformat()
        except OSError:
            return datetime.now().isoformat()

    def _get_file_age_days(self, file_path: str) -> int:
        """Get file age in days"""
        try:
            mtime = os.path.getmtime(file_path)
            age_seconds = datetime.now().timestamp() - mtime
            return int(age_seconds / (24 * 3600))
        except OSError:
            return 0

    def _get_file_line_count(self, file_path: str) -> int:
        """Get number of lines in file"""
        try:
            with open(file_path, "r") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def _estimate_function_size(self, file_path: str, line_number: int) -> int:
        """Estimate the size of a function in lines"""
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            # Simple heuristic: count indented lines after function definition
            size = 1
            base_indent = None

            for i in range(line_number, len(lines)):
                line = lines[i]
                if line.strip() == "":
                    continue

                indent = len(line) - len(line.lstrip())

                if base_indent is None and line.strip():
                    base_indent = indent

                if base_indent is not None and indent > base_indent:
                    size += 1
                elif (
                    base_indent is not None
                    and indent <= base_indent
                    and i > line_number
                ):
                    break

            return size
        except Exception:
            return 10  # Default estimate

    def _estimate_class_size(self, file_path: str, line_number: int) -> int:
        """Estimate the size of a class in lines"""
        # Similar to function size estimation but for classes
        return self._estimate_function_size(file_path, line_number)

    def run_analysis(self) -> Dict[str, Any]:
        """Run complete dead code analysis"""
        self.logger.info("Starting dead code analysis...")

        # Find and analyze all Python files
        python_files = self.find_python_files()
        self.logger.info(f"Found {len(python_files)} Python files")

        for file_path in python_files:
            self.file_ast_data[str(file_path)] = self.analyze_file(file_path)

        # Build dependency graph
        self.dependency_graph = self.build_dependency_graph()

        # Detect dead code candidates
        self.candidates = []
        self.candidates.extend(self.detect_unused_imports())
        self.candidates.extend(self.detect_unused_functions())
        self.candidates.extend(self.detect_unused_classes())
        self.candidates.extend(self.detect_orphaned_files())
        self.candidates.extend(self.correlate_with_coverage())

        # Sort by confidence and potential impact
        self.candidates.sort(key=lambda x: (
            x.confidence, x.size_impact), reverse=True)

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files_analyzed": len(python_files),
                "total_candidates": len(self.candidates),
                "high_confidence_candidates": len(
                    [c for c in self.candidates if c.confidence > 0.8]
                ),
                "potential_lines_saved": sum(c.size_impact for c in self.candidates),
                "orphaned_files": len(self.dependency_graph.orphaned_files),
            },
            "candidates": [
                asdict(c) for c in self.candidates[:50]
            ],  # Top 50 candidates
            "dependency_graph": {
                "total_nodes": len(self.dependency_graph.nodes),
                "total_edges": sum(
                    len(edges) for edges in self.dependency_graph.edges.values()
                ),
                "entry_points": list(self.dependency_graph.entry_points),
                "orphaned_files": list(self.dependency_graph.orphaned_files),
            },
        }

        self.logger.info(
            f"Analysis complete. Found {len(self.candidates)} dead code candidates"
        )
        return report

    def save_report(
        self, report: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """Save analysis report to file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/dead_code_analysis_{timestamp}.json"

        output_file = Path(self.project_root) / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Report saved to {output_file}")
        return str(output_file)


def main():
    """Main entry point for dead code detection"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Dead Code Detector for AI-KindleMint Engine"
    )
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run analysis without making changes"
    )

    args = parser.parse_args()

    detector = DeadCodeDetector(args.config)
    report = detector.run_analysis()
    output_path = detector.save_report(report, args.output)

    print(f"Dead code analysis complete. Report saved to: {output_path}")
    print(
        f"Found {report['summary']['total_candidates']} dead code candidates")
    print(
        f"Potential lines of code that could be removed: {
            report['summary']['potential_lines_saved']}"
    )


if __name__ == "__main__":
    main()
