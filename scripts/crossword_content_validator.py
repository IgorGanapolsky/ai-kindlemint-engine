#!/usr/bin/env python3
"""
Content-aware QA validator for crossword puzzle books.
Validates actual puzzle content, not just PDF structure.
"""

import hashlib
import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import PyPDF2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrosswordContentValidator:
    """Domain-specific validator for crossword puzzle content"""

    def __init__(self):
        self.puzzle_signatures = []
        self.all_solutions = []
        self.all_clues = []
        self.issues = []
        self.warnings = []

    def validate_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Main validation entry point"""
        logger.info(f"Starting content validation for: {pdf_path}")

        start_time = datetime.now()

        # Extract puzzle content from PDF
        puzzles = self._extract_puzzles_from_pdf(pdf_path)
        logger.info(f"Extracted {len(puzzles)} puzzles from PDF")

        # Run all validations
        results = {
            "timestamp": datetime.now().isoformat(),
            "file_path": pdf_path,
            "puzzle_count": len(puzzles),
            "validations": {
                "uniqueness": self._validate_uniqueness(puzzles),
                "completeness": self._validate_completeness(puzzles),
                "content_quality": self._validate_content_quality(puzzles),
                "solutions": self._validate_solutions(puzzles),
                "clue_balance": self._validate_clue_balance(puzzles),
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "processing_time": (datetime.now() - start_time).total_seconds(),
        }

        # Calculate overall score
        passed_checks = sum(1 for v in results["validations"].values() if v["passed"])
        total_checks = len(results["validations"])
        results["score"] = int((passed_checks / total_checks) * 100)
        results["publish_ready"] = results["score"] >= 80 and len(self.issues) == 0

        return results

    def _extract_puzzles_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract puzzle data from PDF"""
        puzzles = []

        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            current_puzzle = None
            puzzle_num = 0

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()

                # Look for puzzle headers
                puzzle_match = re.search(r"Puzzle (\d+):", text)
                if puzzle_match:
                    if current_puzzle:
                        puzzles.append(current_puzzle)

                    puzzle_num = int(puzzle_match.group(1))
                    current_puzzle = {
                        "number": puzzle_num,
                        "page": page_num + 1,
                        "across_clues": {},
                        "down_clues": {},
                        "grid_text": "",
                        "solution_text": "",
                    }

                # Extract clues
                if current_puzzle:
                    # Extract ACROSS clues
                    if "ACROSS" in text:
                        across_section = (
                            text.split("ACROSS")[1].split("DOWN")[0]
                            if "DOWN" in text
                            else text.split("ACROSS")[1]
                        )
                        clue_matches = re.findall(r"(\d+)\.\s*([^\n]+)", across_section)
                        for num, clue in clue_matches:
                            current_puzzle["across_clues"][int(num)] = clue.strip()

                    # Extract DOWN clues
                    if "DOWN" in text:
                        down_section = text.split("DOWN")[1]
                        clue_matches = re.findall(r"(\d+)\.\s*([^\n]+)", down_section)
                        for num, clue in clue_matches:
                            current_puzzle["down_clues"][int(num)] = clue.strip()

                    # Store grid representation
                    current_puzzle["grid_text"] += text

                # Look for solutions
                if "Solution for Puzzle" in text:
                    solution_match = re.search(r"Solution for Puzzle (\d+)", text)
                    if solution_match:
                        sol_num = int(solution_match.group(1))
                        # Find the corresponding puzzle
                        for puzzle in puzzles:
                            if puzzle["number"] == sol_num:
                                puzzle["solution_text"] = text
                                # Extract answer words
                                puzzle["answers"] = self._extract_answers(text)
                                break

            # Don't forget the last puzzle
            if current_puzzle:
                puzzles.append(current_puzzle)

        return puzzles

    def _extract_answers(self, solution_text: str) -> Dict[str, List[str]]:
        """Extract answer words from solution text"""
        answers = {"across": [], "down": []}

        # Look for ACROSS ANSWERS section
        if "ACROSS ANSWERS:" in solution_text:
            across_section = solution_text.split("ACROSS ANSWERS:")[1]
            if "DOWN ANSWERS:" in across_section:
                across_section = across_section.split("DOWN ANSWERS:")[0]

            # Extract words (capital letter sequences)
            words = re.findall(r"\b[A-Z]{3,}\b", across_section)
            answers["across"] = words

        # Look for DOWN ANSWERS section
        if "DOWN ANSWERS:" in solution_text:
            down_section = solution_text.split("DOWN ANSWERS:")[1]
            words = re.findall(r"\b[A-Z]{3,}\b", down_section)
            answers["down"] = words

        return answers

    def _validate_uniqueness(self, puzzles: List[Dict]) -> Dict[str, Any]:
        """Validate that each puzzle is unique"""
        logger.info("Validating puzzle uniqueness...")

        duplicates = []
        puzzle_hashes = {}

        for puzzle in puzzles:
            # Create a signature for this puzzle
            signature = self._create_puzzle_signature(puzzle)
            sig_hash = hashlib.md5(
                json.dumps(signature, sort_keys=True).encode()
            ).hexdigest()

            if sig_hash in puzzle_hashes:
                duplicates.append(
                    {
                        "puzzle": puzzle["number"],
                        "duplicate_of": puzzle_hashes[sig_hash],
                        "signature": sig_hash,
                    }
                )
                self.issues.append(
                    f"Puzzle {puzzle['number']} is duplicate of puzzle {puzzle_hashes[sig_hash]}"
                )
            else:
                puzzle_hashes[sig_hash] = puzzle["number"]

        # Calculate uniqueness score
        unique_count = len(puzzles) - len(duplicates)
        uniqueness_ratio = unique_count / len(puzzles) if puzzles else 0

        passed = uniqueness_ratio >= 0.95  # Allow 5% similarity threshold

        if not passed:
            self.issues.append(
                f"Only {unique_count}/{len(puzzles)} puzzles are unique ({uniqueness_ratio*100:.1f}%)"
            )

        return {
            "passed": passed,
            "unique_puzzles": unique_count,
            "total_puzzles": len(puzzles),
            "uniqueness_ratio": uniqueness_ratio,
            "duplicates": duplicates,
        }

    def _create_puzzle_signature(self, puzzle: Dict) -> Dict:
        """Create a unique signature for a puzzle"""
        return {
            "across_clues": sorted(puzzle["across_clues"].values()),
            "down_clues": sorted(puzzle["down_clues"].values()),
            "answers": puzzle.get("answers", {}),
            "clue_count": len(puzzle["across_clues"]) + len(puzzle["down_clues"]),
        }

    def _validate_completeness(self, puzzles: List[Dict]) -> Dict[str, Any]:
        """Validate that all puzzles have required components"""
        logger.info("Validating puzzle completeness...")

        incomplete_puzzles = []

        for puzzle in puzzles:
            issues = []

            # Check for minimum clues
            if len(puzzle["across_clues"]) < 5:
                issues.append(
                    f"Only {len(puzzle['across_clues'])} ACROSS clues (minimum 5)"
                )

            if len(puzzle["down_clues"]) < 5:
                issues.append(
                    f"Only {len(puzzle['down_clues'])} DOWN clues (minimum 5)"
                )

            # Check for solution
            if not puzzle.get("solution_text"):
                issues.append("No solution found")

            # Check for answers
            answers = puzzle.get("answers", {})
            if not answers.get("across") or not answers.get("down"):
                issues.append("Missing answer words in solution")

            if issues:
                incomplete_puzzles.append(
                    {"puzzle": puzzle["number"], "issues": issues}
                )
                for issue in issues:
                    self.issues.append(f"Puzzle {puzzle['number']}: {issue}")

        passed = len(incomplete_puzzles) == 0

        return {
            "passed": passed,
            "complete_puzzles": len(puzzles) - len(incomplete_puzzles),
            "incomplete_puzzles": incomplete_puzzles,
        }

    def _validate_content_quality(self, puzzles: List[Dict]) -> Dict[str, Any]:
        """Validate content quality (no gibberish, real clues)"""
        logger.info("Validating content quality...")

        quality_issues = []

        for puzzle in puzzles:
            issues = []

            # Check for placeholder clues
            all_clues = list(puzzle["across_clues"].values()) + list(
                puzzle["down_clues"].values()
            )

            for clue in all_clues:
                # Check for generic/placeholder clues
                if any(
                    phrase in clue.lower()
                    for phrase in ["letter word", "puzzle", "crossword entry"]
                ):
                    issues.append(f"Generic clue detected: '{clue}'")

                # Check for very short clues
                if len(clue) < 5:
                    issues.append(f"Clue too short: '{clue}'")

            # Check for repeated clues
            clue_counts = defaultdict(int)
            for clue in all_clues:
                clue_counts[clue] += 1

            for clue, count in clue_counts.items():
                if count > 1:
                    issues.append(f"Clue repeated {count} times: '{clue}'")

            if issues:
                quality_issues.append(
                    {
                        "puzzle": puzzle["number"],
                        "issues": issues[:5],  # Limit to first 5 issues
                    }
                )
                self.warnings.extend(
                    [f"Puzzle {puzzle['number']}: {issue}" for issue in issues[:2]]
                )

        passed = len(quality_issues) == 0

        return {
            "passed": passed,
            "quality_score": (
                (len(puzzles) - len(quality_issues)) / len(puzzles) if puzzles else 0
            ),
            "issues": quality_issues,
        }

    def _validate_solutions(self, puzzles: List[Dict]) -> Dict[str, Any]:
        """Validate that solutions contain real words"""
        logger.info("Validating solutions...")

        invalid_solutions = []

        for puzzle in puzzles:
            issues = []
            answers = puzzle.get("answers", {})

            all_words = answers.get("across", []) + answers.get("down", [])

            # Check for nonsense patterns
            for word in all_words:
                # Check if word is all consonants or all vowels
                vowels = set("AEIOU")
                consonants = set("BCDFGHJKLMNPQRSTVWXYZ")

                if len(word) > 3:
                    if all(c in vowels for c in word):
                        issues.append(f"All vowels: {word}")
                    elif all(c in consonants for c in word):
                        issues.append(f"All consonants: {word}")

                    # Check for random letter sequences
                    if len(set(word)) == len(word) and len(word) > 5:
                        issues.append(f"Random sequence: {word}")

            if issues:
                invalid_solutions.append(
                    {"puzzle": puzzle["number"], "issues": issues[:3]}
                )
                self.issues.extend(
                    [f"Puzzle {puzzle['number']}: {issue}" for issue in issues[:2]]
                )

        passed = len(invalid_solutions) == 0

        return {
            "passed": passed,
            "valid_solutions": len(puzzles) - len(invalid_solutions),
            "issues": invalid_solutions,
        }

    def _validate_clue_balance(self, puzzles: List[Dict]) -> Dict[str, Any]:
        """Validate balance between across and down clues"""
        logger.info("Validating clue balance...")

        imbalanced_puzzles = []

        for puzzle in puzzles:
            across_count = len(puzzle["across_clues"])
            down_count = len(puzzle["down_clues"])

            total = across_count + down_count
            if total > 0:
                across_ratio = across_count / total
                down_ratio = down_count / total

                # Check for severe imbalance (more than 70/30 split)
                if across_ratio > 0.7 or down_ratio > 0.7:
                    imbalanced_puzzles.append(
                        {
                            "puzzle": puzzle["number"],
                            "across": across_count,
                            "down": down_count,
                            "ratio": f"{across_ratio*100:.0f}/{down_ratio*100:.0f}",
                        }
                    )
                    self.warnings.append(
                        f"Puzzle {puzzle['number']}: Imbalanced clues ({across_count} across, {down_count} down)"
                    )

        passed = len(imbalanced_puzzles) == 0

        return {
            "passed": passed,
            "balanced_puzzles": len(puzzles) - len(imbalanced_puzzles),
            "imbalanced": imbalanced_puzzles,
        }

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable report"""
        report = f"""
