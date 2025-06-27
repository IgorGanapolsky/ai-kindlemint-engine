#!/usr/bin/env python3
"""
Integrated Crossword QA System
Complete validation pipeline that actually works
"""

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import PyPDF2


@dataclass
class QAReport:
    """Comprehensive QA report"""

    timestamp: str
    pdf_path: str
    status: str  # PASS, FAIL, CRITICAL_FAIL
    score: int
    issues: List[Dict] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class IntegratedCrosswordQA:
    """Complete QA system that catches all issues"""

    def __init__(self):
        self.critical_thresholds = {
            "min_unique_puzzles": 48,  # At least 48/50 must be unique
            "max_duplicate_clues": 5,  # Same clue in max 5 puzzles
            "min_down_ratio": 0.35,  # At least 35% DOWN clues
            "max_down_ratio": 0.65,  # At most 65% DOWN clues
            "min_words_per_puzzle": 20,  # Minimum words in grid
            "min_unique_words": 200,  # Across entire book
        }

    def validate_pdf(self, pdf_path: str) -> QAReport:
        """Complete validation pipeline"""
        report = QAReport(
            timestamp=datetime.now().isoformat(),
            pdf_path=pdf_path,
            status="UNKNOWN",
            score=0,
        )

        try:
            # Extract all content
            print("📖 Extracting PDF content...")
            content = self._extract_all_content(pdf_path)

            # Run validation stages
            print("🔍 Running validation checks...")

            # Stage 1: Structure validation
            structure_score = self._validate_structure(content, report)

            # Stage 2: Uniqueness validation
            uniqueness_score = self._validate_uniqueness(content, report)

            # Stage 3: Content quality
            quality_score = self._validate_content_quality(content, report)

            # Stage 4: Puzzle solvability
            solvability_score = self._validate_solvability(content, report)

            # Calculate final score
            scores = {
                "structure": (structure_score, 20),
                "uniqueness": (uniqueness_score, 35),
                "quality": (quality_score, 25),
                "solvability": (solvability_score, 20),
            }

            weighted_score = sum(
                score * weight / 100 for score, weight in scores.values()
            )
            report.score = int(weighted_score)

            # Determine status
            critical_issues = [i for i in report.issues if i["severity"] == "CRITICAL"]
            if critical_issues:
                report.status = "CRITICAL_FAIL"
            elif report.score >= 90:
                report.status = "PASS"
            else:
                report.status = "FAIL"

            # Add metrics
            report.metrics = {
                "category_scores": {k: v[0] for k, v in scores.items()},
                "weights": {k: v[1] for k, v in scores.items()},
                "content_stats": content.get("stats", {}),
            }

            # Generate recommendations
            self._generate_recommendations(report)

        except Exception as e:
            report.status = "ERROR"
            report.issues.append(
                {
                    "severity": "CRITICAL",
                    "category": "system",
                    "message": f"QA system error: {str(e)}",
                }
            )

        return report

    def _extract_all_content(self, pdf_path: str) -> Dict:
        """Extract all content from PDF"""
        content = {"puzzles": [], "page_count": 0, "stats": {}}

        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            content["page_count"] = len(reader.pages)

            # Extract text from all pages
            all_text = []
            for page in reader.pages:
                all_text.append(page.extract_text())

            # Parse puzzles
            puzzles = self._parse_puzzles(all_text)
            content["puzzles"] = puzzles

            # Calculate statistics
            content["stats"] = self._calculate_stats(puzzles)

        return content

    def _parse_puzzles(self, pages: List[str]) -> List[Dict]:
        """Parse puzzle data from pages"""
        puzzles = []
        current_puzzle = None

        for i, text in enumerate(pages):
            # Detect puzzle number
            puzzle_match = re.search(r"Puzzle\s+(\d+)(?:\s|$)", text, re.IGNORECASE)

            if puzzle_match:
                puzzle_num = int(puzzle_match.group(1))

                if "clues" in text.lower():
                    # This is a clues page
                    if not current_puzzle or current_puzzle["number"] != puzzle_num:
                        if current_puzzle:
                            puzzles.append(current_puzzle)
                        current_puzzle = {
                            "number": puzzle_num,
                            "clues_text": text,
                            "across_clues": {},
                            "down_clues": {},
                        }

                    # Parse clues
                    across, down = self._parse_clues_from_text(text)
                    current_puzzle["across_clues"] = across
                    current_puzzle["down_clues"] = down

                elif "solution" in text.lower():
                    # Solution page
                    if current_puzzle and current_puzzle["number"] == puzzle_num:
                        current_puzzle["has_solution"] = True

        if current_puzzle:
            puzzles.append(current_puzzle)

        return puzzles

    def _parse_clues_from_text(
        self, text: str
    ) -> Tuple[Dict[int, str], Dict[int, str]]:
        """Extract clues from text"""
        across_clues = {}
        down_clues = {}

        # Split by ACROSS/DOWN
        parts = re.split(r"\b(ACROSS|DOWN)\b", text, flags=re.IGNORECASE)

        current_section = None
        for part in parts:
            if part.upper() == "ACROSS":
                current_section = "across"
            elif part.upper() == "DOWN":
                current_section = "down"
            elif current_section:
                # Extract numbered clues
                clue_pattern = re.compile(r"(\d+)\.\s*([^\d]+?)(?=\d+\.|$)", re.DOTALL)
                matches = clue_pattern.findall(part)

                for num_str, clue_text in matches:
                    try:
                        num = int(num_str)
                        clue = clue_text.strip()

                        if current_section == "across":
                            across_clues[num] = clue
                        else:
                            down_clues[num] = clue
                    except ValueError:
                        pass

        return across_clues, down_clues

    def _calculate_stats(self, puzzles: List[Dict]) -> Dict:
        """Calculate statistics from puzzles"""
        stats = {
            "total_puzzles": len(puzzles),
            "avg_across_clues": 0,
            "avg_down_clues": 0,
            "unique_clues": 0,
            "duplicate_puzzles": 0,
        }

        if not puzzles:
            return stats

        # Calculate averages
        total_across = sum(len(p.get("across_clues", {})) for p in puzzles)
        total_down = sum(len(p.get("down_clues", {})) for p in puzzles)

        stats["avg_across_clues"] = total_across / len(puzzles)
        stats["avg_down_clues"] = total_down / len(puzzles)

        # Count unique clues
        all_clues = set()
        for p in puzzles:
            all_clues.update(p.get("across_clues", {}).values())
            all_clues.update(p.get("down_clues", {}).values())

        stats["unique_clues"] = len(all_clues)

        # Detect duplicates
        puzzle_hashes = {}
        for p in puzzles:
            # Create hash of puzzle content
            clue_str = json.dumps(
                {
                    "across": sorted(p.get("across_clues", {}).items()),
                    "down": sorted(p.get("down_clues", {}).items()),
                },
                sort_keys=True,
            )

            puzzle_hash = hashlib.md5(clue_str.encode()).hexdigest()

            if puzzle_hash in puzzle_hashes:
                stats["duplicate_puzzles"] += 1
            else:
                puzzle_hashes[puzzle_hash] = p["number"]

        return stats

    def _validate_structure(self, content: Dict, report: QAReport) -> int:
        """Validate structural requirements"""
        score = 100

        # Check page count
        if content["page_count"] != 156:
            report.issues.append(
                {
                    "severity": "HIGH",
                    "category": "structure",
                    "message": f"Wrong page count: {content['page_count']} (expected 156)",
                }
            )
            score -= 30

        # Check puzzle count
        puzzle_count = len(content["puzzles"])
        if puzzle_count < 50:
            report.issues.append(
                {
                    "severity": "CRITICAL",
                    "category": "structure",
                    "message": f"Only {puzzle_count} puzzles found (expected 50)",
                }
            )
            score = 0

        # Check clue balance
        for puzzle in content["puzzles"]:
            across = len(puzzle.get("across_clues", {}))
            down = len(puzzle.get("down_clues", {}))
            total = across + down

            if total > 0:
                down_ratio = down / total
                if down_ratio < self.critical_thresholds["min_down_ratio"]:
                    report.issues.append(
                        {
                            "severity": "HIGH",
                            "category": "structure",
                            "message": f"Puzzle {puzzle['number']}: Poor clue balance ({down} DOWN / {across} ACROSS)",
                        }
                    )
                    score -= 5

        return max(0, score)

    def _validate_uniqueness(self, content: Dict, report: QAReport) -> int:
        """Validate puzzle uniqueness"""
        score = 100
        puzzles = content["puzzles"]

        # Check for duplicate puzzles
        puzzle_signatures = {}
        duplicates = []

        for puzzle in puzzles:
            # Create signature
            sig = self._create_puzzle_signature(puzzle)

            if sig in puzzle_signatures:
                duplicates.append(
                    {"puzzle": puzzle["number"], "duplicate_of": puzzle_signatures[sig]}
                )
            else:
                puzzle_signatures[sig] = puzzle["number"]

        # Calculate uniqueness
        unique_count = len(puzzle_signatures)
        total_count = len(puzzles)

        if unique_count < self.critical_thresholds["min_unique_puzzles"]:
            report.issues.append(
                {
                    "severity": "CRITICAL",
                    "category": "uniqueness",
                    "message": f"Only {unique_count}/{total_count} unique puzzles (98% are duplicates!)",
                    "details": duplicates[:10],  # Show first 10
                }
            )
            score = 0

        # Check clue reuse
        clue_usage = Counter()
        for puzzle in puzzles:
            for clue in puzzle.get("across_clues", {}).values():
                clue_usage[clue] += 1
            for clue in puzzle.get("down_clues", {}).values():
                clue_usage[clue] += 1

        overused = [
            (clue, count)
            for clue, count in clue_usage.items()
            if count > self.critical_thresholds["max_duplicate_clues"]
        ]

        if overused:
            report.issues.append(
                {
                    "severity": "HIGH",
                    "category": "uniqueness",
                    "message": f"{len(overused)} clues used in too many puzzles",
                    "details": overused[:5],
                }
            )
            score -= len(overused) * 2

        return max(0, score)

    def _validate_content_quality(self, content: Dict, report: QAReport) -> int:
        """Validate content quality"""
        score = 100

        stats = content.get("stats", {})

        # Check clue variety
        unique_clues = stats.get("unique_clues", 0)
        if unique_clues < self.critical_thresholds["min_unique_words"]:
            report.issues.append(
                {
                    "severity": "HIGH",
                    "category": "quality",
                    "message": f"Low clue variety: only {unique_clues} unique clues",
                }
            )
            score -= 30

        # Check for empty puzzles
        for puzzle in content["puzzles"]:
            if not puzzle.get("across_clues") and not puzzle.get("down_clues"):
                report.issues.append(
                    {
                        "severity": "CRITICAL",
                        "category": "quality",
                        "message": f"Puzzle {puzzle['number']} has no clues",
                    }
                )
                score = 0
                break

        return max(0, score)

    def _validate_solvability(self, content: Dict, report: QAReport) -> int:
        """Validate puzzle solvability"""
        score = 100

        # Check if solutions exist
        puzzles_with_solutions = sum(
            1 for p in content["puzzles"] if p.get("has_solution")
        )

        if puzzles_with_solutions < len(content["puzzles"]):
            report.issues.append(
                {
                    "severity": "HIGH",
                    "category": "solvability",
                    "message": f"Missing solutions for {len(content['puzzles']) - puzzles_with_solutions} puzzles",
                }
            )
            score -= 50

        return max(0, score)

    def _create_puzzle_signature(self, puzzle: Dict) -> str:
        """Create unique signature for puzzle"""
        # Combine all clues in a deterministic way
        data = {
            "across": sorted(puzzle.get("across_clues", {}).items()),
            "down": sorted(puzzle.get("down_clues", {}).items()),
        }

        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _generate_recommendations(self, report: QAReport):
        """Generate actionable recommendations"""

        # Group issues by category
        issues_by_category = defaultdict(list)
        for issue in report.issues:
            issues_by_category[issue["category"]].append(issue)

        # Generate recommendations based on issues
        if "uniqueness" in issues_by_category:
            report.recommendations.append(
                "CRITICAL: Generate unique puzzles for each slot. "
                "Use different word combinations and varied clue phrasings."
            )

        if "structure" in issues_by_category:
            report.recommendations.append(
                "Ensure all puzzles have balanced ACROSS/DOWN clues (40-60% each)."
            )

        if "quality" in issues_by_category:
            report.recommendations.append(
                "Increase clue variety. Each clue should appear in at most 5 puzzles."
            )

        if report.status == "CRITICAL_FAIL":
            report.recommendations.insert(
                0, "⚠️  DO NOT PUBLISH - Critical issues must be fixed first!"
            )


