#!/usr/bin/env python3
"""
Architecture Analysis Agent for AI-KindleMint Engine

This module provides comprehensive architecture analysis capabilities including:
- Dependency visualization and architecture diagrams
- Anti-pattern detection (circular dependencies, tight coupling, code smells)
- Modularity assessment and cohesion analysis
- Performance hotspot identification with Sentry correlation
- Design pattern compliance verification
- Technical debt quantification and tracking
"""

import ast
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import yaml


@dataclass
class ArchitectureMetric:
    """Represents an architecture quality metric"""

    name: str
    value: float
    threshold: float
    status: str  # 'good', 'warning', 'critical'
    description: str
    suggestions: List[str]


@dataclass
class AntiPattern:
    """Represents a detected anti-pattern"""

    pattern_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    location: str
    description: str
    impact: str
    remediation_steps: List[str]
    affected_files: List[str]


@dataclass
class DesignPatternViolation:
    """Represents a design pattern violation"""

    pattern_name: str
    violation_type: str
    file_path: str
    line_number: int
    description: str
    suggested_fix: str


@dataclass
class ModuleAnalysis:
    """Represents analysis of a single module"""

    module_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    cohesion_score: float
    coupling_score: float
    dependencies_in: List[str]
    dependencies_out: List[str]
    public_interface_size: int
    test_coverage: float


class ComplexityCalculator(ast.NodeVisitor):
    """Calculate cyclomatic complexity using AST"""

        """  Init  """
def __init__(self):
        self.complexity = 1  # Base complexity

        """Visit If"""
def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

        """Visit While"""
def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

        """Visit For"""
def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

        """Visit Excepthandler"""
def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

        """Visit With"""
def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

        """Visit Functiondef"""
def visit_FunctionDef(self, node):
        # Don't add complexity for function definitions themselves
        self.generic_visit(node)

        """Visit Asyncfunctiondef"""
def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)


class CohesionCalculator(ast.NodeVisitor):
    """Calculate module cohesion using LCOM metric"""

        """  Init  """
def __init__(self):
        self.methods = {}
        self.instance_variables = set()
        self.current_method = None

        """Visit Functiondef"""
def visit_FunctionDef(self, node):
        self.current_method = node.name
        self.methods[node.name] = set()
        self.generic_visit(node)
        self.current_method = None

        """Visit Attribute"""
def visit_Attribute(self, node):
        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and self.current_method
        ):
            self.instance_variables.add(node.attr)
            self.methods[self.current_method].add(node.attr)
        self.generic_visit(node)

    def calculate_lcom(self) -> float:
        """Calculate Lack of Cohesion of Methods"""
        if len(self.methods) <= 1:
            return 0.0

        # Count pairs of methods that don't share instance variables
        total_pairs = 0
        non_sharing_pairs = 0

        method_list = list(self.methods.keys())
        for i in range(len(method_list)):
            for j in range(i + 1, len(method_list)):
                total_pairs += 1
                method1_vars = self.methods[method_list[i]]
                method2_vars = self.methods[method_list[j]]

                if not method1_vars.intersection(method2_vars):
                    non_sharing_pairs += 1

        return non_sharing_pairs / total_pairs if total_pairs > 0 else 0.0


class ArchitectureAnalyzer:
    """Main architecture analysis engine"""

        """  Init  """