# Crossword Content Validation Report
Generated: {results['timestamp']}
File: {results['file_path']}

## Overall Score: {results['score']}/100
Publish Ready: {'✅ YES' if results['publish_ready'] else '❌ NO'}

## Validation Results:

### Uniqueness Check: {'✅ PASSED' if results['validations']['uniqueness']['passed'] else '❌ FAILED'}
- Unique Puzzles: {results['validations']['uniqueness']['unique_puzzles']}/{results['validations']['uniqueness']['total_puzzles']}
- Uniqueness Rate: {results['validations']['uniqueness']['uniqueness_ratio']*100:.1f}%

### Completeness Check: {'✅ PASSED' if results['validations']['completeness']['passed'] else '❌ FAILED'}
- Complete Puzzles: {results['validations']['completeness']['complete_puzzles']}/{results['puzzle_count']}

### Content Quality: {'✅ PASSED' if results['validations']['content_quality']['passed'] else '❌ FAILED'}
- Quality Score: {results['validations']['content_quality']['quality_score']*100:.1f}%

### Solution Validity: {'✅ PASSED' if results['validations']['solutions']['passed'] else '❌ FAILED'}
- Valid Solutions: {results['validations']['solutions']['valid_solutions']}/{results['puzzle_count']}

### Clue Balance: {'✅ PASSED' if results['validations']['clue_balance']['passed'] else '❌ FAILED'}
- Balanced Puzzles: {results['validations']['clue_balance']['balanced_puzzles']}/{results['puzzle_count']}

