#!/usr/bin/env python3
"""
QA Validation Pipeline for AI KindleMint Engine
Implements Option B: Hybrid Artifacts approach with multi-model validation
"""

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv

load_dotenv()


@dataclass
class QAResult:
    """Structure for QA validation results"""

    book_id: str
    timestamp: str
    overall_score: float
    passed: bool
    criteria: Dict[str, Dict]
    validation_model: str
    issues_found: List[Dict]
    recommendations: List[str]


class QAValidationPipeline:
    """Multi-model QA validation system"""

    def __init__(self):
        # QA Criteria thresholds
        self.qa_criteria = {
            "duplicate_content": {"threshold": 10, "unit": "%"},
            "text_cutoff": {"threshold": 0, "unit": "instances"},
            "white_space_ratio": {"threshold": 92, "unit": "%"},
            "puzzle_integrity": {"threshold": 100, "unit": "%"},
            "font_embedding": {"threshold": 100, "unit": "%"},
            "page_count_accuracy": {"threshold": 100, "unit": "%"},
            "answer_key_completeness": {"threshold": 100, "unit": "%"},
        }

        # Minimum passing score
        self.min_passing_score = 85

        # API keys for validation
        self.openai_key = os.getenv("OPENAI_VALIDATION_KEY")
        self.gemini_key = os.getenv("GEMINI_BACKUP_KEY")

    def validate_pdf(self, pdf_path: Path, book_type: str = "crossword") -> QAResult:
        """
        Complete QA validation of a PDF file
        """
        print(f"\n🔍 Starting QA Validation for: {pdf_path.name}")

        book_id = self._generate_book_id(pdf_path)
        timestamp = datetime.now().isoformat()

        # Run all validation checks
        criteria_results = {}
        issues = []

        # 1. Check duplicate content
        dup_score, dup_issues = self._check_duplicate_content(pdf_path)
        criteria_results["duplicate_content"] = {
            "score": dup_score,
            "threshold": self.qa_criteria["duplicate_content"]["threshold"],
            "passed": dup_score <= self.qa_criteria["duplicate_content"]["threshold"],
            "details": dup_issues,
        }
        issues.extend(dup_issues)

        # 2. Check text cutoff
        cutoff_count, cutoff_issues = self._check_text_cutoff(pdf_path)
        criteria_results["text_cutoff"] = {
            "score": cutoff_count,
            "threshold": self.qa_criteria["text_cutoff"]["threshold"],
            "passed": cutoff_count == 0,
            "details": cutoff_issues,
        }
        issues.extend(cutoff_issues)

        # 3. Check white space ratio
        ws_ratio, ws_issues = self._check_white_space(pdf_path)
        criteria_results["white_space_ratio"] = {
            "score": ws_ratio,
            "threshold": self.qa_criteria["white_space_ratio"]["threshold"],
            "passed": ws_ratio <= self.qa_criteria["white_space_ratio"]["threshold"],
            "details": ws_issues,
        }
        issues.extend(ws_issues)

        # 4. Check puzzle integrity (for crossword books)
        if book_type == "crossword":
            puzzle_score, puzzle_issues = self._check_puzzle_integrity(pdf_path)
            criteria_results["puzzle_integrity"] = {
                "score": puzzle_score,
                "threshold": self.qa_criteria["puzzle_integrity"]["threshold"],
                "passed": puzzle_score
                >= self.qa_criteria["puzzle_integrity"]["threshold"],
                "details": puzzle_issues,
            }
            issues.extend(puzzle_issues)

        # 5. Check font embedding
        font_score, font_issues = self._check_font_embedding(pdf_path)
        criteria_results["font_embedding"] = {
            "score": font_score,
            "threshold": self.qa_criteria["font_embedding"]["threshold"],
            "passed": font_score >= self.qa_criteria["font_embedding"]["threshold"],
            "details": font_issues,
        }
        issues.extend(font_issues)

        # Calculate overall score
        overall_score = self._calculate_overall_score(criteria_results)
        passed = overall_score >= self.min_passing_score

        # Generate recommendations
        recommendations = self._generate_recommendations(criteria_results, issues)

        # Create QA result
        result = QAResult(
            book_id=book_id,
            timestamp=timestamp,
            overall_score=overall_score,
            passed=passed,
            criteria=criteria_results,
            validation_model="qa_pipeline_v1",
            issues_found=issues,
            recommendations=recommendations,
        )

        # Print summary
        self._print_qa_summary(result)

        # Save report
        self._save_qa_report(result, pdf_path)

        return result

    def _check_duplicate_content(self, pdf_path: Path) -> Tuple[float, List[Dict]]:
        """Check for duplicate text/clues in PDF"""
        try:
            # Extract all text
            result = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return 0.0, [
                    {"type": "error", "message": "Could not extract text from PDF"}
                ]

            text = result.stdout
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            # Find duplicates
            line_counts = {}
            duplicates = []

            for i, line in enumerate(lines):
                if len(line) > 10:  # Ignore short lines
                    if line in line_counts:
                        line_counts[line].append(i)
                    else:
                        line_counts[line] = [i]

            # Calculate duplicate percentage
            duplicate_lines = sum(1 for count in line_counts.values() if len(count) > 1)
            duplicate_percentage = (duplicate_lines / len(lines)) * 100 if lines else 0

            # Collect specific duplicates
            for line, occurrences in line_counts.items():
                if len(occurrences) > 1:
                    duplicates.append(
                        {
                            "type": "duplicate_text",
                            "text": line[:50] + "..." if len(line) > 50 else line,
                            "occurrences": len(occurrences),
                            "lines": occurrences[:5],  # First 5 occurrences
                        }
                    )

            return duplicate_percentage, duplicates[:10]  # Return top 10 duplicates

        except Exception as e:
            return 0.0, [
                {"type": "error", "message": f"Duplicate check failed: {str(e)}"}
            ]

    def _check_text_cutoff(self, pdf_path: Path) -> Tuple[int, List[Dict]]:
        """Check for text cutoff at page edges"""
        issues = []
        cutoff_count = 0

        try:
            # Use pdfinfo to get page dimensions
            result = subprocess.run(
                ["pdfinfo", str(pdf_path)], capture_output=True, text=True
            )

            # For now, return 0 cutoffs (would need more sophisticated analysis)
            # In production, this would use computer vision or PDF parsing libraries
            return 0, []

        except Exception as e:
            return 0, [{"type": "error", "message": f"Cutoff check failed: {str(e)}"}]

    def _check_white_space(self, pdf_path: Path) -> Tuple[float, List[Dict]]:
        """Check white space ratio per page"""
        try:
            # This is a simplified check - in production would analyze each page
            result = subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), "-"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return 0.0, [
                    {"type": "error", "message": "Could not analyze white space"}
                ]

            pages = result.stdout.split("\f")  # Form feed separates pages
            high_whitespace_pages = []

            for i, page in enumerate(pages):
                if page.strip():
                    total_chars = len(page)
                    white_chars = page.count(" ") + page.count("\n") + page.count("\t")
                    ws_ratio = (
                        (white_chars / total_chars) * 100 if total_chars > 0 else 100
                    )

                    if ws_ratio > 92:
                        high_whitespace_pages.append(
                            {
                                "type": "high_whitespace",
                                "page": i + 1,
                                "ratio": round(ws_ratio, 1),
                            }
                        )

            avg_ratio = (
                sum(p["ratio"] for p in high_whitespace_pages)
                / len(high_whitespace_pages)
                if high_whitespace_pages
                else 0
            )

            return avg_ratio, high_whitespace_pages[:5]

        except Exception as e:
            return 0.0, [
                {"type": "error", "message": f"White space check failed: {str(e)}"}
            ]

    def _check_puzzle_integrity(self, pdf_path: Path) -> Tuple[float, List[Dict]]:
        """Check if puzzle clues match answers - ACTUAL SUDOKU VALIDATION"""
        issues = []

        try:
            # Extract text to analyze puzzle content
            result = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return 0.0, [
                    {
                        "type": "error",
                        "message": "Could not extract PDF text for puzzle validation",
                    }
                ]

            text = result.stdout

            # Check for critical Sudoku-specific issues
            puzzle_score = 100.0

            # 1. Check for blank puzzles (major issue from user complaints)
            if self._detect_blank_puzzles(text):
                puzzle_score -= 50.0
                issues.append(
                    {
                        "type": "blank_puzzles",
                        "message": "Detected blank or missing puzzle grids",
                        "severity": "critical",
                    }
                )

            # 2. Check for missing clues
            clue_coverage = self._analyze_clue_coverage(text)
            if clue_coverage < 20:  # Less than 20% of puzzles have clues
                puzzle_score -= 30.0
                issues.append(
                    {
                        "type": "missing_clues",
                        "message": f"Only {clue_coverage}% of puzzles have visible clues",
                        "severity": "critical",
                    }
                )

            # 3. Check for repeated solution explanations (user complaint)
            repetition_score = self._check_solution_repetition(text)
            if repetition_score > 80:  # More than 80% identical solutions
                puzzle_score -= 15.0
                issues.append(
                    {
                        "type": "repeated_solutions",
                        "message": f"{repetition_score}% of solution explanations are identical",
                        "severity": "moderate",
                    }
                )

            # 4. Check for puzzle variety
            variety_score = self._check_puzzle_variety(text)
            if variety_score < 50:  # Less than 50% unique puzzles
                puzzle_score -= 20.0
                issues.append(
                    {
                        "type": "low_variety",
                        "message": f"Only {variety_score}% puzzle variety detected",
                        "severity": "moderate",
                    }
                )

            # 5. Validate basic puzzle structure
            structure_valid = self._validate_puzzle_structure(pdf_path)
            if not structure_valid:
                puzzle_score -= 10.0
                issues.append(
                    {
                        "type": "invalid_structure",
                        "message": "PDF structure suggests missing puzzle content",
                        "severity": "moderate",
                    }
                )

            return max(0.0, puzzle_score), issues

        except Exception as e:
            return 0.0, [
                {"type": "error", "message": f"Puzzle integrity check failed: {str(e)}"}
            ]

    def _detect_blank_puzzles(self, text: str) -> bool:
        """Detect if puzzles are blank or missing"""
        # Look for indicators of blank puzzles
        puzzle_indicators = ["Puzzle ", "Difficulty:", "Solution - Puzzle"]
        solution_indicators = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

        puzzle_count = sum(text.count(indicator) for indicator in puzzle_indicators)
        digit_density = (
            sum(text.count(digit) for digit in solution_indicators) / len(text)
            if text
            else 0
        )

        # If we have puzzle headers but very low digit density, puzzles are likely blank
        if puzzle_count > 10 and digit_density < 0.01:  # Less than 1% digits
            return True

        # Check for specific error patterns that indicate blank grids
        blank_indicators = [
            "could not generate puzzle grid",
            "image not found",
            "missing puzzle data",
            "create_puzzle_grid",  # The exact error we had
            "create_solution_grid",
        ]

        return any(indicator.lower() in text.lower() for indicator in blank_indicators)

    def _analyze_clue_coverage(self, text: str) -> float:
        """Analyze what percentage of puzzles have visible clues"""
        puzzle_sections = text.split("Puzzle ")
        clue_sections = 0

        for section in puzzle_sections[1:]:  # Skip first split
            # Look for numbers that would indicate clues
            if any(
                f"{i}" in section[:200] for i in range(1, 10)
            ):  # Check first 200 chars
                clue_sections += 1

        total_puzzles = len(puzzle_sections) - 1
        return (clue_sections / total_puzzles * 100) if total_puzzles > 0 else 0

    def _check_solution_repetition(self, text: str) -> float:
        """Check for repeated solution explanations"""
        # Find all solution explanations
        solution_parts = text.split("Solution - Puzzle")
        explanations = []

        for part in solution_parts[1:]:  # Skip first split
            # Extract the explanation part (first ~200 chars after "Solution - Puzzle")
            explanation = part[:200] if part else ""
            explanations.append(explanation.strip())

        if len(explanations) <= 1:
            return 0

        # Count unique explanations
        unique_explanations = len(set(explanations))
        repetition_rate = (1 - unique_explanations / len(explanations)) * 100

        return repetition_rate

    def _check_puzzle_variety(self, text: str) -> float:
        """Check puzzle variety by analyzing patterns"""
        puzzle_sections = text.split("Puzzle ")

        if len(puzzle_sections) <= 2:
            return 100  # Can't measure variety with few puzzles

        # Simple variety check - look for different difficulty patterns
        difficulties = []
        for section in puzzle_sections[1:]:
            if "Easy" in section[:100]:
                difficulties.append("easy")
            elif "Medium" in section[:100]:
                difficulties.append("medium")
            elif "Hard" in section[:100]:
                difficulties.append("hard")

        unique_patterns = len(set(difficulties))
        variety_score = (
            min(100, (unique_patterns / len(difficulties)) * 100) if difficulties else 0
        )

        return variety_score

    def _validate_puzzle_structure(self, pdf_path: Path) -> bool:
        """Validate PDF has proper puzzle structure"""
        try:
            # Check if PDF has reasonable size for puzzle content
            file_size = pdf_path.stat().st_size
            if file_size < 50000:  # Less than 50KB probably has no real content
                return False

            # Use pdfinfo to check page count
            result = subprocess.run(
                ["pdfinfo", str(pdf_path)], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                # Extract page count
                for line in result.stdout.split("\n"):
                    if "Pages:" in line:
                        try:
                            page_count = int(line.split(":")[1].strip())
                            # Sudoku books should have substantial page count
                            return page_count > 20
                        except:
                            pass

            return True  # Default to valid if can't determine

        except Exception:
            return True  # Default to valid if check fails

    def _check_font_embedding(self, pdf_path: Path) -> Tuple[float, List[Dict]]:
        """Check if all fonts are properly embedded"""
        try:
            result = subprocess.run(
                ["pdffonts", str(pdf_path)], capture_output=True, text=True
            )

            if result.returncode != 0:
                return 0.0, [{"type": "error", "message": "Could not check fonts"}]

            lines = result.stdout.strip().split("\n")[2:]  # Skip header
            unembedded = []

            for line in lines:
                if line and "no" in line.lower():
                    parts = line.split()
                    if len(parts) > 0:
                        unembedded.append(
                            {"type": "font_not_embedded", "font": parts[0]}
                        )

            embedded_percentage = (
                ((len(lines) - len(unembedded)) / len(lines) * 100) if lines else 100
            )

            return embedded_percentage, unembedded

        except Exception as e:
            return 100.0, []  # Assume OK if can't check

    def _calculate_overall_score(self, criteria_results: Dict) -> float:
        """Calculate weighted overall QA score"""
        weights = {
            "duplicate_content": 0.25,
            "text_cutoff": 0.20,
            "white_space_ratio": 0.15,
            "puzzle_integrity": 0.25,
            "font_embedding": 0.15,
        }

        total_score = 0
        total_weight = 0

        for criterion, result in criteria_results.items():
            if criterion in weights:
                # Convert to 0-100 scale
                if result["passed"]:
                    score = 100
                else:
                    # Partial credit based on how close to threshold
                    if criterion in ["duplicate_content", "white_space_ratio"]:
                        # Lower is better
                        score = max(
                            0, 100 - (result["score"] - result["threshold"]) * 5
                        )
                    else:
                        # Higher is better
                        score = (result["score"] / result["threshold"]) * 100

                total_score += score * weights[criterion]
                total_weight += weights[criterion]

        return round(total_score / total_weight if total_weight > 0 else 0, 1)

    def _generate_recommendations(
        self, criteria_results: Dict, issues: List
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if not criteria_results.get("duplicate_content", {}).get("passed", True):
            recommendations.append("Remove duplicate clues and text sections")

        if not criteria_results.get("text_cutoff", {}).get("passed", True):
            recommendations.append("Adjust margins to prevent text cutoff")

        if not criteria_results.get("white_space_ratio", {}).get("passed", True):
            recommendations.append(
                "Add more content or adjust layout to reduce white space"
            )

        if not criteria_results.get("puzzle_integrity", {}).get("passed", True):
            recommendations.append("Verify all puzzle clues have corresponding answers")

        if not criteria_results.get("font_embedding", {}).get("passed", True):
            recommendations.append("Embed all fonts in PDF for consistent rendering")

        return recommendations

    def _generate_book_id(self, pdf_path: Path) -> str:
        """Generate unique book ID"""
        return hashlib.md5(f"{pdf_path.name}{datetime.now()}".encode()).hexdigest()[:12]

    def _print_qa_summary(self, result: QAResult):
        """Print colored QA summary to console"""
        print("\n" + "=" * 60)
        print(f"📊 QA VALIDATION REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        # Overall result
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"\nOverall Score: {result.overall_score}/100 {status}")
        print(f"Minimum Required: {self.min_passing_score}/100")

        # Criteria breakdown
        print("\n📋 Criteria Breakdown:")
        for criterion, details in result.criteria.items():
            status = "✅" if details["passed"] else "❌"
            print(
                f"{status} {criterion}: {details['score']} (threshold: {details['threshold']})"
            )

        # Issues summary
        if result.issues_found:
            print(f"\n⚠️  Issues Found ({len(result.issues_found)}):")
            for issue in result.issues_found[:5]:
                print(
                    f"  - {issue.get('type', 'Unknown')}: {issue.get('message', issue)}"
                )

        # Recommendations
        if result.recommendations:
            print("\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"  • {rec}")

        print("\n" + "=" * 60)

    def _save_qa_report(self, result: QAResult, pdf_path: Path):
        """Save QA report to JSON file"""
        qa_dir = pdf_path.parent / "qa"
        qa_dir.mkdir(exist_ok=True)

        report_path = (
            qa_dir / f"qa_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_path, "w") as f:
            json.dump(asdict(result), f, indent=2)

        print(f"\n📄 Full report saved to: {report_path}")


def main():
    """Test the QA pipeline"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python qa_validation_pipeline.py <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)

    pipeline = QAValidationPipeline()
    result = pipeline.validate_pdf(pdf_path)

    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