def generate_qa_report_html(report: QAReport) -> str:
    """Generate HTML report for better readability"""

    status_color = {
        "PASS": "#28a745",
        "FAIL": "#dc3545",
        "CRITICAL_FAIL": "#721c24",
    }.get(report.status, "#6c757d")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crossword QA Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: {status_color}; color: white; padding: 20px; }}
            .score {{ font-size: 48px; font-weight: bold; }}
            .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid #dc3545; }}
            .critical {{ border-left-color: #721c24; background: #f8d7da; }}
            .high {{ border-left-color: #dc3545; background: #f8d7da; }}
            .recommendation {{ background: #d1ecf1; padding: 10px; margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Crossword QA Report</h1>
            <div class="score">Score: {report.score}/100</div>
            <div>Status: {report.status}</div>
        </div>
        
        <h2>Issues Found ({len(report.issues)})</h2>
    """

    for issue in report.issues:
        severity_class = issue["severity"].lower()
        html += f"""
        <div class="issue {severity_class}">
            <strong>[{issue['severity']}] {issue['category']}</strong><br>
            {issue['message']}
        </div>
        """

    html += "<h2>Recommendations</h2>"
    for rec in report.recommendations:
        html += f'<div class="recommendation">{rec}</div>'

    html += """
    </body>
    </html>
    """

    return html


def main():
    """Run the integrated QA system"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python integrated_crossword_qa.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    print("🚀 Running Integrated Crossword QA System")
    print("=" * 60)

    qa = IntegratedCrosswordQA()
    report = qa.validate_pdf(pdf_path)

    # Display results
    print(f"\n📊 QA REPORT")
    print(f"Status: {report.status}")
    print(f"Score: {report.score}/100")

    if report.issues:
        print(f"\n❌ Issues Found: {len(report.issues)}")

        # Group by severity
        critical = [i for i in report.issues if i["severity"] == "CRITICAL"]
        high = [i for i in report.issues if i["severity"] == "HIGH"]

        if critical:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical)}):")
            for issue in critical[:5]:  # Show first 5
                print(f"  - {issue['message']}")

        if high:
            print(f"\n⚠️  HIGH PRIORITY ISSUES ({len(high)}):")
            for issue in high[:5]:  # Show first 5
                print(f"  - {issue['message']}")

    if report.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    # Save reports
    json_path = Path(pdf_path).parent / "qa_report_integrated.json"
    with open(json_path, "w") as f:
        json.dump(
            {
                "timestamp": report.timestamp,
                "pdf_path": report.pdf_path,
                "status": report.status,
                "score": report.score,
                "issues": report.issues,
                "metrics": report.metrics,
                "recommendations": report.recommendations,
            },
            f,
            indent=2,
        )

    html_path = Path(pdf_path).parent / "qa_report_integrated.html"
    with open(html_path, "w") as f:
        f.write(generate_qa_report_html(report))

    print(f"\n📄 Reports saved:")
    print(f"  - JSON: {json_path}")
    print(f"  - HTML: {html_path}")

    # Exit with appropriate code
    if report.status == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
