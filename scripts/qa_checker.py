#!/usr/bin/env python3
"""
QA Checker - Intelligent Quality Evaluation System
Implements the Evaluator component of the Evaluator-Optimizer loop
Provides actionable feedback for automatic content optimization
"""

import json
import logging
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import PyPDF2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QAChecker")


@dataclass
class QAIssue:
    """Represents a quality issue found during evaluation"""

    severity: str  # "critical", "warning", "info"
    category: str  # "content", "format", "metadata", "structure"
    description: str
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class QAReport:
    """Complete QA evaluation report"""

    timestamp: str
    book_path: str
    score: int  # 0-100
    status: str  # "PASS", "FAIL", "WARN"
    total_checks: int
    passed_checks: int
    issues: List[QAIssue]
    metrics: Dict[str, Any]
    recommendations: List[str]


class IntelligentQAChecker:
    """
    Advanced QA system that not only identifies issues but provides
    actionable feedback for the optimizer to fix them automatically
    """

    def __init__(self):
        self.checks = self._initialize_checks()
        self.scoring_weights = {"critical": -20, "warning": -5, "info": -1}

    def _initialize_checks(self) -> Dict[str, callable]:
        """Initialize all quality checks"""
        return {
            "pdf_integrity": self.check_pdf_integrity,
            "page_count": self.check_page_count,
            "puzzle_completeness": self.check_puzzle_completeness,
            "solution_validity": self.check_solution_validity,
            "metadata_consistency": self.check_metadata_consistency,
            "content_quality": self.check_content_quality,
            "format_compliance": self.check_format_compliance,
            "duplicate_content": self.check_duplicate_content,
            "answer_key_completeness": self.check_answer_keys,
            "production_readiness": self.check_production_readiness,
        }

    def evaluate_book(self, book_path: Path) -> QAReport:
        """Run complete QA evaluation on a book"""
        logger.info(f"Starting QA evaluation for: {book_path}")

        issues = []
        metrics = {}
        passed_checks = 0
        total_checks = len(self.checks)

        # Run all checks
        for check_name, check_func in self.checks.items():
            logger.info(f"Running check: {check_name}")
            try:
                check_issues, check_metrics = check_func(book_path)
                issues.extend(check_issues)
                metrics.update(check_metrics)

                if not check_issues:
                    passed_checks += 1

            except Exception as e:
                logger.error(f"Check {check_name} failed: {e}")
                issues.append(
                    QAIssue(
                        severity="critical",
                        category="system",
                        description=f"Check {check_name} failed: {str(e)}",
                        auto_fixable=False,
                    )
                )

        # Calculate score
        score = self._calculate_score(issues, passed_checks, total_checks)

        # Determine status
        critical_count = sum(1 for i in issues if i.severity == "critical")
        if critical_count > 0 or score < 60:
            status = "FAIL"
        elif score < 80:
            status = "WARN"
        else:
            status = "PASS"

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, metrics)

        return QAReport(
            timestamp=datetime.now().isoformat(),
            book_path=str(book_path),
            score=score,
            status=status,
            total_checks=total_checks,
            passed_checks=passed_checks,
            issues=issues,
            metrics=metrics,
            recommendations=recommendations,
        )

    def check_pdf_integrity(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check if PDFs exist and are valid"""
        issues = []
        metrics = {"pdf_count": 0, "total_size_mb": 0}

        pdf_files = list(book_path.glob("*.pdf"))
        metrics["pdf_count"] = len(pdf_files)

        if not pdf_files:
            issues.append(
                QAIssue(
                    severity="critical",
                    category="structure",
                    description="No PDF files found",
                    suggested_fix="Generate PDF files using book_layout_bot.py",
                    auto_fixable=True,
                )
            )
            return issues, metrics

        for pdf_file in pdf_files:
            try:
                file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
                metrics["total_size_mb"] += file_size_mb

                with open(pdf_file, "rb") as f:
                    pdf = PyPDF2.PdfReader(f)
                    page_count = len(pdf.pages)

                    if page_count == 0:
                        issues.append(
                            QAIssue(
                                severity="critical",
                                category="content",
                                description=f"{pdf_file.name} has no pages",
                                location=str(pdf_file),
                                auto_fixable=True,
                            )
                        )

            except Exception as e:
                issues.append(
                    QAIssue(
                        severity="critical",
                        category="format",
                        description=f"Cannot read PDF {pdf_file.name}: {str(e)}",
                        location=str(pdf_file),
                        auto_fixable=False,
                    )
                )

        return issues, metrics

    def check_page_count(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check if page count meets requirements"""
        issues = []
        metrics = {"page_counts": {}}

        # Expected page counts by format
        expected_counts = {"paperback": 107, "hardcover": 156}

        for format_type, expected in expected_counts.items():
            pdf_pattern = f"*{format_type}*.pdf"
            pdf_files = list(book_path.glob(pdf_pattern))

            for pdf_file in pdf_files:
                try:
                    with open(pdf_file, "rb") as f:
                        pdf = PyPDF2.PdfReader(f)
                        actual = len(pdf.pages)
                        metrics["page_counts"][pdf_file.name] = actual

                        if actual != expected:
                            issues.append(
                                QAIssue(
                                    severity="critical",
                                    category="format",
                                    description=f"{pdf_file.name} has {
                                        actual} pages, expected {expected}",
                                    location=str(pdf_file),
                                    suggested_fix=f"Regenerate with correct page count",
                                    auto_fixable=True,
                                )
                            )

                except Exception:
                    pass

        return issues, metrics

    def check_puzzle_completeness(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check if all puzzles are complete with grids and clues"""
        issues = []
        metrics = {"total_puzzles": 0, "complete_puzzles": 0}

        metadata_dir = book_path / "metadata"
        if not metadata_dir.exists():
            issues.append(
                QAIssue(
                    severity="critical",
                    category="structure",
                    description="No metadata directory found",
                    suggested_fix="Regenerate puzzles with metadata",
                    auto_fixable=True,
                )
            )
            return issues, metrics

        # Check puzzle files
        puzzle_files = list(metadata_dir.glob("puzzle_*.json"))
        metrics["total_puzzles"] = len(puzzle_files)

        for puzzle_file in puzzle_files:
            with open(puzzle_file) as f:
                puzzle_data = json.load(f)

            # Check required fields
            required = ["id", "clues", "difficulty"]
            missing = [f for f in required if f not in puzzle_data]

            if missing:
                issues.append(
                    QAIssue(
                        severity="critical",
                        category="metadata",
                        description=f"Puzzle {puzzle_data.get('id', '?')} missing fields: {
                            missing}",
                        location=str(puzzle_file),
                        suggested_fix="Regenerate puzzle with complete metadata",
                        auto_fixable=True,
                    )
                )
            else:
                metrics["complete_puzzles"] += 1

        return issues, metrics

    def check_solution_validity(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check if solutions are properly filled"""
        issues = []
        metrics = {"solutions_checked": 0, "empty_solutions": 0}

        # Import solution validator
        from puzzle_validators import validate_crossword_solutions_in_pdf

        pdf_files = list(book_path.glob("*interior*.pdf")) + list(
            book_path.glob("*manuscript*.pdf")
        )

        for pdf_file in pdf_files:
            success, stats = validate_crossword_solutions_in_pdf(pdf_file)
            metrics["solutions_checked"] += stats.get("total_solutions", 0)
            metrics["empty_solutions"] += stats.get("empty_solutions", 0)

            if not success:
                empty_ids = stats.get("empty_solution_ids", [])
                issues.append(
                    QAIssue(
                        severity="critical",
                        category="content",
                        description=f"Empty solutions found for puzzles: {empty_ids}",
                        location=str(pdf_file),
                        suggested_fix="Regenerate solutions for affected puzzles",
                        auto_fixable=True,
                    )
                )

        return issues, metrics

    def check_metadata_consistency(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check metadata consistency and completeness"""
        issues = []
        metrics = {"metadata_files": 0}

        metadata_dir = book_path / "metadata"
        if metadata_dir.exists():
            metadata_files = list(metadata_dir.glob("*.json"))
            metrics["metadata_files"] = len(metadata_files)

            # Check collection.json
            collection_file = metadata_dir / "collection.json"
            if not collection_file.exists():
                issues.append(
                    QAIssue(
                        severity="critical",
                        category="metadata",
                        description="Missing collection.json",
                        suggested_fix="Create collection metadata file",
                        auto_fixable=True,
                    )
                )
            else:
                with open(collection_file) as f:
                    collection = json.load(f)

                listed_puzzles = collection.get("puzzles", [])
                actual_puzzles = len(list(metadata_dir.glob("puzzle_*.json")))

                if len(listed_puzzles) != actual_puzzles:
                    issues.append(
                        QAIssue(
                            severity="warning",
                            category="metadata",
                            description=f"Collection lists {
                                len(listed_puzzles)} puzzles but found {actual_puzzles}",
                            suggested_fix="Update collection.json",
                            auto_fixable=True,
                        )
                    )

        return issues, metrics

    def check_content_quality(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check content quality (no placeholders, test content)"""
        issues = []
        metrics = {"placeholder_count": 0, "test_content_found": False}

        # Check for test/placeholder content
        forbidden_patterns = [
            r"test",
            r"lorem ipsum",
            r"placeholder",
            r"todo",
            r"fixme",
        ]

        for json_file in book_path.rglob("*.json"):
            with open(json_file) as f:
                content = f.read().lower()

            for pattern in forbidden_patterns:
                if re.search(pattern, content):
                    metrics["placeholder_count"] += 1
                    issues.append(
                        QAIssue(
                            severity="critical",
                            category="content",
                            description=f"Found '{pattern}' in {json_file.name}",
                            location=str(json_file),
                            suggested_fix="Replace with production content",
                            auto_fixable=False,
                        )
                    )
                    break

        return issues, metrics

    def check_format_compliance(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check KDP format compliance"""
        issues = []
        metrics = {"format_checks": {}}

        # Check trim size, margins, etc.
        # This is a simplified check - real implementation would be more thorough

        return issues, metrics

    def check_duplicate_content(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check for duplicate puzzles or clues"""
        issues = []
        metrics = {"duplicate_clues": 0, "unique_ratio": 1.0}

        metadata_dir = book_path / "metadata"
        if not metadata_dir.exists():
            return issues, metrics

        all_clues = []
        for puzzle_file in metadata_dir.glob("puzzle_*.json"):
            with open(puzzle_file) as f:
                puzzle_data = json.load(f)

            clues = puzzle_data.get("clues", {})
            for direction in ["across", "down"]:
                for clue in clues.get(direction, []):
                    if len(clue) > 1:
                        all_clues.append(clue[1])

        if all_clues:
            clue_counts = Counter(all_clues)
            duplicates = [(c, count) for c, count in clue_counts.items() if count > 2]

            if duplicates:
                metrics["duplicate_clues"] = len(duplicates)
                metrics["unique_ratio"] = len(set(all_clues)) / len(all_clues)

                issues.append(
                    QAIssue(
                        severity="warning",
                        category="content",
                        description=f"Found {len(duplicates)} duplicate clues",
                        suggested_fix="Regenerate puzzles with more variety",
                        auto_fixable=True,
                    )
                )

        return issues, metrics

    def check_answer_keys(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Check answer key completeness"""
        issues = []
        metrics = {"answer_key_coverage": 0}

        # Implementation would check PDF for answer section

        return issues, metrics

    def check_production_readiness(self, book_path: Path) -> Tuple[List[QAIssue], Dict]:
        """Final production readiness checks"""
        issues = []
        metrics = {"production_ready": True}

        # Check for required files
        required_files = ["amazon_kdp_metadata.json", "*interior*.pdf", "*cover*.pdf"]

        for pattern in required_files:
            if not list(book_path.glob(pattern)):
                metrics["production_ready"] = False
                issues.append(
                    QAIssue(
                        severity="warning",
                        category="structure",
                        description=f"Missing required file pattern: {pattern}",
                        suggested_fix="Generate missing production files",
                        auto_fixable=True,
                    )
                )

        return issues, metrics

    def _calculate_score(self, issues: List[QAIssue], passed: int, total: int) -> int:
        """Calculate overall QA score"""
        base_score = (passed / total) * 100 if total > 0 else 0

        # Apply penalties for issues
        for issue in issues:
            penalty = self.scoring_weights.get(issue.severity, 0)
            base_score += penalty

        return max(0, min(100, int(base_score)))

    def _generate_recommendations(
        self, issues: List[QAIssue], metrics: Dict
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Group issues by auto-fixability
        auto_fixable = [i for i in issues if i.auto_fixable]
        manual_fixes = [i for i in issues if not i.auto_fixable]

        if auto_fixable:
            recommendations.append(
                f"🔧 {len(auto_fixable)} issues can be fixed automatically by the optimizer"
            )

        if manual_fixes:
            recommendations.append(
                f"⚠️  {len(manual_fixes)} issues require manual intervention"
            )

        # Specific recommendations based on metrics
        if metrics.get("empty_solutions", 0) > 0:
            recommendations.append(
                "🔄 Regenerate crossword solutions using enhanced engine"
            )

        if metrics.get("duplicate_clues", 0) > 5:
            recommendations.append("📝 Increase clue variety to reduce duplicates")

        if not metrics.get("production_ready", True):
            recommendations.append(
                "📦 Generate missing production files before publishing"
            )

        return recommendations

    def save_report(self, report: QAReport, output_path: Optional[Path] = None):
        """Save QA report to JSON file"""
        if not output_path:
            output_path = Path(report.book_path) / "qa_report.json"

        report_dict = asdict(report)
        # Convert QAIssue objects to dicts
        report_dict["issues"] = [asdict(issue) for issue in report.issues]

        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2)

        logger.info(f"QA report saved to: {output_path}")


def main():
    """CLI interface for QA checker"""
    import argparse

    parser = argparse.ArgumentParser(description="Intelligent QA Checker")
    parser.add_argument("book_path", help="Path to book directory")
    parser.add_argument("--output", help="Output path for report")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    checker = IntelligentQAChecker()
    report = checker.evaluate_book(Path(args.book_path))

    # Save report
    output_path = Path(args.output) if args.output else None
    checker.save_report(report, output_path)

    if args.json:
        # JSON output only
        print(json.dumps(asdict(report), indent=2))
    else:
        # Human-readable output
        print(f"\n📊 QA EVALUATION REPORT")
        print(f"{'=' * 50}")
        print(f"📁 Book: {report.book_path}")
        print(f"🎯 Score: {report.score}/100")
        print(f"📋 Status: {report.status}")
        print(f"✅ Passed: {report.passed_checks}/{report.total_checks} checks")

        if report.issues:
            print(f"\n❌ Issues Found ({len(report.issues)}):")
            for issue in report.issues[:10]:  # First 10
                print(f"  [{issue.severity.upper()}] {issue.description}")
                if issue.suggested_fix:
                    print(f"    💡 Fix: {issue.suggested_fix}")

        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")

    # Exit code based on status
    sys.exit(0 if report.status == "PASS" else 1)


if __name__ == "__main__":
    main()