## Issues Found: {len(results['issues'])}
"""

        if results["issues"]:
            report += "\n### Critical Issues:\n"
            for issue in results["issues"][:10]:
                report += f"- {issue}\n"

            if len(results["issues"]) > 10:
                report += f"\n... and {len(results['issues']) - 10} more issues\n"

        if results["warnings"]:
            report += "\n### Warnings:\n"
            for warning in results["warnings"][:5]:
                report += f"- {warning}\n"

            if len(results["warnings"]) > 5:
                report += f"\n... and {len(results['warnings']) - 5} more warnings\n"

        report += f"\n\nProcessing time: {results['processing_time']:.2f} seconds\n"

        return report


def main():
    """Run content validation on Volume 3"""
    import sys

    # Import config loader
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent))
    from scripts.config_loader import config

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Build default path from config
        base_dir = Path(config.get_path("file_paths.base_output_dir"))
        series_name = config.get(
            "series_defaults.default_series_name", "Large_Print_Crossword_Masters"
        )
        pdf_filename = config.get(
            "file_paths.pdf_filename_pattern", "{title}_interior_FINAL.pdf"
        ).format(title="Large_Print_Crossword_Masters_-_Volume_3")
        pdf_path = str(base_dir / series_name / "volume_3" / "paperback" / pdf_filename)

    validator = CrosswordContentValidator()
    results = validator.validate_pdf(pdf_path)

    # Generate report
    report = validator.generate_report(results)
    print(report)

    # Save results
    output_path = (
        Path(pdf_path).parent
        / f"content_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nValidation results saved to: {output_path}")

    return 0 if results["publish_ready"] else 1


if __name__ == "__main__":
    exit(main())
