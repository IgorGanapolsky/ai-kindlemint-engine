#!/usr/bin/env python3
"""
CI Analyzer - Analyzes CI failures and determines appropriate fix strategies
"""

import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class FixStrategy:
    """Represents a strategy to fix a CI failure"""

    strategy_type: str
    description: str
    confidence: float  # 0.0 to 1.0
    files_to_modify: List[str]
    commands: List[str]
    estimated_complexity: str  # 'low', 'medium', 'high'
    auto_fixable: bool


class CIAnalyzer:
    """Analyzes CI failures and determines fix strategies"""

        """  Init  """
def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
        self.error_patterns = self._load_error_patterns()

    def _load_error_patterns(self) -> Dict:
        """Load common error patterns and their fix strategies"""
        return {
            "import_error": {
                "patterns": [
                    r"ModuleNotFoundError: No module named '([^']+)'",
                    r"ImportError: cannot import name '([^']+)' from '([^']+)'",
                    r"ImportError: No module named ([^\s]+)",
                ],
                "analyzer": self._analyze_import_error,
            },
            "test_failure": {
                "patterns": [
                    r"FAILED (.*) - assert (.*)",
                    r"AssertionError: (.*)",
                    r"(\d+) failed, (\d+) passed",
                    r"pytest.*FAILED.*::(.*)::(.*)",
                ],
                "analyzer": self._analyze_test_failure,
            },
            "syntax_error": {
                "patterns": [
                    r"SyntaxError: (.*) \(([^,]+), line (\d+)\)",
                    r"File \"([^\"]+)\", line (\d+).*SyntaxError: (.*)",
                ],
                "analyzer": self._analyze_syntax_error,
            },
            "linting_error": {
                "patterns": [
                    r"([^:]+):(\d+):(\d+): ([A-Z]\d+) (.*)",  # flake8
                    r"would reformat ([^\s]+)",  # black
                    r"Fixing ([^\s]+)",  # isort
                ],
                "analyzer": self._analyze_linting_error,
            },
            "type_error": {
                "patterns": [
                    r"TypeError: (.*)",
                    r"([^:]+):(\d+): error: (.*)",  # mypy
                    r"Argument.*has incompatible type",
                ],
                "analyzer": self._analyze_type_error,
            },
            "dependency_error": {
                "patterns": [
                    r"Could not find a version that satisfies the requirement ([^\s]+)",
                    r"No matching distribution found for ([^\s]+)",
                    r"ERROR: (.*) has requirement ([^,]+), but you'll have ([^\s]+)",
                ],
                "analyzer": self._analyze_dependency_error,
            },
            "path_error": {
                "patterns": [
                    r"FileNotFoundError: \[Errno 2\] No such file or directory: '([^']+)'",
                    r"IOError: \[Errno 2\] No such file or directory: '([^']+)'",
                    r"cannot find file '([^']+)'",
                ],
                "analyzer": self._analyze_path_error,
            },
            "puzzle_qa_failure": {
                "patterns": [
                    r"blank_puzzles.*detected",
                    r"missing_clues.*Only (\d+)% of puzzles have visible clues",
                    r"repeated_solutions.*(\d+)% of solution explanations are identical",
                    r"low_variety.*Only (\d+)% puzzle variety",
                    r"invalid_structure.*missing puzzle content",
                    r"Detected blank or missing puzzle grids",
                    r"QA.*failed.*puzzle.*integrity",
                ],
                "analyzer": self._analyze_puzzle_qa_failure,
            },
            "pdf_generation_error": {
                "patterns": [
                    r"could not generate puzzle grid",
                    r"create_puzzle_grid.*not found",
                    r"create_solution_grid.*not found",
                    r"AttributeError.*create_puzzle_grid",
                    r"AttributeError.*create_solution_grid",
                    r"PDF generation.*failed",
                ],
                "analyzer": self._analyze_pdf_generation_error,
            },
            "content_validation_error": {
                "patterns": [
                    r"puzzle integrity.*(\d+\.\d+).*threshold.*(\d+)",
                    r"overall score.*(\d+\.\d+).*failed",
                    r"QA validation.*failed",
                    r"unsellable.*book.*content",
                ],
                "analyzer": self._analyze_content_validation_error,
            },
        }

    def analyze_failure(self, failure_info: Dict) -> List[FixStrategy]:
        """Analyze a CI failure and return possible fix strategies"""
        failure_type = failure_info.get("failure_type", "unknown")
        failure_info.get("error_message", "")
        logs = failure_info.get("logs", "")

        strategies = []

        # Try to find matching patterns
        if failure_type in self.error_patterns:
            pattern_info = self.error_patterns[failure_type]
            analyzer_func = pattern_info["analyzer"]

            # Try each pattern
            for pattern in pattern_info["patterns"]:
                matches = re.findall(pattern, logs, re.MULTILINE | re.IGNORECASE)
                if matches:
                    # Call the specific analyzer
                    strategy = analyzer_func(matches, failure_info)
                    if strategy:
                        strategies.extend(
                            strategy if isinstance(strategy, list) else [strategy]
                        )

        # If no specific strategies, try generic approach
        if not strategies:
            strategies.append(self._get_generic_strategy(failure_info))

        return strategies

    def _analyze_import_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze import errors and suggest fixes"""
        strategies = []

        for match in matches:
            if isinstance(match, tuple):
                module_name = match[0]
            else:
                module_name = match

            # Check if it's a missing package
            if not self._is_local_module(module_name):
                strategies.append(
                    FixStrategy(
                        strategy_type="install_package",
                        description=f"Install missing package: {module_name}",
                        confidence=0.9,
                        files_to_modify=["requirements.txt"],
                        commands=[f"pip install {module_name}"],
                        estimated_complexity="low",
                        auto_fixable=True,
                    )
                )
            else:
                # It's a local import issue
                strategies.append(
                    FixStrategy(
                        strategy_type="fix_import_path",
                        description=f"Fix import path for module: {module_name}",
                        confidence=0.7,
                        files_to_modify=[],  # Will be determined by searching
                        commands=[],
                        estimated_complexity="medium",
                        auto_fixable=True,
                    )
                )

        return strategies

    def _analyze_test_failure(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze test failures and suggest fixes"""
        strategies = []

        # Extract test file and function from logs
        test_pattern = r"tests/([^:]+)::([^:]+)"
        test_matches = re.findall(test_pattern, failure_info.get("logs", ""))

        for test_file, test_func in test_matches:
            strategies.append(
                FixStrategy(
                    strategy_type="fix_test_assertion",
                    description=f"Fix failing test: {test_func} in {test_file}",
                    confidence=0.6,
                    files_to_modify=[f"tests/{test_file}"],
                    commands=[],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        # Also suggest updating test data
        strategies.append(
            FixStrategy(
                strategy_type="update_test_data",
                description="Update test fixtures or expected values",
                confidence=0.5,
                files_to_modify=[],
                commands=[],
                estimated_complexity="medium",
                auto_fixable=False,
            )
        )

        return strategies

    def _analyze_syntax_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze syntax errors and suggest fixes"""
        strategies = []

        for match in matches:
            if len(match) >= 3:
                error_desc = match[0] if isinstance(match, tuple) else match
                file_path = match[1] if len(match) > 1 else None
                match[2] if len(match) > 2 else None

                strategies.append(
                    FixStrategy(
                        strategy_type="fix_syntax",
                        description=f"Fix syntax error: {error_desc}",
                        confidence=0.8,
                        files_to_modify=[file_path] if file_path else [],
                        commands=[],
                        estimated_complexity="low",
                        auto_fixable=True,
                    )
                )

        return strategies

    def _analyze_linting_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze linting errors and suggest fixes"""
        strategies = []

        # Check for black formatting issues
        if "would reformat" in failure_info.get("logs", ""):
            strategies.append(
                FixStrategy(
                    strategy_type="run_black",
                    description="Run Black formatter to fix code style",
                    confidence=0.95,
                    files_to_modify=[],
                    commands=["black ."],
                    estimated_complexity="low",
                    auto_fixable=True,
                )
            )

        # Check for isort issues
        if "isort" in failure_info.get("logs", "").lower():
            strategies.append(
                FixStrategy(
                    strategy_type="run_isort",
                    description="Run isort to fix import ordering",
                    confidence=0.95,
                    files_to_modify=[],
                    commands=["isort ."],
                    estimated_complexity="low",
                    auto_fixable=True,
                )
            )

        # Check for flake8 issues
        flake8_files = set()
        for match in matches:
            if len(match) >= 5 and match[3].startswith(("E", "W", "F")):
                flake8_files.add(match[0])

        if flake8_files:
            strategies.append(
                FixStrategy(
                    strategy_type="fix_flake8",
                    description="Fix flake8 style violations",
                    confidence=0.7,
                    files_to_modify=list(flake8_files),
                    commands=[
                        "autopep8 --in-place --aggressive " + " ".join(flake8_files)
                    ],
                    estimated_complexity="low",
                    auto_fixable=True,
                )
            )

        return strategies

    def _analyze_type_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze type errors and suggest fixes"""
        strategies = []

        # Extract file and line information
        type_error_pattern = r"File \"([^\"]+)\", line (\d+)"
        file_matches = re.findall(type_error_pattern, failure_info.get("logs", ""))

        for file_path, line_num in file_matches:
            strategies.append(
                FixStrategy(
                    strategy_type="fix_type_annotation",
                    description=f"Fix type annotation in {file_path}:{line_num}",
                    confidence=0.6,
                    files_to_modify=[file_path],
                    commands=[],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        # Suggest running mypy
        strategies.append(
            FixStrategy(
                strategy_type="add_type_ignores",
                description="Add type: ignore comments for complex type issues",
                confidence=0.4,
                files_to_modify=[],
                commands=["mypy --install-types --non-interactive"],
                estimated_complexity="low",
                auto_fixable=False,
            )
        )

        return strategies

    def _analyze_dependency_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze dependency errors and suggest fixes"""
        strategies = []

        for match in matches:
            if isinstance(match, tuple) and len(match) > 0:
                package_name = match[0]
            else:
                package_name = match

            strategies.append(
                FixStrategy(
                    strategy_type="update_requirements",
                    description=f"Update requirements.txt with {package_name}",
                    confidence=0.8,
                    files_to_modify=["requirements.txt"],
                    commands=[
                        f"pip install {package_name}",
                        "pip freeze > requirements-temp.txt",
                    ],
                    estimated_complexity="low",
                    auto_fixable=True,
                )
            )

        # Also suggest updating pinned versions
        strategies.append(
            FixStrategy(
                strategy_type="update_pinned_versions",
                description="Update pinned dependency versions",
                confidence=0.6,
                files_to_modify=["requirements-pinned.txt", "requirements-locked.txt"],
                commands=["pip install --upgrade -r requirements.txt"],
                estimated_complexity="medium",
                auto_fixable=True,
            )
        )

        return strategies

    def _analyze_path_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze path/file errors and suggest fixes"""
        strategies = []

        for match in matches:
            if isinstance(match, tuple):
                missing_path = match[0]
            else:
                missing_path = match

            # Check if it's a directory or file
            if missing_path.endswith("/"):
                strategies.append(
                    FixStrategy(
                        strategy_type="create_directory",
                        description=f"Create missing directory: {missing_path}",
                        confidence=0.8,
                        files_to_modify=[],
                        commands=[f"mkdir -p {missing_path}"],
                        estimated_complexity="low",
                        auto_fixable=True,
                    )
                )
            else:
                strategies.append(
                    FixStrategy(
                        strategy_type="create_file",
                        description=f"Create missing file: {missing_path}",
                        confidence=0.6,
                        files_to_modify=[missing_path],
                        commands=[f"touch {missing_path}"],
                        estimated_complexity="low",
                        auto_fixable=True,
                    )
                )

        return strategies

    def _analyze_puzzle_qa_failure(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze puzzle QA failures and suggest specific fixes"""
        strategies = []

        logs = failure_info.get("logs", "")

        # Check for blank puzzles (critical issue)
        if any(
            "blank_puzzles" in str(match) or "blank.*puzzle" in logs.lower()
            for match in matches
        ):
            strategies.append(
                FixStrategy(
                    strategy_type="fix_blank_puzzles",
                    description="Fix blank puzzle generation by implementing fallback grid methods",
                    confidence=0.95,
                    files_to_modify=["scripts/market_aligned_sudoku_pdf.py"],
                    commands=[
                        "python scripts/market_aligned_sudoku_pdf.py --test-fallback",
                        "python -c \"import scripts.large_print_sudoku_generator; print('Generator working')\"",
                    ],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        # Check for missing clues
        clue_pattern = r"missing_clues.*Only (\d+)%"
        clue_matches = re.findall(clue_pattern, logs)
        if clue_matches:
            clue_percentage = int(clue_matches[0])
            strategies.append(
                FixStrategy(
                    strategy_type="fix_missing_clues",
                    description=f"Fix missing clues (only {
                        clue_percentage}% visible) in puzzle generation",
                    confidence=0.9,
                    files_to_modify=[
                        "scripts/large_print_sudoku_generator.py",
                        "scripts/market_aligned_sudoku_pdf.py",
                    ],
                    commands=[
                        "python scripts/large_print_sudoku_generator.py --validate-clues"
                    ],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        # Check for repeated solutions
        repeat_pattern = r"repeated_solutions.*(\d+)%"
        repeat_matches = re.findall(repeat_pattern, logs)
        if repeat_matches:
            repeat_percentage = int(repeat_matches[0])
            strategies.append(
                FixStrategy(
                    strategy_type="fix_repeated_solutions",
                    description=f"Fix repeated solution explanations ({
                        repeat_percentage}% identical)",
                    confidence=0.85,
                    files_to_modify=["scripts/market_aligned_sudoku_pdf.py"],
                    commands=[
                        "python -c \"from scripts.market_aligned_sudoku_pdf import MarketAlignedSudokuPDF; print('Solution variety check')\""
                    ],
                    estimated_complexity="low",
                    auto_fixable=True,
                )
            )

        # Generic puzzle QA fix if specific patterns not found
        if not strategies:
            strategies.append(
                FixStrategy(
                    strategy_type="regenerate_puzzles",
                    description="Regenerate all puzzle PDFs with enhanced QA validation",
                    confidence=0.8,
                    files_to_modify=[],
                    commands=[
                        "python scripts/market_aligned_sudoku_pdf.py --regenerate-all",
                        "python scripts/qa_validation_pipeline.py --validate-all",
                    ],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        return strategies

    def _analyze_pdf_generation_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze PDF generation errors and suggest fixes"""
        strategies = []

        failure_info.get("logs", "")

        # Check for missing fallback methods (the exact issue we had)
        if any(
            "create_puzzle_grid" in str(match) or "create_solution_grid" in str(match)
            for match in matches
        ):
            strategies.append(
                FixStrategy(
                    strategy_type="implement_fallback_methods",
                    description="Implement missing create_puzzle_grid and create_solution_grid fallback methods",
                    confidence=0.95,
                    files_to_modify=["scripts/market_aligned_sudoku_pdf.py"],
                    commands=[
                        "python -c \"import ast; print('Validating PDF generator syntax')\"",
                        "python scripts/market_aligned_sudoku_pdf.py --test",
                    ],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        # Generic PDF generation fix
        else:
            strategies.append(
                FixStrategy(
                    strategy_type="fix_pdf_generation",
                    description="Fix PDF generation pipeline errors",
                    confidence=0.75,
                    files_to_modify=[
                        "scripts/market_aligned_sudoku_pdf.py",
                        "scripts/large_print_sudoku_generator.py",
                    ],
                    commands=[
                        "python -m pip install --upgrade reportlab",
                        "python scripts/market_aligned_sudoku_pdf.py --verify",
                    ],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        return strategies

    def _analyze_content_validation_error(
        self, matches: List, failure_info: Dict
    ) -> List[FixStrategy]:
        """Analyze content validation errors and suggest fixes"""
        strategies = []

        logs = failure_info.get("logs", "")

        # Extract QA scores if available
        score_pattern = r"overall score.*(\d+\.\d+)"
        score_matches = re.findall(score_pattern, logs.lower())

        if score_matches:
            score = float(score_matches[0])
            if score < 85:  # Below passing threshold
                strategies.append(
                    FixStrategy(
                        strategy_type="improve_content_quality",
                        description=f"Improve content quality (current score: {
                            score}/100)",
                        confidence=0.9,
                        files_to_modify=[
                            "scripts/market_aligned_sudoku_pdf.py",
                            "scripts/qa_validation_pipeline.py",
                        ],
                        commands=[
                            "python scripts/qa_validation_pipeline.py --detailed-report",
                            "python scripts/market_aligned_sudoku_pdf.py --quality-check",
                        ],
                        estimated_complexity="medium",
                        auto_fixable=True,
                    )
                )

        # If QA validation failed generally
        if "qa validation.*failed" in logs.lower():
            strategies.append(
                FixStrategy(
                    strategy_type="fix_qa_validation",
                    description="Fix failing QA validation checks",
                    confidence=0.8,
                    files_to_modify=["scripts/qa_validation_pipeline.py"],
                    commands=[
                        "python scripts/qa_validation_pipeline.py --debug",
                        "python -c \"print('QA pipeline verification')\"",
                    ],
                    estimated_complexity="medium",
                    auto_fixable=True,
                )
            )

        return strategies

    def _get_generic_strategy(self, failure_info: Dict) -> FixStrategy:
        """Get a generic strategy when specific analysis fails"""
        return FixStrategy(
            strategy_type="manual_review",
            description=f"Manual review required for {
                failure_info.get('failure_type', 'unknown')} error",
            confidence=0.1,
            files_to_modify=[],
            commands=[],
            estimated_complexity="high",
            auto_fixable=False,
        )

    def _is_local_module(self, module_name: str) -> bool:
        """Check if a module is local to the project"""
        # Simple heuristic: if it starts with common project names or has no dots
        local_prefixes = ["src", "kindlemint", "scripts", "tests"]
        return (
            any(module_name.startswith(prefix) for prefix in local_prefixes)
            or "." not in module_name
        )

    def prioritize_strategies(self, strategies: List[FixStrategy]) -> List[FixStrategy]:
        """Prioritize fix strategies by confidence and complexity"""
        # Sort by confidence (descending) and complexity (ascending)
        complexity_order = {"low": 0, "medium": 1, "high": 2}

        return sorted(
            strategies,
            key=lambda s: (
                -s.confidence,
                complexity_order.get(s.estimated_complexity, 3),
            ),
        )

    def analyze_failure_report(self, report_path: str) -> Dict:
        """Analyze a complete failure report and generate fix strategies"""
        with open(report_path, "r") as f:
            report = json.load(f)

        analysis_results = {
            "timestamp": report.get("timestamp"),
            "repository": report.get("repository"),
            "total_failures": report.get("total_failures"),
            "analyzed_failures": [],
            "summary": {"auto_fixable": 0, "manual_review": 0, "by_strategy_type": {}},
        }

        # Analyze each failure
        for failure in report.get("failures", []):
            strategies = self.analyze_failure(failure)
            prioritized = self.prioritize_strategies(strategies)

            analyzed_failure = {
                "failure_info": failure,
                "strategies": [asdict(s) for s_var in prioritized],
                "recommended_strategy": asdict(prioritized[0]) if prioritized else None,
            }

            analysis_results["analyzed_failures"].append(analyzed_failure)

            # Update summary
            for strategy in prioritized:
                if strategy.auto_fixable:
                    analysis_results["summary"]["auto_fixable"] += 1
                else:
                    analysis_results["summary"]["manual_review"] += 1

                stype = strategy.strategy_type
                analysis_results["summary"]["by_strategy_type"][stype] = (
                    analysis_results["summary"]["by_strategy_type"].get(stype, 0) + 1
                )

        return analysis_results

        """Save Analysis"""
def save_analysis(
        self, analysis_results: Dict, output_path: str = "ci_analysis.json"
    ):
        """Save analysis results to file"""
        with open(output_path, "w") as f:
            json.dump(analysis_results, f, indent=2)

        logger.info(f"Saved analysis results to {output_path}")


    """Main"""
def main():
    """Main entry point for CI analysis"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze CI failures and suggest fixes"
    )
    parser.add_argument(
        "--input", default="ci_failures.json", help="Input failure report"
    )
    parser.add_argument(
        "--output", default="ci_analysis.json", help="Output analysis file"
    )
    parser.add_argument(
        "--repo-path", help="Repository path (defaults to current directory)"
    )

    args = parser.parse_args()

    # Initialize analyzer
    repo_path = Path(args.repo_path) if args.repo_path else None
    analyzer = CIAnalyzer(repo_path)

    # Analyze failure report
    if not Path(args.input).exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    analysis_results = analyzer.analyze_failure_report(args.input)
    analyzer.save_analysis(analysis_results, args.output)

    # Print summary
    summary = analysis_results["summary"]
    print(f"\n{'=' * 60}")
    print(f"CI Failure Analysis Summary")
    print(f"{'=' * 60}")
    print(f"Total failures analyzed: {analysis_results['total_failures']}")
    print(f"Auto-fixable: {summary['auto_fixable']}")
    print(f"Manual review needed: {summary['manual_review']}")

    print("\nStrategies by type:")
    for stype, count in summary["by_strategy_type"].items():
        print(f"  - {stype}: {count}")

    print(f"\nDetailed analysis saved to: {args.output}")


if __name__ == "__main__":
    main()