def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.project_root = Path(self.config.get("project_root", os.getcwd()))

        # Analysis results
        self.dependency_graph = nx.DiGraph()
        self.module_analyses: Dict[str, ModuleAnalysis] = {}
        self.metrics: List[ArchitectureMetric] = []
        self.anti_patterns: List[AntiPattern] = []
        self.pattern_violations: List[DesignPatternViolation] = []

        # Thresholds from config
        self.complexity_threshold = self.config.get("complexity_threshold", 10)
        self.coupling_threshold = self.config.get("coupling_threshold", 7)
        self.cohesion_threshold = self.config.get("cohesion_threshold", 0.8)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = Path(__file__).parent / "config" / "cleanup_config.yaml"

        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "project_root": os.getcwd(),
            "complexity_threshold": 10,
            "coupling_threshold": 7,
            "cohesion_threshold": 0.8,
            "exclude_patterns": [
                "*/venv/*",
                "*/node_modules/*",
                "*/.git/*",
                "*/__pycache__/*",
            ],
            "visualization": {
                "output_dir": "reports/architecture_diagrams",
                "formats": ["png", "svg"],
                "dpi": 300,
            },
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("architecture_analyzer")
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
        exclude_patterns = self.config.get("exclude_patterns", [])

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [
                d
                for d_var in dirs
                if not any(Path(root, d).match(pattern) for pattern in exclude_patterns)
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    if not any(
                        file_path.match(pattern) for pattern in exclude_patterns
                    ):
                        python_files.append(file_path)

        return python_files

    def analyze_module(self, file_path: Path) -> ModuleAnalysis:
        """Analyze a single Python module"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            # Calculate metrics
            lines_of_code = len([line for line in content.split("\n") if line.strip()])

            complexity_calc = ComplexityCalculator()
            complexity_calc.visit(tree)
            cyclomatic_complexity = complexity_calc.complexity

            cohesion_calc = CohesionCalculator()
            cohesion_calc.visit(tree)
            cohesion_score = 1.0 - cohesion_calc.calculate_lcom()  # Higher is better

            # Analyze dependencies
            dependencies = self._extract_dependencies(tree, file_path)
            dependencies_in = self._find_incoming_dependencies(file_path)

            # Calculate coupling (number of dependencies)
            coupling_score = len(dependencies)

            # Analyze public interface
            public_interface_size = self._count_public_interface(tree)

            # Get test coverage (placeholder - would integrate with coverage tools)
            test_coverage = self._get_test_coverage(file_path)

            return ModuleAnalysis(
                module_path=str(file_path),
                lines_of_code=lines_of_code,
                cyclomatic_complexity=cyclomatic_complexity,
                cohesion_score=cohesion_score,
                coupling_score=coupling_score,
                dependencies_in=dependencies_in,
                dependencies_out=dependencies,
                public_interface_size=public_interface_size,
                test_coverage=test_coverage,
            )

        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {e}")
            return ModuleAnalysis(
                module_path=str(file_path),
                lines_of_code=0,
                cyclomatic_complexity=0,
                cohesion_score=1.0,
                coupling_score=0,
                dependencies_in=[],
                dependencies_out=[],
                public_interface_size=0,
                test_coverage=0.0,
            )

    def _extract_dependencies(self, tree: ast.AST, file_path: Path) -> List[str]:
        """Extract dependencies from AST"""
        dependencies = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)

        return dependencies

    def _find_incoming_dependencies(self, file_path: Path) -> List[str]:
        """Find modules that depend on this file"""
        # This would be populated during full project analysis
        return []

    def _count_public_interface(self, tree: ast.AST) -> int:
        """Count public functions and classes"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    count += 1
        return count

    def _get_test_coverage(self, file_path: Path) -> float:
        """Get test coverage for the file (placeholder)"""
        # This would integrate with coverage.py or similar tools
        return 0.0

    def build_dependency_graph(self) -> nx.DiGraph:
        """Build dependency graph from all modules"""
        self.logger.info("Building dependency graph...")

        for module_path, analysis in self.module_analyses.items():
            # Add node
            self.dependency_graph.add_node(module_path, **asdict(analysis))

            # Add edges for dependencies
            for dep in analysis.dependencies_out:
                # Try to resolve dependency to actual file path
                resolved_path = self._resolve_dependency(dep, module_path)
                if resolved_path:
                    self.dependency_graph.add_edge(module_path, resolved_path)

        return self.dependency_graph

    def _resolve_dependency(self, dep_name: str, current_file: str) -> Optional[str]:
        """Resolve dependency name to file path"""
        # Simplified resolution - could be enhanced
        for module_path in self.module_analyses:
            if dep_name in module_path or Path(module_path).stem == dep_name:
                return module_path
        return None

    def detect_circular_dependencies(self) -> List[AntiPattern]:
        """Detect circular dependencies in the codebase"""
        patterns = []

        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))

            for cycle in cycles:
                if len(cycle) > 1:  # Skip self-loops
                    cycle_str = " -> ".join([Path(f).name f_varor f_var in cycle])

                    pattern = AntiPattern(
                        pattern_type="circular_dependency",
                        severity="high" if len(cycle) > 3 else "medium",
                        location=cycle_str,
                        description=f"Circular dependency detected: {cycle_str}",
                        impact="Increases coupling, makes code harder to test and maintain",
                        remediation_steps=[
                            "Extract common functionality to a separate module",
                            "Use dependency injection to break the cycle",
                            "Consider using interfaces/protocols",
                            "Refactor to use a mediator pattern",
                        ],
                        affected_files=cycle,
                    )
                    patterns.append(pattern)

        except nx.NetworkXError:
            pass  # No cycles found

        return patterns

    def detect_tight_coupling(self) -> List[AntiPattern]:
        """Detect tightly coupled modules"""
        patterns = []

        for module_path, analysis in self.module_analyses.items():
            if analysis.coupling_score > self.coupling_threshold:
                pattern = AntiPattern(
                    pattern_type="tight_coupling",
                    severity="medium" if analysis.coupling_score < 15 else "high",
                    location=Path(module_path).name,
                    description=f"Module has {
                        analysis.coupling_score} dependencies (threshold: {
                        self.coupling_threshold})",
                    impact="High coupling makes modules difficult to test, modify, and reuse",
                    remediation_steps=[
                        "Extract common dependencies to a service layer",
                        "Use dependency injection",
                        "Apply the Single Responsibility Principle",
                        "Consider breaking the module into smaller, focused modules",
                    ],
                    affected_files=[module_path],
                )
                patterns.append(pattern)

        return patterns

    def detect_low_cohesion(self) -> List[AntiPattern]:
        """Detect modules with low cohesion"""
        patterns = []

        for module_path, analysis in self.module_analyses.items():
            if analysis.cohesion_score < self.cohesion_threshold:
                pattern = AntiPattern(
                    pattern_type="low_cohesion",
                    severity="medium",
                    location=Path(module_path).name,
                    description=f"Module has low cohesion score: {
                        analysis.cohesion_score:.2f} (threshold: {
                        self.cohesion_threshold})",
                    impact="Low cohesion indicates module does not have a single, well-defined purpose",
                    remediation_steps=[
                        "Split module into smaller, more focused modules",
                        "Group related functionality together",
                        "Apply the Single Responsibility Principle",
                        "Extract unrelated functionality to appropriate modules",
                    ],
                    affected_files=[module_path],
                )
                patterns.append(pattern)

        return patterns

    def detect_god_objects(self) -> List[AntiPattern]:
        """Detect god objects (classes/modules that do too much)"""
        patterns = []

        # Large modules
        loc_threshold = self.config.get("god_object_loc_threshold", 500)
        complexity_threshold = self.config.get("god_object_complexity_threshold", 50)

        for module_path, analysis in self.module_analyses.items():
            if (
                analysis.lines_of_code > loc_threshold
                or analysis.cyclomatic_complexity > complexity_threshold
            ):

                pattern = AntiPattern(
                    pattern_type="god_object",
                    severity="high",
                    location=Path(module_path).name,
                    description=f"Large module: {
                        analysis.lines_of_code} LOC, complexity: {
                        analysis.cyclomatic_complexity}",
                    impact="God objects are difficult to understand, test, and maintain",
                    remediation_steps=[
                        "Break module into smaller, focused modules",
                        "Extract classes and functions to appropriate modules",
                        "Apply the Single Responsibility Principle",
                        "Use composition over inheritance",
                    ],
                    affected_files=[module_path],
                )
                patterns.append(pattern)

        return patterns

    def detect_feature_envy(self) -> List[AntiPattern]:
        """Detect feature envy anti-pattern"""
        patterns = []

        # This is a simplified detection - would need more sophisticated analysis
        for module_path, analysis in self.module_analyses.items():
            # If a module depends on many other modules but has few incoming
            # dependencies
            if (
                len(analysis.dependencies_out) > 5
                and len(analysis.dependencies_in) < 2
                and analysis.public_interface_size < 3
            ):

                pattern = AntiPattern(
                    pattern_type="feature_envy",
                    severity="medium",
                    location=Path(module_path).name,
                    description="Module uses functionality from many other modules but offers little in return",
                    impact="Indicates module might be in wrong place or have responsibilities that belong elsewhere",
                    remediation_steps=[
                        "Move functionality closer to the data it uses",
                        "Consider merging with frequently used modules",
                        "Extract common functionality to shared utilities",
                    ],
                    affected_files=[module_path],
                )
                patterns.append(pattern)

        return patterns

    def calculate_architecture_metrics(self) -> List[ArchitectureMetric]:
        """Calculate overall architecture metrics"""
        metrics = []

        if not self.module_analyses:
            return metrics

        # Overall complexity
        avg_complexity = np.mean(
            [a.cyclomatic_complexity for a_var in self.module_analyses.values()]
        )
        max_complexity = max(
            [a.cyclomatic_complexity for a_var in self.module_analyses.values()]
        )

        complexity_metric = ArchitectureMetric(
            name="Average Cyclomatic Complexity",
            value=avg_complexity,
            threshold=self.complexity_threshold,
            status="good" if avg_complexity < self.complexity_threshold else "warning",
            description="Average cyclomatic complexity across all modules",
            suggestions=["Refactor complex methods", "Break down large functions"],
        )
        metrics.append(complexity_metric)

        # Overall coupling
        avg_coupling = np.mean(
            [a.coupling_score for a_var in self.module_analyses.values()]
        )

        coupling_metric = ArchitectureMetric(
            name="Average Coupling",
            value=avg_coupling,
            threshold=self.coupling_threshold,
            status="good" if avg_coupling < self.coupling_threshold else "warning",
            description="Average number of dependencies per module",
            suggestions=["Reduce dependencies", "Use dependency injection"],
        )
        metrics.append(coupling_metric)

        # Overall cohesion
        avg_cohesion = np.mean(
            [a.cohesion_score for a_var in self.module_analyses.values()]
        )

        cohesion_metric = ArchitectureMetric(
            name="Average Cohesion",
            value=avg_cohesion,
            threshold=self.cohesion_threshold,
            status="good" if avg_cohesion > self.cohesion_threshold else "warning",
            description="Average cohesion score across all modules",
            suggestions=[
                "Group related functionality",
                "Apply Single Responsibility Principle",
            ],
        )
        metrics.append(cohesion_metric)

        # Dependency graph metrics
        if self.dependency_graph.number_of_nodes() > 0:
            # Graph density
            density = nx.density(self.dependency_graph)
            density_metric = ArchitectureMetric(
                name="Dependency Graph Density",
                value=density,
                threshold=0.3,
                status="good" if density < 0.3 else "warning",
                description="Density of the dependency graph (0=sparse, 1=complete)",
                suggestions=["Reduce unnecessary dependencies", "Modularize better"],
            )
            metrics.append(density_metric)

            # Centrality analysis
            centrality = nx.degree_centrality(self.dependency_graph)
            max_centrality = max(centrality.values()) if centrality else 0

            centrality_metric = ArchitectureMetric(
                name="Maximum Node Centrality",
                value=max_centrality,
                threshold=0.5,
                status="good" if max_centrality < 0.5 else "warning",
                description="Highest centrality score (indicates potential bottlenecks)",
                suggestions=[
                    "Distribute responsibilities",
                    "Avoid central god objects",
                ],
            )
            metrics.append(centrality_metric)

        return metrics

    def generate_architecture_visualization(
        self, output_dir: Optional[str] = None
    ) -> List[str]:
        """Generate architecture visualization diagrams"""
        if not output_dir:
            output_dir = self.config.get("visualization", {}).get(
                "output_dir", "reports/architecture_diagrams"
            )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files = []

        try:
            # Dependency graph visualization
            plt.figure(figsize=(16, 12))

            if self.dependency_graph.number_of_nodes() > 0:
                # Use a layout algorithm
                if self.dependency_graph.number_of_nodes() < 50:
                    pos = nx.spring_layout(self.dependency_graph, k=3, iterations=50)
                else:
                    pos = nx.random_layout(self.dependency_graph)

                # Draw the graph
                nx.draw(
                    self.dependency_graph,
                    pos,
                    with_labels=True,
                    labels={
                        node: Path(node).stem for node in self.dependency_graph.nodes()
                    },
                    node_color="lightblue",
                    node_size=500,
                    font_size=8,
                    font_weight="bold",
                    arrows=True,
                    edge_color="gray",
                    arrowsize=20,
                )

                plt.title("Module Dependency Graph", fontsize=16, fontweight="bold")
                plt.tight_layout()

                # Save in multiple formats
                for fmt in self.config.get("visualization", {}).get("formats", ["png"]):
                    file_path = output_path / f"dependency_graph.{fmt}"
                    plt.savefig(
                        file_path,
                        dpi=self.config.get("visualization", {}).get("dpi", 300),
                    )
                    generated_files.append(str(file_path))

            plt.close()

            # Complexity heatmap
            if self.module_analyses:
                plt.figure(figsize=(12, 8))

                modules = list(self.module_analyses.keys())
                complexities = [
                    self.module_analyses[m].cyclomatic_complexity for m_var in modules
                ]
                couplings = [self.module_analyses[m].coupling_score for m_var in modules]

                # Create scatter plot
                plt.scatter(complexities, couplings, alpha=0.6, s=100)

                # Add labels for high-complexity modules
                for i, module in enumerate(modules):
                    if (
                        complexities[i] > self.complexity_threshold
                        or couplings[i] > self.coupling_threshold
                    ):
                        plt.annotate(
                            Path(module).stem,
                            (complexities[i], couplings[i]),
                            fontsize=8,
                            ha="left",
                        )

                plt.xlabel("Cyclomatic Complexity")
                plt.ylabel("Coupling Score")
                plt.title("Module Complexity vs Coupling")
                plt.axvline(
                    x=self.complexity_threshold,
                    color="r",
                    linestyle="--",
                    alpha=0.7,
                    label="Complexity Threshold",
                )
                plt.axhline(
                    y=self.coupling_threshold,
                    color="r",
                    linestyle="--",
                    alpha=0.7,
                    label="Coupling Threshold",
                )
                plt.legend()
                plt.grid(True, alpha=0.3)

                for fmt in self.config.get("visualization", {}).get("formats", ["png"]):
                    file_path = output_path / f"complexity_coupling.{fmt}"
                    plt.savefig(
                        file_path,
                        dpi=self.config.get("visualization", {}).get("dpi", 300),
                    )
                    generated_files.append(str(file_path))

                plt.close()

        except Exception as e:
            self.logger.warning(f"Failed to generate visualizations: {e}")

        return generated_files

    def run_analysis(self) -> Dict[str, Any]:
        """Run complete architecture analysis"""
        self.logger.info("Starting architecture analysis...")

        # Find and analyze all Python files
        python_files = self.find_python_files()
        self.logger.info(f"Found {len(python_files)} Python files")

        # Analyze each module
        for file_path in python_files:
            self.module_analyses[str(file_path)] = self.analyze_module(file_path)

        # Build dependency graph
        self.dependency_graph = self.build_dependency_graph()

        # Calculate metrics
        self.metrics = self.calculate_architecture_metrics()

        # Detect anti-patterns
        self.anti_patterns = []
        self.anti_patterns.extend(self.detect_circular_dependencies())
        self.anti_patterns.extend(self.detect_tight_coupling())
        self.anti_patterns.extend(self.detect_low_cohesion())
        self.anti_patterns.extend(self.detect_god_objects())
        self.anti_patterns.extend(self.detect_feature_envy())

        # Generate visualizations
        visualization_files = self.generate_architecture_visualization()

        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_modules": len(self.module_analyses),
                "total_dependencies": self.dependency_graph.number_of_edges(),
                "anti_patterns_found": len(self.anti_patterns),
                "critical_issues": len(
                    [ap for ap in self.anti_patterns if ap.severity == "critical"]
                ),
                "high_issues": len(
                    [ap for ap in self.anti_patterns if ap.severity == "high"]
                ),
                "medium_issues": len(
                    [ap for ap in self.anti_patterns if ap.severity == "medium"]
                ),
                "visualization_files": visualization_files,
            },
            "metrics": [asdict(m) for m_var in self.metrics],
            "anti_patterns": [asdict(ap) for ap in self.anti_patterns],
            "module_analyses": {
                path: asdict(analysis)
                for path, analysis in self.module_analyses.items()
            },
            "dependency_graph": {
                "nodes": list(self.dependency_graph.nodes()),
                "edges": list(self.dependency_graph.edges()),
            },
        }

        self.logger.info(
            f"Architecture analysis complete. Found {
                len(self.anti_patterns)} anti-patterns"
        )
        return report

    def save_report(
        self, report: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """Save analysis report to file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/architecture_analysis_{timestamp}.json"

        output_file = Path(self.project_root) / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Report saved to {output_file}")
        return str(output_file)


    """Main"""
def main():
    """Main entry point for architecture analysis"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Architecture Analyzer for AI-KindleMint Engine"
    )
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument(
        "--visualize", action="store_true", help="Generate visualization diagrams"
    )

    args = parser.parse_args()

    analyzer = ArchitectureAnalyzer(args.config)
    report = analyzer.run_analysis()
    output_path = analyzer.save_report(report, args.output)

    print(f"Architecture analysis complete. Report saved to: {output_path}")
    print(f"Found {report['summary']['anti_patterns_found']} anti-patterns")
    print(f"Critical issues: {report['summary']['critical_issues']}")
    print(f"High priority issues: {report['summary']['high_issues']}")


if __name__ == "__main__":
    main()
